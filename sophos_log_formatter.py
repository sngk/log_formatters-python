def format_log(log_string):
    sections = log_string.split('\n\n')

    for section in sections:
        lines = section.strip().split('\n')
        print(lines[0])  # Print the section header

        for line in lines[1:]:
            print(f"  {line}")

        print()  # Add a newline between sections

# Read log from file
with open('log.txt', 'r') as file:
    log = file.read()

format_log(log)
