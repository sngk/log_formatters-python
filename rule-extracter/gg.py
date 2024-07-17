import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Define the path to the current directory containing the JSON files
jsonDir = os.getcwd()

# List of JSON files and define the master file
jsonFiles = [os.path.join(jsonDir, f) for f in os.listdir(jsonDir) if f.endswith('.json')]
masterFile = os.path.join(jsonDir, 'goldenimage.json')

# Remove the master file from the list if it's included
if masterFile in jsonFiles:
    jsonFiles.remove(masterFile)

# Ensure the master file is the first in the list
jsonFiles.insert(0, masterFile)

# Extract customer names from filenames
customerNames = [os.path.splitext(os.path.basename(f))[0] for f in jsonFiles]

def loadJsonData(fileList):
    allData = []
    for file in fileList:
        with open(file, 'r') as f:
            data = json.load(f)
            allData.append(data.get("Rules", []))
    return allData

def extractCriteria(criteriaList):
    descriptions = []
    for criteria in criteriaList:
        name = criteria.get("name", "Unknown")
        values = criteria.get("values", [])
        for value in values:
            displayValue = value.get("displayValue", value.get("value", "Unknown"))
            descriptions.append({'name': name, 'value': displayValue})
    return descriptions

def extractGroupByFields(groupByFields):
    return [{'name': field.get("name", "Unknown"), 'value': field.get("name", "Unknown")} for field in groupByFields]

def extractData(rules):
    extractedData = {}
    for rule in rules:
        ruleName = rule.get("name")
        if not ruleName:
            continue
        
        description = rule.get("description", "N/A")
        details = rule.get("details", "N/A").replace('\r\n', '<br>').replace('\n', '<br>')
        
        blocks = rule.get("blocks", [])
        if not blocks:
            continue
        block = blocks[0]
        
        filterIn = block.get("filterIn", [])
        filterOut = block.get("filterOut", [])
        primaryCriteria = block.get("primaryCriteria", [])

        filterInDescriptions = extractCriteria(filterIn[0].get("fieldFilters", [])) if filterIn else []
        filterOutDescriptions = extractCriteria(filterOut[0].get("fieldFilters", [])) if filterOut else []
        primaryCriteriaDescriptions = extractCriteria(primaryCriteria[0].get("fieldFilters", [])) if primaryCriteria else []

        values = block.get("values", [])
        thresholdDescriptions = []
        for value in values:
            fieldName = value.get("field", {}).get("name", "Unknown")
            count = value.get("count", "Unknown")
            durationSeconds = block.get("durationSeconds", "Unknown")
            thresholdDescriptions.append(f'{fieldName} >= {count} over {durationSeconds} seconds')

        groupByFields = extractGroupByFields(block.get("groupByFields", []))

        extractedData[ruleName] = {
            "ruleName": ruleName,
            "description": description,
            "details": details,
            "filterIn": filterInDescriptions,
            "filterOut": filterOutDescriptions,
            "primaryCriteria": primaryCriteriaDescriptions,
            "threshold": [{'name': 'threshold', 'value': t} for t in thresholdDescriptions],
            "groupByFields": groupByFields
        }
    return extractedData

def formatDifferences(masterValue, differences, labels):
    formattedDiff = f'[Master]\r\n'
    for value in masterValue:
        formattedDiff += f'{value}\r\n'
    for label, diff in zip(labels, differences):
        formattedDiff += f'[{label}]\r\n'
        if isinstance(diff, list):
            for d in diff:
                formattedDiff += f'{d}\r\n'
        else:
            formattedDiff += f'{diff}\r\n'
    return formattedDiff

def hasDifferences(rule):
    if rule['ruleName']['highlight'] or rule['description']['highlight'] or rule['details']['highlight']:
        return True
    for item in rule['primaryCriteria'] + rule['filterIn'] + rule['filterOut'] + rule['threshold'] + rule['groupByFields']:
        if item['highlight']:
            return True
    return False

