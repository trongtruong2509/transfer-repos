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
import datetime
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class GitHubRepoTransfer:
    """Class to handle GitHub repository transfer operations."""

    def __init__(self, token: str, debug: bool = False, dry_run: bool = False, auto_approve: bool = False, confirm_each: bool = False):
        """
        Initialize the GitHubRepoTransfer class.
        
        Args:
            token: GitHub API token
            debug: Enable debug logging
            dry_run: Enable dry-run mode (no actual transfers)
            auto_approve: Skip confirmation prompts
            confirm_each: Confirm each transfer individually
        """
        self.token = token
        self.dry_run = dry_run
        self.auto_approve = auto_approve
        self.confirm_each = confirm_each
        self.user_login = None  # Will store the authenticated user's login
        self._validation_done = False  # Flag to avoid redundant validation

        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Generate a unique log filename with timestamp and dry-run indicator
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dry_run_suffix = "_dry_run" if dry_run else ""
        log_filename = f"repo_transfer_{timestamp}{dry_run_suffix}.log"
        log_path = logs_dir / log_filename

        # Setup logging with colored console output
        self.logger = logging.getLogger(f"RepoTransfer_{timestamp}{dry_run_suffix}")
        log_level = logging.DEBUG if debug else logging.INFO
        self.logger.setLevel(log_level)

        # Define color codes for console output
        class ColoredFormatter(logging.Formatter):
            """Custom formatter to add colors to log levels in console output."""
            COLORS = {
                'ERROR': '\033[91m',  # Red
                'WARNING': '\033[93m',  # Yellow
                'INFO': '',  # Default color
                'DEBUG': '\033[94m',  # Blue
                'RESET': '\033[0m'  # Reset to default
            }

            def format(self, record):
                log_message = super().format(record)
                # Add colors to specific words in the message
                if record.levelname == 'ERROR':
                    # Color the whole message for errors
                    log_message = f"{self.COLORS['ERROR']}{log_message}{self.COLORS['RESET']}"
                elif record.levelname == 'WARNING':
                    # Color the whole message for warnings
                    log_message = f"{self.COLORS['WARNING']}{log_message}{self.COLORS['RESET']}"
                else:
                    # For other levels, just color specific keywords
                    log_message = log_message.replace("FAILED", f"{self.COLORS['ERROR']}FAILED{self.COLORS['RESET']}")
                    log_message = log_message.replace("ERROR", f"{self.COLORS['ERROR']}ERROR{self.COLORS['RESET']}")
                    log_message = log_message.replace("WARNING", f"{self.COLORS['WARNING']}WARNING{self.COLORS['RESET']}")
                
                return log_message

        # Create console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        console_handler.setLevel(log_level)

        # Create file handler with regular formatting (no colors in log files)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        file_handler.setLevel(log_level)

        # Remove all handlers if already set (avoid duplicate logs)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.propagate = False

        # Define green color code for headers
        GREEN = '\033[92m'  # Bright green
        RESET = '\033[0m'   # Reset to default
        
        self.logger.info(f"{GREEN}GITHUB REPOSITORY TRANSFER TOOL - SESSION STARTED{RESET}")
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
                self.user_login = user_data.get('login')
                self.logger.debug(f"Authenticated as: {self.user_login}")
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
            # First check if the organization exists
            response = self.session.get(f"https://api.github.com/orgs/{org_name}")
            
            if response.status_code == 200:
                # Organization exists, now verify it's actually an organization (not a user)
                org_data = response.json()
                if org_data.get('type') == 'Organization':
                    self.logger.debug(f"Organization access validated: {org_name}")
                    
                    # Check if user has permissions to manage repositories in this organization
                    membership_url = f"https://api.github.com/orgs/{org_name}/memberships/{self.user_login}"
                    membership_response = self.session.get(membership_url)
                    
                    if membership_response.status_code == 200:
                        membership_data = membership_response.json()
                        role = membership_data.get('role')
                        state = membership_data.get('state')
                        
                        if state == 'active' and role in ['admin', 'member']:
                            self.logger.debug(f"User has '{role}' role in organization {org_name}")
                            return True
                        else:
                            self.logger.error(f"User membership in {org_name} is not active or has insufficient permissions")
                            return False
                    else:
                        self.logger.error(f"User is not a member of organization {org_name}")
                        return False
                else:
                    self.logger.error(f"{org_name} exists but is not an organization (likely a user account)")
                    return False
            else:
                self.logger.error(f"Organization not found: {org_name} (Status: {response.status_code} - {response.text})")
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
            
        # Skip organization and repository validation in this method if we're called from process_single_transfer
        # Otherwise, validate everything
        if not hasattr(self, '_validation_done') or not self._validation_done:
            self._log_section_header("Validating Repository Transfer Prerequisites")
            
            # Validate organizations access
            self._log_step(1, 3, f"Checking access to source organization '{source_org}'...")
            if not self.validate_org_access(source_org):
                self._log_step_result(False, f"Cannot access source organization: {source_org}")
                return False
            self._log_step_result(True, f"Source organization access confirmed")
            
            self._log_step(2, 3, f"Checking access to destination organization '{dest_org}'...")
            if not self.validate_org_access(dest_org):
                self._log_step_result(False, f"Cannot access destination organization: {dest_org}")
                return False
            self._log_step_result(True, f"Destination organization access confirmed")
            
            # Validate repository access
            self._log_step(3, 3, f"Checking access to repository '{source_org}/{repo_name}'...")
            if not self.validate_repo_access(source_org, repo_name):
                self._log_step_result(False, f"Cannot access repository: {source_org}/{repo_name}")
                return False
            self._log_step_result(True, f"Repository access confirmed")
            
            self._log_section_header("Validation Successful")
            
            # Removed confirmation prompt here since it's handled in calling methods
        
        # In dry-run mode, just log what would happen
        if self.dry_run:
            self._log_section_header("DRY RUN TRANSFER SIMULATION")
            self._log_step_result(True, f"Would transfer repository {source_org}/{repo_name} to {dest_org}")
            return True
            
        # Perform the actual transfer
        self.logger.info("Initiating repository transfer...")
        try:
            # GitHub API endpoint for repository transfer
            url = f"https://api.github.com/repos/{source_org}/{repo_name}/transfer"
            data = {"new_owner": dest_org}
            
            self._log_step(1, 1, f"Sending transfer request for {source_org}/{repo_name}...")
            response = self.session.post(url, json=data)
            self.logger.debug(f"Transfer API response: {response.status_code} {response.text}")
            
            if response.status_code == 202:
                self._log_step_result(True, f"Repository transfer initiated successfully")
                return True
            else:
                self._log_step_result(False, f"Repository transfer failed", f"GitHub API returned {response.status_code}: {response.text}")
                self.logger.error(f"Transfer failed: {response.status_code} {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Exception during transfer_repository API call: {e}", exc_info=True)
            return False
            
    def _log_section_header(self, title: str) -> None:
        """Log a major section header with consistent formatting and green color."""
        # Define green color code
        GREEN = '\033[92m'  # Bright green
        RESET = '\033[0m'   # Reset to default
        
        # Use error level for headers containing "FAILED" or "ERROR", warning for "WARNING", otherwise green
        if "FAILED" in title or "ERROR" in title:
            self.logger.error(f"{title}")
        elif "WARNING" in title:
            self.logger.warning(f"{title}")
        else:
            # For normal headers, use info level with green color
            self.logger.info(f"{GREEN}{title}{RESET}")
    
    def _log_step(self, step_number: int, total_steps: int, description: str) -> None:
        """Log a numbered step in a multi-step process."""
        self.logger.info(f"Step {step_number}/{total_steps}: {description}")
        
    def _log_step_result(self, success: bool, message: str, details: str = None) -> None:
        """Log the result of a step with visual indicator."""
        # Define color codes
        GREEN = '\033[92m'  # Bright green
        RED = '\033[91m'    # Red
        RESET = '\033[0m'   # Reset to default
        
        # Apply appropriate color to the prefix symbol
        if success:
            prefix = f"{GREEN}✓{RESET}"
            self.logger.info(f"{prefix} {message}")
        else:
            prefix = f"{RED}✗{RESET}"
            # For failed steps, use error level to trigger red coloring
            self.logger.error(f"{prefix} {message}")
        
        if details:
            level = logging.INFO if success else logging.ERROR
            self.logger.log(level, f"  - {details}")
            
    def _log_warning(self, message: str) -> None:
        """Log a warning message with a warning symbol."""
        # Define yellow color for warning symbol
        YELLOW = '\033[93m'  # Yellow
        RESET = '\033[0m'    # Reset to default
        
        # Add yellow color to the warning symbol
        self.logger.warning(f"{YELLOW}⚠{RESET} {message}")
    
    def _prompt_for_confirmation(self, source_org: str, repo_name: str, dest_org: str) -> bool:
        """
        Prompt the user for confirmation before proceeding with the transfer.
        
        Args:
            source_org: Source GitHub organization
            repo_name: Repository name
            dest_org: Destination GitHub organization
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        if self.auto_approve:
            self.logger.info("Auto-approve is enabled, skipping confirmation prompt")
            return True
            
        # Use color for better visibility
        YELLOW = '\033[93m'  # Yellow
        GREEN = '\033[92m'   # Green
        RED = '\033[91m'     # Red
        RESET = '\033[0m'    # Reset to default
        
        print(f"\n{YELLOW}CONFIRMATION REQUIRED{RESET}")
        print(f"You are about to transfer repository: {GREEN}{source_org}/{repo_name}{RESET} to {GREEN}{dest_org}{RESET}")
        
        if self.dry_run:
            print(f"{YELLOW}(DRY RUN MODE: No actual transfer will be performed){RESET}")
        
        try:
            response = input(f"Do you want to proceed with this transfer? (y/N) ").strip().lower()
            if response == 'y' or response == 'yes':
                self.logger.info("User confirmed transfer")
                return True
            else:
                self.logger.info("User declined transfer")
                return False
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            self.logger.info("Operation cancelled by user (KeyboardInterrupt)")
            return False
    
    def _prompt_for_batch_confirmation(self, repos: List[Dict[str, str]]) -> bool:
        """
        Prompt the user for confirmation before proceeding with a batch of transfers.
        
        Args:
            repos: List of repository dictionaries with source_org, repo_name, dest_org keys
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        if self.auto_approve:
            self.logger.info("Auto-approve is enabled, skipping confirmation prompt")
            return True
            
        # Use color for better visibility
        YELLOW = '\033[93m'  # Yellow
        GREEN = '\033[92m'   # Green
        RED = '\033[91m'     # Red
        RESET = '\033[0m'    # Reset to default
        
        print(f"\n{YELLOW}BATCH CONFIRMATION REQUIRED{RESET}")
        print(f"You are about to transfer {GREEN}{len(repos)} repositories{RESET}:")
        
        # Display the list of repositories to be transferred
        for i, repo in enumerate(repos, 1):
            source_org = repo['source_org'].strip()
            repo_name = repo['repo_name'].strip()
            dest_org = repo['dest_org'].strip()
            print(f"  {i}. {GREEN}{source_org}/{repo_name}{RESET} → {GREEN}{dest_org}{RESET}")
        
        if self.dry_run:
            print(f"\n{YELLOW}(DRY RUN MODE: No actual transfers will be performed){RESET}")
        
        try:
            response = input(f"\nDo you want to proceed with all these transfers? (y/N) ").strip().lower()
            if response == 'y' or response == 'yes':
                self.logger.info(f"User confirmed batch transfer of {len(repos)} repositories")
                return True
            else:
                self.logger.info("User declined batch transfer")
                return False
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            self.logger.info("Operation cancelled by user (KeyboardInterrupt)")
            return False
    
    def process_single_transfer(self, source_org: str, repo_name: str, dest_org: str) -> bool:
        """Process a single repository transfer with full validation."""
        self._log_section_header(f"Starting GitHub token and organization validation...")
        self.logger.info(f"Processing transfer request: {source_org}/{repo_name} to {dest_org}")
        # Step 1: Validate token
        self._log_step(1, 3, "Testing GitHub API connection...")
        if not self.validate_token():
            self.logger.error("GitHub token validation failed, aborting transfer")
            self._log_step_result(False, "GitHub API connection failed", "Invalid token or API error")
            self._log_section_header("VALIDATION FAILED - TRANSFER ABORTED")
            return False
        else:
            self._log_step_result(True, f"GitHub API connection successful (authenticated as: {self.user_login})")
        # Step 2: Validate source organization
        self._log_step(2, 3, f"Validating access to source organization '{source_org}'...")
        source_org_valid = self.validate_org_access(source_org)
        if not source_org_valid:
            self._log_step_result(False, f"Failed to access source organization '{source_org}'", 
                                "Organization not found, user not a member, or insufficient permissions")
            self.logger.error(f"Source org validation failed for {source_org}")
            if not self.dry_run:
                self._log_section_header("VALIDATION FAILED - TRANSFER ABORTED")
                return False
            else:
                self._log_warning(f"Continuing in DRY RUN mode despite source org validation failure")
        else:
            self._log_step_result(True, f"Access to source organization '{source_org}' confirmed")
        # Step 3: Validate destination organization
        self._log_step(3, 3, f"Validating access to destination organization '{dest_org}'...")
        dest_org_valid = self.validate_org_access(dest_org)
        if not dest_org_valid:
            self._log_step_result(False, f"Failed to access destination organization '{dest_org}'", 
                                "Organization not found, user not a member, or insufficient permissions")
            self.logger.error(f"Destination org validation failed for {dest_org}")
            if not self.dry_run:
                self._log_section_header("VALIDATION FAILED - TRANSFER ABORTED")
                return False
            else:
                self._log_warning(f"Continuing in DRY RUN mode despite destination org validation failure")
        else:
            self._log_step_result(True, f"Access to destination organization '{dest_org}' confirmed")
        
        # Determine overall validation status
        all_valid = self.user_login and source_org_valid and dest_org_valid
        
        if all_valid:
            self._log_section_header("VALIDATION COMPLETED SUCCESSFULLY")
        elif self.dry_run:
            self._log_section_header("VALIDATION PARTIALLY COMPLETED - CONTINUING IN DRY RUN MODE")
            self._log_warning(f"Simulating transfer: {source_org}/{repo_name} → {dest_org}")
        else:
            self._log_section_header("VALIDATION FAILED - TRANSFER ABORTED")
            return False
        
        # Set a flag to indicate validation is already done
        self._validation_done = True
        
        # Ask for confirmation before proceeding with transfer
        if not self._prompt_for_confirmation(source_org, repo_name, dest_org):
            self._log_section_header("TRANSFER ABORTED BY USER")
            self._validation_done = False  # Reset flag
            return False
            
        # Process the transfer
        self._log_section_header(f"STARTING REPOSITORY TRANSFER")
        try:
            result = self.transfer_repository(source_org, repo_name, dest_org)
        except Exception as e:
            self.logger.error(f"Exception during transfer_repository: {e}", exc_info=True)
            result = False
        self._validation_done = False  # Reset flag
        
        if result:
            self._log_section_header("REPOSITORY TRANSFER COMPLETED SUCCESSFULLY")
        else:
            self._log_section_header("REPOSITORY TRANSFER FAILED")
            
        return result
        
    def process_csv_file(self, csv_path: str) -> Tuple[int, int]:
        """
        Process multiple repository transfers from a CSV file.
        
        CSV format should have columns: source_org,repo_name,dest_org
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Tuple[int, int]: (successful transfers, total transfers)
        """
        self._log_section_header(f"PROCESSING BATCH TRANSFERS FROM CSV")
        self.logger.info(f"CSV file: {csv_path}")
        
        # Step 1: Validate token
        self._log_step(1, 3, "Testing GitHub API connection...")
        if not self.validate_token():
            self._log_step_result(False, "GitHub API connection failed", "Invalid token or API error")
            self._log_section_header("VALIDATION FAILED - TRANSFERS ABORTED")
            return 0, 0
        else:
            self._log_step_result(True, f"GitHub API connection successful (authenticated as: {self.user_login})")
            
        # Step 2: Check file existence and format
        self._log_step(2, 3, f"Validating CSV file format...")
        
        successful = 0
        total = 0
        
        try:
            with open(csv_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate CSV file has required columns
                required_columns = ['source_org', 'repo_name', 'dest_org']
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = [col for col in required_columns if col not in reader.fieldnames]
                    self._log_step_result(False, f"CSV file has invalid format", 
                                        f"Missing required columns: {', '.join(missing)}")
                    self._log_section_header("VALIDATION FAILED - TRANSFERS ABORTED")
                    return 0, 0
                else:
                    self._log_step_result(True, f"CSV file format validated successfully")
                
                # Step 3: Process the repositories
                self._log_step(3, 3, "Processing repository transfers...")
                
                repos = list(reader)
                if not repos:
                    self._log_step_result(False, "No repositories found in CSV file", "File may be empty or malformed")
                    self._log_section_header("BATCH TRANSFER COMPLETED - NO REPOSITORIES PROCESSED")
                    return 0, 0
                
                self._log_section_header(f"TRANSFERRING {len(repos)} REPOSITORIES")
                
                # Get batch confirmation for all transfers if not in confirm_each mode
                if not self.confirm_each and not self.auto_approve:
                    if not self._prompt_for_batch_confirmation(repos):
                        self._log_section_header("BATCH TRANSFER ABORTED BY USER")
                        return 0, 0
                
                for i, row in enumerate(repos, 1):
                    total += 1
                    source_org = row['source_org'].strip()
                    repo_name = row['repo_name'].strip()
                    dest_org = row['dest_org'].strip()
                    
                    self._log_step(i, len(repos), f"Processing {source_org}/{repo_name} → {dest_org}")
                    
                    # Prompt for confirmation before each transfer if in confirm_each mode
                    if self.confirm_each and not self.auto_approve:
                        if not self._prompt_for_confirmation(source_org, repo_name, dest_org):
                            self._log_step_result(False, f"Transfer skipped (user declined)", f"{source_org}/{repo_name} → {dest_org}")
                            continue
                    
                    if self.transfer_repository(source_org, repo_name, dest_org):
                        successful += 1
                        self._log_step_result(True, f"Transfer completed", f"{source_org}/{repo_name} → {dest_org}")
                    else:
                        self._log_step_result(False, f"Transfer failed", f"{source_org}/{repo_name} → {dest_org}")
                
                # Summary section
                if successful == total:
                    self._log_section_header(f"BATCH TRANSFER COMPLETED SUCCESSFULLY")
                    self._log_step_result(True, f"Transferred {successful} out of {total} repositories")
                elif successful > 0:
                    self._log_section_header(f"BATCH TRANSFER COMPLETED WITH PARTIAL SUCCESS")
                    self._log_warning(f"Only {successful} out of {total} repositories were transferred successfully")
                else:
                    self._log_section_header(f"BATCH TRANSFER FAILED")
                    self._log_step_result(False, f"Failed to transfer any repositories", f"0 of {total} succeeded")
        
        except FileNotFoundError:
            self._log_step_result(False, f"CSV file not found", csv_path)
            self._log_section_header("VALIDATION FAILED - TRANSFERS ABORTED")
            return 0, 0
        except Exception as e:
            self._log_step_result(False, f"Error processing CSV file", str(e))
            if successful > 0:
                self._log_section_header(f"BATCH TRANSFER INTERRUPTED - PARTIAL SUCCESS")
                self._log_warning(f"Only {successful} out of {total} repositories were processed before error")
            else:
                self._log_section_header(f"BATCH TRANSFER FAILED")
            
            return successful, total
            
        return successful, total

def log_program_completion(logger, success: bool = True):
    """Add a footer to the log when the program completes."""
    # Define color codes
    GREEN = '\033[92m'  # Bright green
    RED = '\033[91m'    # Red
    RESET = '\033[0m'   # Reset to default
    
    status = "SUCCESSFULLY" if success else "WITH ERRORS"
    
    if success:
        logger.info(f"{GREEN}GITHUB REPOSITORY TRANSFER TOOL - SESSION COMPLETED {status}{RESET}")
    else:
        logger.error(f"GITHUB REPOSITORY TRANSFER TOOL - SESSION COMPLETED {status}")


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
  
  # Use verbose mode for detailed logging
  python3 repo_transfer.py --source-org myorg --repo-name myrepo --dest-org neworg -v
  
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
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose debug logging')
    parser.add_argument('--auto-approve', action='store_true', help='Skip confirmation prompts and automatically approve all transfers')
    parser.add_argument('--confirm-each', action='store_true', help='Confirm each transfer individually (default is to confirm all transfers at once)')
    
    args = parser.parse_args()
    
    # Get GitHub token from environment
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    # Create the transfer instance
    transfer = GitHubRepoTransfer(
        token=github_token,
        debug=args.verbose,
        dry_run=args.dry_run,
        auto_approve=args.auto_approve,
        confirm_each=args.confirm_each
    )
    
    # Process according to selected mode
    if args.csv:
        successful, total = transfer.process_csv_file(args.csv)
        if total == 0:
            log_program_completion(transfer.logger, success=False)
            print("No repositories were processed from the CSV file")
            sys.exit(1)
        elif successful < total:
            log_program_completion(transfer.logger, success=False)
            print(f"Warning: Only {successful} out of {total} repositories were transferred successfully")
            sys.exit(1)
        else:
            log_program_completion(transfer.logger, success=True)
            print(f"Successfully transferred {successful} repositories")
            sys.exit(0)
    
    else:  # Default is single mode
        # Validate required arguments for single mode
        if not all([args.source_org, args.repo_name, args.dest_org]):
            print("Error: --source-org, --repo-name, and --dest-org are required for single transfer mode")
            sys.exit(1)
            
        # Process single transfer
        success = transfer.process_single_transfer(args.source_org, args.repo_name, args.dest_org)
        log_program_completion(transfer.logger, success=success)
        
        if success:
            print(f"Successfully transferred {args.source_org}/{args.repo_name} to {args.dest_org}")
            sys.exit(0)
        else:
            print(f"Failed to transfer {args.source_org}/{args.repo_name} to {args.dest_org}")
            sys.exit(1)
    
    log_program_completion(transfer.logger, success=True)


if __name__ == "__main__":
    main()
