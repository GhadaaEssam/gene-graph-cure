import React, { useEffect, useState } from "react";
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

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

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
    <Container className="py-5">
      {/* 1. Header Section */}
      <div className="mb-4">
        <h2>Welcome back, Dr. Smith</h2>
        <p className="text-muted">
          Here's an overview of your recent activity and analyses
        </p>
      </div>

      {/* 2. Top Stats Cards */}
      <Row className="mb-4 g-3">
        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Total Analyses</p>
            <h3 className="fw-bold">{summary?.totalAnalyses}</h3>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Resistant</p>
            <h3 className="fw-bold">{summary?.resistant}</h3>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Sensitive</p>
            <h3 className="fw-bold">{summary?.sensitive}</h3>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Top Pathway</p>
            <h3 className="fw-bold">{summary?.topPathway}</h3>
            <small className="text-muted">
              {summary?.topPathwayCount} occurrences
            </small>
          </Card>
        </Col>
      </Row>

      {/* 3. Charts Placeholders */}
      <Row className="mb-4 g-3">
        <Col md={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4" style={{ height: "250px" }}>
            <h6 className="fw-bold mb-3">Resistance Distribution</h6>
            <div className="d-flex justify-content-center align-items-center h-100 text-muted bg-light rounded">
              [ Donut Chart Placeholder ]
            </div>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4" style={{ height: "250px" }}>
            <h6 className="fw-bold mb-3">Top Affected Pathways</h6>
            <div className="d-flex justify-content-center align-items-center h-100 text-muted bg-light rounded">
              [ Bar Chart Placeholder ]
            </div>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4" style={{ height: "250px" }}>
            <h6 className="fw-bold mb-3">Analyses Over Time</h6>
            <div className="d-flex justify-content-center align-items-center h-100 text-muted bg-light rounded">
              [ Line Chart Placeholder ]
            </div>
          </Card>
        </Col>
      </Row>

      {/* 4. Recent Analyses Table */}
      <Card className="p-4 border-0 shadow-sm rounded-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h5 className="fw-bold mb-0">Recent Analyses</h5>
          <Button variant="outline-secondary" size="sm" className="rounded-pill px-3">
            View All
          </Button>
        </div>

        <Table hover responsive className="align-middle">
          <thead className="text-muted">
            <tr>
              <th>Patient ID</th>
              <th>Drug Name</th>
              <th>Prediction</th>
              <th>Confidence</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {recentAnalyses.map((item, index) => (
              <tr key={index}>
                <td className="fw-bold">{item.id}</td>
                <td>{item.drug}</td>

                <td>
                  <Badge bg={item.prediction === "Resistant" ? "danger" : "success"}>
                    {item.prediction}
                  </Badge>
                </td>

                <td style={{ width: "200px" }}>
                  <div className="d-flex align-items-center gap-2">
                    <ProgressBar
                      now={item.confidence}
                      variant={item.prediction === "Resistant" ? "danger" : "success"}
                      style={{ height: "6px", width: "100px" }}
                    />
                    <small className="fw-bold">{item.confidence}%</small>
                  </div>
                </td>

                <td className="text-muted">
                  <small>⏱ {item.date}</small>
                </td>

                <td>
                  <Button variant="link" className="text-dark fw-bold p-0">
                    View
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </Container>
  );
}

export default Dashboard;