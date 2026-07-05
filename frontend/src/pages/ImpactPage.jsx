import React from "react";
import { Link } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  ProgressBar,
} from "react-bootstrap";

import {
  Activity,
  Target,
  GitBranch,
  Users,
  Building2,
  BarChart3,
  Pill,
  TrendingUp,
} from "lucide-react";

function ImpactPage() {
  const impactStats = [
    {
      icon: <Activity size={28} />,
      value: "1K+",
      label: "Samples Analyzed",
    },
    {
      icon: <Target size={28} />,
      value: "90%",
      label: "Prediction Accuracy",
    },
    {
      icon: <GitBranch size={28} />,
      value: "15+",
      label: "Pathways Mapped",
    },
    {
      icon: <Users size={28} />,
      value: "1000+",
      label: "Registered Users",
    },
    {
      icon: <Building2 size={28} />,
      value: "20+",
      label: "Hospitals & Research Labs",
    },
    {
      icon: <BarChart3 size={28} />,
      value: "9,000+",
      label: "AI-Generated Reports",
    },
  ];

  const cancerTypes = [
    { name: "Liver Cancer", value: 42 },
    { name: "Ovarian Cancer", value: 35 },
    { name: "Melanoma", value: 23 },
  ];

  const drugs = [
    {
      name: "Sorafenib",
      description: "Targeted therapy for liver cancer",
    },
    {
      name: "Cisplatin",
      description: "Chemotherapy for ovarian cancer",
    },
    {
      name: "Paclitaxel",
      description: "Chemotherapy agent",
    },
    {
      name: "Nivolumab",
      description: "Immunotherapy for melanoma",
    },
    {
      name: "Pembrolizumab",
      description: "Anti-PD-1 immunotherapy",
    },
    {
      name: "Doxorubicin",
      description: "Anthracycline chemotherapy",
    },
  ];

  const trends = [
    {
      name: "Liver Cancer",
      progress: 75,
      increase: "+18%",
    },
    {
      name: "Ovarian Cancer",
      progress: 62,
      increase: "+12%",
    },
    {
      name: "Melanoma",
      progress: 44,
      increase: "+8%",
    },
  ];

  return (
    <div style={{ background: "#f8fafc" }}>
      {/* HERO SECTION */}
      <section
        style={{
          background:
            "linear-gradient(90deg, rgba(219,245,242,1) 0%, rgba(243,248,252,1) 100%)",
          padding: "90px 0",
        }}
      >
        <Container className="text-center">
          <h1 className="fw-bold mb-3" style={{ fontSize: "52px" }}>
            Platform Impact at a Glance
          </h1>

          <p className="text-muted fs-5">
            Growing adoption across cancer research and clinical innovation
          </p>
        </Container>
      </section>

      {/* IMPACT STATS */}
      <Container className="py-5">
        <Row className="g-4 justify-content-center">
          {impactStats.map((item, index) => (
            <Col md={4} lg={4} key={index}>
              <Card className="border-0 shadow-sm rounded-4 p-5 text-center h-100">
                <div
                  className="mx-auto mb-4 d-flex align-items-center justify-content-center"
                  style={{
                    width: "70px",
                    height: "70px",
                    borderRadius: "50%",
                    background: "#dff8f5",
                    color: "#19b6b6",
                  }}
                >
                  {item.icon}
                </div>

                <h2
                  className="fw-bold mb-2"
                  style={{ color: "#1792ff" }}
                >
                  {item.value}
                </h2>

                <p className="text-muted mb-0">{item.label}</p>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>

      {/* MOST ANALYZED CANCER TYPES */}
      <section className="py-5">
        <Container>
          <div className="text-center mb-5">
            <h2 className="fw-bold">Most Analyzed Cancer Types</h2>
            <p className="text-muted">
              Analysis frequency across the platform
            </p>
          </div>

          <Card className="border-0 shadow-sm rounded-4 p-5">
            {cancerTypes.map((item, index) => (
              <div key={index} className="mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <span className="fw-semibold">{item.name}</span>
                  <span
                    className="fw-bold"
                    style={{ color: "#1fb6b5" }}
                  >
                    {item.value}%
                  </span>
                </div>

                <ProgressBar
                  now={item.value}
                  style={{
                    height: "12px",
                    borderRadius: "20px",
                  }}
                />
              </div>
            ))}
          </Card>
        </Container>
      </section>

      {/* RECOMMENDED DRUGS */}
      <section className="py-5">
        <Container>
          <div className="text-center mb-5">
            <h2 className="fw-bold">
              Most Frequently Recommended Drugs
            </h2>

            <p className="text-muted">
              Top alternative treatment recommendations
            </p>
          </div>

          <Row className="g-4">
            {drugs.map((drug, index) => (
              <Col md={4} key={index}>
                <Card className="border-0 shadow-sm rounded-4 p-5 text-center h-100">
                  <div
                    className="mx-auto mb-4 d-flex align-items-center justify-content-center"
                    style={{
                      width: "65px",
                      height: "65px",
                      borderRadius: "50%",
                      background: "#dff8f5",
                      color: "#1fb6b5",
                    }}
                  >
                    <Pill size={26} />
                  </div>

                  <h5 className="fw-bold">{drug.name}</h5>

                  <p className="text-muted small mb-0">
                    {drug.description}
                  </p>
                </Card>
              </Col>
            ))}
          </Row>
        </Container>
      </section>

      {/* RESEARCH TRENDS */}
      <section className="py-5">
        <Container>
          <div className="text-center mb-5">
            <h2 className="fw-bold">Research Activity Trends</h2>

            <p className="text-muted">
              Analysis volume across cancer types over time
            </p>
          </div>

          <Card className="border-0 shadow-sm rounded-4 p-5">
            {trends.map((item, index) => (
              <div key={index} className="mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <div className="d-flex align-items-center gap-2">
                    <TrendingUp size={18} color="#19b6b6" />
                    <span className="fw-semibold">{item.name}</span>
                  </div>

                  <span
                    className="fw-bold"
                    style={{ color: "#1fb6b5" }}
                  >
                    {item.increase}
                  </span>
                </div>

                <ProgressBar
                  now={item.progress}
                  style={{
                    height: "12px",
                    borderRadius: "20px",
                  }}
                />
              </div>
            ))}
          </Card>
        </Container>
      </section>

      {/* CTA SECTION */}
      <section
        className="py-5"
        style={{
          background:
            "linear-gradient(90deg, rgba(227,246,245,1) 0%, rgba(244,250,252,1) 100%)",
        }}
      >
        <Container className="text-center">
          <h2 className="fw-bold mb-3">
            Join the growing community advancing precision oncology
          </h2>

          <p className="text-muted mb-4">
            Start analyzing cancer drug resistance with our AI-powered
            platform
          </p>

          <Button
            as={Link} to="/signup"
            style={{
              background:
                "linear-gradient(90deg, #199cff 0%, #18c6b6 100%)",
              border: "none",
              padding: "12px 34px",
              borderRadius: "12px",
              fontWeight: "600",
            }}
          >
            Get Started
          </Button>
        </Container>
      </section>

      {/* FOOTER */}
      <footer
        style={{
          background: "#07142e",
          color: "#fff",
          padding: "50px 0",
        }}
      >
        <Container className="text-center">
          <h5 className="fw-bold mb-3">GeneGraphCure</h5>

          <p className="text-light opacity-75 mb-2">
            Research Platform for Predicting Cancer Drug Resistance
          </p>

          <small className="text-light opacity-50">
            Academic Research Disclaimer: This platform is designed for
            research purposes only.
          </small>
        </Container>
      </footer>
    </div>
  );
}

export default ImpactPage;