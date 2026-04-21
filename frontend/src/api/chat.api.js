// ==========================
// 🔹 MOCK CHAT (دلوقتي)
// ==========================

export const sendChatMessage = async (message, job_id = null) => {
  return new Promise((resolve) => {
    // محاكاة تأخير الرد
    setTimeout(() => {
      const lowerQ = message.toLowerCase();

      let reply =
        "That's a great question. Based on the uploaded genomic data, I am analyzing the specific pathways involved. Could you specify which treatment alternative you are most interested in exploring?";

      // 👇 رد ذكي لو السؤال عن المقاومة
      if (
        lowerQ.includes("resistant") ||
        lowerQ.includes("resistance")
      ) {
        reply = `Based on the genomic analysis, the patient shows resistance due to several key factors:

**1. MAPK/ERK Pathway Activation**: The analysis detected high activation (87%) of the MAPK/ERK signaling pathway, which is a common bypass mechanism in drug resistance. Mutations in KRAS and BRAF genes are driving this activation.

**2. PI3K/AKT Pathway Alterations**: Secondary resistance mechanisms involve the PI3K/AKT pathway (72% impact score), with mutations in PIK3CA contributing to survival signaling independent of the drug target.

**3. DNA Repair Mechanisms**: Enhanced DNA damage response pathways (65% impact) allow cancer cells to survive drug-induced stress.

These combined mechanisms create multiple escape routes for cancer cells, leading to the predicted resistance profile.`;
      }

      resolve({
        reply,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      });
    }, 1500);
  });
};