import pandas as pd
from io import StringIO

# Raw input data
data = """
"""
# Use StringIO to simulate a file-like object from the raw string data
data_io = StringIO(data)

# Load the data into a DataFrame
df = pd.read_csv(data_io, sep=r'\s{2,}', engine='python')

# Display the DataFrame
print(df)
