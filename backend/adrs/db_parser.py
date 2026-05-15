import pandas as pd
import math
import json
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_gdsc(ic50_csv_path: str, compounds_csv_path: str) -> dict:
    """
    Parse GDSC2 IC50 and compound annotation files.
    Returns a dict keyed by DRUG_NAME (uppercase) with IC50 stats,
    gene targets, and pathway info.

    Args:
        ic50_csv_path:      path to GDSC2_fitted_dose_response.csv
        compounds_csv_path: path to screened_compounds_rel_8.5.csv

    Returns:
        {
          "ERLOTINIB": {
              "drug_name": "Erlotinib",
              "mean_ic50": 1.23,          # in µM, converted from LN_IC50
              "min_ic50":  0.10,
              "max_ic50":  8.50,
              "mean_auc":  0.75,
              "targets":   ["EGFR"],      # cleaned gene symbols only
              "pathway":   "EGFR signaling",
              "cancer_type_ic50": {       # mean IC50 per cancer type
                  "Lung": 0.85,
                  "Breast": 2.10, ...
              }
          }, ...
        }
    """
    logger.info(f"Loading GDSC2 IC50 from {ic50_csv_path}")
    ic50_df = pd.read_csv(ic50_csv_path)

    logger.info(f"Loading compound annotations from {compounds_csv_path}")
    comp_df = pd.read_csv(compounds_csv_path)

    # ── 1. Convert LN_IC50 → IC50 in µM ──────────────────────────
    ic50_df["IC50_uM"] = ic50_df["LN_IC50"].apply(
        lambda x: math.exp(x) if pd.notna(x) else None
    )

    # ── 2. Compute per-drug summary stats ─────────────────────────
    drug_stats = (
        ic50_df.groupby("DRUG_NAME")
        .agg(
            mean_ic50=("IC50_uM", "mean"),
            min_ic50=("IC50_uM", "min"),
            max_ic50=("IC50_uM", "max"),
            mean_auc=("AUC", "mean"),
        )
        .reset_index()
    )

    # ── 3. Compute mean IC50 per drug per cancer type ─────────────
    cancer_ic50 = (
        ic50_df.groupby(["DRUG_NAME", "CANCER_TYPE"])["IC50_uM"]
        .mean()
        .reset_index()
    )
    cancer_ic50_dict = {}
    for drug, grp in cancer_ic50.groupby("DRUG_NAME"):
        cancer_ic50_dict[drug] = dict(
            zip(grp["CANCER_TYPE"], grp["IC50_uM"].round(4))
        )

    # ── 4. Merge compound annotations ─────────────────────────────
    # Use left join — every IC50 drug exists in comp file
    merged = drug_stats.merge(
        comp_df[["DRUG_NAME", "TARGET", "TARGET_PATHWAY"]],
        on="DRUG_NAME",
        how="left"
    )

    # ── 5. Clean TARGET column → list of gene symbols ─────────────
    def extract_gene_targets(target_str: str) -> list:
        """
        Keep only entries that look like gene symbols (short, uppercase).
        Drop mechanism descriptions like 'DNA crosslinker', 'Antimetabolite'.
        A gene symbol: all uppercase OR has digits, length <= 10, no spaces.
        """
        if pd.isna(target_str):
            return []
        candidates = [t.strip() for t in str(target_str).split(",")]
        genes = []
        for c in candidates:
            # Gene symbols: no spaces, not too long, not purely lowercase
            if (
                " " not in c
                and len(c) <= 12
                and c == c.upper()
                and len(c) >= 2
            ):
                genes.append(c)
        return genes

    # ── 6. Build final index ───────────────────────────────────────
    gdsc_index = {}
    for _, row in merged.iterrows():
        drug_name = row["DRUG_NAME"]
        # Skip numeric IDs that slipped through
        if str(drug_name).strip().isdigit():
            continue
        key = drug_name.upper()  # uppercase key for case-insensitive lookup

        gdsc_index[key] = {
            "drug_name":        drug_name,
            "mean_ic50":        round(row["mean_ic50"], 4) if pd.notna(row["mean_ic50"]) else None,
            "min_ic50":         round(row["min_ic50"],  4) if pd.notna(row["min_ic50"])  else None,
            "max_ic50":         round(row["max_ic50"],  4) if pd.notna(row["max_ic50"])  else None,
            "mean_auc":         round(row["mean_auc"],  4) if pd.notna(row["mean_auc"])  else None,
            "targets":          extract_gene_targets(row.get("TARGET", "")),
            "pathway":          row.get("TARGET_PATHWAY", "Unknown"),
            "cancer_type_ic50": cancer_ic50_dict.get(drug_name, {}),
        }

    logger.info(f"GDSC index built: {len(gdsc_index)} drugs")
    return gdsc_index


