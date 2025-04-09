import os
import xml.etree.ElementTree as ET

# removes all XML tags and retains only the text content.
def parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return ET.tostring(root, encoding='unicode', method='text')
    except ET.ParseError as e:
        print(f"Error parsing XML file {file_path}: {e}")
        return ''

def main():
    folder_path = r'C:\Project-EYE\AI Resources\TRAINING_DATA\blogsText\blogs'  # Update this with your folder path
    output_file = r'C:\Project-EYE\Project-EYE\src\trainingText.txt'

    with open(output_file, 'w', encoding='utf-8') as output:
        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                file_path = os.path.join(folder_path, filename)
                xml_content = parse_xml_file(file_path)
                if xml_content:
                    output.write(xml_content)
                    output.write('\n\n')  # Add a blank line between each XML file for readability

    print("All XML files have been printed to trainingText.txt")

if __name__ == "__main__":
    main()
