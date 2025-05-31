#!/usr/bin/env python3
"""
Test the log parser function with the latest log file
"""

import sys
import os
from helpers.parse_transfer_logs import (
    extract_validation_results,
    read_csv_data,
    merge_csv_and_validation,
    generate_markdown_report,
    find_latest_log_file
)

def main():
    # Find the latest log file
    log_file = find_latest_log_file()
    if not log_file:
        print("No log file found. Please run a dry-run first.")
        return 1
    
    print(f"Analyzing log file: {log_file}")
    
    # Read CSV data
    csv_file = 'transfer_repos.csv'
    csv_data = read_csv_data(csv_file)
    
    if not csv_data:
        print(f"No data found in CSV file: {csv_file}")
        return 1
    
    print(f"Found {len(csv_data)} transfers in CSV file")
    
    # Parse log file
    validation_results = extract_validation_results(log_file)
    
    if not validation_results:
        print("No validation results found in log file")
        return 1
    
    print(f"Found {len(validation_results)} validation results in log file")
    
    # Merge data
    merged_data = merge_csv_and_validation(csv_data, validation_results)
    
    # Generate report
    output_file = 'validation_results_test.md'
    generate_markdown_report(merged_data, output_file)
    
    print(f"Test validation report generated: {output_file}")
    
    # Print the contents of the file
    with open(output_file, 'r') as f:
        print("\n" + "=" * 50)
        print(f.read())
        print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
