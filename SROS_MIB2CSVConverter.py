# Updated script to include SYNTAX, MAX-ACCESS, and STATUS fields from MIB files

import os
import re
import csv

# Get the current working directory
current_directory = '/mnt/data'

# Read the OID numbers from numbers.txt
oid_numbers = {}
number_file_path = os.path.join(current_directory, 'numbers.txt')
with open(number_file_path, 'r') as number_file:
    for line in number_file:
        parts = line.strip().split()
        if len(parts) >= 2:
            oid_number = parts[0]
            oid_name = parts[1]
            oid_numbers[oid_name] = oid_number

# Find all .mib files in the current directory
mib_files = [f for f in os.listdir(current_directory) if f.endswith('.mib')]

# Initialize a list to store the OID names, MIB module names, and descriptions
all_oids = []

# Process each MIB file
for mib_file in mib_files:
    mib_file_path = os.path.join(current_directory, mib_file)
    
    # Read the MIB file
    with open(mib_file_path, 'r') as file:
        mib_content = file.read()
    
    # Extract the MIB module name (file name without the extension)
    mib_module_name = os.path.splitext(mib_file)[0]
    
    # Regular expression to match OID names, SYNTAX, MAX-ACCESS, STATUS, and multiline descriptions
    oid_pattern = re.compile(
        r'(\w+)\s+OBJECT-TYPE\s+'
        r'SYNTAX\s+(\S+)\s+'
        r'MAX-ACCESS\s+(\S+)\s+'
        r'STATUS\s+(\S+)\s+'
        r'DESCRIPTION\s+"(.*?)"', 
        re.DOTALL
    )
    
    # Extract OID names, SYNTAX, MAX-ACCESS, STATUS, and descriptions
    oids = oid_pattern.findall(mib_content)
    
    # Add the OID information to the list
    for oid_name, oid_syntax, oid_max_access, oid_status, oid_description in oids:
        # Clean up the description by removing excess whitespace
        oid_description = ' '.join(oid_description.split())
        oid_number = oid_numbers.get(oid_name, 'N/A')
        all_oids.append((oid_name, mib_module_name, oid_number, oid_syntax, oid_max_access, oid_status, oid_description))

# Write all OID information to a single CSV file
csv_file = os.path.join(current_directory, 'mib_oids.csv')
with open(csv_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['OID name', 'MIB module', 'OID', 'SYNTAX', 'MAX-ACCESS', 'STATUS', 'Description'])
    for oid_name, mib_module_name, oid_number, oid_syntax, oid_max_access, oid_status, oid_description in all_oids:
        csv_writer.writerow([oid_name, mib_module_name, oid_number, oid_syntax, oid_max_access, oid_status, oid_description])

csv_file
