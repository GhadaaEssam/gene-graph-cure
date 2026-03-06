import React from "react";
import { Container, Card } from "react-bootstrap";

function InteractiveVisualization() {
  return (
    <Container className="py-5">
      <h2>Interactive Visualization</h2>

      <Card className="p-4 mt-4">
        <h5>Pathway Network Graph</h5>

        {/* Placeholder for Graph */}
        <div
          style={{
            height: "400px",
            background: "#eef2f7",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: "10px"
          }}
        >
          Graph Visualization Placeholder
        </div>
      </Card>
    </Container>
  );
}

export default InteractiveVisualization;