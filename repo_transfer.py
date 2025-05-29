#!/usr/bin/env python3
"""
GitHub Repository Transfer Tool

This tool automates the validation and transfer of repositories from one GitHub organization to another.
It supports both command-line arguments and CSV file input modes and includes validation, logging, and dry-run capabilities.
"""

import os
import sys
import csv
import argparse
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any


class GitHubRepoTransfer:
    """Class to handle GitHub repository transfer operations."""

    def __init__(self, token: str, debug: bool = False, dry_run: bool = False):
        """
        Initialize the GitHubRepoTransfer class.
        
        Args:
            token: GitHub API token
            debug: Enable debug logging
            dry_run: Enable dry-run mode (no actual transfers)
        """
        self.token = token
        self.dry_run = dry_run
        
        # Setup logging
        self.logger = logging.getLogger("RepoTransfer")
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("repo_transfer.log")
            ]
        )
        
        self.logger.info("Initializing GitHub Repository Transfer Tool")
        if dry_run:
            self.logger.info("DRY RUN MODE: No actual transfers will be performed")
        if debug:
            self.logger.debug("Debug logging enabled")
            
        # Initialize session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })
        
    def validate_token(self) -> bool:
        """Validate GitHub token has the necessary permissions."""
        self.logger.debug("Validating GitHub token")
        try:
            response = self.session.get("https://api.github.com/user")
            if response.status_code == 200:
                user_data = response.json()
                self.logger.info(f"Authenticated as: {user_data.get('login')}")
                return True
            else:
                self.logger.error(f"Token validation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Token validation error: {str(e)}")
            return False
            
    def validate_org_access(self, org_name: str) -> bool:
        """
        Validate access to the specified GitHub organization.
        
        Args:
            org_name: Name of the GitHub organization
            
        Returns:
            bool: True if access is valid, False otherwise
        """
        self.logger.debug(f"Validating access to organization: {org_name}")
        try:
            response = self.session.get(f"https://api.github.com/orgs/{org_name}")
            if response.status_code == 200:
                self.logger.debug(f"Organization access validated: {org_name}")
                return True
            else:
                self.logger.error(f"Organization access failed for {org_name}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Organization validation error for {org_name}: {str(e)}")
            return False
            
    def validate_repo_access(self, org_name: str, repo_name: str) -> bool:
        """
        Validate access to the specified repository.
        
        Args:
            org_name: Name of the GitHub organization
            repo_name: Name of the repository
            
        Returns:
            bool: True if access is valid, False otherwise
        """
        self.logger.debug(f"Validating access to repository: {org_name}/{repo_name}")
        try:
            response = self.session.get(f"https://api.github.com/repos/{org_name}/{repo_name}")
            if response.status_code == 200:
                self.logger.debug(f"Repository access validated: {org_name}/{repo_name}")
                return True
            else:
                self.logger.error(f"Repository access failed for {org_name}/{repo_name}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Repository validation error for {org_name}/{repo_name}: {str(e)}")
            return False
    
    def transfer_repository(self, source_org: str, repo_name: str, dest_org: str) -> bool:
        """
        Transfer a repository from source organization to destination organization.
        
        Args:
            source_org: Source GitHub organization
            repo_name: Name of the repository
            dest_org: Destination GitHub organization
            
        Returns:
            bool: True if transfer was successful, False otherwise
        """
        # Validate inputs
        if not all([source_org, repo_name, dest_org]):
            self.logger.error("Missing required parameters for transfer")
            return False
            
        # Validate organizations access
        if not self.validate_org_access(source_org):
            self.logger.error(f"Cannot access source organization: {source_org}")
            return False
            
        if not self.validate_org_access(dest_org):
            self.logger.error(f"Cannot access destination organization: {dest_org}")
            return False
            
        # Validate repository access
        if not self.validate_repo_access(source_org, repo_name):
            self.logger.error(f"Cannot access repository: {source_org}/{repo_name}")
            return False
            
        # In dry-run mode, just log what would happen
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would transfer repository {source_org}/{repo_name} to {dest_org}")
            return True
            
        # Perform the actual transfer
        self.logger.info(f"Transferring repository: {source_org}/{repo_name} to {dest_org}")
        try:
            # GitHub API endpoint for repository transfer
            url = f"https://api.github.com/repos/{source_org}/{repo_name}/transfer"
            data = {"new_owner": dest_org}
            
            response = self.session.post(url, json=data)
            
            if response.status_code in [202, 200]:  # 202 Accepted is the expected response
                self.logger.info(f"Repository transfer initiated successfully: {source_org}/{repo_name} to {dest_org}")
                return True
            else:
                self.logger.error(f"Repository transfer failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Repository transfer error: {str(e)}")
            return False
            
    def process_single_transfer(self, source_org: str, repo_name: str, dest_org: str) -> bool:
        """Process a single repository transfer with full validation."""
        self.logger.info(f"Processing transfer request: {source_org}/{repo_name} to {dest_org}")
        
        # Validate token first
        if not self.validate_token():
            self.logger.error("GitHub token validation failed, aborting transfer")
            return False
            
        # Process the transfer
        return self.transfer_repository(source_org, repo_name, dest_org)
        
    def process_csv_file(self, csv_path: str) -> Tuple[int, int]:
        """
        Process multiple repository transfers from a CSV file.
        
        CSV format should have columns: source_org,repo_name,dest_org
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Tuple[int, int]: (successful transfers, total transfers)
        """
        self.logger.info(f"Processing transfers from CSV file: {csv_path}")
        
        # Validate token first
        if not self.validate_token():
            self.logger.error("GitHub token validation failed, aborting all transfers")
            return 0, 0
            
        successful = 0
        total = 0
        
        try:
            with open(csv_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate CSV file has required columns
                required_columns = ['source_org', 'repo_name', 'dest_org']
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = [col for col in required_columns if col not in reader.fieldnames]
                    self.logger.error(f"CSV file missing required columns: {', '.join(missing)}")
                    return 0, 0
                
                for row in reader:
                    total += 1
                    source_org = row['source_org'].strip()
                    repo_name = row['repo_name'].strip()
                    dest_org = row['dest_org'].strip()
                    
                    self.logger.info(f"Processing CSV row {total}: {source_org}/{repo_name} to {dest_org}")
                    
                    if self.transfer_repository(source_org, repo_name, dest_org):
                        successful += 1
                    else:
                        self.logger.warning(f"Failed to transfer {source_org}/{repo_name} to {dest_org}")
        
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_path}")
            return 0, 0
        except Exception as e:
            self.logger.error(f"Error processing CSV file: {str(e)}")
            return successful, total
            
        self.logger.info(f"CSV processing complete. Successfully transferred {successful} out of {total} repositories")
        return successful, total


