import logging
from typing import Dict

logger = logging.getLogger(__name__)


def normalize_delta_e(delta_e: Dict[str, float]) -> Dict[str, float]:
    """
    Min-max normalize raw ΔE values from GC-PGE to [0.0, 1.0].
    Must be called FIRST in the pipeline before any scoring.

    Args:
        delta_e: raw pathway rewiring scores e.g.
                 {'EGFR_signaling': 0.82, 'PI3K_AKT': 0.61}

    Returns:
        Same dict with all values scaled to [0.0, 1.0]
    """
    if not delta_e:
        logger.warning("normalize_delta_e received empty dict — returning empty")
        return {}

    values = list(delta_e.values())
    min_v  = min(values)
    max_v  = max(values)

    # Edge case: all values identical → everything scores 1.0
    if max_v == min_v:
        logger.warning("All ΔE values are identical — setting all normalized scores to 1.0")
        return {k: 1.0 for k in delta_e}

    normalized = {
        k: round((v - min_v) / (max_v - min_v), 4)
        for k, v in delta_e.items()
    }

    logger.info(f"ΔE normalized: {len(normalized)} pathways, "
                f"range [{min_v:.3f}, {max_v:.3f}] → [0.0, 1.0]")
    return normalized