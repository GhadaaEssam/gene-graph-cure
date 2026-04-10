import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { Link } from "react-router-dom";
// استيراد الأيقونات من مكتبة react-icons
import { 
  FaTableCellsLarge, 
  FaRegFileLines, 
  FaFileInvoice, 
  FaDiagramProject, 
  FaRegMessage, 
  FaArrowRightFromBracket 
} from "react-icons/fa6";

// استدعاء اللوجو بتاعك
import logo from "../../assets/logo01.png";

function PrivateNavbar() {
  return (
    <>
      <style>
        {`
          .custom-nav-link {
            color: #475569 !important;
            transition: color 0.2s ease-in-out;
          }
          /* تعديل هنا عشان يطبق اللون على الـ svg بتاع الأيقونة */
          .custom-nav-link svg {
            color: #94a3b8;
            font-size: 1.1rem;
            transition: color 0.2s ease-in-out;
          }
          .custom-nav-link:hover,
          .custom-nav-link:hover svg {
            color: #2563eb !important;
          }
          .brand-text {
            font-weight: 700;
            color: #1e293b;
            font-size: 1.25rem;
            letter-spacing: 0.5px;
          }
        `}
      </style>

      <Navbar bg="white" expand="lg" className="py-2 border-bottom shadow-sm">
        <Container fluid className="px-4 px-lg-5">
          
          <Navbar.Brand as={Link} to="/" className="d-flex align-items-center gap-2">
            <img
              src={logo}
              alt="Home"
              height="36"
              className="d-inline-block align-top"
            />
            <span className="brand-text">HOME</span>
          </Navbar.Brand>

          <Navbar.Toggle aria-controls="private-navbar-nav" />

          <Navbar.Collapse id="private-navbar-nav">
            <Nav className="ms-auto align-items-center gap-3 gap-lg-4">

              <Nav.Link as={Link} to="/dashboard" className="custom-nav-link fw-medium d-flex align-items-center gap-2">
                <FaTableCellsLarge /> Dashboard
              </Nav.Link>

              <Nav.Link as={Link} to="/new-analysis" className="custom-nav-link fw-medium d-flex align-items-center gap-2">
                <FaRegFileLines /> New Analysis
              </Nav.Link>

              <Nav.Link as={Link} to="/results" className="custom-nav-link fw-medium d-flex align-items-center gap-2">
                <FaFileInvoice /> Results
              </Nav.Link>

              <Nav.Link as={Link} to="/visualization" className="custom-nav-link fw-medium d-flex align-items-center gap-2">
                <FaDiagramProject /> Visualization
              </Nav.Link>

              <Nav.Link as={Link} to="/chat" className="custom-nav-link fw-medium d-flex align-items-center gap-2">
                <FaRegMessage /> Chat Assistant
              </Nav.Link>

              <div className="d-none d-lg-block" style={{ height: '24px', width: '1px', backgroundColor: '#e2e8f0' }}></div>

              <Nav.Link as={Link} to="/logout" className="custom-nav-link fw-medium d-flex align-items-center gap-2">
                <FaArrowRightFromBracket /> Log Out
              </Nav.Link>

            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </>
  );
}

export default PrivateNavbar;