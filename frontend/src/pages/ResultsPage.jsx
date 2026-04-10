import React from "react";
import { Container, Row, Col, Card, ProgressBar, Badge, Button } from "react-bootstrap";
import { ExclamationTriangleFill, Diagram3, ChatDots, Download, Share, ChatLeftText } from "react-bootstrap-icons";
import Nav2 from "../components/layout/PrivateNavbar"; // استوردنا النافبار الجديدة

function ResultsPage() {
  const pathways = [
    { name: "MAPK/ERK Signaling", impact: 87, genes: ["KRAS", "BRAF", "MEK1"] },
    { name: "PI3K/AKT Pathway", impact: 72, genes: ["PIK3CA", "AKT1", "PTEN"] },
    { name: "DNA Damage Response", impact: 65, genes: ["TP53", "ATM", "BRCA1"] },
  ];

  return (
    <Container className="py-5">
      <h2 className="fw-bold" style={{ color: "#0f2027" }}>Analysis Results</h2>
      <p className="text-muted mb-4">Patient P-428 - Cisplatin</p>

      {/* الـ Alert بتاع المقاومة (أحمر) */}
      <Card className="border-0 mb-4" style={{ backgroundColor: "#fff5f5", borderLeft: "5px solid #dc3545", borderRadius: "10px" }}>
        <Card.Body className="d-flex align-items-center justify-content-between p-4">
          <div className="d-flex align-items-center">
            <ExclamationTriangleFill size={40} color="#dc3545" className="me-3" />
            <div>
              <Badge bg="danger" className="mb-2">Resistant</Badge>
              <h3 className="fw-bold mb-0 text-dark">Drug Resistance Predicted</h3>
              <p className="text-muted mb-0">The model predicts this patient is likely <strong className="text-danger">resistant</strong> to Cisplatin.</p>
            </div>
          </div>
          <div className="text-end">
            <h1 className="fw-bold mb-0" style={{ fontSize: "3rem", color: "#0f2027" }}>85%</h1>
            <p className="text-muted mb-0">Confidence Score</p>
          </div>
        </Card.Body>
      </Card>

      <Row>
        {/* العمود الشمال: التفاصيل والمسارات */}
        <Col md={8}>
          
          <Card className="shadow-sm border-0 mb-4 p-3" style={{ borderRadius: "12px" }}>
            <Card.Body>
              <h5 className="fw-bold mb-4"><Diagram3 className="me-2 text-success" /> Key Affected Pathways</h5>
              {pathways.map((pw, index) => (
                <div key={index} className="mb-4">
                  <div className="d-flex justify-content-between mb-1">
                    <strong style={{ color: "#0f2027" }}>{pw.name}</strong>
                    <span className="text-muted" style={{ fontSize: "0.9rem" }}>Impact: {pw.impact}%</span>
                  </div>
                  <ProgressBar variant="dark" now={pw.impact} style={{ height: "6px" }} className="mb-2" />
                  <div>
                    {pw.genes.map((gene, i) => (
                      <Badge key={i} bg="light" text="dark" className="me-2 border shadow-sm">{gene}</Badge>
                    ))}
                  </div>
                </div>
              ))}
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0 mb-4 p-3 bg-light" style={{ borderRadius: "12px" }}>
            <Card.Body>
              <h5 className="fw-bold mb-3">Clinical Interpretation</h5>
              <p className="text-muted mb-0" style={{ lineHeight: "1.7" }}>
                Based on the genomic profile, the model identified significant alterations in key resistance pathways. 
                The <strong>MAPK/ERK signaling pathway</strong> shows the highest activation score (87%), suggesting 
                potential bypass mechanisms that could reduce drug efficacy. The presence of mutations in <strong>KRAS</strong> and <strong>BRAF</strong> genes further supports this prediction.
              </p>
            </Card.Body>
          </Card>

        </Col>

        {/* العمود اليمين: الأزرار */}
        <Col md={4}>
          <Card className="shadow-sm border-0 mb-4 p-2" style={{ borderRadius: "12px" }}>
            <Card.Body>
              <h5 className="fw-bold mb-4">Actions</h5>
              <div className="d-grid gap-3">
                <Button variant="info" className="text-white fw-bold py-2"><Diagram3 className="me-2"/> View Interactive Graph</Button>
                <Button variant="outline-secondary" className="text-start py-2 fw-semibold text-dark"><ChatDots className="me-2"/> Ask AI Assistant</Button>
                <Button variant="outline-secondary" className="text-start py-2 fw-semibold text-dark"><Download className="me-2"/> Export Report</Button>
                <Button variant="outline-secondary" className="text-start py-2 fw-semibold text-dark"><Share className="me-2"/> Share Analysis</Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default ResultsPage;