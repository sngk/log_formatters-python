import csv
from io import StringIO

data = """
"""


csv_data = csv.reader(StringIO(data), delimiter='\t')

header = next(csv_data)

name_index = header.index("Name")
itemdata_index = header.index("ItemData")

for row in csv_data:
    name = row[name_index]
    itemdata = row[itemdata_index]
    print(f"Name: {name} \t\t\t{itemdata}")