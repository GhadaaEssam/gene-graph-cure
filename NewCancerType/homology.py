import pandas as pd
import requests
import time

print("🚀 Step 4: Building Gene Homology Network (Paralogs)...")

# 1. قراءة الفهرس من الملف الأول
print("⏳ جاري قراءة فهرس الجينات...")
df_matrix = pd.read_csv('1-data_result.csv')
all_genes = df_matrix.columns[1:].tolist()
# بنحول الأسماء لـ حروف كبيرة (Upper) عشان نتجنب أي غلطات في الحروف
gene_to_index = {str(gene).strip().upper(): idx for idx, gene in enumerate(all_genes)}

# 2. قراءة الجينات المهمة (اللي واخده 1)
df_pubmed = pd.read_csv('2-pubmed_result.csv')
important_genes = df_pubmed[df_pubmed['result_num'] == 1]['gene'].tolist()
print(f"✅ تم سحب {len(important_genes)} جين مهم للبحث عن عائلاتهم.")

homolog_data = []
server = "https://rest.ensembl.org"
id_to_symbol_cache = {} # عشان نسرع التحويل ومنسألش السيرفر مرتين

def get_symbol(ensembl_id):
    if ensembl_id in id_to_symbol_cache: return id_to_symbol_cache[ensembl_id]
    try:
        r = requests.get(f"{server}/lookup/id/{ensembl_id}?", headers={"Content-Type": "application/json"}, timeout=5)
        if r.status_code == 200:
            name = r.json().get('display_name', ensembl_id)
            id_to_symbol_cache[ensembl_id] = str(name).strip().upper()
            return id_to_symbol_cache[ensembl_id]
    except: pass
    return ensembl_id

print("🔍 جاري الاتصال بـ Ensembl (ممكن تاخد دقيقة عشان بنجيب عائلات الجينات)...")

for i, gene in enumerate(important_genes):
    gene_upper = str(gene).strip().upper()
    print(f"🔄 جاري معالجة جين [{i+1}/{len(important_genes)}]: {gene} ...", end="\r", flush=True)
    
    ext = f"/homology/symbol/human/{gene}?target_species=human;type=paralogues"
    try:
        r = requests.get(server+ext, headers={"Content-Type" : "application/json"}, timeout=10)
        if r.status_code == 200:
            decoded = r.json()
            if 'data' in decoded and len(decoded['data']) > 0:
                homologies = decoded['data'][0].get('homologies', [])
                for h in homologies:
                    perc_id = h.get('target', {}).get('perc_id', 0)
                    
                    # هناخد نسبة تشابه أعلى من 20%
                    if perc_id > 20: 
                        target_ensembl = h.get('target', {}).get('id', '')
                        target_symbol = get_symbol(target_ensembl)
                        
                        # بنتأكد إن الجين الأصلي والجين المشابه موجودين في الفهرس بتاعنا
                        if gene_upper in gene_to_index and target_symbol in gene_to_index:
                            idx_a = gene_to_index[gene_upper]
                            idx_b = gene_to_index[target_symbol]
                            
                            if idx_a != idx_b:
                                homolog_data.append({'row': idx_a, 'col': idx_b})
    except Exception:
        continue
    time.sleep(0.1) # حماية من الحظر

# حفظ الملف
df_homolog = pd.DataFrame(homolog_data)
if not df_homolog.empty:
    df_homolog = df_homolog.drop_duplicates()
    df_homolog.to_csv('homolog_AML.csv', index=False)
    print("\n\n✅ تم حفظ الملف الخامس بنجاح: homolog_AML.csv")
    print(f"   - إجمالي عدد الروابط (Homology Edges): {len(df_homolog)}")
    print("\n👀 عينة من الملف (أرقام زي الدرايف بالظبط):")
    print(df_homolog.head().to_string(index=False))
else:
    print("\n⚠️ ملقيناش تفاعلات قوية، ممكن نعدل نسبة التشابه.")

print("\n🎉 هانت جداً! لو الملف ده طلع مظبوط، هنعمل الملف السادس والأخير (اللي كله أصفار) في سطرين كود ونحتفل!")