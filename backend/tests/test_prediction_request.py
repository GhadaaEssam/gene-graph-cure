import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.predict import ModelKey, PredictionRequest


class PredictionRequestTest(unittest.TestCase):
    def test_breast_multiomics_requires_all_optional_omics_files(self):
        with self.assertRaisesRegex(ValueError, "breast_multiomics requires"):
            PredictionRequest(
                model=ModelKey.breast_multiomics,
                geo_features=object(),
                meth_features=object(),
                cnv_features=object(),
            )

    def test_non_multiomics_rejects_optional_omics_files(self):
        with self.assertRaisesRegex(ValueError, "only supported"):
            PredictionRequest(
                model=ModelKey.breast,
                geo_features=object(),
                meth_features=object(),
            )

    def test_uploaded_files_matches_service_payload(self):
        request = PredictionRequest(
            model=ModelKey.breast_multiomics,
            geo_features="rna",
            meth_features="meth",
            cnv_features="cnv",
            snv_features="snv",
            include_graph=False,
        )

        self.assertFalse(request.include_graph)
        self.assertEqual(request.uploaded_files, {
            "geo_features": "rna",
            "meth_features": "meth",
            "cnv_features": "cnv",
            "snv_features": "snv",
        })


if __name__ == "__main__":
    unittest.main()
