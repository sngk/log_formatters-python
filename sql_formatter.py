import pandas as pd
from io import StringIO

# Placeholder for the raw data as a string
data = """
"""

# Use StringIO to read the string data into a pandas DataFrame
df = pd.read_csv(StringIO(data), sep='\t')

# Export the DataFrame to a CSV file
df.to_csv('formatted_output.csv', index=False)

print("Data has been exported to formatted_output.csv")
