import csv

# Read raw data from file
with open('data.txt', 'r') as file:
    data = file.read()

csv_data = csv.reader(data.splitlines(), delimiter='\t')

header = next(csv_data)

name_index = header.index("Name")
itemdata_index = header.index("ItemData")

for row in csv_data:
    name = row[name_index]
    itemdata = row[itemdata_index]
    print(f"Name: {name} \t\t\t{itemdata}")
