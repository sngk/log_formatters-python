import pandas as pd

with open('data.txt', 'r') as file:
    data = file.read()
df = pd.read_csv(pd.compat.StringIO(data), sep='\t')
print(df)
