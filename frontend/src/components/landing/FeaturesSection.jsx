import React from "react";
import { Container, Row, Col, Card } from "react-bootstrap";
import { BarChart3, Brain, ShieldCheck, Network } from "lucide-react";

function FeaturesSection() {
  return (
    <div style={{ padding: "100px 0", background: "white" }}>
      <Container>

        <div className="text-center mb-5">
          <h2 className="fw-bold">Key Platform Features</h2>
          <p className="text-muted">
            Designed for precision oncology research
          </p>
        </div>

        <Row className="g-4">

          <Col md={3}>
            <Card className="feature-card p-4 border-0 text-center">
              <BarChart3 size={40} color="#1f8cff" />
              <h6 className="mt-3 fw-semibold">Resistance Scoring</h6>
              <p className="text-muted small">
                Quantitative resistance prediction score.
              </p>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="feature-card p-4 border-0 text-center">
              <Network size={40} color="#1f8cff" />
              <h6 className="mt-3 fw-semibold">Pathway Graphs</h6>
              <p className="text-muted small">
                Interactive biological network visualization.
              </p>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="feature-card p-4 border-0 text-center">
              <Brain size={40} color="#1f8cff" />
              <h6 className="mt-3 fw-semibold">AI Assistant</h6>
              <p className="text-muted small">
                Natural language explanation of predictions.
              </p>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="feature-card p-4 border-0 text-center">
              <ShieldCheck size={40} color="#1f8cff" />
              <h6 className="mt-3 fw-semibold">Clinical Trust</h6>
              <p className="text-muted small">
                Transparent model aligned with research ethics.
              </p>
            </Card>
          </Col>

        </Row>

      </Container>
    </div>
  );
}

export default FeaturesSection;