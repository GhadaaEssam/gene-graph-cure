const BASE_URL = "http://127.0.0.1:8000/dashboard";

const getAuthHeaders = () => {
  const token = localStorage.getItem("userToken");

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const emptySummary = {
  doctorName: "Doctor",
  totalAnalyses: 0,
  resistant: 0,
  sensitive: 0,
  topPathway: "N/A",
  topPathwayCount: 0,
  resistanceDistribution: [
    { label: "Resistant", count: 0 },
    { label: "Sensitive", count: 0 },
  ],
  topAffectedPathways: [],
  analysesOverTime: [],
};

export const getDashboardSummary = async () => {
  try {
    const response = await fetch(`${BASE_URL}/summary`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Dashboard Summary Error:", error);
    return emptySummary;
  }
};

export const getRecentAnalyses = async () => {
  try {
    const response = await fetch(`${BASE_URL}/recent`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Recent Analyses Error:", error);
    return [];
  }
};
