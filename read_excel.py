import pandas as pd

df = pd.read_excel('GM RCK CONT LIST 2026.xlsx')
df_clean = df.dropna(how='all')

print(f"Total members: {len(df_clean)}")
print(f"\nColumns: {list(df_clean.columns)}")
print(f"\nFirst 5 rows:")
print(df_clean.head().to_string())
print(f"\nLast 5 rows:")
print(df_clean.tail().to_string())
