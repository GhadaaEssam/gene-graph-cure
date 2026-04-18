import pandas as pd
import requests
import io

print("⏳ جاري قراءة الجينات من ملف PubMed...")
try:
    # قراءة الجينات اللي طلعناها من الخطوة اللي فاتت
    df_pubmed = pd.read_csv('2-pubmed_result.csv')
    genes = df_pubmed['Gene'].tolist()
    print(f"✅ قرينا {len(genes)} جين. جاري الاتصال بقاعدة بيانات STRING...")

    # إعدادات STRING API
    string_api_url = "https://string-db.org/api/tsv/network"
    params = {
        "identifiers": "\r".join(genes), # الجينات بتاعتنا
        "species": 9606,                 # كود الإنسان (Homo sapiens)
        "required_score": 600,           # زي ما البيبر طلبت بالظبط
        "network_type": "functional"
    }

    # الاتصال بالـ API
    response = requests.post(string_api_url, data=params)

    if response.status_code == 200:
        # قراءة النتيجة وتحويلها لجدول
        df_ppi = pd.read_csv(io.StringIO(response.text), sep='\t')
        
        if not df_ppi.empty:
            # هناخد بس اسم الجين الأول، الجين التاني، وقوة التفاعل
            df_ppi_clean = df_ppi[['preferredName_A', 'preferredName_B', 'score']]
            df_ppi_clean.columns = ['Gene_A', 'Gene_B', 'Score']
            
            # حفظ الملف
            df_ppi_clean.to_csv('ppi_link.csv', index=False)
            print(f"\n🎉 تمت المهمة بنجاح! لقينا {len(df_ppi_clean)} تفاعل بين الجينات.")
            print("تم حفظ الملف باسم 'ppi_link.csv'")
            print("\n🔥 عينة من التفاعلات:")
            print(df_ppi_clean.head())
        else:
            print("⚠️ ملقيناش تفاعلات قوية (أكبر من 600) بين الجينات دي.")
    else:
        print(f"❌ حصلت مشكلة في الاتصال بموقع STRING. كود الخطأ: {response.status_code}")

except FileNotFoundError:
    print("❌ إيرور: مش لاقي ملف '2-pubmed_result.csv'! اتأكدي إنه في نفس الفولدر.")