const BASE_URL = "http://127.0.0.1:8000/chat";

export const sendChatMessage = async (message, job_id = null) => {
  try {

    const token = localStorage.getItem("userToken");

    const response = await fetch(`${BASE_URL}/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
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

    return await response.json();

  } catch (error) {
    console.error("API Chat Error:", error);

    return {
      reply: "I'm having trouble connecting to my brain (server). Please try again later.",
      timestamp: new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      })
    };
  }
};