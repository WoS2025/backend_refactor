import base64

# Read the content of the file
with open('test_data.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Encode the content
encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

# Write the encoded content to a new file
with open('test_data_base64.txt', 'w', encoding='utf-8') as file:
    file.write(encoded_content)

print("Encoded content has been written to test_data_base64.txt")