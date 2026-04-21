import pandas as pd
import numpy as np

print("🚀 Step 1: Building Master Matrix & Extracting Survival Labels...")

# 1. قراءة ملف التعبير الجيني
print("⏳ جاري قراءة ملف RNA-seq (data_mrna_seq_v2_rsem.txt)...")
df_rna = pd.read_csv('data_mrna_seq_v2_rsem.txt', sep='\t')
df_rna = df_rna.dropna(subset=['Hugo_Symbol'])
if 'Entrez_Gene_Id' in df_rna.columns:
    df_rna = df_rna.drop(columns=['Entrez_Gene_Id'])

df_rna = df_rna.groupby('Hugo_Symbol').mean().reset_index()

# تدوير المصفوفة
df_rna.set_index('Hugo_Symbol', inplace=True)
df_matrix = df_rna.T
df_matrix.index.name = 'Sample_ID'
df_matrix.reset_index(inplace=True)

# Normalization
numeric_cols = df_matrix.columns[1:]
df_matrix[numeric_cols] = np.log2(df_matrix[numeric_cols].astype(float) + 1)
df_matrix = df_matrix.fillna(0)

df_matrix.to_csv('1-data_result.csv', index=False)
print(f"✅ تم حفظ الملف الأول: 1-data_result.csv (عدد المرضى: {len(df_matrix)})")

# ==========================================
# 2. استنتاج الـ Labels من ملف الكلينيكال
# ==========================================
print("\n⏳ جاري قراءة ملف الكلينيكال واستنتاج الاستجابة...")
df_clin = pd.read_csv('data_clinical_patient.txt', sep='\t', comment='#')

# دمج المرضى اللي في الجينات مع بياناتهم الكلينيكال
# ملحوظة: أكواد الـ RNA-seq ساعات بتبقى أطول شوية (زي TCGA-AB-2856-03A)، فهنطابق أول 12 حرف بس
df_matrix['Short_ID'] = df_matrix['Sample_ID'].astype(str).str[:12]
df_clin['Short_ID'] = df_clin['PATIENT_ID'].astype(str)

merged_df = pd.merge(df_matrix[['Sample_ID', 'Short_ID']], df_clin[['Short_ID', 'OS_STATUS', 'OS_MONTHS']], on='Short_ID', how='left')

labels = []
counts = {'Resistant (1)': 0, 'Sensitive (0)': 0, 'Unknown (0 by default)': 0}

for index, row in merged_df.iterrows():
    status = str(row['OS_STATUS']).upper()
    months = row['OS_MONTHS']
    
    label = 0 # Default Sensitive
    
    try:
        months = float(months)
        # اللوجيك: لو توفى في أقل من 12 شهر = مقاوم (1)
        if 'DECEASED' in status and months < 12.0:
            label = 1
            counts['Resistant (1)'] += 1
        # لو عاش أكتر من 12 شهر = مستجيب (0)
        elif months >= 12.0:
            label = 0
            counts['Sensitive (0)'] += 1
        else:
            label = 0 # أي حالة تانية غير واضحة
            counts['Unknown (0 by default)'] += 1
    except:
        label = 0
        counts['Unknown (0 by default)'] += 1
        
    labels.append({'sample_name': row['Sample_ID'], 'Class': label})

df_sample = pd.DataFrame(labels)
df_sample.to_csv('sample.csv', index=False)

print("\n📊 إحصائيات الـ Labels اللي طلعناها:")
for k, v in counts.items():
    print(f"   - {k}: {v} مريض")
    
print("\n✅ تم حفظ الملف التاني: sample.csv")
print("🎉 الخطوة الأولى تمت بنجاح! إحنا كده بنينا الأساس 100% صح.")