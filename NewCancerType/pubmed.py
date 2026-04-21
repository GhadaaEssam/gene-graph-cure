import pandas as pd
import requests
import urllib.parse
import re
import time

print("🚀 Step 2: Real PubMed Text-Mining & Gene Indexing...")

# ---------------------------------------------------------
# 1. إعدادات البحث (تقدري تغيريها لأي نوع كانسر ودواء بعدين)
# ---------------------------------------------------------
DISEASE = "Acute Myeloid Leukemia"
DRUG = "Cytarabine"
# البحث بيبحث عن المرض + الدواء + المقاومة
search_query = f'"{DISEASE}"[Title/Abstract] AND "{DRUG}"[Title/Abstract] AND "Resistance"[Title/Abstract]'

# ---------------------------------------------------------
# 2. قراءة الجينات من الملف الأساسي
# ---------------------------------------------------------
print("⏳ جاري قراءة فهرس الجينات من 1-data_result.csv...")
df_matrix = pd.read_csv('1-data_result.csv')
all_genes = df_matrix.columns[1:].tolist()
print(f"✅ تم تحميل {len(all_genes)} جين للبحث عنهم في الأبحاث.")

# ---------------------------------------------------------
# 3. الاتصال بـ PubMed وجلب الأبحاث
# ---------------------------------------------------------
print(f"\n🔍 جاري البحث في PubMed عن: {search_query}")
encoded_query = urllib.parse.quote(search_query)

# هنجيب أرقام (PMIDs) لأهم 300 بحث
search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded_query}&retmax=300&retmode=json"
r_search = requests.get(search_url).json()
pmids = r_search.get('esearchresult', {}).get('idlist', [])

print(f"✅ لقينا {len(pmids)} بحث مرتبطين بالموضوع. جاري تحميل الملخصات (Abstracts)...")

# تحميل نصوص الملخصات
fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=text&rettype=abstract"
r_fetch = requests.get(fetch_url)
abstracts_text = r_fetch.text
print("✅ تم تحميل نصوص الأبحاث بنجاح. جاري التنقيب عن الجينات (Text Mining)...")

# ---------------------------------------------------------
# 4. البحث عن الجينات داخل النصوص
# ---------------------------------------------------------
important_genes = set()
# البحث هيكون Case-Sensitive للجينات اللي حروفها أكتر من 2 عشان نتجنب الأخطاء
for gene in all_genes:
    gene_str = str(gene).strip()
    if len(gene_str) > 2:
        # بنعمل Regex عشان ندور على الكلمة كاسم جين مستقل مش جزء من كلمة تانية
        pattern = r'\b' + re.escape(gene_str) + r'\b'
        if re.search(pattern, abstracts_text):
            important_genes.add(gene_str)

print(f"🎯 الماينينج خلص! لقينا {len(important_genes)} جين ليهم علاقة بالمقاومة في الأبحاث.")

# ---------------------------------------------------------
# 5. بناء الملف التالت زي الدرايف بالظبط
# ---------------------------------------------------------
print("\n🏗️ جاري بناء الملف التالت (2-pubmed_result.csv)...")
pubmed_data = []

for gene in all_genes:
    result_num = 1 if str(gene).strip() in important_genes else 0
    pubmed_data.append({'gene': gene, 'result_num': result_num})

df_pubmed_new = pd.DataFrame(pubmed_data)
df_pubmed_new.to_csv('2-pubmed_result.csv', index=False)

print(f"✅ تم حفظ الملف بنجاح!")
print(f"   - إجمالي عدد الجينات: {len(df_pubmed_new)}")
print(f"   - عدد الجينات المهمة (اللي واخده 1): {df_pubmed_new['result_num'].sum()}")
print("\n🎉 الخطوة التانية الحقيقية تمت بنجاح! إحنا كده شغالين بشفافية علمية 100%.")