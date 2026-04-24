import React, { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
// 👇 هنجهزه للباك
import { getGraphData } from "../api/graphApi";

const GraphVisualization = ({ job_id }) => {
  const cyRef = useRef(null);
  const [elements, setElements] = useState([]);

  // =========================
  // 1️⃣ Load Data (Mock / API)
  // =========================
  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const data = await getGraphData(job_id);
        setElements(data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchGraph();
  }, [job_id]);

  // =========================
  // 2️⃣ Init Cytoscape
  // =========================
  useEffect(() => {
    if (!elements.length) return;

    const cy = cytoscape({
      container: cyRef.current,

      elements,

      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "#94a3b8",
            color: "#000",
            "text-valign": "center",
            "text-halign": "center",
            width: 30,
            height: 30
          }
        },

        // 👇 genes المهمة
        {
          selector: '[type = "gene"][highlight = "true"]',
          style: {
            "background-color": "#ef4444",
            width: 50,
            height: 50
          }
        },

        // 👇 pathways
        {
          selector: '[type = "pathway"]',
          style: {
            "background-color": "#22c55e",
            shape: "round-rectangle",
            width: 60,
            height: 40
          }
        },

        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#cbd5e1"
          }
        }
      ],

      layout: {
        name: "cose"
      },

      zoomingEnabled: true,
      userZoomingEnabled: true,
      panningEnabled: true,
      userPanningEnabled: true
    });

    cy.on("tap", "node", (event) => {
      const node = event.target;
      console.log(node.data());
    });

    return () => cy.destroy();
  }, [elements]);

  return (
    <div
      ref={cyRef}
      style={{
        width: "100%",
        height: "500px",
        border: "1px solid #ddd",
        borderRadius: "10px"
      }}
    />
  );
};

export default GraphVisualization;