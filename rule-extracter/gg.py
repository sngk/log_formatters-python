import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Define the path to the current directory containing the JSON files
json_dir = os.getcwd()

# List of JSON files and define the master file
json_files = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
master_file = os.path.join(json_dir, 'goldenimage.json')

# Remove the master file from the list if it's included
if master_file in json_files:
    json_files.remove(master_file)

# Ensure the master file is the first in the list
json_files.insert(0, master_file)

# Extract customer names from filenames
customer_names = [os.path.splitext(os.path.basename(f))[0] for f in json_files]

def load_json_data(file_list):
    all_data = []
    for file in file_list:
        with open(file, 'r') as f:
            data = json.load(f)
            all_data.append(data.get("Rules", []))
    return all_data

def extract_criteria(criteria_list):
    descriptions = []
    for criteria in criteria_list:
        name = criteria.get("name", "Unknown")
        values = criteria.get("values", [])
        for value in values:
            display_value = value.get("displayValue", value.get("value", "Unknown"))
            descriptions.append({'name': name, 'value': display_value})
    return descriptions

def extract_group_by_fields(group_by_fields):
    return [{'name': field.get("name", "Unknown"), 'value': field.get("name", "Unknown")} for field in group_by_fields]

def extract_data(rules):
    extracted_data = {}
    for rule in rules:
        rule_name = rule.get("name")
        if not rule_name:
            continue
        
        description = rule.get("description", "N/A")
        details = rule.get("details", "N/A").replace('\r\n', '<br>').replace('\n', '<br>')
        
        blocks = rule.get("blocks", [])
        if not blocks:
            continue
        block = blocks[0]
        
        filter_in = block.get("filterIn", [])
        filter_out = block.get("filterOut", [])
        primary_criteria = block.get("primaryCriteria", [])

        filter_in_descriptions = extract_criteria(filter_in[0].get("fieldFilters", [])) if filter_in else []
        filter_out_descriptions = extract_criteria(filter_out[0].get("fieldFilters", [])) if filter_out else []
        primary_criteria_descriptions = extract_criteria(primary_criteria[0].get("fieldFilters", [])) if primary_criteria else []

        values = block.get("values", [])
        threshold_descriptions = []
        for value in values:
            field_name = value.get("field", {}).get("name", "Unknown")
            count = value.get("count", "Unknown")
            duration_seconds = block.get("durationSeconds", "Unknown")
            threshold_descriptions.append(f'{field_name} >= {count} over {duration_seconds} seconds')

        group_by_fields = extract_group_by_fields(block.get("groupByFields", []))

        extracted_data[rule_name] = {
            "ruleName": rule_name,
            "description": description,
            "details": details,
            "filterIn": filter_in_descriptions,
            "filterOut": filter_out_descriptions,
            "primaryCriteria": primary_criteria_descriptions,
            "threshold": [{'name': 'threshold', 'value': t} for t in threshold_descriptions],
            "groupByFields": group_by_fields
        }
    return extracted_data

def format_differences(master_value, differences, labels):
    formatted_diff = f'[Master]\r\n'
    for value in master_value:
        formatted_diff += f'{value}\r\n'
    for label, diff in zip(labels, differences):
        formatted_diff += f'[{label}]\r\n'
        if isinstance(diff, list):
            for d in diff:
                formatted_diff += f'{d}\r\n'
        else:
            formatted_diff += f'{diff}\r\n'
    return formatted_diff

def has_differences(rule):
    if rule['ruleName']['highlight'] or rule['description']['highlight'] or rule['details']['highlight']:
        return True
    for item in rule['primaryCriteria'] + rule['filterIn'] + rule['filterOut'] + rule['threshold'] + rule['groupByFields']:
        if item['highlight']:
            return True
    return False

def compare_data(master_data, data_list, labels):
    comparison_result = {}

    for rule_name, master_rule in master_data.items():
        comparison_result[rule_name] = {}
        for key, master_value in master_rule.items():
            if key == "ruleName":  # Skip ruleName for comparison
                comparison_result[rule_name][key] = {
                    "value": f'[Master] {master_value}',
                    "highlight": False,
                    "exact_match": True
                }
                continue
            
            all_same = True
            differences = []
            for other_data in data_list:
                other_rule = other_data.get(rule_name)
                if other_rule:
                    other_value = other_rule.get(key)
                    if isinstance(master_value, list) and isinstance(other_value, list):
                        master_value_sorted = sorted(master_value, key=lambda x: x['value'] if isinstance(x, dict) else x)
                        other_value_sorted = sorted(other_value, key=lambda x: x['value'] if isinstance(x, dict) else x)
                        if master_value_sorted != other_value_sorted:
                            all_same = False
                            differences.append(other_value)
                        else:
                            differences.append(master_value)
                    else:
                        if master_value != other_value:
                            all_same = False
                            differences.append(other_value)
                        else:
                            differences.append(master_value)
                else:
                    all_same = False
                    differences.append('None')
            
            if isinstance(master_value, list):
                value_list = []
                for item in master_value:
                    if isinstance(item, dict):
                        value_list.append({'name': item['name'], 'value': f'[Master] {item["value"]}', 'highlight': not all_same})
                for idx, other_rule in enumerate(data_list):
                    other_value = other_rule.get(rule_name, {}).get(key, [])
                    for item in other_value:
                        if isinstance(item, dict):
                            value_list.append({'name': item['name'], 'value': f'[{labels[idx + 1]}] {item["value"]}', 'highlight': not all_same})
                comparison_result[rule_name][key] = value_list
            else:
                if all_same:
                    comparison_result[rule_name][key] = {
                        "value": f'[Master] {master_value}',
                        "highlight": False,
                        "exact_match": True
                    }
                else:
                    formatted_diff = format_differences([master_value], differences, labels[1:])
                    comparison_result[rule_name][key] = {
                        "value": formatted_diff.replace('\r\n', '<br>').replace('\n', '<br>'),
                        "highlight": True,
                        "exact_match": False
                    }

        comparison_result[rule_name]['has_differences'] = has_differences(comparison_result[rule_name])

    return comparison_result, "Comparison complete. Differences highlighted."

@app.route('/')
def index():
    filter_differences = request.args.get('filter', 'all')
    selected_customer = request.args.get('customer', 'all')

    # Perform default comparison with all customers
    all_rules = load_json_data(json_files)
    master_data = extract_data(all_rules[0])
    other_data = [extract_data(rules) for rules in all_rules[1:]]
    labels = customer_names

    compared_data, message = compare_data(master_data, other_data, labels)

    return render_template('index.html', rules=compared_data, message=message, customer_names=customer_names[1:], selected_customer=selected_customer, filter_differences=filter_differences)

@app.route('/compare')
def compare():
    filter_differences = request.args.get('filter', 'all')
    selected_customer = request.args.get('customer', 'all')

    if selected_customer == 'all':
        selected_files = json_files[1:]  # Exclude the master file
    else:
        selected_files = [os.path.join(json_dir, f'{selected_customer}.json')]

    all_rules = load_json_data([master_file] + selected_files)
    master_data = extract_data(all_rules[0])
    other_data = [extract_data(rules) for rules in all_rules[1:]]
    labels = ['Master'] + [selected_customer] if selected_customer != 'all' else customer_names[1:]
    compared_data, message = compare_data(master_data, other_data, labels)

    return render_template('index.html', rules=compared_data, message=message, customer_names=customer_names[1:], selected_customer=selected_customer, filter_differences=filter_differences)

if __name__ == '__main__':
    app.run(debug=True)
