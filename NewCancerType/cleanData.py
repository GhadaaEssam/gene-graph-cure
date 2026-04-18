import pandas as pd

print("جاري تنظيف الملف من الصفوف الوهمية...")
df = pd.read_csv('data_x_all.csv')

# هنمسح أي صف (مريض) مالوش كود أو اسمه فاضي
df_clean = df.dropna(subset=['Sample_ID'])

# حفظ الملف النظيف
df_clean.to_csv('data_x_all.csv', index=False)
print(f"✅ تم التنظيف بنجاح! عدد المرضى الحقيقيين دلوقتي: {len(df_clean)}")