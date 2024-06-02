import sys
from bs4 import BeautifulSoup
from openpyxl import Workbook

def main(input_path, output_path):
    # Load the HTML content from the file
    with open(input_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Create a new Excel workbook and select the active sheet
    wb = Workbook()
    ws = wb.active

    # Add headers to the Excel sheet
    headers = ["Title", "Severity Level", "Package Manager", "Vulnerable Module",
               "Overview", "Remediation", "Affected Versions"]
    ws.append(headers)

    # Find all the card titles
    cards = soup.find_all('h2', class_='card__title')

    # Loop through each card and extract information
    for card in cards:
        title = card.text if card else "No card title found"

        # Extract severity
        severity = card.find_next('div', class_='label')
        if severity:
            severity_level = severity['class'][1].split('--')[-1]
            severity_text = severity.find('span', class_='label__text').text
        else:
            severity_level = "No severity found"
            severity_text = "No severity text found"

        # Extract package manager
        package_manager = card.find_next('li', text=lambda text: text and 'Package Manager:' in text)
        package_manager_text = package_manager.text.split(':', 1)[-1].strip() if package_manager else "No package manager found"

        # Extract vulnerable module
        vulnerable_module = card.find_next('li', text=lambda text: text and 'Vulnerable module:' in text)
        vulnerable_module_text = vulnerable_module.text.split(':')[-1].strip() if vulnerable_module else "No vulnerable module found"

        # Extract overview section
        nvd_description = card.find_next('h2', id='nvd-description')
        overview_text = "No overview found"
        if nvd_description:
            next_sibling = nvd_description.find_next_sibling()
            text_within_section = []
            while next_sibling and next_sibling.name != 'h2':
                if next_sibling.name == 'p' and 'Note:' not in next_sibling.get_text():
                    text_within_section.append(next_sibling.get_text())
                elif next_sibling.name == 'ul':
                    for li in next_sibling.find_all('li'):
                        if 'Note:' not in li.get_text():
                            text_within_section.append(li.get_text())
                next_sibling = next_sibling.find_next_sibling()
            overview_text = "\n".join(text_within_section) if text_within_section else "No overview found"

        # Extract remediation section
        remediation = card.find_next('h2', id='remediation')
        remediation_content = []
        if remediation:
            for sibling in remediation.find_next_siblings():
                if sibling.name == 'h2':
                    break
                if sibling.name == 'p':
                    remediation_content.append(sibling.text)

        remediation_text = "\n".join(remediation_content) if remediation_content else "No remediation found"

        # Extract detailed paths and affected versions
        detailed_paths = card.find_next('h3', class_='card__section__title', text='Detailed paths')
        affected_versions = set()
        if detailed_paths:
            list_items = detailed_paths.find_next('ul', class_='card__meta__paths').find_all('li')
            for item in list_items:
                introduced_through = item.find('span', class_='list-paths__item__introduced')
                if introduced_through:
                    path_text = introduced_through.text
                    if vulnerable_module_text and vulnerable_module_text in path_text:
                        version = path_text.split('›')[-1].strip()
                        affected_versions.add(version)

        # Combine multiple affected versions into a single string
        affected_versions_str = ', '.join(affected_versions) if affected_versions else 'No affected versions found'

        # Add data to the Excel sheet
        data_row = [title, severity_level, package_manager_text, vulnerable_module_text,
                    overview_text, remediation_text, affected_versions_str]
        ws.append(data_row)

    # Save the Excel file
    wb.save(output_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python container.py <input_html_path> <output_xlsx_path>")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        main(input_path, output_path)
