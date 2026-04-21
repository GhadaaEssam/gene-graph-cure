export const getGraphData = async (job_id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        nodes: [
          { id: "TP53", type: "gene", highlight: true },
          { id: "KRAS", type: "gene", highlight: true },
          { id: "GENE3", type: "gene" },
          { id: "MAPK", type: "pathway" }
        ],
        links: [
          { source: "TP53", target: "MAPK" },
          { source: "KRAS", target: "MAPK" },
          { source: "GENE3", target: "TP53" }
        ]
      });
    }, 1000);
  });
};