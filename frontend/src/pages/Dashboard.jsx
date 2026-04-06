import React from "react";
import { Container, Row, Col, Card, Table, Badge, Button, ProgressBar } from "react-bootstrap";

function Dashboard() {
  // Mock Data: بيانات وهمية لجدول التحليلات عشان يظهر زي الصورة بالظبط
  const recentAnalyses = [
    { id: "P-001", drug: "Osimertinib", prediction: "Resistant", confidence: 89, date: "2024-12-18" },
    { id: "P-002", drug: "Gefitinib", prediction: "Sensitive", confidence: 92, date: "2024-12-17" },
    { id: "P-003", drug: "Erlotinib", prediction: "Resistant", confidence: 76, date: "2024-12-16" },
    { id: "P-004", drug: "Afatinib", prediction: "Sensitive", confidence: 88, date: "2024-12-15" },
    { id: "P-005", drug: "Crizotinib", prediction: "Resistant", confidence: 81, date: "2024-12-14" },
  ];

  return (
    <Container className="py-5">
      {/* 1. Header Section */}
      <div className="mb-4">
        <h2>Welcome back, Dr. Smith</h2>
        <p className="text-muted">Here's an overview of your recent activity and analyses</p>
      </div>

      {/* 2. Top Stats Cards */}
      <Row className="mb-4 g-3">
        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Total Analyses</p>
            <h3 className="fw-bold">127</h3>
            <small className="text-success">+12 this month</small>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Resistant</p>
            <h3 className="fw-bold">57</h3>
            <small className="text-muted">44.9% of total</small>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Sensitive</p>
            <h3 className="fw-bold">70</h3>
            <small className="text-muted">55.1% of total</small>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="p-3 border-0 shadow-sm rounded-4">
            <p className="text-muted mb-1">Top Pathway</p>
            <h3 className="fw-bold">MAPK/ERK</h3>
            <small className="text-muted">28 occurrences</small>
          </Card>
        </Col>
      </Row>

      {/* 3. Charts Placeholders */}
      <Row className="mb-4 g-3">
        <Col md={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4" style={{ height: "250px" }}>
            <h6 className="fw-bold mb-3">Resistance Distribution</h6>
            <div className="d-flex justify-content-center align-items-center h-100 text-muted" style={{ backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
              [ Donut Chart Placeholder ]
            </div>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4" style={{ height: "250px" }}>
            <h6 className="fw-bold mb-3">Top Affected Pathways</h6>
            <div className="d-flex justify-content-center align-items-center h-100 text-muted" style={{ backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
              [ Bar Chart Placeholder ]
            </div>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="p-3 border-0 shadow-sm rounded-4" style={{ height: "250px" }}>
            <h6 className="fw-bold mb-3">Analyses Over Time</h6>
            <div className="d-flex justify-content-center align-items-center h-100 text-muted" style={{ backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
              [ Line Chart Placeholder ]
            </div>
          </Card>
        </Col>
      </Row>

      {/* 4. Recent Analyses Table */}
      <Card className="p-4 border-0 shadow-sm rounded-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h5 className="fw-bold mb-0">Recent Analyses</h5>
          <Button variant="outline-secondary" size="sm" className="rounded-pill px-3">View All</Button>
        </div>
        
        <Table hover responsive className="align-middle">
          <thead className="text-muted" style={{ borderBottom: "2px solid #eee" }}>
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
              <tr key={index} style={{ borderBottom: "1px solid #f0f0f0" }}>
                <td className="fw-bold">{item.id}</td>
                <td>{item.drug}</td>
                <td>
                  <Badge 
                    bg={item.prediction === "Resistant" ? "danger" : "success"} 
                    style={{ opacity: 0.8, padding: "6px 12px", borderRadius: "6px" }}
                  >
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
                <td className="text-muted"><small>⏱ {item.date}</small></td>
                <td>
                  <Button variant="link" className="text-dark fw-bold text-decoration-none p-0">
                    👁 View Details
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