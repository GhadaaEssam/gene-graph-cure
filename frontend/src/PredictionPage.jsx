import React, { useState } from 'react';
import { startPrediction } from './api/predict';
import { checkJobStatus } from './api/jobs';

export default function PredictionPage() {
  const [file, setFile] = useState(null);
  const [cancerType, setCancerType] = useState('Breast Cancer');
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [result, setResult] = useState(null);

  const handleRunAnalysis = async () => {
    if (!file) {
      alert('Please upload omics data first!');
      return;
    }

    setLoading(true);
    setResult(null);
    setStatusText('Starting Job...');

    try {
      // 1. إرسال الطلب للباك اند الوهمي
      const requestData = { cancer_type: cancerType, omics_data: file };
      const response = await startPrediction(requestData);
      
      let currentStatus = response.status;
      let jobData = null;

      // 2. عمل Polling عشان نسأل على النتيجة كل ثانيتين
      while (currentStatus !== 'COMPLETED' && currentStatus !== 'FAILED') {
        setStatusText(`Job Status: ${currentStatus}... Polling again...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        jobData = await checkJobStatus(response.job_id);
        currentStatus = jobData.status;
      }

      // 3. عرض النتائج لما تخلص
      if (currentStatus === 'COMPLETED' && jobData) {
        setResult(jobData);
        setStatusText('Analysis Complete!');
      }

    } catch (error) {
      console.error("Error during prediction:", error);
      setStatusText('An error occurred!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Gene Graph Cure - Prediction</h1>
      
      {/* 1. Upload Section */}
      <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px' }}>
        <h3>1. Upload Omics Data</h3>
        <select value={cancerType} onChange={(e) => setCancerType(e.target.value)} style={{ marginRight: '10px' }}>
          <option value="Breast Cancer">Breast Cancer</option>
          <option value="Lung Cancer">Lung Cancer</option>
        </select>
        <input type="file" onChange={(e) => setFile(e.target.files[0] || null)} />
        <br /><br />
        <button onClick={handleRunAnalysis} disabled={loading} style={{ padding: '10px 20px', cursor: 'pointer' }}>
          {loading ? 'Running...' : 'Run Analysis'}
        </button>
      </div>

      {/* 2. Loading State */}
      {loading && (
        <div style={{ color: 'blue', marginBottom: '20px' }}>
          ⏳ {statusText}
        </div>
      )}

      {/* 3. Results Section */}
      {result && (
        <div style={{ border: '1px solid green', padding: '20px' }}>
          <h3 style={{ color: 'green' }}>✅ Results (Job ID: {result.job_id})</h3>
          <p><strong>Resistance Score:</strong> {result.resistance_score}</p>
          
          <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
            <div style={{ flex: 1, height: '150px', background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              [cite_start][ Graph Component Placeholder ] [cite: 132]
            </div>
            <div style={{ flex: 1, height: '150px', background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              [cite_start][ Charts Placeholder ] [cite: 133]
            </div>
          </div>
        </div>
      )}
    </div>
  );
}