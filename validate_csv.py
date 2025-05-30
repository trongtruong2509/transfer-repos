#!/usr/bin/env python3
"""
Transfer CSV Validation Tool

This script validates the transfer_repos.csv file to ensure it's properly formatted
and all repositories exist before creating a PR.
"""

import os
import sys
import csv
import requests
import argparse
from typing import List, Dict, Tuple, Any

def validate_token() -> bool:
    """Validate GitHub token has the necessary permissions."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable is required")
        return False
        
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"Authenticated as: {user_data.get('login')}")
            return True
        else:
            print(f"Token validation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return False

def validate_org_access(org_name: str, headers: Dict[str, str]) -> bool:
    """Validate access to the specified GitHub organization."""
    print(f"Validating access to organization: {org_name}")
    try:
        response = requests.get(f"https://api.github.com/orgs/{org_name}", headers=headers)
        
        if response.status_code == 200:
            org_data = response.json()
            if org_data.get('type') == 'Organization':
                print(f"✓ Organization exists: {org_name}")
                return True
            else:
                print(f"✗ Error: {org_name} exists but is not an organization (likely a user account)")
                return False
        else:
            print(f"✗ Error: Organization not found: {org_name} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Error: Organization validation error for {org_name}: {str(e)}")
        return False

def validate_repo_exists(org_name: str, repo_name: str, headers: Dict[str, str]) -> bool:
    """Validate repository exists in the specified organization."""
    print(f"Checking if repository exists: {org_name}/{repo_name}")
    try:
        response = requests.get(f"https://api.github.com/repos/{org_name}/{repo_name}", headers=headers)
        
        if response.status_code == 200:
            print(f"✓ Repository exists: {org_name}/{repo_name}")
            return True
        else:
            print(f"✗ Error: Repository not found: {org_name}/{repo_name} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Error: Repository validation error for {org_name}/{repo_name}: {str(e)}")
        return False

def validate_csv_file(csv_path: str) -> Tuple[bool, List[Dict[str, str]]]:
    """Validate CSV file format and return repositories for validation."""
    if not os.path.exists(csv_path):
        print(f"✗ Error: CSV file not found: {csv_path}")
        return False, []
        
    repositories = []
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate CSV has required columns
            if not all(field in reader.fieldnames for field in ['source_org', 'repo_name', 'dest_org']):
                print("✗ Error: CSV must have 'source_org', 'repo_name', and 'dest_org' columns")
                return False, []
                
            # Process each row
            line_num = 1
            for row in reader:
                line_num += 1
                # Validate all fields are present
                if not all(row.get(field) for field in ['source_org', 'repo_name', 'dest_org']):
                    print(f"✗ Error on line {line_num}: All fields must have values")
                    return False, []
                    
                repositories.append(row)
                
            if not repositories:
                print("✗ Error: CSV file is empty or has no data rows")
                return False, []
                
            print(f"✓ CSV format is valid with {len(repositories)} repositories to transfer")
            return True, repositories
    except Exception as e:
        print(f"✗ Error processing CSV file: {str(e)}")
        return False, []

def main():
    """Main entry point of the script."""
    parser = argparse.ArgumentParser(
        description='Validate repository transfer CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--csv', metavar='FILE', help='Path to CSV file to validate', default='transfer_repos.csv')
    args = parser.parse_args()
    
    print("\n=== REPOSITORY TRANSFER CSV VALIDATION ===\n")
    
    # Validate GitHub token
    if not validate_token():
        sys.exit(1)
        
    token = os.environ.get('GITHUB_TOKEN')
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Validate CSV file
    is_valid, repositories = validate_csv_file(args.csv)
    if not is_valid:
        sys.exit(1)
    
    # Track organizations to validate
    orgs_to_validate = set()
    for repo in repositories:
        orgs_to_validate.add(repo['source_org'])
        orgs_to_validate.add(repo['dest_org'])
    
    # Validate organization access
    print("\n--- Validating Organizations ---")
    invalid_orgs = []
    for org in orgs_to_validate:
        if not validate_org_access(org, headers):
            invalid_orgs.append(org)
    
    if invalid_orgs:
        print(f"\n✗ Error: Invalid organizations: {', '.join(invalid_orgs)}")
        sys.exit(1)
    
    # Validate repositories exist
    print("\n--- Validating Repositories ---")
    invalid_repos = []
    for repo in repositories:
        if not validate_repo_exists(repo['source_org'], repo['repo_name'], headers):
            invalid_repos.append(f"{repo['source_org']}/{repo['repo_name']}")
    
    if invalid_repos:
        print(f"\n✗ Error: Invalid repositories: {', '.join(invalid_repos)}")
        sys.exit(1)
    
    # Summary
    print("\n=== VALIDATION SUMMARY ===")
    print(f"✓ CSV file is valid: {args.csv}")
    print(f"✓ All organizations are valid: {', '.join(orgs_to_validate)}")
    print(f"✓ All repositories exist in their source organizations")
    print(f"✓ Ready to create a PR with {len(repositories)} repository transfers!")
    print("\nNext steps:")
    print("1. Create a new branch")
    print("2. Commit your changes to transfer_repos.csv")
    print("3. Push and create a PR to the main branch")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
