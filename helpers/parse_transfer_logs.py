#!/usr/bin/env python3
"""
Log Parser for GitHub Repository Transfers

This script parses log files from repository transfer dry runs and
generates a structured validation report in Markdown format.
"""

import os
import re
import glob
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def extract_validation_results(log_file_path: str, log_type: str = 'dry_run') -> List[Dict]:
    """
    Parse the log file and extract validation results for each repository transfer.
    
    Args:
        log_file_path: Path to the log file
        log_type: Type of log to parse ('dry_run' or 'real_run')
        
    Returns:
        List of dictionaries containing validation results for each repository
    """
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return []
    
    results = []
    current_repo = None
    source_org_status = None
    dest_org_status = None
    repo_status = None
    error_message = None
    is_dry_run = log_type == 'dry_run'
    
    with open(log_file_path, 'r') as f:
        for line in f:
            # Match the repository being processed
            repo_match = re.search(r'Processing ([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+) → ([a-zA-Z0-9_-]+)', line)
            if repo_match:
                # Save previous repository data if exists
                if current_repo:
                    results.append({
                        'source': f"{current_repo['source_org']}/{current_repo['repo_name']}",
                        'destination': current_repo['dest_org'],
                        'source_org_status': source_org_status or 'unknown',
                        'dest_org_status': dest_org_status or 'unknown',
                        'repo_status': repo_status or 'unknown',
                        'error_message': error_message
                    })
                
                # Reset for new repository
                source_org = repo_match.group(1)
                repo_name = repo_match.group(2)
                dest_org = repo_match.group(3)
                
                current_repo = {
                    'source_org': source_org,
                    'repo_name': repo_name,
                    'dest_org': dest_org
                }
                source_org_status = None
                dest_org_status = None
                repo_status = None
                error_message = None
            
            # Match success indicators based on log type
            if is_dry_run and line.strip().endswith('Transfer completed') and current_repo:
                if source_org_status is None:
                    source_org_status = 'passed'
                if dest_org_status is None:
                    dest_org_status = 'passed'
                if repo_status is None:
                    repo_status = 'passed'
            
            # For real run logs, we need to look for different success patterns
            if not is_dry_run and 'Repository transfer initiated successfully' in line and current_repo:
                if source_org_status is None:
                    source_org_status = 'passed'
                if dest_org_status is None:
                    dest_org_status = 'passed'
                if repo_status is None:
                    repo_status = 'passed'
                
            # Match specific validation steps that are common to both log types
            if 'Source organization access confirmed' in line:
                source_org_status = 'passed'
            
            if 'Destination organization access confirmed' in line:
                dest_org_status = 'passed'
                
            if 'Repository access confirmed' in line:
                repo_status = 'passed'
            
            # Match validation errors with detailed patterns
            
            # Organization errors
            org_not_found = re.search(r'Organization not found: ([a-zA-Z0-9_-]+)', line)
            if org_not_found:
                org_name = org_not_found.group(1)
                error_msg = f"Organization not found: {org_name}"
                
                # Determine if it's source or destination based on context
                if current_repo and org_name == current_repo['source_org']:
                    source_org_status = 'failed'
                    error_message = error_msg
                elif current_repo and org_name == current_repo['dest_org']:
                    dest_org_status = 'failed'
                    error_message = error_msg
            
            # Source org access errors
            if 'Cannot access source organization:' in line:
                source_org_status = 'failed'
                source_org_match = re.search(r'Cannot access source organization: ([a-zA-Z0-9_-]+)', line)
                if source_org_match:
                    error_message = f"Source organization not accessible: {source_org_match.group(1)}"
            
            # Destination org access errors
            if 'Cannot access destination organization:' in line:
                dest_org_status = 'failed'
                dest_org_match = re.search(r'Cannot access destination organization: ([a-zA-Z0-9_-]+)', line)
                if dest_org_match:
                    error_message = f"Destination organization not accessible: {dest_org_match.group(1)}"
            
            # Repository access errors
            repo_access_failed = re.search(r'Repository access failed for ([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', line)
            if repo_access_failed:
                repo_status = 'failed'
                error_message = f"Repository not accessible: {repo_access_failed.group(1)}"
            
            if 'Cannot access repository:' in line:
                repo_status = 'failed'
                repo_match = re.search(r'Cannot access repository: ([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', line)
                if repo_match:
                    error_message = f"Repository not accessible: {repo_match.group(1)}"
            
            # Match common failure patterns for both log types
            if 'Transfer failed' in line and current_repo:
                if not error_message:
                    # Generic error if no specific error was found
                    error_message = "Transfer failed"
            
            # Real run specific errors
            if not is_dry_run and 'Repository transfer failed' in line and current_repo:
                # Real run logs show repository transfer failures with specific GitHub API errors
                repo_status = 'failed'
                
            # Extract specific API error message for real runs
            if not is_dry_run and 'GitHub API returned' in line and current_repo:
                api_error_match = re.search(r'GitHub API returned (\d+): (.*)', line)
                if api_error_match:
                    status_code = api_error_match.group(1)
                    error_detail = api_error_match.group(2)
                    
                    # Try to extract specific error message from the JSON response
                    # Look for patterns like "message":"Repositories cannot be transferred..."
                    error_message_match = re.search(r'"message":"([^"]+)"', error_detail)
                    
                    # Also look for more detailed error messages in the errors array
                    detailed_error_match = re.search(r'"errors":\[\{"[^}]*"message":"([^"]+)"', error_detail)
                    
                    if detailed_error_match:
                        # This gets the more specific error message from the errors array
                        api_message = detailed_error_match.group(1)
                        error_message = f"API Error: {api_message}"
                    elif error_message_match:
                        # Fallback to the main message
                        api_message = error_message_match.group(1)
                        error_message = f"API Error: {api_message}"
                    else:
                        # Last resort if no message pattern matches
                        error_message = f"API Error ({status_code})"
                    
                    # Mark as failed if it hasn't been already
                    repo_status = 'failed'
    
    # Add the last repository if exists
    if current_repo:
        results.append({
            'source': f"{current_repo['source_org']}/{current_repo['repo_name']}",
            'destination': current_repo['dest_org'],
            'source_org_status': source_org_status or 'unknown',
            'dest_org_status': dest_org_status or 'unknown',
            'repo_status': repo_status or 'unknown',
            'error_message': error_message
        })
    
    return results

