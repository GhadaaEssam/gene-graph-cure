export const mockGraphData = {
  nodes: [
    {
      id: "TP53",
      type: "gene",
      score:2.5,
      description: "Tumor suppressor gene",
      highlight: true,
    },
    {
      id: "BRCA1",
      type: "gene",
      score: 0.89,
      description: "DNA repair gene",
    },
    {
      id: "EGFR",
      type: "gene",
      score: 0.78,
      description: "Growth factor receptor",
    },
    {
      id: "PI3K-AKT",
      type: "pathway",
      weight: 1.4,
      description: "Cell survival signaling pathway",
    },
    {
      id: "Cell_Cycle",
      type: "pathway",
      weight: 1.1,
      description: "Cell cycle regulation pathway",
    },
    {
      id: "Apoptosis",
      type: "pathway",
      weight: 1.3,
      description: "Programmed cell death pathway",
    },
    {
      id: "Drug_A",
      type: "drug",
      score: 0.82,
      description: "Targeted therapy drug A",
    },
    {
      id: "Drug_B",
      type: "drug",
      score: 0.76,
      description: "Chemotherapy drug B",
    },
  ],

  links: [
    {
      source: "TP53",
      target: "BRCA1",
      correlation: 0.88,
    },
    {
      source: "TP53",
      target: "Apoptosis",
      correlation: 0.92,
    },
    {
      source: "BRCA1",
      target: "Cell_Cycle",
      correlation: 0.81,
    },
    {
      source: "EGFR",
      target: "PI3K-AKT",
      correlation: 0.9,
    },
    {
      source: "PI3K-AKT",
      target: "Cell_Cycle",
      correlation: 0.87,
    },
    {
      source: "Apoptosis",
      target: "Drug_A",
      correlation: 0.85,
    },
    {
      source: "EGFR",
      target: "Drug_B",
      correlation: 0.74,
    },
    {
      source: "BRCA1",
      target: "Drug_A",
      correlation: 0.79,
    },
  ],
};