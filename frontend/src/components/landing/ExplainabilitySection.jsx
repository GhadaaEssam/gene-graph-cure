import React from "react";
import { Container, Row, Col } from "react-bootstrap";

function ExplainabilitySection() {
  return (
    <div style={{ padding: "100px 0", background: "#f8fafc" }}>
      <Container>
        <Row className="align-items-center">

          <Col md={6}>
            <h2 className="fw-bold mb-4">
              Why Explainability Matters
            </h2>

            <p className="text-muted mb-3">
              Traditional AI models act as black boxes. 
              In medical decision-making, transparency is essential.
            </p>

            <p className="text-muted">
              Our pathway-aware graph model highlights biological 
              mechanisms driving drug resistance, ensuring trust 
              and interpretability.
            </p>
          </Col>

          <Col md={6} className="text-center">
            <div className="explain-box">
              Black Box AI ❌  
              <br /><br />
              Explainable AI ✅
            </div>
          </Col>

        </Row>
      </Container>
    </div>
  );
}

export default ExplainabilitySection;