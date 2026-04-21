import pandas as pd
import numpy as np

print("🚀 Step 5: Generating Dummy Node Features...")

# 1. قراءة الفهرس عشان نعرف عدد الجينات بالظبط
df_matrix = pd.read_csv('1-data_result.csv')
num_genes = len(df_matrix.columns) - 1 # بنطرح عمود الـ Sample_ID
print(f"✅ عدد الجينات اللي هنعملها أصفار: {num_genes}")

# 2. إنشاء مصفوفة كلها أصفار (20 عمود)
columns = [f'V{i}' for i in range(1, 21)]
zeros_data = np.zeros((num_genes, 20), dtype=int)

df_dummy = pd.DataFrame(zeros_data, columns=columns)

# 3. حفظ الملف (هنخليه يبدأ الترقيم زي الإكسيل من 1)
df_dummy.index = df_dummy.index + 1
df_dummy.to_csv('3-data_x_all.csv', index=True)

print("✅ تم حفظ الملف السادس والأخير بنجاح: 3-data_x_all.csv")
print("🎉 تمت المهمة بنجاح ساحق! الفولدر اتقفل بالضبة والمفتاح.")