def read_csv_data(csv_file_path: str) -> List[Dict]:
    """
    Read the CSV file and return a list of dictionaries with repository transfer information.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        List of dictionaries with source_org, repo_name, and dest_org
    """
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return []
    
    transfers = []
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transfers.append({
                'source_org': row.get('source_org', ''),
                'repo_name': row.get('repo_name', ''),
                'dest_org': row.get('dest_org', '')
            })
    
    return transfers

def merge_csv_and_validation(csv_data: List[Dict], validation_results: List[Dict]) -> List[Dict]:
    """
    Merge CSV data with validation results.
    
    Args:
        csv_data: List of dictionaries from the CSV file
        validation_results: List of dictionaries from the log file
        
    Returns:
        List of dictionaries with merged data
    """
    merged_data = []
    
    # Create a lookup for validation results
    validation_lookup = {
        f"{result['source']} → {result['destination']}": result 
        for result in validation_results
    }
    
    for row in csv_data:
        source = f"{row['source_org']}/{row['repo_name']}"
        destination = row['dest_org']
        key = f"{source} → {destination}"
        
        merged_row = {
            'source': source,
            'destination': destination,
            'source_org_status': 'unknown',
            'dest_org_status': 'unknown',
            'repo_status': 'unknown',
            'error_message': None
        }
        
        if key in validation_lookup:
            result = validation_lookup[key]
            merged_row.update({
                'source_org_status': result['source_org_status'] or 'unknown',
                'dest_org_status': result['dest_org_status'] or 'unknown',
                'repo_status': result['repo_status'] or 'unknown',
                'error_message': result['error_message']
            })
        
        merged_data.append(merged_row)
    
    return merged_data

def generate_markdown_report(merged_data: List[Dict], output_file: str, log_type: str = 'dry_run') -> None:
    """
    Generate a Markdown report from the merged data.
    
    Args:
        merged_data: List of dictionaries with merged data
        output_file: Path to the output file
        log_type: Type of log being parsed ('dry_run' or 'real_run')
    """
    # Calculate statistics
    passed = sum(1 for row in merged_data if 
                row['source_org_status'] == 'passed' and 
                row['dest_org_status'] == 'passed' and 
                row['repo_status'] == 'passed')
    failed = sum(1 for row in merged_data if 
                row['source_org_status'] == 'failed' or 
                row['dest_org_status'] == 'failed' or 
                row['repo_status'] == 'failed')
    unknown = len(merged_data) - passed - failed
    
    # Identify errors for detailed reporting
    errors = [row for row in merged_data if row['error_message']]
    
    is_dry_run = log_type == 'dry_run'
    
    with open(output_file, 'w') as f:
        # Different headers based on log type
        if is_dry_run:
            f.write("### Repository Transfer Validation Results\n\n")
            f.write("The following repositories were validated for transfer:\n\n")
        else:
            f.write("### Repository Transfer Execution Results\n\n")
            f.write("The following repositories were processed for transfer:\n\n")
            
        f.write("| Source Org | Repository | Destination Org | Status |\n")
        f.write("|------------|------------|-----------------|--------|\n")
        
        for row in merged_data:
            # Extract source org and repo name from source
            source_parts = row['source'].split('/')
            source_org = source_parts[0]
            repo_name = source_parts[1] if len(source_parts) > 1 else ""
            destination_org = row['destination']
            
            # Determine overall status with descriptive message
            if row['source_org_status'] == 'failed':
                status = "❌ Failed - Source org invalid"
            elif row['dest_org_status'] == 'failed':
                status = "❌ Failed - Destination org invalid"
            elif row['repo_status'] == 'failed':
                status = "❌ Failed - Repository not found"
            elif row['error_message'] and "cannot be transferred to the original owner" in row['error_message'].lower():
                status = "❌ Failed - Original owner"
            elif row['error_message']:
                status = f"❌ Failed - {row['error_message']}"
            elif row['source_org_status'] == 'unknown' or row['dest_org_status'] == 'unknown' or row['repo_status'] == 'unknown':
                status = "⚠️ Unknown"
            else:
                if is_dry_run:
                    status = "✅ Passed validation"
                else:
                    status = "✅ Successfully transferred"
            
            f.write(f"| {source_org} | {repo_name} | {destination_org} | {status} |\n")
        
        f.write("\n")

        # Add summary statistics with different wording based on log type
        f.write(f"### Summary\n\n")
        if is_dry_run:
            f.write(f"- ✅ **Ready to transfer**: {passed} repositories\n")
            if failed > 0:
                f.write(f"- ❌ **Failed validation**: {failed} repositories\n")
        else:
            f.write(f"- ✅ **Successfully transferred**: {passed} repositories\n")
            if failed > 0:
                f.write(f"- ❌ **Failed to transfer**: {failed} repositories\n")
                
        if unknown > 0:
            f.write(f"- ⚠️ **Unknown status**: {unknown} repositories\n")
            
        # Add error details section for real runs
        if not is_dry_run and errors:
            f.write("\n### Error Details\n\n")
            for error in errors:
                source = error['source']
                dest = error['destination']
                msg = error['error_message'] or "Unknown error"
                f.write(f"- **{source} → {dest}**: {msg}\n")
        if unknown > 0:
            f.write(f"- ⚠️ **Unknown status**: {unknown} repositories\n")

