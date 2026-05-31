import React, { useEffect, useState, useRef } from "react";
import ForceGraph3D from "react-force-graph-3d";

import { mockGraphData } from "../mock/mockGraphData";

const GraphVisualization = ({ job_id }) => {
  const fgRef = useRef();

  const [graphData, setGraphData] = useState({
    nodes: [],
    links: [],
  });

  const [selectedNode, setSelectedNode] = useState(null);
  const [hoverNode, setHoverNode] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [focusedNode, setFocusedNode] = useState(null);

  // =========================
  // LOAD MOCK DATA
  // =========================
  useEffect(() => {
    try {
      setLoading(true);

      // لاحقًا هنبدلها بالـ API
      setGraphData(mockGraphData);

      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to load graph data");
    } finally {
      setLoading(false);
    }
  }, [job_id]);

  // =========================
  // GET CONNECTED NODES
  // =========================
  const getConnectedNodes = (node, links) => {
    const connected = new Set();

    links.forEach((link) => {
      const source =
        typeof link.source === "object"
          ? link.source.id
          : link.source;

      const target =
        typeof link.target === "object"
          ? link.target.id
          : link.target;

      if (source === node.id) connected.add(target);
      if (target === node.id) connected.add(source);
    });

    return connected;
  };

  // =========================
  // RESET CAMERA
  // =========================
  const resetCamera = () => {
    setFocusedNode(null);
    setSelectedNode(null);

    if (fgRef.current) {
      fgRef.current.cameraPosition(
        { x: 0, y: 0, z: 300 },
        { x: 0, y: 0, z: 0 },
        1200
      );
    }
  };

  // =========================
  // EXPORT GRAPH IMAGE
  // =========================
  const exportGraphImage = () => {
  if (!fgRef.current) return;

  requestAnimationFrame(() => {
    const canvas = fgRef.current.renderer().domElement;

    const image = canvas.toDataURL("image/png");

    const link = document.createElement("a");

    link.href = image;
    link.download = "genegraph-visualization.png";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
  });
};

  // =========================
  // LOADING STATE
  // =========================
  if (loading) {
    return (
      <div style={centerBox("#f8fafc", "#475569")}>
        Loading graph visualization...
      </div>
    );
  }

  // =========================
  // ERROR STATE
  // =========================
  if (error) {
    return (
      <div style={centerBox("#fef2f2", "#b91c1c")}>
        {error}
      </div>
    );
  }

  // =========================
  // EMPTY STATE
  // =========================
  if (!graphData.nodes.length) {
    return (
      <div style={centerBox("#f8fafc", "#64748b")}>
        No biological relationships found
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        gap: "20px",
        height: "650px",
      }}
    >
      {/* ================= GRAPH ================= */}
      <div
        style={{
          flex: 1,
          position: "relative",
          border: "1px solid #e5e7eb",
          borderRadius: "16px",
          overflow: "hidden",
          background: "#f8fafc",
        }}
      >
        {/* ================= BUTTONS ================= */}
        <div
          style={{
            position: "absolute",
            top: "20px",
            left: "20px",
            zIndex: 10,
            display: "flex",
            gap: "10px",
          }}
        >
          {/* RESET BUTTON */}
          <button
            onClick={resetCamera}
            style={{
              padding: "10px 16px",
              borderRadius: "10px",
              border: "none",
              background: "#0f172a",
              color: "white",
              fontWeight: "600",
              cursor: "pointer",
              boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
            }}
          >
            Reset View
          </button>

          {/* EXPORT BUTTON */}
          <button
            onClick={exportGraphImage}
            style={{
              padding: "10px 16px",
              borderRadius: "10px",
              border: "none",
              background: "#2563eb",
              color: "white",
              fontWeight: "600",
              cursor: "pointer",
              boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
            }}
          >
            Export Graph
          </button>
        </div>

        <ForceGraph3D
          ref={fgRef}
          graphData={graphData}
          backgroundColor="#f8fafc"

          // ================= NODE COLORS =================
          nodeColor={(node) => {
  // ===== Focus Mode =====
  if (focusedNode) {
    const connected = getConnectedNodes(
      focusedNode,
      graphData.links
    );

    const isFocused = node.id === focusedNode.id;
    const isConnected = connected.has(node.id);

    if (isFocused) return "#f59e0b";

    if (isConnected) return "#3b82f6";

    return "#cbd5e1";
  }

  // ===== Pathways =====
  if (node.type === "pathway") {
    return "#22c55e";
  }

  // ===== Drugs =====
  if (node.type === "drug") {
    return "#a855f7";
  }

  // ===== Importance-Based Colors =====
  const score = node.score || 0;

  if (score >= 0.9) return "#dc2626"; // Strong red

  if (score >= 0.75) return "#f97316"; // Orange

  if (score >= 0.5) return "#3b82f6"; // Blue

  return "#94a3b8"; // Gray
}}

          // ================= NODE SIZE =================
          nodeVal={(node) => {
  const isFocused =
    focusedNode && node.id === focusedNode.id;

  if (isFocused) return 30;

  if (focusedNode) return 8;

  // ===== Pathways =====
  if (node.type === "pathway") {
    return (node.weight || 1) * 22;
  }

  // ===== Score-based scaling =====
  const score = node.score || 0.3;

  return score * 30;
}}

          // ================= LINKS =================
          linkColor={(link) => {
            if (!focusedNode) return "#94a3b8";

            const source =
              typeof link.source === "object"
                ? link.source.id
                : link.source;

            const target =
              typeof link.target === "object"
                ? link.target.id
                : link.target;

            const isConnected =
              source === focusedNode.id ||
              target === focusedNode.id;

            return isConnected ? "#3b82f6" : "#e2e8f0";
          }}

          linkWidth={(link) => {
            if (!focusedNode) return 1.5;

            const source =
              typeof link.source === "object"
                ? link.source.id
                : link.source;

            const target =
              typeof link.target === "object"
                ? link.target.id
                : link.target;

            const isConnected =
              source === focusedNode.id ||
              target === focusedNode.id;

            return isConnected ? 4 : 1;
          }}

          linkOpacity={(link) => {
            if (!focusedNode) return 0.6;

            const source =
              typeof link.source === "object"
                ? link.source.id
                : link.source;

            const target =
              typeof link.target === "object"
                ? link.target.id
                : link.target;

            const isConnected =
              source === focusedNode.id ||
              target === focusedNode.id;

            return isConnected ? 1 : 0.15;
          }}

          // ================= LABELS =================
          nodeLabel={(node) => `
${node.id}

Type: ${node.type}
Score: ${node.score || "N/A"}

${node.description || ""}
          `}

          // ================= INTERACTIONS =================
          onNodeHover={(node) => {
            setHoverNode(node);
          }}

          onNodeClick={(node) => {
            setSelectedNode(node);
            setFocusedNode(node);

            // ================= CAMERA FOCUS =================
            if (fgRef.current && node) {
              const distance = 120;

              fgRef.current.cameraPosition(
                {
                  x: node.x + distance,
                  y: node.y + distance,
                  z: node.z + distance,
                },
                node,
                1200
              );
            }
          }}

          enableNodeDrag={true}
          enableNavigationControls={true}
          showNavInfo={false}
        />
      </div>

      {/* ================= SIDEBAR ================= */}
      <div
        style={{
          width: "320px",
          padding: "20px",
          borderRadius: "16px",
          background: "#ffffff",
          border: "1px solid #e5e7eb",
          boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
        }}
      >
        <h3
          style={{
            marginBottom: "20px",
            fontWeight: "700",
          }}
        >
          Node Details
        </h3>

        {!selectedNode ? (
          <p style={{ color: "#64748b" }}>
            Click on a node to inspect details
          </p>
        ) : (
          <>
            <div style={{ marginBottom: "16px" }}>
              <strong>Name:</strong>
              <p>{selectedNode.id}</p>
            </div>

            <div style={{ marginBottom: "16px" }}>
              <strong>Type:</strong>
              <p>{selectedNode.type}</p>
            </div>

            {selectedNode.score && (
              <div style={{ marginBottom: "16px" }}>
                <strong>Score:</strong>
                <p>{selectedNode.score.toFixed(3)}</p>
              </div>
            )}

            {selectedNode.description && (
              <div style={{ marginBottom: "16px" }}>
                <strong>Description:</strong>
                <p>{selectedNode.description}</p>
              </div>
            )}

            {selectedNode.weight && (
              <div style={{ marginBottom: "16px" }}>
                <strong>Pathway Weight:</strong>
                <p>{selectedNode.weight.toFixed(3)}</p>
              </div>
            )}

            {selectedNode.highlight && (
              <div
                style={{
                  padding: "8px 12px",
                  background: "#fee2e2",
                  color: "#b91c1c",
                  borderRadius: "10px",
                  fontWeight: "600",
                  display: "inline-block",
                }}
              >
                Anchor Gene
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// ================= UI HELPER =================
const centerBox = (bg, color) => ({
  height: "650px",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  borderRadius: "16px",
  background: bg,
  border: "1px solid #e5e7eb",
  fontSize: "18px",
  fontWeight: "600",
  color,
});

export default GraphVisualization;