import pandas as pd

# Read raw data from file
with open('data.txt', 'r') as file:
    data = file.read()

# Use StringIO to simulate a file-like object from the raw string data
data_io = pd.compat.StringIO(data)

# Load the data into a DataFrame
df = pd.read_csv(data_io, sep=r'\s{2,}', engine='python')

# Print the DataFrame to console
print(df)
