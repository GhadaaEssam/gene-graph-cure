import React, { useRef, useState } from "react";
import { Container, Card, Form, Button, Spinner } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom"; // إضافة useNavigate هنا
import { FaArrowLeft, FaCheckCircle } from "react-icons/fa";
import { FiUpload } from "react-icons/fi";
import { IoInformationCircleOutline } from "react-icons/io5";

function NewAnalysis() {
  const mainFileRef = useRef(null);
  const mutationFileRef = useRef(null);
  const cnvFileRef = useRef(null);
  const methFileRef = useRef(null);

  // تعريف دالة التنقل
  const navigate = useNavigate();

  const [cancerType, setCancerType] = useState("");
  const [files, setFiles] = useState({
    main: null,
    mutation: null,
    cnv: null,
    meth: null,
  });
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleUploadClick = (ref) => {
    if (ref.current) ref.current.click();
  };

  const handleFileChange = (e, fileType) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFiles((prev) => ({ ...prev, [fileType]: selectedFile }));
    }
  };

  const handleRunAnalysis = () => {
    if (!cancerType || cancerType === "Select a cancer type") {
      alert("Please select a cancer type first.");
      return;
    }
    if (!files.main) {
      alert("Please upload the main Genomic Data File.");
      return;
    }

    setIsAnalyzing(true);

    // محاكاة وقت التحليل (ثانيتين)
    setTimeout(() => {
      setIsAnalyzing(false);
      
      // النقل لصفحة النتائج مع تمرير الداتا الوهمية في الـ state
      navigate("/results", {
        state: {
          cancerType: cancerType,
          riskScore: 84,
          status: "High Resistance Risk",
          detectedMutations: ["TP53 (Exon 6)", "EGFR (L858R)"],
          recommendedAction: "Consider alternative combination therapies.",
        }
      });
    }, 2000);
  };

  return (
    <div className="new-analysis-page py-5">
      <style>
        {`
          .new-analysis-page { background-color: #f8fafc; min-height: 100vh; }
          .back-link { color: #14b8a6; text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: color 0.2s; }
          .back-link:hover { color: #0d9488; }
          .custom-card { border: none; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
          
          .upload-area { cursor: pointer; transition: all 0.2s ease; background-color: #ffffff; }
          .main-upload-area { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 40px 20px; text-align: center; }
          .main-upload-area:hover, .main-upload-area.active { border-color: #14b8a6; background-color: #f0fdfa; }
          
          .small-upload-area { border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; display: flex; align-items: center; gap: 12px; color: #475569; font-size: 0.95rem; }
          .small-upload-area:hover, .small-upload-area.active { border-color: #14b8a6; background-color: #f0fdfa; color: #0f766e; }
          
          .btn-run-analysis { background: linear-gradient(to right, #7dd3fc, #6ee7b7); border: none; color: #064e3b; font-weight: 700; padding: 12px; border-radius: 8px; width: 100%; transition: opacity 0.2s; }
          .btn-run-analysis:hover { opacity: 0.9; color: #064e3b; }
          .btn-run-analysis:disabled { opacity: 0.6; cursor: not-allowed; }
          
          .privacy-notice { background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 20px; display: flex; gap: 15px; }
        `}
      </style>

      <Container style={{ maxWidth: "800px" }}>
        
        <div className="mb-4">
          <Link to="/dashboard" className="back-link d-flex align-items-center gap-2">
            <FaArrowLeft /> Back to Dashboard
          </Link>
        </div>

        <div className="mb-4">
          <h2 className="fw-bold text-dark mb-1">New Analysis</h2>
          <p className="text-secondary">Upload patient genomic data to predict drug resistance</p>
        </div>

        <Card className="custom-card mb-4 p-4 p-md-5">
          <Form>
            <Form.Group className="mb-4">
              <Form.Label className="fw-bold text-dark" style={{ fontSize: "0.9rem" }}>Cancer Type</Form.Label>
              <Form.Select 
                className="bg-light border-0 shadow-sm" 
                style={{ padding: "12px" }}
                value={cancerType}
                onChange={(e) => setCancerType(e.target.value)}
              >
                <option>Select a cancer type</option>
                <option value="Breast Cancer">Breast Cancer</option>
                <option value="Lung Cancer">Lung Cancer</option>
                <option value="Leukemia">Leukemia</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label className="fw-bold text-dark" style={{ fontSize: "0.9rem" }}>Genomic Data File <span className="text-danger">*</span></Form.Label>
              <div className={`upload-area main-upload-area ${files.main ? 'active' : ''}`} onClick={() => handleUploadClick(mainFileRef)}>
                {files.main ? (
                  <div>
                    <FaCheckCircle className="text-success mb-2" style={{ fontSize: "2.5rem" }} />
                    <h6 className="text-success fw-bold">{files.main.name}</h6>
                    <span className="text-secondary" style={{fontSize: "0.8rem"}}>File ready for analysis</span>
                  </div>
                ) : (
                  <div>
                    <FiUpload className="text-secondary mb-3" style={{ fontSize: "2.5rem" }} />
                    <div><span className="text-success fw-bold">Click to upload</span> <span className="text-secondary">or drag and drop</span></div>
                    <div className="text-secondary mt-1" style={{ fontSize: "0.85rem" }}>VCF, CSV, or TXT (max 10MB)</div>
                  </div>
                )}
              </div>
              <input type="file" className="d-none" ref={mainFileRef} accept=".vcf,.csv,.txt" onChange={(e) => handleFileChange(e, 'main')} />
            </Form.Group>

            <div className="mb-4">
              <h6 className="fw-bold text-dark mb-1" style={{ fontSize: "0.9rem" }}>Multi-Omics Data (Optional)</h6>
              <p className="text-secondary mb-3" style={{ fontSize: "0.85rem" }}>Upload additional omics data to improve prediction accuracy</p>
              <div className="d-flex flex-column gap-3">
                <div>
                  <div className={`upload-area small-upload-area ${files.mutation ? 'active' : ''}`} onClick={() => handleUploadClick(mutationFileRef)}>
                    {files.mutation ? <FaCheckCircle className="text-success" /> : <FiUpload />}
                    <span>{files.mutation ? files.mutation.name : "Click to upload mutation data"}</span>
                  </div>
                  <input type="file" className="d-none" ref={mutationFileRef} onChange={(e) => handleFileChange(e, 'mutation')} />
                </div>
                <div>
                  <div className={`upload-area small-upload-area ${files.cnv ? 'active' : ''}`} onClick={() => handleUploadClick(cnvFileRef)}>
                    {files.cnv ? <FaCheckCircle className="text-success" /> : <FiUpload />}
                    <span>{files.cnv ? files.cnv.name : "Click to upload CNV data"}</span>
                  </div>
                  <input type="file" className="d-none" ref={cnvFileRef} onChange={(e) => handleFileChange(e, 'cnv')} />
                </div>
                <div>
                  <div className={`upload-area small-upload-area ${files.meth ? 'active' : ''}`} onClick={() => handleUploadClick(methFileRef)}>
                    {files.meth ? <FaCheckCircle className="text-success" /> : <FiUpload />}
                    <span>{files.meth ? files.meth.name : "Click to upload methylation data"}</span>
                  </div>
                  <input type="file" className="d-none" ref={methFileRef} onChange={(e) => handleFileChange(e, 'meth')} />
                </div>
              </div>
            </div>

            <Button className="btn-run-analysis mt-2" onClick={handleRunAnalysis} disabled={isAnalyzing}>
              {isAnalyzing ? (
                <><Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" /> Analyzing Data...</>
              ) : (
                "Run Analysis"
              )}
            </Button>
          </Form>
        </Card>

        <div className="privacy-notice shadow-sm">
          <IoInformationCircleOutline className="text-primary fs-3 flex-shrink-0" />
          <div>
            <div className="text-primary fw-bold mb-1">Data Privacy Notice</div>
            <p className="text-primary opacity-75 m-0" style={{fontSize: "0.85rem"}}>
              All patient data is anonymized and encrypted. No personally identifiable information (PII) should be included.
            </p>
          </div>
        </div>

      </Container>
    </div>
  );
}

export default NewAnalysis;