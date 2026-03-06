import React from "react";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import logo from "../../assets/logo01.png";

function MainNavbar() {
  return (
    <Navbar bg="white" expand="lg" className="py-2 border-bottom">
      <Container>

        {/* Logo */}
        <Navbar.Brand as={Link} to="/">
          <img
            src={logo}
            alt="GeneGraphCure"
            height="32"
            className="d-inline-block align-top"
          />
        </Navbar.Brand>

        <Navbar.Toggle />

        <Navbar.Collapse>
          <Nav className="ms-auto align-items-center gap-3">

            <Nav.Link as={Link} to="/model" className="text-dark fw-medium">
              Model
            </Nav.Link>

            <Nav.Link as={Link} to="/impact" className="text-dark fw-medium">
              Impact
            </Nav.Link>

            <Nav.Link as={Link} to="/login" className="text-dark fw-medium">
              Login
            </Nav.Link>

            <Button
              as={Link}
              to="/signup"
              variant="primary"
              size="sm"
              className="px-3"
            >
              Sign Up
            </Button>

          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default MainNavbar;