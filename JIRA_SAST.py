import os
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json

def create_jira_ticket(summary, description, file_path, assignee_email):
    # Create the JSON payload for the JIRA ticket
    data = {
        "fields": {
            "project": {
                "key": "DEVELOPER"
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "Epic"
            },
            "assignee": {
                "emailAddress": assignee_email
            }
        }
    }

    # Make the HTTP POST request to create the JIRA ticket
    response = requests.post(
        f"{jira_url}/rest/api/2/issue",
        auth=jira_auth,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )

    if response.status_code == 201:
        issue_key = response.json().get('key')
        print(f"Successfully created JIRA ticket with key: {issue_key}")
        return issue_key
    else:
        print(f"Failed to create JIRA ticket: {response.content}")
        return None

def add_attachment(issue_key, file_path):
    # Define the URL for adding an attachment to the created issue
    attachment_url = f"{jira_url}/rest/api/2/issue/{issue_key}/attachments"

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        files = {'file': file}
        headers = {
            'X-Atlassian-Token': 'no-check'
        }

        # Make the HTTP POST request to add the attachment
        response = requests.post(
            attachment_url,
            auth=jira_auth,
            headers=headers,
            files=files
        )

    if response.status_code == 200:
        print(f"Successfully added attachment to JIRA ticket {issue_key}")
    else:
        print(f"Failed to add attachment: {response.content}")

# Read configuration from environment variables
try:
    jira_username = os.environ['JIRA_USERNAME']
    jira_api_token = os.environ['JIRA_API_TOKEN']
    jira_url = os.environ['JIRA_URL']
    assignee_email = os.environ['JIRA_ASSIGNEE']
    severity_level = os.environ['JIRA_SEVERITY']
except KeyError as e:
    print(f"Environment variable error: {e}")
    exit(1)

# Read the Excel file
file_path = 'source_code_analysis.xlsx'
df = pd.read_excel(file_path)

# Filter rows with specified severity level
filtered_severity_df = df[df['Severity'].str.lower() == severity_level.lower()]

# JIRA API authentication
jira_auth = HTTPBasicAuth(jira_username, jira_api_token)

if __name__ == "__main__":
    for index, row in filtered_severity_df.iterrows():
        summary = "Reponame: Severity High Source Code Analysis Vulnerabilities"
        
        # Split the Best Practices into bullet points
        best_practices_bullets = "\n".join([f"- {line.strip()}" for line in row['Best Practices'].split("\n")])

        description = f"""
*Title:* {row['Title']}
*Count:* {row['Count']}
*Location:* {row['Location']}
*Description:* {row['Description']}
*Best Practices:* 
{best_practices_bullets}
        """

        # Remove leading whitespace from each line
        description = "\n".join(line.strip() for line in description.strip().split("\n"))

        issue_key = create_jira_ticket(summary, description, file_path, assignee_email)
        if issue_key:
            add_attachment(issue_key, file_path)
