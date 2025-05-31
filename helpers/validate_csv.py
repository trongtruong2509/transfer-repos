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
    """Validate CSV file format and return repositories for validation.
    
    This function performs comprehensive validation of the CSV file format:
    1. Checks if the file exists
    2. Verifies it's a valid CSV with headers
    3. Ensures all required columns are present
    4. Validates each row has valid data (non-empty values, correct format)
    5. Checks for duplicate entries
    """
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"✗ Error: CSV file not found: {csv_path}")
        return False, []
    
    # Check if file is readable and not empty
    if os.path.getsize(csv_path) == 0:
        print(f"✗ Error: CSV file is empty: {csv_path}")
        return False, []
        
    repositories = []
    duplicates = set()
    required_fields = ['source_org', 'repo_name', 'dest_org']
    
    try:
        with open(csv_path, 'r') as csvfile:
            # First check if file is a valid CSV with headers
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            if ',' not in sample:
                print(f"✗ Error: File does not appear to be a valid CSV: {csv_path}")
                return False, []
            
            reader = csv.DictReader(csvfile)
            
            # Check if the file has any headers at all
            if not reader.fieldnames:
                print(f"✗ Error: CSV file has no headers: {csv_path}")
                return False, []
                
            # Validate CSV has required columns
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            if missing_fields:
                print(f"✗ Error: CSV is missing required columns: {', '.join(missing_fields)}")
                return False, []
                
            # Process each row with comprehensive validation
            line_num = 1
            for row in reader:
                line_num += 1
                
                # Check for empty fields
                empty_fields = [field for field in required_fields if not row.get(field, '').strip()]
                if empty_fields:
                    print(f"✗ Error on line {line_num}: Empty values for fields: {', '.join(empty_fields)}")
                    return False, []
                
                # Check for invalid characters in fields
                for field in required_fields:
                    value = row.get(field, '')
                    if any(c in value for c in ['<', '>', '|', ':', '"', '?', '*']):
                        print(f"✗ Error on line {line_num}: Invalid characters in {field}: {value}")
                        return False, []
                
                # Check for duplicate repository transfers
                repo_key = f"{row['source_org']}/{row['repo_name']}/{row['dest_org']}"
                if repo_key in duplicates:
                    print(f"✗ Error on line {line_num}: Duplicate repository transfer: {row['source_org']}/{row['repo_name']} to {row['dest_org']}")
                    return False, []
                
                duplicates.add(repo_key)
                repositories.append(row)
                
            if not repositories:
                print("✗ Error: CSV file has no data rows")
                return False, []
                
            print(f"✓ CSV format is valid with {len(repositories)} repositories to transfer")
            return True, repositories
    except csv.Error as e:
        print(f"✗ Error: Invalid CSV format: {str(e)}")
        return False, []
    except UnicodeDecodeError:
        print(f"✗ Error: CSV file has invalid encoding. Please ensure it's saved as UTF-8")
        return False, []
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
    parser.add_argument('--format-only', action='store_true', help='Only validate CSV format, skip repo and org checks')
    args = parser.parse_args()
    
    # Step 1: Validate CSV file format
    print("\n--- Validating CSV Format ---")
    is_valid, repositories = validate_csv_file(args.csv)
    if not is_valid:
        print("\n✗ CSV format validation failed. Please fix the issues and try again.")
        sys.exit(1)
    
    print(f"✓ CSV format validation successful: {args.csv}")
    
    # Exit if only format validation was requested
    if args.format_only:
        print("\n=== VALIDATION SUMMARY ===")
        print(f"✓ CSV file format is valid: {args.csv}")
        print(f"✓ Found {len(repositories)} repository transfers")
        sys.exit(0)
    
    # Step 2: Validate GitHub token
    if not validate_token():
        sys.exit(1)
        
    token = os.environ.get('GITHUB_TOKEN')
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
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
    print(f"✓ CSV file format is valid: {args.csv}")
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
