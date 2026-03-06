import React from "react";
import { Container, Row, Col } from "react-bootstrap";

function Step({ number, title, description }) {
  return (
    <div className="text-center position-relative">
      <div className="step-circle mb-3">
        {number}
      </div>
      <h6 className="fw-semibold">{title}</h6>
      <p className="text-muted small px-3">{description}</p>
    </div>
  );
}

function HowItWorksSection() {
  return (
    <div style={{ padding: "100px 0", backgroundColor: "#ffffff" }}>
      <Container>

        {/* Title */}
        <div className="text-center mb-5">
          <h2 className="fw-bold">How Our Model Works</h2>
          <p className="text-muted">
            A transparent, pathway-aware machine learning pipeline
          </p>
        </div>

        {/* Timeline Line */}
        <div className="timeline-line d-none d-md-block"></div>

        {/* Steps */}
        <Row className="text-center g-4 position-relative">

          <Col md={3}>
            <Step
              number="1"
              title="Data Integration"
              description="Multi-omics data including mutations, CNV, and methylation are integrated."
            />
          </Col>

          <Col md={3}>
            <Step
              number="2"
              title="Pathway Mapping"
              description="Genes are mapped into biological pathways for structured representation."
            />
          </Col>

          <Col md={3}>
            <Step
              number="3"
              title="Graph Learning"
              description="Graph neural networks analyze pathway interactions."
            />
          </Col>

          <Col md={3}>
            <Step
              number="4"
              title="Explainable Output"
              description="The system predicts resistance and highlights influential pathways."
            />
          </Col>

        </Row>

      </Container>
    </div>
  );
}

export default HowItWorksSection;