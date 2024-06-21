import pandas as pd

# Read raw data from file
with open('data.txt', 'r') as file:
    data = file.read()

# Use StringIO to read the string data into a pandas DataFrame
df = pd.read_csv(pd.compat.StringIO(data), sep='\t')

# Print the DataFrame to console
print(df)
