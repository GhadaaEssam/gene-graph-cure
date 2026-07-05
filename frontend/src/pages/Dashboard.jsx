import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Table,
  Badge,
  Button,
  ProgressBar,
} from "react-bootstrap";

import {
  getDashboardSummary,
  getRecentAnalyses,
} from "../api/dashboardApi";

const chartColors = {
  Resistant: "#dc3545",
  Sensitive: "#198754",
  Unknown: "#6c757d",
};

const toNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
};

const formatShortDate = (date) => {
  if (!date || date === "N/A") {
    return "N/A";
  }

  const parts = String(date).split("-");
  if (parts.length === 3) {
    return `${parts[1]}/${parts[2]}`;
  }

  return date;
};

const EmptyChart = ({ children }) => (
  <div className="dashboard-empty-chart">{children}</div>
);

const ResistanceDistributionChart = ({ data = [] }) => {
  const source = Array.isArray(data) ? data : [];
  const items = source.filter((item) => toNumber(item.count) > 0);
  const total = items.reduce((sum, item) => sum + toNumber(item.count), 0);

  if (!total) {
    return <EmptyChart>No prediction data yet</EmptyChart>;
  }

  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="dashboard-donut-wrap">
      <svg viewBox="0 0 120 120" className="dashboard-donut" role="img">
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="#e9ecef"
          strokeWidth="14"
        />

        {items.map((item) => {
          const count = toNumber(item.count);
          const dash = (count / total) * circumference;
          const dashOffset = -offset;
          offset += dash;

          return (
            <circle
              key={item.label}
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              stroke={chartColors[item.label] || chartColors.Unknown}
              strokeWidth="14"
              strokeDasharray={`${dash} ${circumference - dash}`}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              transform="rotate(-90 60 60)"
            />
          );
        })}

        <text x="60" y="57" textAnchor="middle" className="donut-total">
          {total}
        </text>
        <text x="60" y="74" textAnchor="middle" className="donut-label">
          analyses
        </text>
      </svg>

      <div className="dashboard-chart-legend">
        {items.map((item) => {
          const count = toNumber(item.count);
          const percent = Math.round((count / total) * 100);

          return (
            <div className="dashboard-legend-row" key={item.label}>
              <span
                className="dashboard-legend-dot"
                style={{ backgroundColor: chartColors[item.label] || chartColors.Unknown }}
              />
              <span>{item.label}</span>
              <strong>{percent}%</strong>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const TopPathwaysChart = ({ data = [] }) => {
  const source = Array.isArray(data) ? data : [];
  const items = source.filter((item) => toNumber(item.count) > 0).slice(0, 5);
  const maxCount = Math.max(...items.map((item) => toNumber(item.count)), 1);

  if (!items.length) {
    return <EmptyChart>No pathway data yet</EmptyChart>;
  }

  return (
    <div className="dashboard-bar-chart">
      {items.map((item) => {
        const count = toNumber(item.count);
        const width = `${Math.max(8, (count / maxCount) * 100)}%`;

        return (
          <div className="dashboard-bar-row" key={item.name}>
            <div className="dashboard-bar-header">
              <span className="dashboard-bar-label" title={item.name}>
                {item.name}
              </span>
              <span className="dashboard-bar-meta">
                {count} {count === 1 ? "hit" : "hits"} - {toNumber(item.averageImpact)}% avg
              </span>
            </div>
            <div className="dashboard-bar-track">
              <div className="dashboard-bar-fill" style={{ width }} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

const AnalysesOverTimeChart = ({ data = [] }) => {
  const source = Array.isArray(data) ? data : [];
  const items = source.filter((item) => toNumber(item.count) > 0);

  if (!items.length) {
    return <EmptyChart>No analysis timeline yet</EmptyChart>;
  }

  const width = 320;
  const height = 150;
  const padding = 24;
  const maxCount = Math.max(...items.map((item) => toNumber(item.count)), 1);

  const points = items.map((item, index) => {
    const x = items.length === 1
      ? width / 2
      : padding + (index * (width - padding * 2)) / (items.length - 1);
    const y = height - padding - (toNumber(item.count) / maxCount) * (height - padding * 2);

    return { x, y, ...item };
  });

  const pointString = points.map((point) => `${point.x},${point.y}`).join(" ");
  const areaString = [
    `${points[0].x},${height - padding}`,
    pointString,
    `${points[points.length - 1].x},${height - padding}`,
  ].join(" ");

  return (
    <div className="dashboard-line-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img">
        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          stroke="#e9ecef"
          strokeWidth="2"
        />
        <line
          x1={padding}
          y1={padding}
          x2={padding}
          y2={height - padding}
          stroke="#e9ecef"
          strokeWidth="2"
        />
        <polygon points={areaString} fill="#dbeafe" opacity="0.75" />
        <polyline
          points={pointString}
          fill="none"
          stroke="#2563eb"
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {points.map((point) => (
          <g key={point.date}>
            <circle cx={point.x} cy={point.y} r="4" fill="#2563eb" />
            <text
              x={point.x}
              y={point.y - 10}
              textAnchor="middle"
              className="line-point-label"
            >
              {point.count}
            </text>
          </g>
        ))}
      </svg>

      <div className="d-flex justify-content-between text-muted small">
        <span>{formatShortDate(items[0].date)}</span>
        <span>{formatShortDate(items[items.length - 1].date)}</span>
      </div>
    </div>
  );
};

function Dashboard() {
  const [summary, setSummary] = useState({});
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);

        const [summaryData, recentData] = await Promise.all([
          getDashboardSummary(),
          getRecentAnalyses(),
        ]);

        setSummary(summaryData);
        setRecentAnalyses(recentData);
      } catch (err) {
        console.error("Dashboard error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <h5>Loading dashboard...</h5>
      </Container>
    );
  }

  return (
    <Container className="py-5 dashboard-page">
      <style>{`
        .dashboard-page {
          color: #172033;
        }

        .dashboard-chart-card {
          min-height: 280px;
        }

        .dashboard-empty-chart {
          align-items: center;
          background: #f8fafc;
          border: 1px dashed #cbd5e1;
          border-radius: 8px;
          color: #64748b;
          display: flex;
          font-size: 0.9rem;
          height: 190px;
          justify-content: center;
          text-align: center;
        }

        .dashboard-donut-wrap {
          align-items: center;
          display: grid;
          gap: 14px;
          grid-template-columns: minmax(120px, 1fr) minmax(110px, 0.8fr);
          min-height: 190px;
        }

        .dashboard-donut {
          height: 160px;
          width: 100%;
        }

        .donut-total {
          fill: #172033;
          font-size: 22px;
          font-weight: 700;
        }

        .donut-label,
        .line-point-label {
          fill: #64748b;
          font-size: 10px;
        }

        .dashboard-chart-legend {
          display: grid;
          gap: 10px;
        }

        .dashboard-legend-row {
          align-items: center;
          display: grid;
          gap: 8px;
          grid-template-columns: 10px 1fr auto;
          font-size: 0.88rem;
        }

        .dashboard-legend-dot {
          border-radius: 999px;
          display: inline-block;
          height: 10px;
          width: 10px;
        }

        .dashboard-bar-chart {
          display: flex;
          flex-direction: column;
          gap: 10px;
          height: 198px;
          justify-content: space-between;
          overflow: hidden;
          padding-top: 2px;
        }

        .dashboard-bar-row {
          display: grid;
          gap: 6px;
          min-width: 0;
        }

        .dashboard-bar-header {
          align-items: center;
          display: grid;
          gap: 8px;
          grid-template-columns: minmax(0, 1fr) auto;
          min-width: 0;
        }

        .dashboard-bar-label {
          color: #172033;
          font-size: 0.82rem;
          font-weight: 700;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dashboard-bar-meta {
          color: #64748b;
          font-size: 0.72rem;
          font-weight: 600;
          white-space: nowrap;
        }

        .dashboard-bar-track {
          background: #e9ecef;
          border-radius: 999px;
          height: 9px;
          overflow: hidden;
        }

        .dashboard-bar-fill {
          background: linear-gradient(90deg, #0f766e, #2563eb);
          border-radius: 999px;
          height: 100%;
        }

        .dashboard-line-chart svg {
          display: block;
          height: 170px;
          width: 100%;
        }

        .analysis-title {
          max-width: 260px;
        }

        @media (max-width: 767px) {
          .dashboard-donut-wrap {
            grid-template-columns: 1fr;
          }

          .dashboard-donut {
            height: 140px;
          }
        }
      `}</style>

      <div className="mb-4">
        <h2>Welcome, Dr. {summary?.doctorName || "User"}</h2>
        <p className="text-muted">
          Here is an overview of your recent activity and analyses.
        </p>
      </div>

      <Row className="mb-4 g-3">
        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4 h-100">
            <p className="text-muted mb-1">Total Analyses</p>
            <h3 className="fw-bold mb-0">{summary?.totalAnalyses ?? 0}</h3>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4 h-100">
            <p className="text-muted mb-1">Resistant</p>
            <h3 className="fw-bold mb-0 text-danger">{summary?.resistant ?? 0}</h3>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4 h-100">
            <p className="text-muted mb-1">Sensitive</p>
            <h3 className="fw-bold mb-0 text-success">{summary?.sensitive ?? 0}</h3>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4 h-100">
            <p className="text-muted mb-1">Top Pathway</p>
            <h5 className="fw-bold mb-1 text-truncate">{summary?.topPathway || "N/A"}</h5>
            <small className="text-muted">
              {summary?.topPathwayCount ?? 0} occurrences
            </small>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4 g-3">
        <Col lg={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4 dashboard-chart-card">
            <h6 className="fw-bold mb-3">Resistance Distribution</h6>
            <ResistanceDistributionChart data={summary?.resistanceDistribution} />
          </Card>
        </Col>

        <Col lg={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4 dashboard-chart-card">
            <h6 className="fw-bold mb-3">Top Affected Pathways</h6>
            <TopPathwaysChart data={summary?.topAffectedPathways} />
          </Card>
        </Col>

        <Col lg={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4 dashboard-chart-card">
            <h6 className="fw-bold mb-3">Analyses Over Time</h6>
            <AnalysesOverTimeChart data={summary?.analysesOverTime} />
          </Card>
        </Col>
      </Row>

      <Card className="p-4 border-0 shadow-sm rounded-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h5 className="fw-bold mb-0">Recent Analyses</h5>
          <Button
            variant="outline-secondary"
            size="sm"
            className="rounded-pill px-3"
            onClick={() => navigate("/new-analysis")}
          >
            New Analysis
          </Button>
        </div>

        <Table hover responsive className="align-middle">
          <thead className="text-muted">
            <tr>
              <th>Analysis</th>
              <th>Drug Name</th>
              <th>Prediction</th>
              <th>Confidence</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {recentAnalyses.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center text-muted py-4">
                  No analyses have been run yet.
                </td>
              </tr>
            ) : (
              recentAnalyses.map((item, index) => {
                const isResistant = item.prediction === "Resistant";
                const resultId = item.analysis_code || item.id;

                return (
                  <tr key={resultId || index}>
                    <td>
                      <div className="fw-bold analysis-title">
                        {item.title || `${item.cancerType || "Cancer"} analysis`}
                      </div>
                      <small className="text-muted">{item.cancerType || "N/A"}</small>
                    </td>
                    <td>{item.drug || "Unknown drug"}</td>

                    <td>
                      <Badge bg={isResistant ? "danger" : "success"}>
                        {item.prediction || "Unknown"}
                      </Badge>
                    </td>

                    <td style={{ width: "200px" }}>
                      <div className="d-flex align-items-center gap-2">
                        <ProgressBar
                          now={toNumber(item.confidence)}
                          variant={isResistant ? "danger" : "success"}
                          style={{ height: "6px", width: "100px" }}
                        />
                        <small className="fw-bold">{toNumber(item.confidence)}%</small>
                      </div>
                    </td>

                    <td className="text-muted">
                      <small>{item.date || "N/A"}</small>
                    </td>

                    <td>
                      <Button
                        variant="link"
                        className="text-dark fw-bold p-0"
                        onClick={() => navigate(`/results/${resultId}`)}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </Table>
      </Card>
    </Container>
  );
}

export default Dashboard;
