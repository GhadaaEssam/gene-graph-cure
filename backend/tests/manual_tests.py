import requests
import pandas as pd
import numpy as np
import os
import traceback

BASE_URL = "http://localhost:8000/predict"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def load_fixture(name):
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, "rb") as f:
        return f.read()

def post(filename, file_bytes, model="ovarian", include_graph=False):
    response = requests.post(
        BASE_URL,
        files={"geo_features": (filename, file_bytes, "text/csv")},
        data={"model": model},
        params={"include_graph": include_graph}
    )
    print(f"  STATUS: {response.status_code}")
    try:
        body = response.json()
        print(f"  BODY (keys): {list(body.keys()) if isinstance(body, dict) else body}")
    except Exception:
        print(f"  BODY (raw): {response.text[:500]}")
        body = None
    return response, body

def test_happy_path():
    response, body = post("sample.csv", load_fixture("ovarian_sample.csv"), model="ovarian")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "out" in body
    assert "vimp_g" in body
    assert "structured_core_genes" in body
    assert "input_alignment" in body
    print("✓ Happy path passed")

def test_graph_excluded():
    response, body = post("sample.csv", load_fixture("ovarian_sample.csv"), model="ovarian", include_graph=False)
    assert response.status_code == 200
    assert "graph" not in body, "graph matrix should be excluded when include_graph=False"
    assert "graph_shape" in body
    print(f"✓ Graph exclusion passed — shape: {body['graph_shape']}")

def test_partial_gene_coverage():
    response, body = post("sample.csv", load_fixture("partial_genes_sample.csv"), model="ovarian")
    assert response.status_code == 200
    report = body["input_alignment"]
    print(f"  Alignment report summary: match_rate={report['match_rate']}, contract_match_rate={report.get('contract_match_rate')}, missing={report['missing_genes']}, extra={report['extra_genes']}")
    assert report["match_rate"] < 1.0, "match_rate should reflect missing and extra genes"
    assert report["missing_genes"] > 0
    assert report["extra_genes"] > 0
    assert report.get("contract_match_rate") is not None, "contract_match_rate should be present"
    print(f"✓ Partial coverage passed — match_rate: {report['match_rate']:.2f}, contract_match_rate: {report['contract_match_rate']:.2f}")

def test_output_length_matches_samples():
    fixture = load_fixture("ovarian_sample.csv")
    n_samples = pd.read_csv(__import__("io").BytesIO(fixture)).shape[0]
    response, body = post("sample.csv", fixture, model="ovarian")
    assert response.status_code == 200
    assert len(body["out"]) == n_samples, f"Expected {n_samples} predictions, got {len(body['out'])}"
    print(f"✓ Output length matches samples ({n_samples} samples)")

def test_genes_as_rows():
    response, body = post("sample.csv", load_fixture("genes_as_rows_sample.csv"), model="ovarian")
    assert response.status_code == 200
    assert "out" in body
    print("✓ Genes-as-rows orientation passed")

def test_below_match_threshold():
    response, body = post("sample.csv", load_fixture("bad_genes_sample.csv"), model="ovarian")
    assert response.status_code in (400, 422), f"Expected 400 or 422, got {response.status_code}"
    print("✓ Below match threshold correctly rejected")

def test_contract_match_rate_used_for_threshold():
    # partial_genes_sample still passes because contract coverage is above 70%
    # this confirms threshold validation uses contract_match_rate, not match_rate
    response, body = post("sample.csv", load_fixture("partial_genes_sample.csv"), model="ovarian")
    assert response.status_code == 200, "request should pass if contract_match_rate >= 0.70 even if match_rate < 1.0"
    report = body["input_alignment"]
    assert report.get("contract_match_rate", 0) >= 0.70
    print(f"✓ Threshold uses contract_match_rate: {report['contract_match_rate']:.2f}")

def test_unsupported_model_key():
    response, body = post("sample.csv", load_fixture("ovarian_sample.csv"), model="unknown_cancer")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✓ Unsupported model key correctly rejected")

def test_missing_file():
    response = requests.post(
        BASE_URL,
        data={"model": "ovarian"},
        params={"include_graph": False}
    )
    print(f"  STATUS: {response.status_code}")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✓ Missing file correctly rejected")

if __name__ == "__main__":
    tests = [
        test_graph_excluded,
        test_partial_gene_coverage,
        test_contract_match_rate_used_for_threshold
    ]

    failed = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {repr(e)}")
            traceback.print_exc()
            failed.append(test.__name__)

    print(f"\n{'='*50}")
    print(f"{len(tests) - len(failed)}/{len(tests)} tests passed")
    if failed:
        print(f"Failed: {failed}")