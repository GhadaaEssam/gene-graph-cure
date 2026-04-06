import React from "react";
import { Container, Card, Form, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

function SignUpPage() {
  const navigate = useNavigate(); 

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

          {/* الزرار بعد التظبيط */}
          <Button 
            variant="primary" 
            className="w-100 mt-3" 
            onClick={() => navigate('/dashboard')}
          >
            Sign Up
          </Button>
        </Form>
      </Card>
    </Container>
  );
}

export default SignUpPage;