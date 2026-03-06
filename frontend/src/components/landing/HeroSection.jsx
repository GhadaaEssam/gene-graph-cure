import React from "react";
import { Container, Button } from "react-bootstrap";

function HeroSection() {
  return (
    <div
      style={{
        background: "linear-gradient(to bottom, #eaf3fb, #ffffff)",
        padding: "100px 0",
        textAlign: "center"
      }}
    >
      <Container>
        <h1 className="fw-bold mb-3" style={{ fontSize: "42px" }}>
          Predicting Cancer Drug Resistance
        </h1>

        <h2 className="fw-bold mb-4" style={{ color: "#1f8cff" }}>
          Through Explainable AI
        </h2>

        <p className="text-muted mb-5" style={{ maxWidth: "700px", margin: "0 auto" }}>
          GeneGraphCure uses graph-based, pathway-aware machine learning
          to predict and explain cancer drug resistance with transparency.
        </p>

        <div className="d-flex justify-content-center gap-3">
          <Button variant="primary" size="lg">
            Get Started
          </Button>

          <Button variant="outline-secondary" size="lg">
            Watch Demo
          </Button>
        </div>
      </Container>
    </div>
  );
}

export default HeroSection;