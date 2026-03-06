import React from "react";
import { Container, Card, Form, Button } from "react-bootstrap";

function SignUpPage() {
  return (
    <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: "90vh" }}>
      <Card style={{ width: "450px", padding: "25px" }}>
        <h3 className="text-center mb-4">Create Account</h3>

        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Full Name</Form.Label>
            <Form.Control type="text" placeholder="Enter full name" />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Email Address</Form.Label>
            <Form.Control type="email" placeholder="researcher@university.edu" />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Password</Form.Label>
            <Form.Control type="password" placeholder="Create password" />
          </Form.Group>

          <Button variant="primary" className="w-100">
            Sign Up
          </Button>
        </Form>
      </Card>
    </Container>
  );
}

export default SignUpPage;