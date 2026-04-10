import React from "react";
import { Container, Row, Col, Card, Badge, ProgressBar, Button } from "react-bootstrap";
import { Link, useLocation } from "react-router-dom";
import { FaArrowLeft, FaTriangleExclamation, FaShareNodes, FaDownload, FaRegMessage, FaNetworkWired } from "react-icons/fa6";

function Results() {
  // استلام الداتا اللي مبعوتة من صفحة NewAnalysis
  const location = useLocation();
  const passedData = location.state;

  // الداتا الافتراضية (عشان لو اليوزر عمل ريفريش، الصفحة متضربش وتفضل بالشكل اللي في صورتك)
  const defaultData = {
    patientId: "Patient P-428",
    drug: passedData?.cancerType ? `Targeted Therapy for ${passedData.cancerType}` : "Cisplatin",
    prediction: passedData?.status || "Resistant",
    confidence: passedData?.riskScore || 85,
    pathways: [
      { name: "MAPK/ERK Signaling", impact: 87, genes: ["KRAS", "BRAF", "MEK1"] },
      { name: "PI3K/AKT Pathway", impact: 72, genes: ["PIK3CA", "AKT1", "PTEN"] },
      { name: "DNA Damage Response", impact: 65, genes: passedData?.detectedMutations || ["TP53", "ATM", "BRCA1"] }
    ],
    interpretation: passedData?.recommendedAction 
      ? `Based on the genomic profile, the model identified significant alterations. ${passedData.recommendedAction}` 
      : "Based on the genomic profile, the model identified significant alterations in key resistance pathways. The MAPK/ERK signaling pathway shows the highest activation score (87%), suggesting potential bypass mechanisms that could reduce drug efficacy. The presence of mutations in KRAS and BRAF genes further supports this prediction.",
    alternatives: [
      "Trametinib (MEK inhibitor)", 
      "Cobimetinib (MEK inhibitor)",
      "Everolimus (mTOR inhibitor)", 
      "Dabrafenib (BRAF inhibitor)",
      "Combination: EGFR + MEK inhibitor"
    ],
    aiQuestions: [
      "Why is this patient resistant?",
      "Which biological mechanisms are involved?",
      "What are the alternative treatment options?"
    ]
  };

  // دمج الداتا المبعوتة مع الداتا الافتراضية
  const data = { ...defaultData, ...passedData };

  return (
    <div className="results-page py-4">
      <style>
        {`
          .results-page { background-color: #f8fafc; min-height: calc(100vh - 70px); font-family: 'Segoe UI', system-ui, sans-serif; }
          .back-link { color: #14b8a6; text-decoration: none; font-weight: 500; font-size: 0.85rem; transition: color 0.2s; }
          .back-link:hover { color: #0d9488; }
          
          /* كارت التحذير الأساسي (أحمر) */
          .alert-card { background-color: #fff5f5; border: 1px solid #fecaca; border-radius: 12px; }
          .alert-icon-wrapper { background-color: #ef4444; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 1.5rem; }
          
          /* الكروت العادية */
          .custom-card { border: 1px solid #e2e8f0; border-radius: 12px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
          .card-title { color: #0f2027; font-weight: 700; font-size: 1.05rem; display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
          
          /* مسارات الجينات (Pathways) */
          .pathway-item { margin-bottom: 20px; }
          .gene-badge { background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; font-weight: 600; font-size: 0.75rem; margin-right: 6px; padding: 4px 8px; border-radius: 6px; }
          .custom-progress { height: 6px; border-radius: 3px; background-color: #e2e8f0; margin: 8px 0; }
          .custom-progress .progress-bar { background-color: #0f2027; }
          
          /* الأزرار (Actions) */
          .btn-action-primary { background: linear-gradient(90deg, #0ea5e9, #14b8a6); border: none; color: white; font-weight: 600; padding: 10px; border-radius: 8px; transition: opacity 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
          .btn-action-primary:hover { opacity: 0.9; color: white; }
          .btn-action-outline { background: white; border: 1px solid #cbd5e1; color: #334155; font-weight: 600; padding: 10px; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; justify-content: flex-start; gap: 10px; text-align: left; }
          .btn-action-outline:hover { background: #f8fafc; border-color: #94a3b8; }
          
          /* الأقسام السفلية */
          .interpretation-card { background-color: #f0f9ff; border: 1px solid #e0f2fe; }
          .alternatives-card { background-color: #fff1f2; border: 1px solid #ffe4e6; }
          .ai-card { background-color: #f0fdfa; border: 1px solid #ccfbf1; }
          
          /* مربعات البدائل والأسئلة */
          .option-box { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; color: #334155; font-size: 0.9rem; font-weight: 500; height: 100%; display: flex; align-items: center; cursor: pointer; transition: border-color 0.2s; }
          .option-box:hover { border-color: #14b8a6; }
          .alt-option-box { border-color: #fecaca; }
          .alt-option-box:hover { border-color: #ef4444; }
        `}
      </style>

      <Container style={{ maxWidth: "1000px" }}>
        
        {/* زر الرجوع */}
        <div className="mb-3">
          <Link to="/dashboard" className="back-link d-flex align-items-center gap-2">
            <FaArrowLeft /> Back to Dashboard
          </Link>
        </div>

        {/* عنوان الصفحة */}
        <div className="mb-4">
          <h3 className="fw-bold text-dark mb-1">Analysis Results</h3>
          <p className="text-secondary" style={{ fontSize: "0.9rem" }}>{data.patientId} - {data.drug}</p>
        </div>

        {/* كارت النتيجة الأساسي (أحمر) */}
        <Card className="alert-card mb-4 p-4 shadow-sm">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div className="d-flex align-items-center gap-3">
              <div className="alert-icon-wrapper shadow-sm">
                <FaTriangleExclamation />
              </div>
              <div>
                <Badge bg="danger" className="mb-1 px-2 py-1 rounded-pill" style={{fontSize: "0.7rem"}}>Resistant</Badge>
                <h4 className="fw-bold m-0" style={{ color: "#0f2027" }}>Drug {data.prediction} Predicted</h4>
                <span className="text-secondary" style={{fontSize: "0.9rem"}}>The model predicts this patient is likely <strong>resistant</strong> to {data.drug}</span>
              </div>
            </div>
            <div className="text-end">
              <h2 className="fw-bold m-0" style={{ color: "#0f2027", fontSize: "2.5rem" }}>{data.confidence}%</h2>
              <span className="text-secondary" style={{fontSize: "0.85rem"}}>Confidence Score</span>
            </div>
          </div>
        </Card>

        {/* القسم الأوسط (الجينات والأكشنز) */}
        <Row className="mb-4 g-4">
          
          {/* العمود الأول: Pathways */}
          <Col lg={8}>
            <Card className="custom-card p-4 h-100">
              <div className="card-title">
                <FaNetworkWired className="text-success fs-5" /> Key Affected Pathways
              </div>
              
              {data.pathways.map((pathway, index) => (
                <div key={index} className="pathway-item">
                  <div className="d-flex justify-content-between align-items-end mb-1">
                    <span className="fw-bold text-dark" style={{fontSize: "0.95rem"}}>{pathway.name}</span>
                    <span className="text-secondary" style={{fontSize: "0.8rem"}}>Impact: {pathway.impact}%</span>
                  </div>
                  <ProgressBar now={pathway.impact} className="custom-progress shadow-sm" />
                  <div className="mt-2">
                    {pathway.genes.map((gene, i) => (
                      <span key={i} className="gene-badge">{gene}</span>
                    ))}
                  </div>
                </div>
              ))}
            </Card>
          </Col>

          {/* العمود الثاني: Actions */}
          <Col lg={4}>
            <Card className="custom-card p-4 h-100">
              <div className="card-title mb-3">Actions</div>
              <div className="d-flex flex-column gap-3">
                <Button className="btn-action-primary w-100 shadow-sm">
                  <FaNetworkWired className="fs-5" /> View Interactive Graph
                </Button>
                <button className="btn-action-outline w-100">
                  <FaRegMessage className="text-secondary" /> Ask AI Assistant
                </button>
                <button className="btn-action-outline w-100">
                  <FaDownload className="text-secondary" /> Export Report
                </button>
                <button className="btn-action-outline w-100">
                  <FaShareNodes className="text-secondary" /> Share Analysis
                </button>
              </div>
            </Card>
          </Col>
        </Row>

        {/* كارت التفسير السريري */}
        <Card className="custom-card interpretation-card mb-4 p-4">
          <div className="card-title m-0 mb-2" style={{color: "#0369a1"}}>Clinical Interpretation</div>
          <p className="m-0" style={{color: "#334155", fontSize: "0.95rem", lineHeight: "1.6"}}>
            {data.interpretation}
          </p>
        </Card>

        {/* كارت العلاجات البديلة */}
        <Card className="custom-card alternatives-card mb-4 p-4">
          <div className="card-title m-0 mb-1" style={{color: "#be123c"}}>Alternative Treatment Options</div>
          <p className="mb-4" style={{color: "#e11d48", fontSize: "0.85rem"}}>Based on the resistance profile, consider these potential alternatives (not guaranteed treatments):</p>
          
          <Row className="g-3">
            {data.alternatives.map((alt, index) => (
              <Col md={6} key={index}>
                <div className="option-box alt-option-box">{alt}</div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* كارت المساعد الذكي */}
        <Card className="custom-card ai-card mb-4 p-4">
          <div className="card-title m-0 mb-1" style={{color: "#0f766e"}}>
            <FaRegMessage className="me-1" /> Ask AI Assistant
          </div>
          <p className="mb-4" style={{color: "#0f766e", fontSize: "0.85rem", opacity: 0.8}}>Click on a question to ask the AI assistant:</p>
          
          <div className="d-flex flex-column gap-2">
            {data.aiQuestions.map((question, index) => (
              <div key={index} className="option-box" style={{borderColor: "#5eead4", color: "#0f766e"}}>
                {question}
              </div>
            ))}
          </div>
        </Card>

      </Container>
    </div>
  );
}

export default Results;