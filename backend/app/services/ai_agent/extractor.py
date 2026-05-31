def extract_top_genes(result: dict, k: int = 5):

    genes = result.get("structured_core_genes", [])

    return [
        (
            gene["name"],
            float(gene["score"])
        )
        for gene in genes[:k]
    ]


def extract_top_pathways(result: dict, k: int = 5):

    pathways = result.get("structured_core_pathways", [])

    return [
        (
            pathway["name"],
            float(pathway["weight"])
        )
        for pathway in pathways[:k]
    ]