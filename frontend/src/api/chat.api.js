// src/api/chat.api.js

const BASE_URL = "http://127.0.0.1:8000/chat"; // تأكدي من تطابق المسار مع ملف الـ main.py

export const sendChatMessage = async (message, job_id = null) => {
  try {
    const response = await fetch(`${BASE_URL}/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        message: message, 
        job_id: job_id 
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to get response from AI");
    }

    // الباك إند هيرجع { "reply": "...", "timestamp": "..." }
    return await response.json();
    
  } catch (error) {
    console.error("API Chat Error:", error);
    // ممكن نرجع رد افتراضي في حالة فشل الاتصال بالسيرفر تماماً
    return {
      reply: "I'm having trouble connecting to my brain (server). Please try again later.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  }
}; 