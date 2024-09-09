import json

# Define input and output file paths
input_file = "./audio/metadata.jsonl"
output_file = 'modified_file.jsonl'
path_to_add = "../mixing & switshing/"


# Open the input file for reading
with open(input_file, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()

# Open the output file for writing
with open(output_file, 'w', encoding='utf-8') as outfile:
    for line in lines:
        # Load each line as a JSON object
        data = json.loads(line)
        
        # Modify the file_name field
        data['file_name'] = f'{path_to_add}' + data['file_name']
        
        # Write the modified object back to the output file
        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

print("File names updated successfully.")