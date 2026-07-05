from pathlib import Path
from threading import Lock

from app.services.gc_pge_service import GC_PGE_Service


class ModelServiceRegistry:
    def __init__(
        self,
        weights_dir: Path,
        model_inputs_dir: Path,
        model_files: dict[str, str],
    ):
        self.weights_dir = weights_dir
        self.model_inputs_dir = model_inputs_dir
        self.model_files = model_files
        self.services: dict[str, GC_PGE_Service] = {}
        self._lock = Lock()

    @property
    def available_models(self) -> list[str]:
        return sorted(self.model_files.keys())

    def get_service(self, model_key: str) -> GC_PGE_Service:
        normalized_key = self._normalize_model_key(model_key)

        with self._lock:
            if normalized_key not in self.services:
                model_path = self.weights_dir / self.model_files[normalized_key]
                if not model_path.exists():
                    raise FileNotFoundError(f"Model weights not found: {model_path}")

                self.services[normalized_key] = GC_PGE_Service(
                    model_path=str(model_path),
                    static_inputs_dir=self.get_static_inputs_dir(normalized_key),
                )

            return self.services[normalized_key]

    def get_static_inputs_dir(self, model_key: str) -> Path:
        normalized_key = self._normalize_model_key(model_key)
        static_inputs_dir = self.model_inputs_dir / normalized_key
        if not static_inputs_dir.exists():
            raise FileNotFoundError(
                f"Static model inputs directory not found: {static_inputs_dir}"
            )
        return static_inputs_dir

    def _normalize_model_key(self, model_key: str) -> str:
        normalized_key = model_key.strip().lower()
        if normalized_key not in self.model_files:
            available = ", ".join(self.available_models)
            raise ValueError(
                f"Unsupported model '{model_key}'. Available models: {available}"
            )
        return normalized_key
