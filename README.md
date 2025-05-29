# GitHub Repository Transfer Tool

A Python-based tool to automate validation and transfer of repositories between GitHub organizations.

## Features

- Validate GitHub access tokens and permissions before transfer
- Transfer repositories between organizations
- Two operation modes:
  - Single repository transfer via command-line arguments
  - Batch transfer via CSV file
- Comprehensive logging
- Dry-run mode to simulate transfers without actually performing them
- Debug mode for verbose logging

## Requirements

- Python 3.6+
- Required Python packages:
  - requests

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Environment Setup

Before running the tool, you need to set up your GitHub API token as an environment variable:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

Make sure the token has appropriate permissions to access and transfer repositories in the specified organizations.

### Single Repository Transfer

To transfer a single repository:

```bash
python repo_transfer.py --source-org SOURCE_ORG --repo-name REPO_NAME --dest-org DEST_ORG
```

This is the default mode, so the `--single` flag is optional.

### Batch Transfer via CSV

To transfer multiple repositories defined in a CSV file:

```bash
python repo_transfer.py --csv path/to/repos.csv
```

The CSV file should have the following format:

```
source_org,repo_name,dest_org
org1,repo1,org2
org1,repo2,org3
...
```

### Additional Options

- `--dry-run`: Simulate the transfer process without actually transferring repos
- `-v, --verbose`: Enable verbose debug logging

## Logging

The tool logs all operations to both the console and individual log files in the `logs` directory. Each run creates a new log file with a timestamp (e.g., `logs/repo_transfer_20250529_165122.log`), making it easy to track different transfer sessions.

## License

MIT
