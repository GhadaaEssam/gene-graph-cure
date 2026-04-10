import React, { useRef, useState } from "react";
import { Container, Card, Form, Button, Spinner } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCheckCircle } from "react-icons/fa";
import { FiUpload } from "react-icons/fi";
import { IoInformationCircleOutline } from "react-icons/io5";

function NewAnalysis() {
  const mainFileRef = useRef(null);
  const mutationFileRef = useRef(null);
  const cnvFileRef = useRef(null);
  const methFileRef = useRef(null);

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

    setTimeout(() => {
      setIsAnalyzing(false);
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
    // Changed py-5 to py-3 to reduce vertical padding on the whole page
    <div className="new-analysis-page py-3">
      <style>
        {`
          /* Changed min-height to account for a typical navbar height and prevent scrolling */
          .new-analysis-page { background-color: #f8fafc; min-height: calc(100vh - 70px); display: flex; flex-direction: column; justify-content: center; }
          .back-link { color: #14b8a6; text-decoration: none; font-weight: 500; font-size: 0.85rem; transition: color 0.2s; }
          .back-link:hover { color: #0d9488; }
          .custom-card { border: none; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
          
          .upload-area { cursor: pointer; transition: all 0.2s ease; background-color: #ffffff; }
          /* Reduced padding on the main upload area from 40px 20px to 20px 15px */
          .main-upload-area { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px 15px; text-align: center; }
          .main-upload-area:hover, .main-upload-area.active { border-color: #14b8a6; background-color: #f0fdfa; }
          
          /* Reduced padding on small upload areas */
          .small-upload-area { border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 10px; color: #475569; font-size: 0.85rem; }
          .small-upload-area:hover, .small-upload-area.active { border-color: #14b8a6; background-color: #f0fdfa; color: #0f766e; }
          
          .btn-run-analysis { background: linear-gradient(to right, #7dd3fc, #6ee7b7); border: none; color: #064e3b; font-weight: 700; padding: 10px; border-radius: 8px; width: 100%; transition: opacity 0.2s; }
          .btn-run-analysis:hover { opacity: 0.9; color: #064e3b; }
          .btn-run-analysis:disabled { opacity: 0.6; cursor: not-allowed; }
          
          /* Reduced padding on privacy notice */
          .privacy-notice { background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; gap: 12px; }
        `}
      </style>

      {/* Kept max-width at 800px as requested earlier, but you can change it if needed */}
      <Container style={{ maxWidth: "800px" }}>
        
        {/* Reduced margin bottom from mb-4 to mb-2 */}
        <div className="mb-2">
          <Link to="/dashboard" className="back-link d-flex align-items-center gap-2">
            <FaArrowLeft /> Back to Dashboard
          </Link>
        </div>

        {/* Reduced margin bottom from mb-4 to mb-3 */}
        <div className="mb-3">
          <h3 className="fw-bold text-dark mb-1">New Analysis</h3>
          <p className="text-secondary" style={{ fontSize: "0.9rem" }}>Upload patient genomic data to predict drug resistance</p>
        </div>

        {/* Reduced card padding from p-4 p-md-5 to p-3 p-md-4 and margin from mb-4 to mb-3 */}
        <Card className="custom-card mb-3 p-3 p-md-4">
          <Form>
            {/* Reduced form group margin from mb-4 to mb-3 */}
            <Form.Group className="mb-3">
              <Form.Label className="fw-bold text-dark" style={{ fontSize: "0.85rem" }}>Cancer Type</Form.Label>
              <Form.Select 
                className="bg-light border-0 shadow-sm" 
                style={{ padding: "8px 12px", fontSize: "0.9rem" }}
                value={cancerType}
                onChange={(e) => setCancerType(e.target.value)}
              >
                <option>Select a cancer type</option>
                <option value="Breast Cancer">Breast Cancer</option>
                <option value="Lung Cancer">Lung Cancer</option>
                <option value="Leukemia">Leukemia</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label className="fw-bold text-dark" style={{ fontSize: "0.85rem" }}>Genomic Data File <span className="text-danger">*</span></Form.Label>
              <div className={`upload-area main-upload-area ${files.main ? 'active' : ''}`} onClick={() => handleUploadClick(mainFileRef)}>
                {files.main ? (
                  <div>
                    <FaCheckCircle className="text-success mb-1" style={{ fontSize: "1.8rem" }} />
                    <h6 className="text-success fw-bold m-0">{files.main.name}</h6>
                    <span className="text-secondary" style={{fontSize: "0.75rem"}}>File ready for analysis</span>
                  </div>
                ) : (
                  <div>
                    <FiUpload className="text-secondary mb-2" style={{ fontSize: "1.8rem" }} />
                    <div><span className="text-success fw-bold" style={{fontSize: "0.9rem"}}>Click to upload</span> <span className="text-secondary" style={{fontSize: "0.9rem"}}>or drag and drop</span></div>
                    <div className="text-secondary mt-1" style={{ fontSize: "0.8rem" }}>VCF, CSV, or TXT (max 10MB)</div>
                  </div>
                )}
              </div>
              <input type="file" className="d-none" ref={mainFileRef} accept=".vcf,.csv,.txt" onChange={(e) => handleFileChange(e, 'main')} />
            </Form.Group>

            {/* Reduced margin bottom from mb-4 to mb-3 */}
            <div className="mb-3">
              <div className="d-flex justify-content-between align-items-end mb-2">
                <h6 className="fw-bold text-dark m-0" style={{ fontSize: "0.85rem" }}>Multi-Omics Data (Optional)</h6>
                <span className="text-secondary" style={{ fontSize: "0.75rem" }}>Improve prediction accuracy</span>
              </div>
              
              {/* Reduced gap between small upload areas from gap-3 to gap-2 */}
              <div className="d-flex flex-column gap-2">
                <div>
                  <div className={`upload-area small-upload-area ${files.mutation ? 'active' : ''}`} onClick={() => handleUploadClick(mutationFileRef)}>
                    {files.mutation ? <FaCheckCircle className="text-success" /> : <FiUpload />}
                    <span>{files.mutation ? files.mutation.name : "Upload mutation data"}</span>
                  </div>
                  <input type="file" className="d-none" ref={mutationFileRef} onChange={(e) => handleFileChange(e, 'mutation')} />
                </div>
                <div>
                  <div className={`upload-area small-upload-area ${files.cnv ? 'active' : ''}`} onClick={() => handleUploadClick(cnvFileRef)}>
                    {files.cnv ? <FaCheckCircle className="text-success" /> : <FiUpload />}
                    <span>{files.cnv ? files.cnv.name : "Upload CNV data"}</span>
                  </div>
                  <input type="file" className="d-none" ref={cnvFileRef} onChange={(e) => handleFileChange(e, 'cnv')} />
                </div>
                <div>
                  <div className={`upload-area small-upload-area ${files.meth ? 'active' : ''}`} onClick={() => handleUploadClick(methFileRef)}>
                    {files.meth ? <FaCheckCircle className="text-success" /> : <FiUpload />}
                    <span>{files.meth ? files.meth.name : "Upload methylation data"}</span>
                  </div>
                  <input type="file" className="d-none" ref={methFileRef} onChange={(e) => handleFileChange(e, 'meth')} />
                </div>
              </div>
            </div>

            <Button className="btn-run-analysis mt-1" onClick={handleRunAnalysis} disabled={isAnalyzing}>
              {isAnalyzing ? (
                <><Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" /> Analyzing Data...</>
              ) : (
                "Run Analysis"
              )}
            </Button>
          </Form>
        </Card>

        <div className="privacy-notice shadow-sm">
          <IoInformationCircleOutline className="text-primary fs-4 flex-shrink-0" />
          <p className="text-primary opacity-75 m-0" style={{fontSize: "0.8rem"}}>
            <strong>Data Privacy Notice:</strong> All patient data is anonymized and encrypted. No PII should be included.
          </p>
        </div>

      </Container>
    </div>
  );
}

export default NewAnalysis;