import io
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.v1.predict import MODEL_FILES, MODEL_INPUTS_DIR, WEIGHTS_DIR
from app.services.model_service_registry import ModelServiceRegistry


INTEGRATION_MODEL_KEYS = ("ovarian", "liver", "breast", "immunotherapy")
SAMPLE_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ovarian_sample.csv"


class UploadedBytes:
    def __init__(self, content: bytes) -> None:
        self.content = content

    async def read(self) -> bytes:
        return self.content


def integration_assets_available() -> bool:
    if not WEIGHTS_DIR.exists() or not MODEL_INPUTS_DIR.exists():
        return False

    for model_key in INTEGRATION_MODEL_KEYS:
        model_file = MODEL_FILES.get(model_key)
        if not model_file:
            return False
        if not (WEIGHTS_DIR / model_file).is_file():
            return False
        if not (MODEL_INPUTS_DIR / model_key).is_dir():
            return False

    return True


def skip_without_integration_assets(test_func):
    return unittest.skipUnless(
        integration_assets_available(),
        "GC-PGE integration assets are missing: expected real weights/ and model_inputs/",
    )(test_func)


def ovarian_sample_bytes() -> bytes:
    if SAMPLE_FIXTURE.is_file():
        return SAMPLE_FIXTURE.read_bytes()

    expected_genes = pd.read_csv(
        MODEL_INPUTS_DIR / "ovarian" / "expected_geo_genes.csv",
    )["gene"].astype(str)
    sample = pd.DataFrame(
        [[f"sample_1", *([0.0] * len(expected_genes))]],
        columns=["sample_id", *expected_genes.tolist()],
    )
    return sample.to_csv(index=False).encode("utf-8")


class GCPGEServiceIntegrationTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.registry = ModelServiceRegistry(
            weights_dir=WEIGHTS_DIR,
            model_inputs_dir=MODEL_INPUTS_DIR,
            model_files=MODEL_FILES,
        )

    @skip_without_integration_assets
    def test_service_instantiation(self):
        for model_key in INTEGRATION_MODEL_KEYS:
            with self.subTest(model_key=model_key):
                service = self.registry.get_service(model_key)

                self.assertIsNotNone(service.model)
                self.assertIsNotNone(service.gene_aligner)

    @skip_without_integration_assets
    async def test_predict_base_returns_valid_response(self):
        result = await self._predict_ovarian(include_graph=False)

        self.assertIn("out", result)
        self.assertIn("vimp_g", result)
        self.assertIn("structured_core_genes", result)
        self.assertIn("input_alignment", result)

    @skip_without_integration_assets
    async def test_alignment_report_present(self):
        result = await self._predict_ovarian()
        report = result["input_alignment"]

        self.assertGreaterEqual(report["match_rate"], 0.0)
        self.assertLessEqual(report["match_rate"], 1.0)
        self.assertIsInstance(report["missing_gene_names"], list)
        self.assertIsInstance(report["matched_gene_names"], list)

    @skip_without_integration_assets
    async def test_low_match_rate_raises(self):
        service = self.registry.get_service("ovarian")
        bad_file = b"sample_id,NOT_A_MODEL_GENE_1,NOT_A_MODEL_GENE_2\nsample_1,1.0,2.0\n"

        with self.assertRaisesRegex(ValueError, "match.*minimum"):
            await service.predict_from_files(
                {"geo_features": UploadedBytes(bad_file)},
                include_graph=False,
            )

    @skip_without_integration_assets
    async def test_graph_excluded_when_flag_false(self):
        result = await self._predict_ovarian(include_graph=False)

        self.assertNotIn("graph", result)
        self.assertIn("graph_shape", result)

    @skip_without_integration_assets
    async def test_output_length_matches_samples(self):
        sample_bytes = ovarian_sample_bytes()
        result = await self._predict_ovarian(sample_bytes=sample_bytes)
        n_samples = pd.read_csv(io.BytesIO(sample_bytes)).shape[0]

        self.assertEqual(len(result["out"]), n_samples)

    async def _predict_ovarian(
        self,
        include_graph: bool = True,
        sample_bytes: bytes | None = None,
    ) -> dict:
        service = self.registry.get_service("ovarian")
        content = sample_bytes if sample_bytes is not None else ovarian_sample_bytes()
        return await service.predict_from_files(
            {"geo_features": UploadedBytes(content)},
            include_graph=include_graph,
        )


if __name__ == "__main__":
    unittest.main()
