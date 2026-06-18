import React, { useState, useEffect, useMemo, useRef, useCallback } from "react";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from "three";
import { X, ExternalLink, Hexagon } from "lucide-react";

/* ----------------------------------------------------------------------- *
 *  Edge-type visual language
 *  ppi        — protein-protein interaction  (blue)
 *  homology   — sequence/structural homology (green)
 *  pathway    — shared biological pathway    (purple)
 *  resistance — part of the drug-resistance backbone (gold, always on top)
 * ----------------------------------------------------------------------- */
const EDGE_STYLE = {
  ppi: { color: "#3b82f6", label: "PPI" },
  homology: { color: "#10b981", label: "Homology" },
  pathway: { color: "#a855f7", label: "Pathway" },
};
const RESISTANCE_COLOR = "#FFD700";

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

/* Build a quick PubMed search link for a gene symbol */
const pubmedLink = (geneName, extra = "") =>
  `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(
    geneName + (extra ? " " + extra : "")
  )}`;

function nodeIdOf(ref) {
  return typeof ref === "object" ? ref.id : ref;
}

export default function InteractiveVisualization() {
  const fgRef = useRef();
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selected, setSelected] = useState(null); // { kind: 'node'|'link', data }
  const [hover, setHover] = useState(null); // { kind, data }
  const [activeEdgeFilters, setActiveEdgeFilters] = useState([
    "ppi",
    "homology",
    "pathway",
  ]);
  const containerRef = useRef();
  const [dims, setDims] = useState({ width: 800, height: 600 });

  /* ---------------------------------------------------------------- *
   *  Demo data — replace this block with the API response mapping.
   *  Shape expected from /predict, mapped into force-graph format:
   *    structured_core_genes[i] -> node.isCore = true
   *    vimp_g[i]                -> node.importance
   *    cor[i]                   -> node.correlation
   *    graph[i][j]               -> edge weight / existence
   * ---------------------------------------------------------------- */
  useEffect(() => {
    const nodes = [
      { id: "TP53", importance: 0.95, correlation: 0.91, isAnchor: true, isCore: true },
      { id: "EGFR", importance: 0.82, correlation: 0.76, isAnchor: false, isCore: true },
      { id: "PIK3CA", importance: 0.74, correlation: 0.64, isAnchor: false, isCore: true },
      { id: "AKT1", importance: 0.68, correlation: 0.58, isAnchor: false, isCore: true },
      { id: "MTOR", importance: 0.61, correlation: 0.5, isAnchor: false, isCore: true },
      { id: "BRCA1", importance: 0.55, correlation: 0.41, isAnchor: true, isCore: true },
      { id: "ABCB1", importance: 0.49, correlation: 0.33, isAnchor: false, isCore: false },
      { id: "ERBB2", importance: 0.44, correlation: 0.39, isAnchor: false, isCore: false },
      { id: "MDM2", importance: 0.38, correlation: 0.21, isAnchor: false, isCore: false },
      { id: "CDKN1A", importance: 0.31, correlation: 0.18, isAnchor: false, isCore: false },
      { id: "PTEN", importance: 0.27, correlation: -0.12, isAnchor: false, isCore: false },
      { id: "RAF1", importance: 0.22, correlation: 0.15, isAnchor: false, isCore: false },
    ];

    const links = [
      // resistance backbone -> all endpoints are isCore genes
      { source: "TP53", target: "EGFR", type: "pathway", weight: 0.95 },
      { source: "EGFR", target: "PIK3CA", type: "ppi", weight: 0.88 },
      { source: "PIK3CA", target: "AKT1", type: "ppi", weight: 0.85 },
      { source: "AKT1", target: "MTOR", type: "ppi", weight: 0.79 },
      { source: "TP53", target: "BRCA1", type: "pathway", weight: 0.72 },
      // ordinary edges -> at least one endpoint is not core
      { source: "EGFR", target: "ERBB2", type: "homology", weight: 0.66 },
      { source: "TP53", target: "MDM2", type: "ppi", weight: 0.6 },
      { source: "MDM2", target: "CDKN1A", type: "pathway", weight: 0.4 },
      { source: "PIK3CA", target: "PTEN", type: "homology", weight: 0.35 },
      { source: "AKT1", target: "RAF1", type: "ppi", weight: 0.3 },
      { source: "ABCB1", target: "MTOR", type: "pathway", weight: 0.28 },
      { source: "ERBB2", target: "RAF1", type: "homology", weight: 0.25 },
    ];

    setGraphData({ nodes, links });
  }, []);

  /* ---------------------------------------------------------------- *
   *  Resize handling — keep the canvas filling its flex column
   * ---------------------------------------------------------------- */
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDims({ width, height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  /* ---------------------------------------------------------------- *
   *  Derived: resistance backbone = edges where BOTH endpoints isCore
   * ---------------------------------------------------------------- */
  const processedLinks = useMemo(() => {
    return graphData.links.map((l) => {
      const sourceCore =
        typeof l.source === "object" ? l.source.isCore : graphData.nodes.find((n) => n.id === l.source)?.isCore;
      const targetCore =
        typeof l.target === "object" ? l.target.isCore : graphData.nodes.find((n) => n.id === l.target)?.isCore;
      return { ...l, isResistance: !!(sourceCore && targetCore) };
    });
  }, [graphData]);

  const filteredLinks = useMemo(
    () => processedLinks.filter((l) => l.isResistance || activeEdgeFilters.includes(l.type)),
    [processedLinks, activeEdgeFilters]
  );

  const importanceRange = useMemo(() => {
    const vals = graphData.nodes.map((n) => n.importance ?? 0);
    return { min: Math.min(...vals, 0), max: Math.max(...vals, 1) };
  }, [graphData.nodes]);

  /* ---------------------------------------------------------------- *
   *  Node visual encoding
   * ---------------------------------------------------------------- */
  const nodeSize = useCallback(
    (node) => {
      const { min, max } = importanceRange;
      const norm = max > min ? (node.importance - min) / (max - min) : 0.5;
      const base = 4 + norm * 10; // 4..14 radius units
      return node.isCore ? base * 1.15 : base;
    },
    [importanceRange]
  );

  const nodeColor = useCallback((node) => {
    if (node.isAnchor) return "#FFD700";
    const t = clamp(node.importance ?? 0, 0, 1);
    if (t > 0.8) return "#ef4444";
    if (t > 0.6) return "#f97316";
    if (t > 0.4) return "#eab308";
    return "#3b82f6";
  }, []);

  /* Custom 3D object per node: sphere + glowing ring if part of resistance path */
  const nodeThreeObject = useCallback(
    (node) => {
      const group = new THREE.Group();
      const radius = nodeSize(node) * 0.6;
      const color = nodeColor(node);

      const sphereGeo = new THREE.SphereGeometry(radius, 16, 16);
      const sphereMat = new THREE.MeshLambertMaterial({
        color,
        emissive: color,
        emissiveIntensity: node.isCore ? 0.45 : 0.15,
      });
      const sphere = new THREE.Mesh(sphereGeo, sphereMat);
      group.add(sphere);

      if (node.isCore) {
        const ringGeo = new THREE.TorusGeometry(radius * 1.6, radius * 0.12, 8, 32);
        const ringMat = new THREE.MeshBasicMaterial({
          color: RESISTANCE_COLOR,
          transparent: true,
          opacity: 0.85,
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2;
        group.add(ring);
      }
      return group;
    },
    [nodeSize, nodeColor]
  );

  /* ---------------------------------------------------------------- *
   *  Link visual encoding
   * ---------------------------------------------------------------- */
  const linkWidth = useCallback((link) => {
    const w = link.weight ?? 0.3;
    const base = 0.6 + w * 3.2;
    return link.isResistance ? base * 1.6 : base;
  }, []);

  const linkColor = useCallback((link) => {
    if (link.isResistance) return RESISTANCE_COLOR;
    return EDGE_STYLE[link.type]?.color ?? "#888888";
  }, []);

  const linkDirectionalParticles = useCallback((link) => (link.isResistance ? 3 : 0), []);
  const linkDirectionalParticleSpeed = useCallback(() => 0.006, []);
  const linkDirectionalParticleWidth = useCallback(() => 2.2, []);

  /* ---------------------------------------------------------------- *
   *  Interaction handlers
   * ---------------------------------------------------------------- */
  const handleNodeClick = useCallback((node) => setSelected({ kind: "node", data: node }), []);
  const handleLinkClick = useCallback((link) => setSelected({ kind: "link", data: link }), []);

  const handleNodeHover = useCallback((node) => {
    setHover(node ? { kind: "node", data: node } : null);
    document.body.style.cursor = node ? "pointer" : "default";
  }, []);

  const handleLinkHover = useCallback((link) => {
    setHover(link ? { kind: "link", data: link } : null);
    document.body.style.cursor = link ? "pointer" : "default";
  }, []);

  const toggleEdgeFilter = (key) => {
    setActiveEdgeFilters((prev) => {
      const next = prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key];
      return next.length ? next : prev; // keep at least one active
    });
  };

  /* ---------------------------------------------------------------- *
   *  Render
   * ---------------------------------------------------------------- */
  return (
    <div style={styles.page}>
      {/* ---------------- 3D canvas column ---------------- */}
      <div ref={containerRef} style={styles.canvasCol}>
        {/* Legend */}
        <div style={styles.legendCard}>
          <div style={styles.legendHeader}>
            <Hexagon size={16} color="#94a3b8" />
            <span style={styles.legendTitle}>GENE NETWORK</span>
          </div>
          <div style={styles.legendDivider} />
          <LegendDot color={RESISTANCE_COLOR} ring label="Resistance path node" />
          <LegendDot color="#ef4444" label="High importance" />
          <LegendDot color="#3b82f6" label="Lower importance" />
          <div style={styles.legendDivider} />
          {Object.entries(EDGE_STYLE).map(([key, s]) => (
            <LegendLine key={key} color={s.color} label={s.label} />
          ))}
          <LegendLine color={RESISTANCE_COLOR} label="Resistance backbone" thick />
        </div>

        {/* Edge filter toggle */}
        <div style={styles.filterGroup}>
          {Object.entries(EDGE_STYLE).map(([key, s]) => {
            const active = activeEdgeFilters.includes(key);
            return (
              <button
                key={key}
                onClick={() => toggleEdgeFilter(key)}
                style={{
                  ...styles.filterBtn,
                  ...(active ? styles.filterBtnActive : {}),
                }}
              >
                {s.label}
              </button>
            );
          })}
        </div>

        {/* Hover tooltip */}
        {hover && (
          <div style={styles.tooltipCard}>
            {hover.kind === "node" ? (
              <>
                <div style={styles.tooltipTitle}>{hover.data.id}</div>
                <div style={styles.tooltipMeta}>
                  Importance: {hover.data.importance?.toFixed(2)} · Correlation:{" "}
                  {hover.data.correlation?.toFixed(2)}
                </div>
                {hover.data.isCore && <span style={styles.badgeGold}>Resistance path</span>}
              </>
            ) : (
              <>
                <div style={styles.tooltipTitle}>
                  {nodeIdOf(hover.data.source)} ↔ {nodeIdOf(hover.data.target)}
                </div>
                <div style={styles.tooltipMeta}>
                  Type: {EDGE_STYLE[hover.data.type]?.label ?? hover.data.type} · Weight:{" "}
                  {hover.data.weight?.toFixed(2)}
                </div>
                {hover.data.isResistance && <span style={styles.badgeGold}>Resistance backbone</span>}
              </>
            )}
          </div>
        )}

        <ForceGraph3D
          ref={fgRef}
          width={dims.width}
          height={dims.height}
          graphData={{ nodes: graphData.nodes, links: filteredLinks }}
          backgroundColor="#020617"
          showNavInfo={false}
          nodeLabel={() => ""}
          nodeThreeObject={nodeThreeObject}
          nodeThreeObjectExtend={false}
          linkWidth={linkWidth}
          linkColor={linkColor}
          linkOpacity={1}
          linkDirectionalParticles={linkDirectionalParticles}
          linkDirectionalParticleSpeed={linkDirectionalParticleSpeed}
          linkDirectionalParticleWidth={linkDirectionalParticleWidth}
          linkDirectionalParticleColor={() => RESISTANCE_COLOR}
          onNodeClick={handleNodeClick}
          onLinkClick={handleLinkClick}
          onNodeHover={handleNodeHover}
          onLinkHover={handleLinkHover}
          enableNodeDrag={true}
          enableNavigationControls={true}
        />
      </div>

      {/* ---------------- side info panel ---------------- */}
      <div style={styles.sidePanel}>
        <div style={styles.sidePanelHeader}>
          <h2 style={styles.sidePanelTitle}>
            {selected ? (selected.kind === "node" ? "Gene details" : "Interaction details") : "Network info"}
          </h2>
          {selected && (
            <button style={styles.closeBtn} onClick={() => setSelected(null)} aria-label="Close">
              <X size={16} color="#94a3b8" />
            </button>
          )}
        </div>
        <div style={styles.sideDivider} />

        {!selected ? (
          <div>
            <p style={styles.mutedText}>
              انقري على أي جين (node) أو علاقة (edge) في الجراف عشان تشوفي تفاصيلها هنا.
            </p>
            <div style={styles.smallMuted}>
              {graphData.nodes.length} genes · {processedLinks.length} interactions ·{" "}
              {processedLinks.filter((l) => l.isResistance).length} on the resistance path
            </div>
          </div>
        ) : selected.kind === "node" ? (
          <NodeDetailPanel node={selected.data} allLinks={processedLinks} onSelectLink={setSelected} />
        ) : (
          <LinkDetailPanel link={selected.data} />
        )}
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------- *
 *  Sub-components
 * ----------------------------------------------------------------------- */

function LegendDot({ color, label, ring }) {
  return (
    <div style={styles.legendRow}>
      <span
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: color,
          border: ring ? `2px solid ${color}` : "none",
          boxShadow: ring ? "0 0 0 2px rgba(255,215,0,0.25)" : "none",
          display: "inline-block",
        }}
      />
      <span style={styles.legendLabel}>{label}</span>
    </div>
  );
}

function LegendLine({ color, label, thick }) {
  return (
    <div style={styles.legendRow}>
      <span style={{ width: 16, height: thick ? 3 : 2, background: color, borderRadius: 2, display: "inline-block" }} />
      <span style={styles.legendLabel}>{label}</span>
    </div>
  );
}

function StatRow({ label, value }) {
  return (
    <div style={styles.statRow}>
      <span style={styles.statLabel}>{label}</span>
      <span style={styles.statValue}>{value}</span>
    </div>
  );
}

function NodeDetailPanel({ node, allLinks, onSelectLink }) {
  const connections = allLinks.filter(
    (l) => nodeIdOf(l.source) === node.id || nodeIdOf(l.target) === node.id
  );

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
        <span style={styles.geneName}>{node.id}</span>
        {node.isAnchor && <span style={styles.badgeGoldSolid}>Anchor gene</span>}
      </div>
      {node.isCore && <span style={styles.badgeGoldStrong}>On drug-resistance path</span>}

      <div style={styles.statBlock}>
        <StatRow label="Importance (vimp_g)" value={node.importance?.toFixed(3)} />
        <StatRow label="Correlation" value={node.correlation?.toFixed(3)} />
        <StatRow label="Connections" value={connections.length} />
      </div>

      <a
        href={pubmedLink(node.id, "drug resistance")}
        target="_blank"
        rel="noopener noreferrer"
        style={styles.pubmedBtn}
      >
        View on PubMed <ExternalLink size={14} />
      </a>

      {connections.length > 0 && (
        <>
          <div style={styles.sectionLabel}>Interactions ({connections.length})</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {connections.map((l, i) => {
              const otherId = nodeIdOf(l.source) === node.id ? nodeIdOf(l.target) : nodeIdOf(l.source);
              return (
                <div
                  key={i}
                  onClick={() => onSelectLink({ kind: "link", data: l })}
                  style={{
                    ...styles.connectionRow,
                    border: l.isResistance ? `1px solid ${RESISTANCE_COLOR}` : "1px solid transparent",
                  }}
                >
                  <span style={{ fontSize: 14 }}>{otherId}</span>
                  <span
                    style={{
                      ...styles.typeChip,
                      background: l.isResistance ? RESISTANCE_COLOR : EDGE_STYLE[l.type]?.color,
                      color: l.isResistance ? "#1a1300" : "white",
                    }}
                  >
                    {EDGE_STYLE[l.type]?.label ?? l.type}
                  </span>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

function LinkDetailPanel({ link }) {
  const sourceId = nodeIdOf(link.source);
  const targetId = nodeIdOf(link.target);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
        <span style={styles.linkPairName}>{sourceId}</span>
        <span style={{ color: "#64748b", fontSize: 20 }}>↔</span>
        <span style={styles.linkPairName}>{targetId}</span>
      </div>

      {link.isResistance && <span style={styles.badgeGoldStrong}>Drug-resistance backbone edge</span>}

      <div style={styles.statBlock}>
        <StatRow label="Relation type" value={EDGE_STYLE[link.type]?.label ?? link.type} />
        <StatRow label="Weight" value={link.weight?.toFixed(3)} />
      </div>

      <div style={styles.smallMuted2}>Look up this gene pair together:</div>
      <a
        href={pubmedLink(`${sourceId} AND ${targetId}`)}
        target="_blank"
        rel="noopener noreferrer"
        style={styles.pubmedBtn}
      >
        {sourceId} + {targetId} on PubMed <ExternalLink size={14} />
      </a>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <a href={pubmedLink(sourceId)} target="_blank" rel="noopener noreferrer" style={styles.pubmedBtnSmall}>
          {sourceId} only
        </a>
        <a href={pubmedLink(targetId)} target="_blank" rel="noopener noreferrer" style={styles.pubmedBtnSmall}>
          {targetId} only
        </a>
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------- *
 *  Inline styles — no UI library dependency required
 * ----------------------------------------------------------------------- */
const styles = {
  page: {
    display: "flex",
    width: "100%",
    height: "100vh",
    background: "#020617",
    fontFamily: "Inter, Roboto, sans-serif",
  },
  canvasCol: { flex: 1, position: "relative" },
  legendCard: {
    position: "absolute",
    top: 16,
    left: 16,
    zIndex: 5,
    background: "rgba(15,23,42,0.92)",
    color: "white",
    padding: 12,
    borderRadius: 8,
    border: "1px solid #334155",
    minWidth: 190,
  },
  legendHeader: { display: "flex", alignItems: "center", gap: 8, marginBottom: 8 },
  legendTitle: { fontSize: 12, fontWeight: 700, letterSpacing: 0.5 },
  legendDivider: { borderTop: "1px solid #334155", margin: "8px 0" },
  legendRow: { display: "flex", alignItems: "center", gap: 8, padding: "3px 0" },
  legendLabel: { fontSize: 12, color: "#cbd5e1" },
  filterGroup: {
    position: "absolute",
    top: 16,
    right: 16,
    zIndex: 5,
    display: "flex",
    background: "rgba(15,23,42,0.92)",
    border: "1px solid #334155",
    borderRadius: 8,
    overflow: "hidden",
  },
  filterBtn: {
    background: "transparent",
    border: "none",
    color: "#94a3b8",
    fontSize: 11,
    padding: "6px 10px",
    cursor: "pointer",
  },
  filterBtnActive: { color: "white", background: "rgba(255,255,255,0.08)" },
  tooltipCard: {
    position: "absolute",
    bottom: 16,
    left: 16,
    zIndex: 5,
    background: "rgba(15,23,42,0.95)",
    color: "white",
    padding: 12,
    borderRadius: 8,
    border: "1px solid #475569",
    maxWidth: 260,
    pointerEvents: "none",
  },
  tooltipTitle: { fontSize: 14, fontWeight: 700 },
  tooltipMeta: { fontSize: 12, color: "#94a3b8", marginTop: 2 },
  badgeGold: {
    display: "inline-block",
    marginTop: 6,
    background: RESISTANCE_COLOR,
    color: "#1a1300",
    fontSize: 10,
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: 10,
  },
  badgeGoldSolid: {
    background: "#FFD700",
    color: "#1a1300",
    fontSize: 12,
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: 10,
  },
  badgeGoldStrong: {
    display: "inline-block",
    background: RESISTANCE_COLOR,
    color: "#1a1300",
    fontSize: 12,
    fontWeight: 700,
    padding: "3px 10px",
    borderRadius: 10,
    marginBottom: 12,
  },
  sidePanel: {
    width: 360,
    background: "#0f172a",
    color: "white",
    padding: 24,
    borderLeft: "1px solid #334155",
    overflowY: "auto",
  },
  sidePanelHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  sidePanelTitle: { fontSize: 18, fontWeight: 700, margin: 0 },
  closeBtn: { background: "transparent", border: "none", cursor: "pointer", padding: 4 },
  sideDivider: { borderTop: "1px solid #334155", margin: "12px 0 16px" },
  mutedText: { color: "#94a3b8", marginBottom: 16, lineHeight: 1.6, textAlign: "right" },
  smallMuted: { fontSize: 12, color: "#64748b" },
  smallMuted2: { fontSize: 12, color: "#64748b", marginTop: 16, marginBottom: 8 },
  statBlock: { background: "rgba(255,255,255,0.04)", borderRadius: 8, padding: 12, marginTop: 12 },
  statRow: { display: "flex", justifyContent: "space-between", padding: "4px 0" },
  statLabel: { fontSize: 14, color: "#94a3b8" },
  statValue: { fontSize: 14, fontWeight: 600 },
  geneName: { fontSize: 28, fontWeight: 700 },
  linkPairName: { fontSize: 20, fontWeight: 700 },
  pubmedBtn: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    marginTop: 16,
    padding: "10px 12px",
    borderRadius: 8,
    background: "#1e293b",
    color: "#93c5fd",
    textDecoration: "none",
    fontSize: 14,
    fontWeight: 600,
    border: "1px solid #334155",
  },
  pubmedBtnSmall: {
    flex: 1,
    textAlign: "center",
    padding: "8px 6px",
    borderRadius: 8,
    background: "rgba(255,255,255,0.04)",
    color: "#93c5fd",
    textDecoration: "none",
    fontSize: 13,
    border: "1px solid #334155",
  },
  sectionLabel: { fontSize: 13, fontWeight: 600, color: "#cbd5e1", marginTop: 24, marginBottom: 8 },
  connectionRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "rgba(255,255,255,0.03)",
    borderRadius: 6,
    padding: "8px 10px",
    cursor: "pointer",
  },
  typeChip: { fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 8 },
};
