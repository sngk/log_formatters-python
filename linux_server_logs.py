import pandas as pd

def parse_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path, sep='\t')  # Assuming tab-separated values based on the headers format
    
    # Prompt the user for the column name
    column_name = input("Please enter the column name: ").strip()
    
    # Check if the specified column exists in the DataFrame (case-insensitive)
    columns_lower = [col.lower() for col in df.columns]
    if column_name.lower() not in columns_lower:
        return f"Column '{column_name}' not found in the CSV file."
    
    # Get the actual column name
    actual_column_name = df.columns[columns_lower.index(column_name.lower())]
    
    # Display the specified column
    column_data = df[actual_column_name]
    
    # Generate a summary for each column
    summary = {}
    for col in df.columns:
        unique_values = df[col].value_counts().to_dict()
        summary[col] = unique_values
    
    return column_data, summary

# Example usage
file_path = r'E:\linux_server_logs.csv'  # Use raw string notation for Windows paths
column_data, summary = parse_csv(file_path)

print(f"Data in the specified column:")
print(column_data)

print("\nSummary of each column:")
for col, values in summary.items():
    print(f"\nColumn: {col}")
    for value, count in values.items():
        print(f"{value}: {count}")
