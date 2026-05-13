import logging
from typing import Dict, List, Optional

import networkx as nx

from backend.app.schemas.adrs import ADRSRequest, ADRSResponse
from ...adrs.cache import get_cached_result, save_recommendations
from ...adrs.recommender import rank_drugs

logger = logging.getLogger(__name__)


class ADRSServiceError(Exception):
    """Exception raised when ADRS cannot produce a recommendation."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class ADRSService:
    """Internal ADRS service layer.

    Encapsulates ADRS orchestration, cache access, and graph state.
    """

    def __init__(
        self,
        graph: nx.Graph,
        gdsc_index: Dict[str, Dict],
        session_factory: Optional[object] = None
    ):
        self.graph = graph
        self.gdsc_index = gdsc_index
        self.session_factory = session_factory

    def recommend(self, request: ADRSRequest) -> ADRSResponse:
        """Run the ADRS recommendation workflow and return a typed response."""
        if self.session_factory is not None:
            cached = self._get_cached_result(request.patient_id, request.resistant_drug)
            if cached is not None:
                return self._build_response(request, cached, cached=True)

        result = rank_drugs(
            G=self.graph,
            gdsc_index=self.gdsc_index,
            delta_e=request.delta_e,
            core_genes=request.core_genes,
            resistant_drug=request.resistant_drug,
            top_n=request.top_n,
            threshold=request.threshold
        )

        if result.get("error") and not result.get("recommendations"):
            raise ADRSServiceError(
                result.get("code", "UNKNOWN_ERROR"),
                result.get("error", "ADRS pipeline failed")
            )

        if self.session_factory is not None and result.get("recommendations"):
            self._save_recommendations(request.patient_id, request.resistant_drug, result)

        return self._build_response(request, result, cached=False)

    def health(self) -> Dict[str, object]:
        """Return service health and graph load metadata."""
        if self.graph is None:
            return {
                "status": "unavailable",
                "reason": "Graph not loaded",
                "db_cache": "connected" if self.session_factory else "disconnected"
            }

        drug_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "drug"]
        gene_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "gene"]
        pw_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "pathway"]

        return {
            "status": "ok",
            "drugs_loaded": len(drug_nodes),
            "genes_loaded": len(gene_nodes),
            "pathways_loaded": len(pw_nodes),
            "graph_nodes": self.graph.number_of_nodes(),
            "graph_edges": self.graph.number_of_edges(),
            "db_cache": "connected" if self.session_factory else "disconnected"
        }

    def _build_response(
        self,
        request: ADRSRequest,
        result: Dict[str, object],
        cached: bool
    ) -> ADRSResponse:
        """Build a typed ADRSResponse from pipeline output."""
        return ADRSResponse(
            patient_id=request.patient_id,
            resistant_drug=request.resistant_drug,
            recommendations=result.get("recommendations", []),
            llm_context=result.get("llm_context"),
            meta=result.get("meta"),
            cached=cached
        )

    def _get_cached_result(
        self,
        patient_id: str,
        resistant_drug: str
    ) -> Optional[Dict[str, object]]:
        """Return a cached recommendation result if available."""
        try:
            with self.session_factory() as session:
                return get_cached_result(patient_id, resistant_drug, session)
        except Exception as exc:
            logger.warning(
                f"ADRS cache lookup failed for patient={patient_id} drug={resistant_drug}: {exc}"
            )
            return None

    def _save_recommendations(
        self,
        patient_id: str,
        resistant_drug: str,
        result: Dict[str, object]
    ) -> bool:
        """Persist recommendation results to the ADRS cache."""
        try:
            with self.session_factory() as session:
                return save_recommendations(patient_id, resistant_drug, result, session)
        except Exception as exc:
            logger.warning(
                f"ADRS cache save failed for patient={patient_id} drug={resistant_drug}: {exc}"
            )
            return False

    @classmethod
    def from_app_state(cls, app: object, session_factory: Optional[object] = None) -> "ADRSService":
        """Create a service from FastAPI app state."""
        graph = getattr(app.state, "graph", None)
        gdsc_index = getattr(app.state, "gdsc_index", None)

        if graph is None or gdsc_index is None:
            raise ValueError("ADRS graph and GDSC index must be loaded on app state")

        return cls(graph=graph, gdsc_index=gdsc_index, session_factory=session_factory)
