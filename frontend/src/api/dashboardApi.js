// ==========================
// 🔹 MOCK DASHBOARD API
// ==========================

const mockDelay = (ms) =>
  new Promise((resolve) => setTimeout(resolve, ms));

/**
 * 1️⃣ Dashboard Summary Stats
 */
export const getDashboardSummary = async () => {
  await mockDelay(1000);

  return {
    totalAnalyses: 127,
    resistant: 57,
    sensitive: 70,
    topPathway: "MAPK/ERK",
    topPathwayCount: 28,
  };
};

/**
 * 2️⃣ Recent Analyses Table
 */
export const getRecentAnalyses = async () => {
  await mockDelay(1000);

  return [
    {
      id: "P-001",
      drug: "Osimertinib",
      prediction: "Resistant",
      confidence: 89,
      date: "2024-12-18",
    },
    {
      id: "P-002",
      drug: "Gefitinib",
      prediction: "Sensitive",
      confidence: 92,
      date: "2024-12-17",
    },
    {
      id: "P-003",
      drug: "Erlotinib",
      prediction: "Resistant",
      confidence: 76,
      date: "2024-12-16",
    },
    {
      id: "P-004",
      drug: "Afatinib",
      prediction: "Sensitive",
      confidence: 88,
      date: "2024-12-15",
    },
    {
      id: "P-005",
      drug: "Crizotinib",
      prediction: "Resistant",
      confidence: 81,
      date: "2024-12-14",
    },
  ];
};