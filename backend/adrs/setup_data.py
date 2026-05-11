"""
Run this script ONCE to parse raw data files and save indexes.
Never run at request time — only during setup.

Usage:
    python -m backend.adrs.setup_data
"""
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from backend.adrs.db_parser import parse_gdsc, save_gdsc_index

# ── Paths ─────────────────────────────────────────────────────────
DATA_DIR    = Path("backend/adrs/data")
IC50_FILE   = DATA_DIR / "GDSC2_fitted_dose_response.csv"
COMP_FILE   = DATA_DIR / "screened_compounds_rel_8.5.csv"
GDSC_OUT    = DATA_DIR / "gdsc_index.json"

def run():
    # ── GDSC ──────────────────────────────────────────────────────
    print("\n── Parsing GDSC data ──────────────────────────────────")
    gdsc = parse_gdsc(str(IC50_FILE), str(COMP_FILE))
    save_gdsc_index(gdsc, str(GDSC_OUT))

    # Quick verification
    print(f"✓ GDSC drugs indexed: {len(gdsc)}")
    sample = next(iter(gdsc.values()))
    print(f"✓ Sample entry: {sample['drug_name']} | IC50={sample['mean_ic50']} | targets={sample['targets']}")

    # ── DrugBank (add this block once XML arrives) ─────────────────
    drugbank_xml = DATA_DIR / "full_database.xml"
    if drugbank_xml.exists():
        print("\n── Parsing DrugBank XML ───────────────────────────────")
        from backend.adrs.db_parser import parse_drugbank, save_drugbank_index
        db = parse_drugbank(str(drugbank_xml))
        save_drugbank_index(db, str(DATA_DIR / "drugbank_index.json"))
        print(f"✓ DrugBank drugs indexed: {len(db)}")
    else:
        print("\n⚠ DrugBank XML not found — skipping (run again once file arrives)")

if __name__ == "__main__":
    run()