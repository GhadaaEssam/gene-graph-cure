import React from "react";
import { Container } from "react-bootstrap";

function FooterSection() {
  return (
    <div style={{ background: "#0d1b2a", color: "white", padding: "40px 0" }}>
      <Container className="text-center">
        <h6 className="fw-bold">GeneGraphCure</h6>
        <p className="small mb-0">
          © 2026 All Rights Reserved.
        </p>
      </Container>
    </div>
  );
}

export default FooterSection;