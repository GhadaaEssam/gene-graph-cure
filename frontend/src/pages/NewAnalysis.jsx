import React, { useState } from "react";
import { Container, Card, Form, Button, Spinner } from "react-bootstrap";
// 1. دي الفيشة بتاعتك اللي عملناها قبل كده وبنستدعيها هنا
import { startPrediction } from "../api/predict";

function NewAnalysis() {
  // 2. هنا بنعمل "ذاكرة" للصفحة عشان تحفظ اختيارات اليوزر
  const [cancerType, setCancerType] = useState("Liver Cancer (Sorafenib)");
  const [mutationFile, setMutationFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // 3. دي الفانكشن اللي هتشتغل لما اليوزر يدوس على الزرار
  const handleRunAnalysis = async () => {
    setIsLoading(true); // بنشغل علامة التحميل

    try {
      // هنا بننادي على الفانكشن بتاعتك (الـ API الوهمي) وبنبعتلها الداتا!
      const response = await startPrediction({ 
        cancer_type: cancerType, 
        omics_data: mutationFile ? mutationFile.name : "No file" 
      });

      console.log("رد الـ API:", response);
      
      // بنطلع رسالة تأكيد مؤقتة لحد ما نعمل صفحة النتائج
      alert("✅ Analysis Started Successfully! Job ID: " + response.job_id);
      
    } catch (error) {
      console.error("Error:", error);
      alert("❌ حصلت مشكلة في الربط");
    } finally {
      setIsLoading(false); // بنوقف علامة التحميل
    }
  };

  return (
    <Container className="py-5">
      <h2 className="mb-4">New Cancer Drug Resistance Analysis</h2>

      <Card className="p-4">

        {/* Cancer Type */}
        <Form.Group className="mb-3">
          <Form.Label>Select Cancer Type</Form.Label>
          <Form.Select 
            value={cancerType} 
            onChange={(e) => setCancerType(e.target.value)}
          >
            <option>Liver Cancer (Sorafenib)</option>
            <option>Ovarian Cancer (Cisplatin)</option>
            <option>Melanoma (Immunotherapy)</option>
          </Form.Select>
        </Form.Group>

        {/* Multi-Omics Upload */}
        <h5 className="mt-4">Multi-Omics Data (Optional)</h5>

        <Form.Group className="mb-3">
          <Form.Label>Somatic Mutation Profiles</Form.Label>
          <Form.Control 
            type="file" 
            onChange={(e) => setMutationFile(e.target.files[0])}
          />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Copy Number Variation (CNV)</Form.Label>
          <Form.Control type="file" />
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>DNA Methylation Levels</Form.Label>
          <Form.Control type="file" />
        </Form.Group>

        {/* 4. ربطنا الزرار بالفانكشن بتاعتنا */}
        <Button 
          variant="success" 
          className="mt-3" 
          onClick={handleRunAnalysis}
          disabled={isLoading}
        >
          {isLoading ? <Spinner animation="border" size="sm" /> : "Run Analysis"}
        </Button>

      </Card>
    </Container>
  );
}

export default NewAnalysis;