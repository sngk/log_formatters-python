import csv
import json

# Fields to extract
selected_fields = ["MPERuleID","CommonEventID","BaseRule","MapTag1", "MapTag2", "MapTag3", "MapTag4", "MapTag5", "MapTag6", "MapTag7", "MapTag8", "MapTag9", "MapTag10", "MapVMID", "MapSIP", "MapDIP", "MapSName", "MapDName", "MapSPort", "MapDPort", "MapProtocolID", "MapLogin", "MapAccount", "MapGroup", "MapDomain", "MapSession", "MapProcess", "MapObject", "MapURL", "MapSender", "MapRecipient", "MapSubject", "MapBytesIn", "MapBytesOut", "MapItemsIn", "MapItemsOut", "MapDuration", "MapAmount", "MapQuantity", "MapRate", "MapSize" "MapSMAC", "MapDMAC", "MapSNATIP", "MapDNATIP", "MapSInterface", "MapDInterface", "MapPID", "MapSeverity", "MapVersion", "MapCommand", "MapObjectName", "MapSNATPort", "MapDNATPort", "MapDomainOrigin", "MapHash", "MapPolicy", "MapVendorInfo", "MapResult", "MapObjectType", "MapCVE", "MapUserAgent", "MapParentProcessId", "MapParentProcessName", "MapParentProcessPath", "MapSerialNumber", "MapReason", "MapStatus", "MapThreatId", "MapThreatName", "MapSessionType", "MapAction", "MapResponseCode"]

# Prepare list to store JSON entries
output = []

# Read the TSV file
with open('data.txt', 'r', encoding='utf-8') as file:
    csv_data = csv.reader(file.read().splitlines(), delimiter='\t')
    header = next(csv_data)

    name_index = header.index("Name")
    field_indexes = {field: header.index(field) for field in selected_fields if field in header}

    for row in csv_data:
        entry = {"Name": row[name_index]}
        for field, index in field_indexes.items():
            value = row[index].strip()
            if value and value != "NULL":
                entry[field] = value
        output.append(entry)

# Output as JSON
print(json.dumps(output, indent=2))
