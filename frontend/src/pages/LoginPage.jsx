import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Container, Form, Button, Card, InputGroup, Alert, Spinner } from "react-bootstrap";
import { Envelope, Lock } from "react-bootstrap-icons"; 
// تأكدي إن مسار اللوجو صحيح
import logo from "../assets/logo01.png"; 
// استيراد الـ API
import { loginUser } from "../api/auth.api";

function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError(""); // مسح الخطأ لو اليوزر بدأ يكتب تاني
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // 1. بعت الداتا لـ API الدخول
      const response = await loginUser(formData);
      
      // 2. تخزين بيانات اليوزر في الـ LocalStorage عشان نستخدمها في الداشبورد
      localStorage.setItem("userToken", response.token);
      localStorage.setItem("userName", response.user.name);
      
      // 3. التوجيه لصفحة الداشبورد
      navigate("/dashboard");
      
    } catch (err) {
      setError(err.message || "Failed to sign in. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // خلفية خفيفة جداً زي اللي في التصميم
    <div style={{ backgroundColor: "#f4fcfc", minHeight: "100vh", display: "flex", alignItems: "center", padding: "40px 0" }}>
      <style>
        {`
          .input-custom { background-color: #f8f9fa; border-left: none; font-size: 0.95rem; }
          .input-custom:focus { box-shadow: none; border-color: #dee2e6; }
          .icon-bg { background-color: #f8f9fa; border-right: none; }
          .btn-login { background: linear-gradient(90deg, #0ea5e9, #14b8a6); border: none; padding: 12px; border-radius: 8px; font-weight: 600; color: white; transition: opacity 0.2s; }
          .btn-login:hover { opacity: 0.9; color: white; }
          .btn-login:disabled { opacity: 0.7; cursor: not-allowed; }
          .forgot-link { font-size: 0.85rem; color: #14b8a6; text-decoration: none; font-weight: 500; transition: color 0.2s; }
          .forgot-link:hover { color: #0d9488; }
          .link-teal { color: #14b8a6; font-weight: 600; text-decoration: none; }
          .link-teal:hover { color: #0d9488; text-decoration: underline; }
        `}
      </style>

      <Container className="d-flex flex-column align-items-center">
        
        {/* Header Section (Logo & Titles) */}
        <div className="text-center mb-4">
          <img src={logo} alt="GeneGraph Cure Logo" style={{ width: "90px", marginBottom: "15px" }} />
          <h5 className="fw-bold mb-1" style={{ color: "#0f2027", fontSize: "1.1rem" }}>Gene Graph Cure</h5>
          <p className="text-secondary mb-3" style={{ fontSize: "0.8rem" }}>Predicting Cancer Drug Resistance With GNN & AI</p>
          
          <h3 className="fw-bold mb-1" style={{ color: "#0f2027" }}>Welcome Back</h3>
          <p className="text-muted" style={{ fontSize: "0.9rem" }}>Sign in to access your analysis dashboard</p>
        </div>

        {/* Login Card */}
        <Card className="shadow-sm border-0 p-2" style={{ width: "100%", maxWidth: "420px", borderRadius: "16px" }}>
          <Card.Body className="p-4">
            
            {error && <Alert variant="danger" className="p-2 text-center" style={{ fontSize: "0.85rem" }}>{error}</Alert>}

            <Form onSubmit={handleSubmit}>
              
              <Form.Group className="mb-4">
                <Form.Label style={{ fontSize: "0.85rem", fontWeight: "700", color: "#334155" }}>Email Address</Form.Label>
                <InputGroup>
                  <InputGroup.Text className="icon-bg"><Envelope color="#94a3b8" /></InputGroup.Text>
                  <Form.Control 
                    type="email" 
                    name="email" 
                    placeholder="researcher@university.edu" 
                    required 
                    onChange={handleChange} 
                    className="input-custom" 
                  />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-4">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <Form.Label className="m-0" style={{ fontSize: "0.85rem", fontWeight: "700", color: "#334155" }}>Password</Form.Label>
                  <Link to="#" className="forgot-link">Forgot password?</Link>
                </div>
                <InputGroup>
                  <InputGroup.Text className="icon-bg"><Lock color="#94a3b8" /></InputGroup.Text>
                  <Form.Control 
                    type="password" 
                    name="password" 
                    placeholder="••••••••" 
                    required 
                    onChange={handleChange} 
                    className="input-custom" 
                  />
                </InputGroup>
              </Form.Group>

              <Button type="submit" disabled={isLoading} className="btn-login w-100 mt-2">
                {isLoading ? (
                  <><Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" /> Signing In...</>
                ) : (
                  "Sign In"
                )}
              </Button>
            </Form>
            
            <div className="text-center mt-4" style={{ fontSize: "0.9rem" }}>
              <span className="text-muted">Don't have an account? </span>
              <Link to="/signup" className="link-teal">Sign up</Link>
            </div>
          </Card.Body>
        </Card>

        {/* Footer Text */}
        <div className="text-center mt-4 text-muted" style={{ fontSize: "0.75rem" }}>
          By continuing, you agree to our Terms of Service and Privacy Policy
        </div>

      </Container>
    </div>
  );
}

export default LoginPage;