export const buildGraphData = (apiData) => {
  const nodes = [];
  const links = [];

  // ===== Genes =====
  apiData?.structured_core_genes?.forEach((gene) => {
    nodes.push({
      id: gene.name,
      type: "gene",
      score: gene.score,
      correlation: gene.correlation,
      highlight: gene.is_anchor,
    });
  });

  // ===== Pathways =====
  apiData?.structured_core_pathways?.forEach((pathway) => {
    nodes.push({
      id: pathway.name,
      type: "pathway",
      weight: pathway.weight,
    });
  });

  // ===== Links =====
  apiData?.structured_core_genes?.forEach((gene) => {
    apiData?.structured_core_pathways?.forEach((pathway) => {
      links.push({
        source: gene.name,
        target: pathway.name,
      });
    });
  });

  return {
    nodes,
    links,
  };
};