import React, { useEffect, useState } from "react";
import {
  Container,
  Row,
  Col,
  Card,
  Badge,
  ProgressBar,
  Button,
} from "react-bootstrap";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  FaArrowLeft,
  FaCircleCheck,
  FaTriangleExclamation,
  FaNetworkWired,
} from "react-icons/fa6";
import { getAnalysisResult } from "../api/analysisApi";

const normalizePrediction = (value) => {
  const normalized = String(value || "").trim().toLowerCase();

  if (["1", "1.0", "true", "resistant", "resistance"].includes(normalized)) {
    return "Resistant";
  }

  if (["0", "0.0", "false", "sensitive", "sensitivity"].includes(normalized)) {
    return "Sensitive";
  }

  return "Unknown";
};

function Results() {
  const { job_id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (job_id) {
      localStorage.setItem("currentJobId", job_id);
    }
  }, [job_id]);

  // ---------------- FETCH RESULTS ----------------
  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);

        const result = await getAnalysisResult(job_id);
        setData(result);
      } catch (err) {
        console.error(err);
        setError("Failed to load results");
      } finally {
        setLoading(false);
      }
    };

    if (job_id) fetchResults();
  }, [job_id]);

  // ---------------- ACTIONS ----------------
  const handleDownload = () => {
    window.open(
      `http://localhost:8000/api/report/${job_id}`,
      "_blank"
    );
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    alert("Link copied!");
  };

  // ---------------- STATES ----------------
  if (loading) {
    return (
      <Container className="text-center py-5">
        <h5>Loading analysis results...</h5>
        <p className="text-muted">
          Please wait while we process your data
        </p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="text-center py-5">
        <h5 className="text-danger">{error}</h5>
        <Link to="/new-analysis">Run New Analysis</Link>
      </Container>
    );
  }

  if (!data && !loading) {
    return (
      <Container className="text-center py-5">
        <h5>No results found</h5>
        <Link to="/new-analysis">Run New Analysis</Link>
      </Container>
    );
  }

  const recommendations = (
    data.adrsRecommendations?.length
      ? data.adrsRecommendations
      : data.alternatives || []
  )
    .map((item) => (
      typeof item === "string"
        ? { drug_name: item }
        : item
    ))
    .filter((item) => item?.drug_name || item?.name);

  const prediction = normalizePrediction(data.prediction);
  const isResistant = prediction === "Resistant";
  const isSensitive = prediction === "Sensitive";
  const resultTone = isResistant ? "resistant" : isSensitive ? "sensitive" : "unknown";
  const resultBadge = isResistant ? "High Risk" : isSensitive ? "Lower Risk" : "Result Pending";
  const resultTitle = isResistant
    ? "Drug Resistance Predicted"
    : isSensitive
      ? "Drug Sensitivity Predicted"
      : "Prediction Unavailable";

  // ---------------- UI ----------------
  return (
    <div className="results-page py-4">
      <style>{`
        .results-page {
          background-color: #f8fafc;
          min-height: calc(100vh - 70px);
          font-family: 'Segoe UI', system-ui, sans-serif;
        }

        .back-link {
          color: #14b8a6;
          text-decoration: none;
          font-weight: 500;
          font-size: 0.85rem;
        }

        .result-status-card {
          border-radius: 12px;
        }

        .result-status-card.resistant {
          background-color: #fff5f5;
          border: 1px solid #fecaca;
        }

        .result-status-card.sensitive {
          background-color: #f0fdf4;
          border: 1px solid #bbf7d0;
        }

        .result-status-card.unknown {
          background-color: #f8fafc;
          border: 1px solid #cbd5e1;
        }

        .result-icon-wrapper {
          color: white;
          width: 50px;
          height: 50px;
          border-radius: 50%;
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .result-icon-wrapper.resistant {
          background-color: #ef4444;
        }

        .result-icon-wrapper.sensitive {
          background-color: #16a34a;
        }

        .result-icon-wrapper.unknown {
          background-color: #64748b;
        }

        .custom-card {
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          background: white;
        }

        .gene-badge {
          background-color: #f1f5f9;
          padding: 4px 8px;
          border-radius: 6px;
          font-size: 0.75rem;
          margin-right: 6px;
        }

        .custom-progress {
          height: 6px;
        }

        .recommendation-item {
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 14px;
          height: 100%;
          background: #ffffff;
        }

        .recommendation-score {
          background-color: #ecfeff;
          color: #0f766e;
          border: 1px solid #99f6e4;
          border-radius: 999px;
          padding: 3px 8px;
          font-size: 0.75rem;
          font-weight: 700;
        }

        .recommendation-chip {
          background-color: #f1f5f9;
          border-radius: 999px;
          display: inline-block;
          font-size: 0.72rem;
          margin: 3px 4px 0 0;
          padding: 3px 8px;
        }
      `}</style>

      <Container style={{ maxWidth: "1000px" }}>
        {/* BACK */}
        <div className="mb-3">
          <Link to="/dashboard" className="back-link d-flex align-items-center gap-2">
            <FaArrowLeft /> Back to Dashboard
          </Link>
        </div>

        {/* TITLE */}
        <div className="mb-4">
          <h3 className="fw-bold">Analysis Results</h3>
        </div>

        {/* MAIN CARD */}
        <Card className={`result-status-card ${resultTone} mb-4 p-4`}>
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            
            <div className="d-flex align-items-center gap-3">
              <div className={`result-icon-wrapper ${resultTone}`}>
                {isResistant ? <FaTriangleExclamation /> : <FaCircleCheck />}
              </div>

              <div>
                <Badge bg={isResistant ? "danger" : isSensitive ? "success" : "secondary"}>
                  {resultBadge}
                </Badge>
                <h4 className="fw-bold m-0">
                  {resultTitle}
                </h4>
                <span className="text-muted">
                  {data.cancerType}
                </span>
              </div>
            </div>

            <div className="text-end">
              <h2 className="fw-bold m-0">{data.riskScore}%</h2>
              <span className="text-muted">Confidence</span>
            </div>
          </div>
        </Card>

        {/* PATHWAYS + ACTIONS */}
        <Row className="mb-4 g-4">
          <Col lg={8}>
            <Card className="custom-card p-4">
              <h5 className="mb-3">
                <FaNetworkWired className="me-2 text-success" />
                Key Pathways
              </h5>

              {data.pathways?.map((p, i) => (
                <div key={i} className="mb-3">
                  <div className="d-flex justify-content-between">
                    <strong>{p.name}</strong>
                    <span>{p.impact}%</span>
                  </div>

                  <ProgressBar now={p.impact} className="custom-progress mb-2" />

                  <div>
                    {p.genes?.map((g, idx) => (
                      <span key={idx} className="gene-badge">
                        {g}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </Card>
          </Col>

          {/* ACTIONS */}
          <Col lg={4}>
            <Card className="custom-card p-4">
              <h5 className="mb-3">Actions</h5>

              <Button className="w-100 mb-2" onClick={() => navigate("/visualization")}>
                View Graph
              </Button>

              <Button
                variant="outline-secondary"
                className="w-100 mb-2"
                onClick={() => navigate("/chat", {
                                state: { job_id }
                              })}
              >
                Ask AI
              </Button>

              <Button
                variant="outline-secondary"
                className="w-100 mb-2"
                onClick={handleDownload}
              >
                Download Report
              </Button>

              <Button
                variant="outline-secondary"
                className="w-100"
                onClick={handleShare}
              >
                Share
              </Button>
            </Card>
          </Col>
        </Row>

        {/* INTERPRETATION */}
        <Card className="custom-card p-4 mb-4">
          <h5>Clinical Interpretation</h5>
          <p>{data.interpretation}</p>
        </Card>

        {/* ALTERNATIVES */}
        <Card className="custom-card p-4">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
            <div>
              <h5 className="mb-1">ADRS Drug Recommendations</h5>
              <span className="text-muted">
                Resistant drug: {data.resistantDrug || "Unknown"}
              </span>
            </div>
            {recommendations.length > 0 && (
              <Badge bg="success">{recommendations.length} found</Badge>
            )}
          </div>

          {recommendations.length > 0 ? (
            <Row className="g-3">
              {recommendations.map((drug, i) => (
                <Col md={6} key={`${drug.drug_name || drug.name}-${i}`}>
                  <div className="recommendation-item">
                    <div className="d-flex justify-content-between gap-3 mb-2">
                      <strong>{drug.drug_name || drug.name}</strong>
                      {drug.sd_score !== undefined && (
                        <span className="recommendation-score">
                          {(Number(drug.sd_score) * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>

                    {drug.mechanism_of_action && (
                      <p className="text-muted mb-2" style={{ fontSize: "0.86rem" }}>
                        {drug.mechanism_of_action}
                      </p>
                    )}

                    {drug.targeted_genes?.length > 0 && (
                      <div className="mb-2">
                        <small className="fw-bold text-secondary">Genes</small>
                        <div>
                          {drug.targeted_genes.slice(0, 6).map((gene) => (
                            <span key={gene} className="recommendation-chip">
                              {gene}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {drug.targeted_pathways?.length > 0 && (
                      <div>
                        <small className="fw-bold text-secondary">Pathways</small>
                        <div>
                          {drug.targeted_pathways.slice(0, 4).map((pathway) => (
                            <span key={pathway} className="recommendation-chip">
                              {pathway}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </Col>
              ))}
            </Row>
          ) : (
            <p className="text-muted mb-0">
              ADRS did not return drug recommendations for this analysis.
            </p>
          )}
        </Card>
      </Container>
    </div>
  );
}

export default Results;
