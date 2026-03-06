import React from "react";
import { Container, Card, Form, Button } from "react-bootstrap";

function NewAnalysis() {
  return (
    <Container className="py-5">
      <h2 className="mb-4">New Cancer Drug Resistance Analysis</h2>

      <Card className="p-4">

        {/* Cancer Type */}
        <Form.Group className="mb-3">
          <Form.Label>Select Cancer Type</Form.Label>
          <Form.Select>
            <option>Liver Cancer (Sorafenib)</option>
            <option>Ovarian Cancer (Cisplatin)</option>
            <option>Melanoma (Immunotherapy)</option>
          </Form.Select>
        </Form.Group>

        {/* Multi-Omics Upload */}
        <h5 className="mt-4">Multi-Omics Data (Optional)</h5>

        <Form.Group className="mb-3">
          <Form.Label>Somatic Mutation Profiles</Form.Label>
          <Form.Control type="file" />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Copy Number Variation (CNV)</Form.Label>
          <Form.Control type="file" />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>DNA Methylation Levels</Form.Label>
          <Form.Control type="file" />
        </Form.Group>

        <Button variant="success" className="mt-3">
          Run Analysis
        </Button>

      </Card>
    </Container>
  );
}

export default NewAnalysis;