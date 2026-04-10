import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Container, Form, Button, Card, InputGroup, Alert } from "react-bootstrap";
import { Person, Envelope, Lock } from "react-bootstrap-icons"; 

// 1. استيراد اللوجو بالشكل الصحيح في رياكت (تأكدي إن المسار ده صح بالنسبة لملف الـ SignUp)
import logo from "../assets/logo01.png"; 

function SignUpPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  
  // 2. إضافة حالة للخطأ عشان نعرضه بشكل أشيك من الـ alert
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError(""); // مسح الخطأ بمجرد ما المستخدم يبدأ يكتب تاني
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match!");
      return;
    }
    console.log("Account created for:", formData.fullName);
    navigate("/new-analysis");
  };

  return (
    // استخدام calc عشان نخصم مساحة الـ Navbar التقريبية ونمنع السكرول
    <div style={{ backgroundColor: "#f8fafc", minHeight: "calc(100vh - 70px)", display: "flex", alignItems: "center", padding: "20px 0" }}>
      <Container className="d-flex flex-column align-items-center">
        
        {/* Logo and Header */}
        <div className="text-center mb-3">
          {/* استخدام اللوجو المستورد */}
          <img src={logo} alt="GeneGraph Logo" style={{ width: "45px", marginBottom: "8px" }} />
          <h3 className="fw-bold mb-1" style={{ color: "#0f2027" }}>Create Account</h3>
          <p className="text-muted" style={{ fontSize: "0.9rem" }}>Join the research platform</p>
        </div>

        {/* Form Card - تم تصغير العرض والمسافات الداخلية */}
        <Card className="shadow-sm border-0" style={{ width: "100%", maxWidth: "420px", borderRadius: "12px" }}>
          <Card.Body className="p-4">
            
            {/* عرض رسالة الخطأ هنا */}
            {error && <Alert variant="danger" className="p-2 text-center" style={{ fontSize: "0.85rem" }}>{error}</Alert>}

            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label style={{ fontSize: "0.85rem", fontWeight: "600", color: "#475569" }}>Full Name</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Person color="gray" /></InputGroup.Text>
                  <Form.Control type="text" name="fullName" placeholder="Dr. Jane Smith" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none", fontSize: "0.95rem" }} />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label style={{ fontSize: "0.85rem", fontWeight: "600", color: "#475569" }}>Email Address</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Envelope color="gray" /></InputGroup.Text>
                  <Form.Control type="email" name="email" placeholder="researcher@university.edu" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none", fontSize: "0.95rem" }} />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label style={{ fontSize: "0.85rem", fontWeight: "600", color: "#475569" }}>Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Lock color="gray" /></InputGroup.Text>
                  <Form.Control type="password" name="password" placeholder="••••••••" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none", fontSize: "0.95rem" }} />
                </InputGroup>
              </Form.Group>

              <Form.Group className="mb-4">
                <Form.Label style={{ fontSize: "0.85rem", fontWeight: "600", color: "#475569" }}>Confirm Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text style={{ backgroundColor: "#f8f9fa", borderRight: "none" }}><Lock color="gray" /></InputGroup.Text>
                  <Form.Control type="password" name="confirmPassword" placeholder="••••••••" required onChange={handleChange} style={{ backgroundColor: "#f8f9fa", borderLeft: "none", fontSize: "0.95rem" }} />
                </InputGroup>
              </Form.Group>

              <Button type="submit" className="w-100 fw-bold border-0" style={{ background: "linear-gradient(90deg, #2193b0, #6dd5ed)", padding: "10px", borderRadius: "8px", transition: "opacity 0.2s" }}>
                Create Account
              </Button>
            </Form>
            
            <div className="text-center mt-3" style={{ fontSize: "0.85rem" }}>
              <span className="text-muted">Already have an account? </span>
              <Link to="/login" style={{ color: "#2193b0", fontWeight: "bold", textDecoration: "none" }}>Sign in</Link>
            </div>
          </Card.Body>
        </Card>

        {/* Footer Text */}
        <div className="text-center mt-3 text-muted" style={{ fontSize: "0.75rem", maxWidth: "400px" }}>
          By creating an account, you agree to our Terms of Service and Privacy Policy.
        </div>

      </Container>
    </div>
  );
}

export default SignUpPage;