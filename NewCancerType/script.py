import pandas as pd
import numpy as np
from scipy.special import erfinv
from scipy.stats import rankdata
import os

# 1. أسماء الملفات (تأكدي إن السكريبت في نفس فولدر الداتا)
CLINICAL_FILE = 'data_clinical_patient.txt'
EXPRESSION_FILE = 'data_mrna_seq_v2_rsem.txt'

print("⏳ reading files")

# قراءة الملف السريري (ملفات cBioPortal بيبقى فيها 4 سطور شرح في الأول فبنتخطاهم)
df_clin = pd.read_csv(CLINICAL_FILE, sep='\t', skiprows=4)

# قراءة ملف الجينات
df_expr = pd.read_csv(EXPRESSION_FILE, sep='\t')

print("✅ تمت القراءة. جاري تظبيط البيانات السريرية (Labels)...")

# 2. استخراج الـ Labels (R vs NR) بناءً على حالة المريض
# هنستخدم OS_STATUS (Overall Survival) كمؤشر للمقاومة
# 1:DECEASED -> مقاوم (R) | 0:LIVING -> حساس (NR)
if 'OS_STATUS' in df_clin.columns:
    df_clin = df_clin.dropna(subset=['OS_STATUS'])
    df_clin['Label'] = np.where(df_clin['OS_STATUS'].str.contains('1:DECEASED|Dead', case=False, na=False), 'R', 'NR')
else:
    print("⚠️ ملقيتش عمود OS_STATUS، راجعي أسماء الأعمدة في ملف clinical")

# هناخد كود المريض والـ Label بس عشان نعمل sample.csv
df_sample = df_clin[['PATIENT_ID', 'Label']].copy()
df_sample.rename(columns={'PATIENT_ID': 'Sample_ID'}, inplace=True)

print("✅ جاري تظبيط ملف التعبير الجيني (Matrix Transpose)...")

# 3. تظبيط ملف الجينات
df_expr = df_expr.dropna(subset=['Hugo_Symbol']) # نتأكد إن الجين ليه اسم
df_expr = df_expr.drop(columns=['Entrez_Gene_Id']) # هنشيل الـ ID ده مش محتاجينه
# هنخلي اسم الجين هو الـ Index عشان نقلب الماتريكس
df_expr = df_expr.groupby('Hugo_Symbol').mean() # لو فيه جينات متكررة ناخد المتوسط
df_expr = df_expr.T # Transpose: قلبنا الصفوف أعمدة
df_expr.index.name = 'Sample_ID'
df_expr.reset_index(inplace=True)

# تظبيط كود المريض في ملف الجينات عشان يطابق الملف السريري
# أكواد TCGA بتبقى طويلة TCGA-AB-2856-03، إحنا محتاجين أول 12 حرف بس
df_expr['Sample_ID'] = df_expr['Sample_ID'].str[:12]

# 4. دمج الملفين عشان نتأكد إننا واخدين المرضى اللي ليهم داتا وجينات بس
print("✅ جاري دمج الداتا وتطبيق الـ Rank-Gauss Normalization...")
df_final = pd.merge(df_sample, df_expr, on='Sample_ID', how='inner')

# فصل الـ Labels عن الجينات
df_final_sample = df_final[['Sample_ID', 'Label']]
df_final_genes = df_final.drop(columns=['Label'])

# 5. تطبيق الـ Rank-Gauss Transformation (زي ما البيبر بتاعتكم طلبت بالظبط)
def rank_gauss_transform(x):
    n = len(x)
    # نحسب الرانك
    ranks = rankdata(x)
    # نحولها لـ probabilities
    p = ranks / (n + 1)
    # نطبق الـ Inverse Error Function
    return np.sqrt(2) * erfinv(2 * p - 1)

# هنطبق المعادلة دي على كل جين (عمود) لوحده
genes_only = df_final_genes.drop(columns=['Sample_ID'])
transformed_genes = genes_only.apply(rank_gauss_transform, axis=0)

# نرجع عمود الـ Sample_ID
transformed_genes.insert(0, 'Sample_ID', df_final_genes['Sample_ID'])

# 6. حفظ الملفات النهائية
transformed_genes.to_csv('data_x_all.csv', index=False)
df_final_sample.to_csv('sample.csv', index=False)

print("🎉 ألف مبروك! الملفات جاهزة:")
print(f"1️⃣ عدد العينات النهائي: {len(df_final_sample)} عينة.")
print(f"2️⃣ عدد الجينات: {len(transformed_genes.columns) - 1} جين.")
print("تم حفظ 'data_x_all.csv' و 'sample.csv' بنجاح! 🚀")