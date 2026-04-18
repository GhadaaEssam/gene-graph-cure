import pandas as pd
import re
import time
import http.client
from urllib.error import URLError, HTTPError
from Bio import Entrez

# ضروري عشان سيرفرات NCBI تسمحلك بالبحث
Entrez.email = "jomana.student@example.com" 

def mine_pubmed_genes(gene_list):
    query = '("cytarabine"[Title/Abstract]) AND ("acute myeloid leukemia"[Title/Abstract] OR "AML"[Title/Abstract]) AND ("resistance"[Title/Abstract] OR "sensitivity"[Title/Abstract])'
    print(f"🔍 بنبحث في PubMed بالمعادلة دي:\n{query}")

    # 1. البحث في PubMed (هناخد أحدث 150 بحث)
    handle = Entrez.esearch(db="pubmed", term=query, retmax=150)
    record = Entrez.read(handle)
    handle.close()
    id_list = record["IdList"]

    print(f"✅ لقينا {len(id_list)} بحث، جاري تحميل الملخصات...")

    # 2. تحميل الملخصات (متقسمة لدفعات لتجنب سقوط السيرفر)
    genes_found = []
    batch_size = 50  # هنحمل 50 بحث بـ 50 بحث
    
    if id_list:
        for start in range(0, len(id_list), batch_size):
            end = min(len(id_list), start + batch_size)
            batch_ids = id_list[start:end]
            print(f"📥 جاري تحميل الدفعة من {start+1} لـ {end}...")

            # محاولات إعادة الاتصال لو النت قطع
            attempt = 0
            while attempt < 3:
                try:
                    handle = Entrez.efetch(db="pubmed", id=batch_ids, retmode="xml")
                    papers = Entrez.read(handle)
                    handle.close()

                    # 3. استخراج النصوص ومطابقتها
                    for paper in papers.get('PubmedArticle', []):
                        try:
                            abstract = paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
                            # بندور على أي كلمة من 3 لـ 7 حروف كلها كابيتال
                            potential_genes = set(re.findall(r'\b[A-Z][A-Z0-9]{2,6}\b', str(abstract)))
                            
                            # تقاطع مع لستة الجينات اللي عندنا في الداتا النظيفة
                            matched_genes = potential_genes.intersection(gene_list)
                            genes_found.extend(list(matched_genes))
                        except (KeyError, IndexError):
                            continue 
                    break # لو نجح، يكسر حلقة المحاولات ويدخل على الدفعة اللي بعدها
                    
                except (http.client.IncompleteRead, HTTPError, URLError) as e:
                    attempt += 1
                    print(f"⚠️ السيرفر قطع الاتصال، بنحاول تاني (محاولة {attempt}/3)...")
                    time.sleep(2) # نستنى ثانيتين قبل ما نحاول تاني
            
            if attempt == 3:
                print("❌ فشلنا في تحميل الدفعة دي بعد 3 محاولات، هنتخطاها.")

    # 4. تجميع الجينات
    if genes_found:
        final_genes = pd.Series(genes_found).value_counts().reset_index()
        final_genes.columns = ['Gene', 'Frequency']
        return final_genes
    else:
        return pd.DataFrame()

# ================= التنفيذ =================
try:
    print("⏳ جاري قراءة أسماء الجينات فقط من ملف الداتا...")
    
    # هنقرا أول صف بس (أسماء العواميد)
    df_columns = pd.read_csv('data_x_all.csv', nrows=0).columns
    
    # الفلترة الذكية
    my_genes = set([col for col in df_columns if not col.startswith('Unnamed') and col != 'Sample_ID'])
    
    print(f"✅ قرينا {len(my_genes)} جين سليم من الفايل.")

    print("🚀 جاري استخراج الجينات من PubMed...")
    result_df = mine_pubmed_genes(my_genes)

    if not result_df.empty:
        result_df.to_csv('2-pubmed_result.csv', index=False)
        print("\n🎉 تمت المهمة بنجاح! تم حفظ الملف باسم 2-pubmed_result.csv")
        print("\n🔥 أهم 5 جينات ظهرت في الأبحاث وليهم علاقة بالمقاومة:")
        print(result_df.head(5))
    else:
        print("⚠️ ملقيناش جينات متطابقة، جربي ترني السكريبت تاني.")
        
except FileNotFoundError:
    print("❌ إيرور: مش لاقي ملف 'data_x_all.csv'! اتأكدي إنه موجود في نفس الفولدر.")