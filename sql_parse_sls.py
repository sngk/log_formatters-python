import pandas as pd
from io import StringIO
import textwrap

with open('data.txt', 'r', encoding='utf-8') as file:
    data = file.read()
data_io = StringIO(data)
df = pd.read_csv(data_io, sep='\t', engine='python')

# --- SETTINGS ---
WRAP_WIDTH = 100  

for idx, row in df.iterrows():
    print("="*80)
    print(f"RECORD {idx+1}")
    print("="*80)
    for col in df.columns:
        val = row[col]
        val_str = "" if pd.isna(val) else str(val)
        if len(val_str) > WRAP_WIDTH:
            val_str = '\n'.join(textwrap.wrap(val_str, WRAP_WIDTH))
        print(f"{col}:\n{val_str}")
    print("\n") 

# print only N records
# for idx, row in df.head(N).iterrows():
#     ... (same as above)
