import React from "react";
import { Container, Row, Col, Card, Badge, ProgressBar, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

function ResultsPage() {
  const navigate = useNavigate();

  // دي الداتا الوهمية اللي بعدين هنبدلها بالداتا اللي راجعة من الـ API بتاعك
  const pathways = [
    { name: "MAPK/ERK Signaling", impact: 87, genes: ["KRAS", "BRAF", "MEK1"] },
    { name: "PI3K/AKT Pathway", impact: 72, genes: ["PIK3CA", "AKT1", "PTEN"] },
    { name: "DNA Damage Response", impact: 65, genes: ["TP53", "ATM", "BRCA1"] }
  ];

  const alternatives = [
    "Trametinib (MEK inhibitor)", "Cobimetinib (MEK inhibitor)",
    "Everolimus (mTOR inhibitor)", "Dabrafenib (BRAF inhibitor)",
    "Combination: EGFR + MEK inhibitor"
  ];

  return (
    <Container className="py-5" style={{ maxWidth: "1100px" }}>
      {/* Header */}
      <div className="mb-4">
        <Button variant="link" className="text-decoration-none p-0 mb-2" style={{ color: "#00B4D8" }} onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </Button>
        <h2 className="fw-bold mb-1">Analysis Results</h2>
        <p className="text-muted">Patient P-428 - Cisplatin</p>
      </div>

      {/* Main Alert Card */}
      <Card className="p-4 mb-4 border-0 rounded-4" style={{ backgroundColor: "#fff5f5", border: "1px solid #ffcccc" }}>
        <div className="d-flex justify-content-between align-items-center">
          <div className="d-flex gap-3 align-items-center">
            <div style={{ width: "50px", height: "50px", backgroundColor: "#ff4d4f", borderRadius: "50%", color: "white", display: "flex", justifyContent: "center", alignItems: "center", fontSize: "24px", fontWeight: "bold" }}>
              !
            </div>
            <div>
              <Badge bg="danger" className="mb-1">Resistant</Badge>
              <h3 className="fw-bold mb-1">Drug Resistance Predicted</h3>
              <p className="mb-0 text-muted">The model predicts this patient is likely <strong className="text-dark">resistant</strong> to Cisplatin</p>
            </div>
          </div>
          <div className="text-end">
            <h1 className="fw-bold mb-0" style={{ fontSize: "48px" }}>85%</h1>
            <p className="text-muted mb-0">Confidence Score</p>
          </div>
        </div>
      </Card>

      <Row className="g-4">
        {/* Left Column: Details */}
        <Col md={8}>
          
          {/* Key Affected Pathways */}
          <Card className="p-4 mb-4 border-0 shadow-sm rounded-4">
            <h5 className="fw-bold mb-4">🧬 Key Affected Pathways</h5>
            {pathways.map((pathway, index) => (
              <div key={index} className="mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <span className="fw-bold">{pathway.name}</span>
                  <span className="text-muted">Impact: {pathway.impact}%</span>
                </div>
                <ProgressBar now={pathway.impact} variant="dark" style={{ height: "8px" }} className="mb-2" />
                <div className="d-flex gap-2">
                  {pathway.genes.map((gene, i) => (
                    <Badge key={i} bg="light" text="dark" className="border px-2 py-1">{gene}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </Card>

          {/* Clinical Interpretation */}
          <Card className="p-4 mb-4 border-0 shadow-sm rounded-4" style={{ backgroundColor: "#f8fafd" }}>
            <h5 className="fw-bold mb-3">Clinical Interpretation</h5>
            <p className="text-muted mb-0" style={{ lineHeight: "1.6" }}>
              Based on the genomic profile, the model identified significant alterations in key resistance pathways. The <strong>MAPK/ERK signaling pathway</strong> shows the highest activation score (87%), suggesting potential bypass mechanisms that could reduce drug efficacy. The presence of mutations in <strong>KRAS</strong> and <strong>BRAF</strong> genes further supports this prediction. Clinical consideration of alternative therapeutic strategies or combination therapies may be warranted.
            </p>
          </Card>

          {/* Alternative Treatment Options */}
          <Card className="p-4 mb-4 border-0 rounded-4" style={{ backgroundColor: "#fffafa", border: "1px solid #ffe5e5" }}>
            <h5 className="fw-bold mb-3" style={{ color: "#c92a2a" }}>Alternative Treatment Options</h5>
            <p className="text-danger mb-4" style={{ fontSize: "14px" }}>Based on the resistance profile, consider these potential alternatives (not guaranteed treatments):</p>
            <Row className="g-3">
              {alternatives.map((alt, index) => (
                <Col md={6} key={index}>
                  <Card className="p-3 border rounded-3 text-center shadow-sm h-100">
                    <span className="text-muted">{alt}</span>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>

        </Col>

        {/* Right Column: Actions */}
        <Col md={4}>
          <Card className="p-4 border-0 shadow-sm rounded-4 position-sticky" style={{ top: "20px" }}>
            <h5 className="fw-bold mb-4">Actions</h5>
            <div className="d-flex flex-column gap-3">
              <Button onClick={() => navigate('/visualization')} style={{ backgroundColor: "#00C4B4", border: "none", padding: "12px", fontWeight: "bold" }}>
                View Interactive Graph
              </Button>
              <Button variant="outline-secondary" onClick={() => navigate('/chat')} style={{ padding: "12px", textAlign: "left" }}>
                💬 Ask AI Assistant
              </Button>
              <Button variant="outline-secondary" style={{ padding: "12px", textAlign: "left" }}>
                📥 Export Report
              </Button>
              <Button variant="outline-secondary" style={{ padding: "12px", textAlign: "left" }}>
                🔗 Share Analysis
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default ResultsPage;