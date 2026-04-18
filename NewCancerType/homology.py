import pandas as pd
import requests
import time

print("⏳ جاري قراءة الجينات من ملف PubMed...")
try:
    df_pubmed = pd.read_csv('2-pubmed_result.csv')
    genes = df_pubmed['Gene'].tolist()
    print(f"✅ قرينا {len(genes)} جين. جاري الاتصال بسيرفرات Ensembl API...")

    homologs_data = []
    server = "https://rest.ensembl.org"

    print("🔍 جاري البحث عن الجينات المتشابهة (Paralogs) لكل جين... (ممكن تاخد دقيقتين)")
    
    # هنمشي على الجينات واحد واحد
    for i, gene in enumerate(genes):
        # بنطبع التقدم عشان ماتحسيش إن السكريبت هنج
        if i % 10 == 0:
            print(f"--> خلصنا {i} من {len(genes)} جين...")
            
        ext = f"/homology/symbol/human/{gene}?target_species=human;type=paralogues"
        
        try:
            r = requests.get(server+ext, headers={ "Content-Type" : "application/json" })
            if r.status_code == 200:
                decoded = r.json()
                if 'data' in decoded and len(decoded['data']) > 0:
                    homologies = decoded['data'][0].get('homologies', [])
                    for h in homologies:
                        target_gene = h.get('target', {}).get('id', '') # كود الجين المتشابه
                        perc_id = h.get('target', {}).get('perc_id', 0) # نسبة التشابه
                        
                        # هناخد الجينات اللي نسبة التشابه بينهم أعلى من 20% بس عشان الدقة
                        if perc_id > 20:
                            homologs_data.append({
                                'Gene_A': gene, 
                                'Gene_B_Ensembl': target_gene, 
                                'Similarity_Percent': perc_id
                            })
            # لازم نوقف السكريبت جزء من الثانية عشان سيرفرات Ensembl متعملناش Block
            time.sleep(0.1) 
        except Exception as e:
            continue

    # حفظ الملف النهائي
    df_homolog = pd.DataFrame(homologs_data)
    if not df_homolog.empty:
        df_homolog.to_csv('homolog_AML.csv', index=False)
        print("\n🎉 تمت المهمة بنجاح!")
        print(f"✅ لقينا {len(df_homolog)} علاقة تشابه بين الجينات.")
        print("تم حفظ الملف باسم 'homolog_AML.csv'")
        print("\n🔥 عينة من الداتا:")
        print(df_homolog.head())
    else:
        print("⚠️ ملقيناش داتا قوية للجينات دي.")

except FileNotFoundError:
    print("❌ إيرور: مش لاقي ملف '2-pubmed_result.csv'! اتأكدي إنه في نفس الفولدر.")