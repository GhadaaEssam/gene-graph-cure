import React, { useEffect, useState } from "react";
import ForceGraph3D from "react-force-graph-3d";
import { getGraphData } from "../api/graphApi";

const GraphVisualization = ({ job_id }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  useEffect(() => {
    const fetchData = async () => {
      const data = await getGraphData(job_id);
      setGraphData(data);
    };

    fetchData();
  }, [job_id]);

  return (
    <div style={{ height: "600px", border: "1px solid #ddd", borderRadius: "10px" }}>
      <ForceGraph3D
        graphData={graphData}

        // 👇 لون النود
        nodeColor={(node) => {
          if (node.type === "pathway") return "#22c55e";
          if (node.highlight) return "#ef4444";
          return "#94a3b8";
        }}

        // 👇 حجم النود
        nodeVal={(node) => {
          if (node.type === "pathway") return 10;
          if (node.highlight) return 8;
          return 4;
        }}

        // 👇 اسم النود
        nodeLabel="id"

        // 👇 لما تدوسي
        onNodeClick={(node) => {
          console.log(node);
        }}
      />
    </div>
  );
};

export default GraphVisualization;