def compareData(masterData, dataList, labels):
    comparisonResult = {}

    for ruleName, masterRule in masterData.items():
        comparisonResult[ruleName] = {}
        for key, masterValue in masterRule.items():
            if key == "ruleName":  # Skip ruleName for comparison
                comparisonResult[ruleName][key] = {
                    "value": f'[Master] {masterValue}',
                    "highlight": False,
                    "exact_match": True
                }
                continue
            
            allSame = True
            differences = []
            for otherData in dataList:
                otherRule = otherData.get(ruleName)
                if otherRule:
                    otherValue = otherRule.get(key)
                    if isinstance(masterValue, list) and isinstance(otherValue, list):
                        masterValueSorted = sorted(masterValue, key=lambda x: x['value'] if isinstance(x, dict) else x)
                        otherValueSorted = sorted(otherValue, key=lambda x: x['value'] if isinstance(x, dict) else x)
                        if masterValueSorted != otherValueSorted:
                            allSame = False
                            differences.append(otherValue)
                        else:
                            differences.append(masterValue)
                    else:
                        if masterValue != otherValue:
                            allSame = False
                            differences.append(otherValue)
                        else:
                            differences.append(masterValue)
                else:
                    allSame = False
                    differences.append('None')
            
            if isinstance(masterValue, list):
                valueList = []
                for item in masterValue:
                    if isinstance(item, dict):
                        valueList.append({'name': item['name'], 'value': f'[Master] {item["value"]}', 'highlight': not allSame})
                for idx, otherRule in enumerate(dataList):
                    otherValue = otherRule.get(ruleName, {}).get(key, [])
                    for item in otherValue:
                        if isinstance(item, dict):
                            valueList.append({'name': item['name'], 'value': f'[{labels[idx + 1]}] {item["value"]}', 'highlight': not allSame})
                comparisonResult[ruleName][key] = valueList
            else:
                if allSame:
                    comparisonResult[ruleName][key] = {
                        "value": f'[Master] {masterValue}',
                        "highlight": False,
                        "exact_match": True
                    }
                else:
                    formattedDiff = formatDifferences([masterValue], differences, labels[1:])
                    comparisonResult[ruleName][key] = {
                        "value": formattedDiff.replace('\r\n', '<br>').replace('\n', '<br>'),
                        "highlight": True,
                        "exact_match": False
                    }

        comparisonResult[ruleName]['has_differences'] = hasDifferences(comparisonResult[ruleName])

    return comparisonResult, "Comparison complete. Differences highlighted."

@app.route('/')
def index():
    filterDifferences = request.args.get('filter', 'all')
    selectedCustomer = request.args.get('customer', 'all')

    # Perform default comparison with all customers
    allRules = loadJsonData(jsonFiles)
    masterData = extractData(allRules[0])
    otherData = [extractData(rules) for rules in allRules[1:]]
    labels = customerNames

    comparedData, message = compareData(masterData, otherData, labels)

    return render_template('index.html', rules=comparedData, message=message, customerNames=customerNames[1:], selectedCustomer=selectedCustomer, filterDifferences=filterDifferences)

@app.route('/compare')
def compare():
    filterDifferences = request.args.get('filter', 'all')
    selectedCustomer = request.args.get('customer', 'all')

    if selectedCustomer == 'all':
        selectedFiles = jsonFiles[1:]  # Exclude the master file
    else:
        selectedFiles = [os.path.join(jsonDir, f'{selectedCustomer}.json')]

    allRules = loadJsonData([masterFile] + selectedFiles)
    masterData = extractData(allRules[0])
    otherData = [extractData(rules) for rules in allRules[1:]]
    labels = ['Master'] + [selectedCustomer] if selectedCustomer != 'all' else customerNames[1:]
    comparedData, message = compareData(masterData, otherData, labels)

    return render_template('index.html', rules=comparedData, message=message, customerNames=customerNames[1:], selectedCustomer=selectedCustomer, filterDifferences=filterDifferences)

if __name__ == '__main__':
    app.run(debug=True)
