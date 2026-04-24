import React from "react";
import { Container, Row, Col, Card } from "react-bootstrap";
import { Shield, Activity, Cpu } from "lucide-react";

function ChallengeSection() {
  return (
    <div style={{ padding: "80px 0", backgroundColor: "#f8fafc" }}>
      <Container>

        {/* Section Title */}
        <div className="text-center mb-5">
          <h2 className="fw-bold">Understanding the Challenge</h2>
          <p className="text-muted">
            Cancer treatment resistance remains one of medicine's greatest challenges
          </p>
        </div>

        {/* Cards */}
        <Row className="g-4">

          <Col md={4}>
            <Card className="h-100 shadow-sm border-0 p-4 text-center">
              <div className="mb-3">
                <Shield size={40} color="#1f8cff" />
              </div>
              <h5 className="fw-semibold">Cancer Therapies</h5>
              <p className="text-muted small">
                Modern cancer treatment relies on targeted therapies and
                immunotherapy. However, patient responses vary due to
                molecular complexity.
              </p>
            </Card>
          </Col>

          <Col md={4}>
            <Card className="h-100 shadow-sm border-0 p-4 text-center">
              <div className="mb-3">
                <Activity size={40} color="#1f8cff" />
              </div>
              <h5 className="fw-semibold">Drug Resistance</h5>
              <p className="text-muted small">
                Tumors evolve resistance through genetic mutations and pathway
                rewiring, reducing treatment effectiveness.
              </p>
            </Card>
          </Col>

          <Col md={4}>
            <Card className="h-100 shadow-sm border-0 p-4 text-center">
              <div className="mb-3">
                <Cpu size={40} color="#1f8cff" />
              </div>
              <h5 className="fw-semibold">AI Solution</h5>
              <p className="text-muted small">
                Our explainable AI model predicts resistance patterns and
                provides biological insights to guide therapy decisions.
              </p>
            </Card>
          </Col>

        </Row>

      </Container>
    </div>
  );
}

export default ChallengeSection;