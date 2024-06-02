import os
import sys
from bs4 import BeautifulSoup
from openpyxl import Workbook
import pandas as pd

def main(input_path, output_path):
    # Load the HTML file
    with open(input_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all the <h2 class="card__title"> elements, severity, description, file location, and best practices
    cards_data = []

    cards = soup.find_all('div', class_='card')
    print(f"Found {len(cards)} cards")

    for card in cards:
        title_element = card.find('h2', class_='card__title')
        if title_element:
            title = title_element.get_text(strip=True)

            # Extract severity
            severity_element = card.find('div', class_='severity-icon')
            severity = 'unknown'
            if severity_element:
                severity_classes = severity_element.get('class', [])
                for cls in severity_classes:
                    if 'severity-icon--' in cls:
                        severity = cls.replace('severity-icon--', '')
                        break

            # Extract description
            description_element = card.find('div', class_='card__summary').find('p')
            description = description_element.get_text(strip=True) if description_element else 'No description found'

            # Extract file location
            location_element = card.find('div', class_='file-location').find('strong')
            location = location_element.get_text(strip=True) if location_element else 'No location found'

            # Extract best practices
            best_practices_element = card.find('div', class_='card__section').find('h2', id='best-practices-for-prevention')
            best_practices = ''
            if best_practices_element:
                best_practices_list = best_practices_element.find_next('ul')
                if best_practices_list:
                    best_practices_items = best_practices_list.find_all('li')
                    best_practices = '\n'.join([item.get_text(strip=True) for item in best_practices_items])

            # Store the extracted information
            cards_data.append((title, severity, description, location, best_practices))
        else:
            print("No title element found for this card")

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(cards_data, columns=["Title", "Severity", "Description", "Location", "Best Practices"])

    # Group by Title and Severity, count occurrences, and create a new DataFrame
    grouped_df = df.groupby(['Title', 'Severity']).size().reset_index(name='Count')

    # Combine Location values for each group
    location_combined = df.groupby(['Title', 'Severity'])['Location'].apply(lambda x: '\n'.join(x)).reset_index(name='Location')

    # Combine Description and Best Practices values for each group
    description_combined = df.groupby(['Title', 'Severity'])['Description'].apply(lambda x: '\n'.join(pd.Series(x).unique())).reset_index(name='Description')
    best_practices_combined = df.groupby(['Title', 'Severity'])['Best Practices'].apply(lambda x: '\n'.join(pd.Series(x).unique())).reset_index(name='Best Practices')

    # Merge all the DataFrames
    merged_df = pd.merge(grouped_df, location_combined, on=['Title', 'Severity'])
    merged_df = pd.merge(merged_df, description_combined, on=['Title', 'Severity'])
    merged_df = pd.merge(merged_df, best_practices_combined, on=['Title', 'Severity'])

    # Create a new Excel workbook and worksheet
    wb = Workbook()
    ws = wb.active

    # Write headers
    ws.append(["Title", "Severity", "Count", "Location", "Description", "Best Practices"])

    # Write data rows
    for index, row in merged_df.iterrows():
        ws.append([row['Title'], row['Severity'], row['Count'], row['Location'], row['Description'], row['Best Practices']])

    # Save the workbook
    wb.save(output_path)
    print(f"Grouped and combined data has been saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python SAST.py <input_html_path> <output_xlsx_path>")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        main(input_path, output_path)
