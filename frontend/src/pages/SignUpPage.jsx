import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Container, Form, Button, Card, InputGroup } from "react-bootstrap";
import { Person, Envelope, Lock } from "react-bootstrap-icons"; // لازم تكوني مسطبة react-bootstrap-icons

function SignUpPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    console.log("Account created for:", formData.fullName);
   navigate("/new-analysis");
  };

  return (
    <div style={{ backgroundColor: "#f4fcfc", minHeight: "100vh", display: "flex", alignItems: "center", paddingTop: "40px" }}>
      <Container className="d-flex flex-column align-items-center">
        
        {/* Logo and Header */}
        <div className="text-center mb-4">
          <img src="../assets/logo01.png" alt="GeneGraph Logo" style={{ width: "50px", marginBottom: "10px" }} />
          <h2 className="fw-bold" style={{ color: "#0f2027" }}>Create Account</h2>
          <p className="text-muted">Join the research platform</p>
        </div>

        {/* Form Card */}
        <Card className="shadow-sm border-0" style={{ width: "100%", maxWidth: "450px", borderRadius: "12px" }}>
          <Card.Body className="p-4 p-md-5">
            <Form onSubmit={handleSubmit}>
              
              <Form.Group className="mb-3">
                <Form.Label style={{ fontSize: "0.9rem", fontWeight: "600" }}>Full Name</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Person color="gray" /></InputGroup.Text>
                  <Form.Control type="text" name="fullName" placeholder="Dr. Jane Smith" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none" }} />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label style={{ fontSize: "0.9rem", fontWeight: "600" }}>Email Address</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Envelope color="gray" /></InputGroup.Text>
                  <Form.Control type="email" name="email" placeholder="researcher@university.edu" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none" }} />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label style={{ fontSize: "0.9rem", fontWeight: "600" }}>Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Lock color="gray" /></InputGroup.Text>
                  <Form.Control type="password" name="password" placeholder="••••••••" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none" }} />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-4">
                <Form.Label style={{ fontSize: "0.9rem", fontWeight: "600" }}>Confirm Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Lock color="gray" /></InputGroup.Text>
                  <Form.Control type="password" name="confirmPassword" placeholder="••••••••" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none" }} />
                </InputGroup>
              </Form.Group>

              <Button type="submit" className="w-100 fw-bold border-0" style={{ background: "linear-gradient(90deg, #2193b0, #6dd5ed)", padding: "10px", borderRadius: "8px" }}>
                Create Account
              </Button>
            </Form>
            
            <div className="text-center mt-4" style={{ fontSize: "0.9rem" }}>
              <span className="text-muted">Already have an account? </span>
              <Link to="/login" style={{ color: "#2193b0", fontWeight: "bold", textDecoration: "none" }}>Sign in</Link>
            </div>
          </Card.Body>
        </Card>

        {/* Footer Text */}
        <div className="text-center mt-4 text-muted" style={{ fontSize: "0.75rem", maxWidth: "450px" }}>
          By creating an account, you agree to our Terms of Service and Privacy Policy
        </div>

      </Container>
    </div>
  );
}

export default SignUpPage;