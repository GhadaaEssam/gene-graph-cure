import React from "react";
import { Container, Row, Col } from "react-bootstrap";

function ResearchAudienceSection() {
  return (
    <div style={{ padding: "100px 0", background: "#f8fafc" }}>
      <Container>

        <Row className="mb-5">
          <Col md={12} className="text-center">
            <h2 className="fw-bold">Built for Researchers & Clinicians</h2>
            <p className="text-muted">
              Supporting academic labs, oncology researchers, and healthcare innovators.
            </p>
          </Col>
        </Row>

        <Row>
          <Col md={6}>
            <h5 className="fw-semibold">Academic Research</h5>
            <p className="text-muted">
              Empowering research labs with graph-based predictive analytics.
            </p>
          </Col>

          <Col md={6}>
            <h5 className="fw-semibold">Clinical Decision Support</h5>
            <p className="text-muted">
              Providing explainable insights for therapeutic strategy refinement.
            </p>
          </Col>
        </Row>

      </Container>
    </div>
  );
}

export default ResearchAudienceSection;