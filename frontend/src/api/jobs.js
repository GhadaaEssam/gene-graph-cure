// فانكشن بتسأل عن حالة الـ Job باستخدام الـ id
export const checkJobStatus = async (jobId) => {
  console.log(`Checking status for job: ${jobId}`);

  // محاكاة تأخير الرد
  await new Promise(resolve => setTimeout(resolve, 800));

  // بنرجع بيانات وهمية (Mock Data) عشان شهد تعرضها في صفحة النتائج
  return {
    job_id: jobId,
    status: 'COMPLETED',
    resistance_score: 0.85,
    core_genes: ['TP53', 'BRCA1', 'EGFR'],
    pathway_scores: { 
      'Apoptosis': 0.92, 
      'DNA Repair': 0.75,
      'Cell Cycle': 0.60 
    }
  };
};