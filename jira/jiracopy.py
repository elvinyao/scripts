import requests
import json
import yaml
import os
from getpass import getpass


class JiraTicketCloner:
    """
    Tool for cloning Jira tickets with customizable fields and automatic linking.
    """

    def __init__(self, jira_url, username, api_token):
        """
        Initialize the Jira API client.
        
        Args:
            jira_url: Base URL of your Jira instance
            username: Jira username (email)
            api_token: Jira API token
        """
        self.jira_url = jira_url.rstrip('/')
        self.auth = (username, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_ticket(self, ticket_key):
        """
        Get details of a Jira ticket.
        
        Args:
            ticket_key: Jira ticket key (e.g., 'PROJ-123')
            
        Returns:
            dict: Ticket data
        """
        url = f"{self.jira_url}/rest/api/2/issue/{ticket_key}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get ticket: {response.status_code} - {response.text}")
        
        return response.json()
    
    def get_createmeta_fields(self, project_key, issue_type_id):
        """
        Get available fields for creating a ticket in specified project and issue type.
        
        Args:
            project_key: Project key
            issue_type_id: Issue type ID
            
        Returns:
            dict: Available fields and their details
        """
        url = f"{self.jira_url}/rest/api/2/issue/createmeta/{project_key}/issuetypes/{issue_type_id}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get createmeta: {response.status_code} - {response.text}")
        
        return response.json()
    
    def create_ticket(self, project_key, ticket_data, custom_summary=None, 
                     custom_assignee=None, custom_reporter=None, target_project=None):
        """
        Create a new ticket based on existing ticket data.
        
        Args:
            project_key: Project key where the new ticket will be created
            ticket_data: Original ticket data
            custom_summary: Optional custom summary for the new ticket
            custom_assignee: Optional custom assignee for the new ticket
            custom_reporter: Optional custom reporter for the new ticket
            target_project: Optional target project key (if different from original)
            
        Returns:
            dict: New ticket data
        """
        original_fields = ticket_data.get('fields', {})
        issue_type_id = original_fields.get('issuetype', {}).get('id')
        
        # Use target project if specified, otherwise use original project
        target_project_key = target_project or project_key
        
        # Get available fields for the target project and issue type
        createmeta = self.get_createmeta_fields(target_project_key, issue_type_id)
        available_fields = createmeta.get('values', {})
        
        # Start with basic fields
        fields = {
            "project": {"key": target_project_key},
            "issuetype": original_fields.get('issuetype', {})
        }
        
        # Set custom or original summary
        if custom_summary:
            fields["summary"] = custom_summary
        elif "summary" in available_fields and original_fields.get('summary'):
            fields["summary"] = original_fields.get('summary')
        
        # Handle assignee
        if custom_assignee:
            fields["assignee"] = {"name": custom_assignee}
        elif "assignee" in available_fields and original_fields.get('assignee'):
            fields["assignee"] = original_fields.get('assignee')
            
        # Handle reporter
        if custom_reporter:
            fields["reporter"] = {"name": custom_reporter}
        elif "reporter" in available_fields and original_fields.get('reporter'):
            fields["reporter"] = original_fields.get('reporter')
        
        # Copy standard fields if they exist in available fields and have non-empty values
        standard_fields = [
            "description", "priority", "labels", "components", 
            "fixVersions", "versions", "duedate"
        ]
        
        for field in standard_fields:
            if field in available_fields and original_fields.get(field):
                fields[field] = original_fields.get(field)
        
        # Copy custom fields (including epic link) if they exist in available fields and have non-empty values
        for field_name, field_value in original_fields.items():
            if field_name.startswith('customfield_') and field_value:
                # Skip comments and attachments fields
                if 'comment' not in field_name.lower() and 'attachment' not in field_name.lower():
                    if field_name in available_fields:
                        fields[field_name] = field_value
        
        # Create new ticket
        url = f"{self.jira_url}/rest/api/2/issue"
        payload = {"fields": fields}
        
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create ticket: {response.status_code} - {response.text}")
        
        return response.json()
    
    def create_link(self, source_key, target_key, link_type="relates to"):
        """
        Create a link between two tickets.
        
        Args:
            source_key: Source ticket key
            target_key: Target ticket key
            link_type: Type of link
            
        Returns:
            bool: Success status
        """
        url = f"{self.jira_url}/rest/api/2/issueLink"
        payload = {
            "type": {
                "name": link_type
            },
            "inwardIssue": {
                "key": source_key
            },
            "outwardIssue": {
                "key": target_key
            }
        }
        
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code not in [200, 201, 204]:
            raise Exception(f"Failed to create link: {response.status_code} - {response.text}")
        
        return True
    
    def clone_ticket(self, ticket_key, custom_summary=None, custom_assignee=None, 
                    custom_reporter=None, target_project=None):
        """
        Clone a Jira ticket with custom fields and create link.
        
        Args:
            ticket_key: Original ticket key to clone
            custom_summary: Optional custom summary for the new ticket
            custom_assignee: Optional custom assignee for the new ticket
            custom_reporter: Optional custom reporter for the new ticket
            target_project: Optional target project key (if different from original)
            
        Returns:
            str: New ticket key
        """
        # Get original ticket data
        original_ticket = self.get_ticket(ticket_key)
        
        # Extract project key
        project_key = ticket_key.split('-')[0]
        
        # Create new ticket
        new_ticket = self.create_ticket(
            project_key, 
            original_ticket, 
            custom_summary, 
            custom_assignee, 
            custom_reporter,
            target_project
        )
        
        new_ticket_key = new_ticket.get('key')
        
        # Create link between tickets
        self.create_link(ticket_key, new_ticket_key)
        
        return new_ticket_key


def load_config(config_path='config.yaml'):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        dict: Configuration data
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Validate required fields
    required_fields = ['jira_url', 'username']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Required field '{field}' missing in configuration file")
    
    return config


def main():
    try:
        # Load configuration
        config = load_config()
        
        # Get API token securely if not in config
        api_token = config.get('api_token')
        if not api_token:
            api_token = getpass("Enter your Jira API token: ")
        
        # Initialize cloner
        cloner = JiraTicketCloner(
            config['jira_url'],
            config['username'],
            api_token
        )
        
        # Process tickets to clone
        tickets_to_clone = config.get('tickets_to_clone', [])
        if not tickets_to_clone:
            ticket_key = input("Enter ticket key to clone: ")
            tickets_to_clone = [{'ticket_key': ticket_key}]
        
        for ticket_config in tickets_to_clone:
            ticket_key = ticket_config.get('ticket_key')
            if not ticket_key:
                print("Skipping entry with missing ticket_key")
                continue
            
            # Clone the ticket
            new_ticket_key = cloner.clone_ticket(
                ticket_key,
                ticket_config.get('summary'),
                ticket_config.get('assignee'),
                ticket_config.get('reporter'),
                ticket_config.get('target_project')
            )
            
            print(f"Successfully cloned ticket {ticket_key}! New ticket key: {new_ticket_key}")
            print(f"View at: {config['jira_url']}/browse/{new_ticket_key}")
    
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
