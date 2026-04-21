import pandas as pd
import requests

print("🚀 Step 3: Building Protein-Protein Interaction (PPI) Network...")

# 1. قراءة الفهرس من الملف الأول (عشان نترجم الأسماء لأرقام)
print("⏳ جاري قراءة فهرس الجينات...")
df_matrix = pd.read_csv('1-data_result.csv')
all_genes = df_matrix.columns[1:].tolist()
# عمل قاموس بيحول اسم الجين لرقمه (مثال: FLT3 -> 331)
gene_to_index = {gene: idx for idx, gene in enumerate(all_genes)}

# 2. قراءة الـ 253 جين المهمين من الملف التالت
df_pubmed = pd.read_csv('2-pubmed_result.csv')
important_genes = df_pubmed[df_pubmed['result_num'] == 1]['gene'].tolist()
print(f"✅ تم سحب {len(important_genes)} جين مهم للبحث عن تفاعلاتهم.")

# 3. الاتصال بقاعدة بيانات STRING
print("🔍 جاري الاتصال بـ STRING DB لجلب التفاعلات (ممكن تاخد 10 ثواني)...")
string_api_url = "https://string-db.org/api/json/network"

# إعدادات البحث (هنبعت الجينات، ونطلب التفاعلات الموثوقة بس score > 400)
params = {
    "identifiers": "\r".join(important_genes),
    "species": 9606, # كود الإنسان في قواعد البيانات
    "required_score": 400, 
    "caller_identity": "GeneGraphCure" 
}

try:
    response = requests.post(string_api_url, data=params)
    interactions = response.json()
    print(f"✅ السيرفر رد! لقينا {len(interactions)} تفاعل بروتيني محتمل.")
except Exception as e:
    print(f"❌ حصل مشكلة في الاتصال: {e}")
    interactions = []

# 4. بناء ملف الـ PPI بالأرقام (Indices) زي ملف الدرايف
print("🏗️ جاري ترجمة أسماء الجينات لأرقام (Indices)...")
ppi_data = []

for interaction in interactions:
    gene_a = interaction['preferredName_A']
    gene_b = interaction['preferredName_B']
    
    # بنتأكد إن الجينين موجودين عندنا في الفهرس
    if gene_a in gene_to_index and gene_b in gene_to_index:
        idx_a = gene_to_index[gene_a]
        idx_b = gene_to_index[gene_b]
        
        # بنمنع الجين إنه يتفاعل مع نفسه
        if idx_a != idx_b:
            ppi_data.append({'row': idx_a, 'col': idx_b})

df_ppi = pd.DataFrame(ppi_data)

# حفظ الملف
if not df_ppi.empty:
    df_ppi = df_ppi.drop_duplicates() # مسح الروابط المتكررة
    df_ppi.to_csv('ppi_link.csv', index=False)
    print(f"\n✅ تم حفظ الملف الرابع بنجاح: ppi_link.csv")
    print(f"   - إجمالي عدد الروابط (Edges) في الشبكة: {len(df_ppi)}")
    print("\n👀 عينة من الملف (زي الدرايف بالظبط):")
    print(df_ppi.head().to_string(index=False))
else:
    print("⚠️ ملقيناش تفاعلات، جربي ترني الكود تاني.")

print("\n🎉 الخطوة التالتة تمت بنجاح! فاضل خطوة الهومولوجي (الجينات المتشابهة) ونبقى قفلنا الداتا 100%.")