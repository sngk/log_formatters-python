import re
from collections import defaultdict
import statistics

def parse_memory_usage(file_path):
    date_regex = re.compile(r'\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] Memory Usage:')
    mem_regex = re.compile(r'Mem:\s+(\d+.?\d+[GM])\s+(\d+.?\d+[GM])\s+(\d+.?\d+[GM])')

    data = defaultdict(lambda: defaultdict(list))
    
    def convert_to_gb(value):
        if value.endswith('G'):
            return float(value[:-1])
        elif value.endswith('M'):
            return float(value[:-1]) / 1024
        return float(value)  # Default case

    current_date = None
    with open(file_path, 'r') as file:
        for line in file:
            date_match = date_regex.match(line)
            if date_match:
                current_date = date_match.group(1)
                continue
            
            mem_match = mem_regex.match(line)
            if mem_match and current_date:
                total, used, free = mem_match.groups()
                data[current_date]['total'].append(convert_to_gb(total))
                data[current_date]['used'].append(convert_to_gb(used))
                data[current_date]['free'].append(convert_to_gb(free))

    statistics_summary = {}
    for date, stats in data.items():
        statistics_summary[date] = {
            'average': {k: sum(v) / len(v) for k, v in stats.items()},
            'median': {k: statistics.median(v) for k, v in stats.items()}
        }

    return data, statistics_summary

def display_statistics(data, statistics_summary):
    print("Daily Statistics:")
    for date, stats in statistics_summary.items():
        print(f"Date: {date}")
        print("  Averages:")
        for key, value in stats['average'].items():
            print(f"    {key}: {value:.2f}G")
        print("  Medians:")
        for key, value in stats['median'].items():
            print(f"    {key}: {value:.2f}G")
        print()

file_path = 'mem.log'
data, statistics_summary = parse_memory_usage(file_path)
display_statistics(data, statistics_summary)
