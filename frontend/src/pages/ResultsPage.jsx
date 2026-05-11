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
  FaTriangleExclamation,
  FaDownload,
  FaShareNodes,
  FaNetworkWired,
  FaRegMessage,
} from "react-icons/fa6";
import { getAnalysisResult } from "../api/analysisApi";

function Results() {
  const { job_id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

        .alert-card {
          background-color: #fff5f5;
          border: 1px solid #fecaca;
          border-radius: 12px;
        }

        .alert-icon-wrapper {
          background-color: #ef4444;
          color: white;
          width: 50px;
          height: 50px;
          border-radius: 50%;
          display: flex;
          justify-content: center;
          align-items: center;
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
        <Card className="alert-card mb-4 p-4">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            
            <div className="d-flex align-items-center gap-3">
              <div className="alert-icon-wrapper">
                <FaTriangleExclamation />
              </div>

              <div>
                <Badge bg="danger">High Risk</Badge>
                <h4 className="fw-bold m-0">
                  Drug Resistance Predicted
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
                onClick={() => navigate("/chat")}
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
          <h5>Alternative Treatments</h5>

          <Row>
            {data.alternatives?.map((a, i) => (
              <Col md={6} key={i} className="mb-2">
                <div className="border p-2 rounded">{a}</div>
              </Col>
            ))}
          </Row>
        </Card>
      </Container>
    </div>
  );
}

export default Results;