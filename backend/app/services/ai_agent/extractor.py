import numpy as np

def get_top_pathways(weights, pathway_names, k=5):

    weights = np.array(weights)

    idx = weights.argsort()[-k:][::-1]

    return [(pathway_names[i], float(weights[i])) for i in idx]

def get_top_gene_pairs(graph, gene_names, k=10):

    import numpy as np
    graph = np.array(graph)

    edges = []

    for i in range(len(graph)):
        for j in range(i+1, len(graph)):
            edges.append((gene_names[i], gene_names[j], graph[i][j]))

    edges.sort(key=lambda x: x[2], reverse=True)

    return edges[:k]