def find_latest_log_file(log_dir: str = 'logs', log_type: str = 'dry_run') -> Optional[str]:
    """
    Find the latest log file in the specified directory.
    
    Args:
        log_dir: Directory containing log files
        log_type: Type of log to find ('dry_run' or 'real_run')
        
    Returns:
        Path to the latest log file, or None if no file found
    """
    # Determine the pattern based on log type
    if log_type == 'dry_run':
        pattern = 'repo_transfer_*_dry_run.log'
    else:  # real_run
        # For real run logs, they don't have the '_dry_run' suffix
        pattern = 'repo_transfer_*.log'
        # Exclude dry run logs to avoid matching them
        exclude_pattern = '*_dry_run.log'
    
    # Get all matching log files
    log_files = glob.glob(os.path.join(log_dir, pattern))
    
    # For real run, exclude dry run logs
    if log_type == 'real_run':
        exclude_files = set(glob.glob(os.path.join(log_dir, exclude_pattern)))
        log_files = [f for f in log_files if f not in exclude_files]
    
    if not log_files:
        return None
    
    # Sort by modification time (newest first)
    return sorted(log_files, key=os.path.getmtime, reverse=True)[0]

def main():
    """
    Main function to run the log parser.
    """
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Parse repository transfer logs and generate a report')
    parser.add_argument('--mode', choices=['dry_run', 'real_run'], default='dry_run',
                      help='Type of log to parse (dry_run or real_run)')
    parser.add_argument('--log-file', help='Specific log file to parse (optional)')
    parser.add_argument('--csv-file', default='transfer_repos.csv',
                      help='CSV file with repository transfer information (default: transfer_repos.csv)')
    parser.add_argument('--output-file', default='validation_results.md',
                      help='Output Markdown file (default: validation_results.md)')
    
    args = parser.parse_args()
    log_type = args.mode
    
    # Determine the log file to use
    if args.log_file:
        log_file = args.log_file
    else:
        log_file = find_latest_log_file(log_type=log_type)
    
    if not log_file:
        print(f"No {log_type} log file found. Please run a {log_type} first.")
        return
    
    print(f"Analyzing {log_type} log file: {log_file}")
    
    # Read CSV data
    csv_file = args.csv_file
    csv_data = read_csv_data(csv_file)
    
    if not csv_data:
        print(f"No data found in CSV file: {csv_file}")
        return
    
    print(f"Found {len(csv_data)} transfers in CSV file")
    
    # Parse log file
    validation_results = extract_validation_results(log_file, log_type)
    
    if not validation_results:
        print("No validation results found in log file")
        with open(args.output_file, 'w') as f:
            f.write("### Repository Transfer Validation Results\n\n")
            f.write(f"⚠️ No validation data available. The {log_type} may have failed to generate logs.\n\n")
            f.write("Please check the workflow logs for more details.\n")
        return
    
    print(f"Found {len(validation_results)} validation results in log file")
    
    # If we have CSV data, merge it for the most complete picture
    if csv_data:
        merged_data = merge_csv_and_validation(csv_data, validation_results)
        generate_markdown_report(merged_data, args.output_file, log_type)
    else:
        # Otherwise just use the validation results directly
        generate_markdown_report(validation_results, args.output_file, log_type)
    
    print(f"Validation report generated: {args.output_file}")

if __name__ == "__main__":
    main()
