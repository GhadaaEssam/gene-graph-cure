// src/api/dashboardApi.js

const BASE_URL = "http://127.0.0.1:8000/dashboard";

/**
 * دالة مساعدة لجلب التوكن من التخزين المحلي
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem("userToken"); // تأكدي إن الاسم هنا هو نفس اللي بتسيفيه وقت اللوج إن
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`, // ده السطر اللي ناقص!
  };
};

/**
 * 1️⃣ Dashboard Summary Stats
 */
export const getDashboardSummary = async () => {
  try {
    const response = await fetch(`${BASE_URL}/summary`, {
      method: "GET",
      headers: getAuthHeaders(), // بنبعت الهيدرز اللي فيها التوكن
    });
    
    if (!response.ok) {
        // لو التوكن منتهي أو مش موجود، هيرجع 401
        throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Dashboard Summary Error:", error);
    return {
      doctorName: "Doctor",
      totalAnalyses: 0,
      resistant: 0,
      sensitive: 0,
      topPathway: "N/A",
      topPathwayCount: 0,
    };
  }
};

/**
 * 2️⃣ Recent Analyses Table
 */
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