def main():
    """Main entry point of the script."""
    parser = argparse.ArgumentParser(
        description='GitHub Repository Transfer Tool',
        epilog='''
Examples:
  # Transfer a single repository (default mode)
  python3 repo_transfer.py --source-org myorg --repo-name myrepo --dest-org neworg
  
  # Transfer a single repository with dry-run to test without making actual changes
  python3 repo_transfer.py --source-org myorg --repo-name myrepo --dest-org neworg --dry-run
  
  # Transfer multiple repositories from a CSV file
  python3 repo_transfer.py --csv repos_to_transfer.csv
  
  # Use debug mode for verbose logging
  python3 repo_transfer.py --source-org myorg --repo-name myrepo --dest-org neworg --debug
  
Note: GitHub token must be set in the GITHUB_TOKEN environment variable.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Mode selection arguments
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--csv', metavar='FILE', help='Path to CSV file containing transfer information (with columns: source_org,repo_name,dest_org)')
    mode_group.add_argument('--single', action='store_true', help='Single repository transfer mode (default)', default=True)
    
    # Single transfer arguments
    parser.add_argument('--source-org', metavar='ORG', help='Source GitHub organization')
    parser.add_argument('--repo-name', metavar='REPO', help='Repository name')
    parser.add_argument('--dest-org', metavar='ORG', help='Destination GitHub organization')
    
    # Common arguments
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual transfers, just validation)')
    parser.add_argument('--debug', action='store_true', help='Enable verbose debug logging')
    
    args = parser.parse_args()
    
    # Get GitHub token from environment
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    # Create the transfer instance
    transfer = GitHubRepoTransfer(
        token=github_token,
        debug=args.debug,
        dry_run=args.dry_run
    )
    
    # Process according to selected mode
    if args.csv:
        successful, total = transfer.process_csv_file(args.csv)
        if total == 0:
            print("No repositories were processed from the CSV file")
            sys.exit(1)
        elif successful < total:
            print(f"Warning: Only {successful} out of {total} repositories were transferred successfully")
            sys.exit(1)
        else:
            print(f"Successfully transferred {successful} repositories")
            sys.exit(0)
    
    else:  # Default is single mode
        # Validate required arguments for single mode
        if not all([args.source_org, args.repo_name, args.dest_org]):
            print("Error: --source-org, --repo-name, and --dest-org are required for single transfer mode")
            sys.exit(1)
            
        # Process single transfer
        if transfer.process_single_transfer(args.source_org, args.repo_name, args.dest_org):
            print(f"Successfully transferred {args.source_org}/{args.repo_name} to {args.dest_org}")
            sys.exit(0)
        else:
            print(f"Failed to transfer {args.source_org}/{args.repo_name} to {args.dest_org}")
            sys.exit(1)


if __name__ == "__main__":
    main()
