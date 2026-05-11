// src/api/analysisApi.js
const getAuthHeaders = () => {
  const token = localStorage.getItem("userToken");
  return {
    "Authorization": `Bearer ${token}`
  };
};
// 1️⃣ Start analysis
export const runAnalysis = async (formData) => {
  const response = await fetch("http://localhost:8000/analysis/run", {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  const data = await response.json();
  return data;
};

// 2️⃣ Get analysis result
export const getAnalysisResult = async (job_id) => {
  const response = await fetch(
    `http://localhost:8000/analyses/${job_id}`, {
    headers: getAuthHeaders(), 
  
});

  const data = await response.json();
  return data;
};