def save_gdsc_index(gdsc_index: dict, output_path: str) -> None:
    """Save parsed GDSC index to JSON for fast loading at runtime."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(gdsc_index, f, indent=2)
    logger.info(f"GDSC index saved to {output_path}")


def load_gdsc_index(json_path: str) -> dict:
    """Load pre-parsed GDSC index from JSON. Use this at runtime, not parse_gdsc()."""
    with open(json_path) as f:
        return json.load(f)


def query_dgidb(gene_symbol: str) -> list:
    """
    Fallback: query DGIdb API for drugs targeting a gene.
    Returns list of drug name strings.
    Called only when DrugBank has zero results for a gene.
    """
    url = f"https://dgidb.org/api/v2/interactions.json?genes={gene_symbol}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        matched = data.get("matchedTerms", [])
        if not matched:
            return []
        drugs = [
            i["drugName"]
            for i in matched[0].get("interactions", [])
            if i.get("drugName")
        ]
        logger.info(f"DGIdb fallback for {gene_symbol}: {len(drugs)} drugs found")
        return drugs
    except requests.exceptions.Timeout:
        logger.warning(f"DGIdb timeout for gene {gene_symbol} — skipping fallback")
        return []
    except Exception as e:
        logger.warning(f"DGIdb error for gene {gene_symbol}: {e}")
        return []
    

import xml.etree.ElementTree as ET


def parse_drugbank(xml_path: str) -> dict:
    """
    Parse DrugBank full_database.xml using iterparse (memory-safe).
    Extracts small molecule drugs only.
    Run ONCE at setup time — never at request time.
    """
    NS = "http://www.drugbank.ca"

    def tag(name):
        return f"{{{NS}}}{name}"

    drugbank_index = {}
    current        = {}
    inside_drug    = False
    drug_type      = None

    logger.info(f"Parsing DrugBank XML: {xml_path} (this takes 2-5 minutes)")

    for event, elem in ET.iterparse(xml_path, events=("start", "end")):

        if event == "start" and elem.tag == tag("drug"):
            drug_type   = elem.get("type", "")
            inside_drug = True
            current     = {
                "drug_id":   "",
                "drug_name": "",
                "targets":   [],
                "pathways":  [],
                "mechanism": ""
            }

        if not inside_drug:
            continue

        if event == "end" and elem.tag == tag("drugbank-id"):
            if elem.get("primary") == "true" and not current["drug_id"]:
                current["drug_id"] = elem.text or ""

        if event == "end" and elem.tag == tag("name") and not current["drug_name"]:
            current["drug_name"] = elem.text or ""

        if event == "end" and elem.tag == tag("mechanism-of-action"):
            current["mechanism"] = (elem.text or "")[:500]

        if event == "end" and elem.tag == tag("polypeptide"):
            gene = elem.find(f"{{{NS}}}gene-name")
            if gene is not None and gene.text:
                symbol = gene.text.strip()
                if symbol and symbol not in current["targets"]:
                    current["targets"].append(symbol)

        if event == "end" and elem.tag == tag("pathway"):
            pname = elem.find(f"{{{NS}}}name")
            if pname is not None and pname.text:
                name = pname.text.strip()
                if name and name not in current["pathways"]:
                    current["pathways"].append(name)

        if event == "end" and elem.tag == tag("drug"):
            inside_drug = False
            if (
                drug_type == "small molecule"
                and current["drug_name"]
                and current["drug_id"]
            ):
                key = current["drug_name"].upper()
                drugbank_index[key] = {
                    "drug_id":   current["drug_id"],
                    "drug_name": current["drug_name"],
                    "targets":   current["targets"],
                    "pathways":  current["pathways"],
                    "mechanism": current["mechanism"]
                }
            elem.clear()
            current     = {}
            inside_drug = False

    logger.info(f"DrugBank index built: {len(drugbank_index)} small molecule drugs")
    return drugbank_index


def save_drugbank_index(drugbank_index: dict, output_path: str) -> None:
    """Save parsed DrugBank index to JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(drugbank_index, f, indent=2, ensure_ascii=False)
    logger.info(f"DrugBank index saved to {output_path}")


def load_drugbank_index(json_path: str) -> dict:
    """Load pre-parsed DrugBank index. Use this at runtime."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)