export const mockGraphData = {
  nodes: [
    { id: "TP53", type: "gene", score: 0.95, vimp: 0.98, description: "Tumor suppressor gene", highlight: true },
    { id: "BRCA1", type: "gene", score: 0.89, vimp: 0.72, description: "DNA repair gene" },
    { id: "EGFR", type: "gene", score: 0.78, vimp: 0.65, description: "Growth factor receptor" },
    { id: "MYC", type: "gene", score: 0.92, vimp: 0.88, description: "Oncogene regulator" },
    { id: "PTEN", type: "gene", score: 0.81, vimp: 0.6, description: "Tumor suppressor" },
    { id: "AKT1", type: "gene", score: 0.77, vimp: 0.55, description: "Signaling gene" }
  ],

  links: [
    { source: "TP53", target: "BRCA1", relation: "PPI", confidence: 0.9 },
    { source: "TP53", target: "EGFR", relation: "Homology", confidence: 0.7 },
    { source: "EGFR", target: "AKT1", relation: "Pathway", confidence: 0.95 },
    { source: "PTEN", target: "AKT1", relation: "PPI", confidence: 0.85 },
    { source: "MYC", target: "TP53", relation: "PPI", confidence: 0.8 },
    { source: "BRCA1", target: "PTEN", relation: "Homology", confidence: 0.75 }
  ]
};