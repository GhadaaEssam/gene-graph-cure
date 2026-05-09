// فانكشن وهمية لبداية التحليل
export const startPrediction = async (data) => {
  console.log("إرسال الطلب للباك اند بالبيانات:", data);

  // محاكاة تأخير الشبكة (1 ثانية)
  await new Promise(resolve => setTimeout(resolve, 1000));

  // إرجاع رد وهمي يحتوي على job_id وحالة مبدئية
  return {
    job_id: `job_${Math.random().toString(36).substring(7)}`,
    status: 'PENDING'
  };
};