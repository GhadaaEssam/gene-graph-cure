// src/api/analysisApi.js

// ==========================
// 🔹 MOCK BACKEND (دلوقتي)
// ==========================

const mockDelay = (ms) =>
  new Promise((resolve) => setTimeout(resolve, ms));

// 1️⃣ Start analysis (New Analysis Page)
export const runAnalysis = async (formData) => {
  await mockDelay(1500);

  return {
    job_id: "job_" + Math.floor(Math.random() * 10000),
    status: "queued",
  };
};

// 2️⃣ Get analysis result (Results Page)
export const getAnalysisResult = async (job_id) => {
  await mockDelay(1500);

  return {
    job_id,
    cancerType: "Breast Cancer",
    riskScore: 84,
    pathways: [
      {
        name: "MAPK/ERK Signaling",
        impact: 87,
        genes: ["KRAS", "BRAF", "MEK1"],
      },
      {
        name: "PI3K/AKT Pathway",
        impact: 72,
        genes: ["PIK3CA", "AKT1", "PTEN"],
      },
    ],
    interpretation:
      "This is a simulated result. Backend is not connected yet.",
    alternatives: ["Trametinib", "Cobimetinib", "Everolimus"],
  };
};