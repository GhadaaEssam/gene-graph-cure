// src/api/graphApi.js

const BASE_URL = "http://127.0.0.1:8000/graph";

export const getGraphData = async (job_id) => {
  try {
    // بنبعت الـ job_id كـ Path Parameter
    // لو مفيش id بنبعت 'default' عشان السيرفر ما يضربش
    const response = await fetch(`${BASE_URL}/${job_id || 'default'}`);

    if (!response.ok) {
      throw new Error("Failed to fetch graph data");
    }

    // هيرجع الـ JSON اللي فيه الـ nodes والـ links
    return await response.json();

  } catch (error) {
    console.error("Graph API Error:", error);
    // نرجع جراف فاضي في حالة الخطأ عشان الـ Component ما يظهرش Error
    return { nodes: [], links: [] };
  }
};