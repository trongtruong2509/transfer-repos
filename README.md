# GitHub Repository Transfer Tool

A Python-based tool to automate validation and transfer of repositor### GitHub Actions Integration

This tool is integrated with GitHub Actions to automate repository transfers via Pull Requests.

### How It Works

1. Create a Pull Request with changes to `transfer_repos.csv`
2. GitHub Actions will automatically:
   - Run unit tests and integration tests
   - Validate the CSV format and check repository existence
   - If validation passes, perform a dry-run using the repositories listed in `transfer_repos.csv`
   - Upload the dry-run logs as an artifact for review
   - Add a detailed comment to the PR with validation and dry-run results GitHub organizations.

[![Repository Transfer Workflow](https://github.com/OWNER/REPO/actions/workflows/repo-transfer-pr.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/repo-transfer-pr.yml)

## Features

- Validate GitHub access tokens and permissions before transfer
- Thorough organization validation checks (existence, type, and user membership)
- Transfer repositories between organizations
- Two operation modes:
  - Single repository transfer via command-line arguments
  - Batch transfer via CSV file
- Comprehensive logging with session-specific log files
- Dry-run mode to simulate transfers without actually performing them
- Debug mode for verbose logging

## Requirements

- Python 3.6+
- Required Python packages:
  - requests

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/github-repo-transfer.git
   cd github-repo-transfer
   ```

2. Install the required packages:
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

### Example Usage

1. Transfer a single repository:
   ```bash
   python repo_transfer.py --source-org my-source-org --repo-name my-repo --dest-org my-dest-org
   ```

2. Transfer multiple repositories using a CSV file:
   ```bash
   python repo_transfer.py --csv sample_repos.csv
   ```

3. Perform a dry run (no actual transfers):
   ```bash
   python repo_transfer.py --source-org my-source-org --repo-name my-repo --dest-org my-dest-org --dry-run
   ```

4. Enable verbose logging:
   ```bash
   python repo_transfer.py --source-org my-source-org --repo-name my-repo --dest-org my-dest-org -v
   ```

## GitHub Actions Integration

This tool is integrated with GitHub Actions to automate repository transfers via Pull Requests.

### How It Works

1. Create a Pull Request with changes to `transfer_repos.csv`
2. GitHub Actions will automatically:
   - Run unit tests and integration tests
   - If tests pass, perform a dry-run using the repositories listed in `transfer_repos.csv`
   - Upload the dry-run logs as an artifact for review

### Setting Up GitHub Actions

1. Configure the required secrets in your GitHub repository settings:
   - `GITHUB_TOKEN_ADMIN`: GitHub token with admin access
   - `GITHUB_TOKEN_MEMBER`: GitHub token with member access (for testing)
   - `GITHUB_TOKEN_READONLY`: GitHub token with read-only access (for testing)
   - `GITHUB_TOKEN_ORG1`: Token for source organization
   - `GITHUB_TOKEN_ORG2`: Token for destination organization

2. Configure the repository variables in your GitHub repository settings:
   - `TEST_ORG_1`: Name of the first test organization
   - `TEST_ORG_2`: Name of the second test organization
   - `TEST_USER`: GitHub username for testing
   - `TEST_REPO_SUFFIX`: Suffix for test repositories (optional)
   - `TEST_REPO`: Name of the test repository (optional)

3. Create a Pull Request with changes to `transfer_repos.csv` to trigger the workflow

### Example CSV Format

```csv
source_org,repo_name,dest_org
nova-iris,test-repo-1,baohtruong
nova-iris,test-repo-2,baohtruong
baohtruong,test-repo-3,nova-iris
```

## Testing

## Environment Configuration

The tool uses environment variables for configuration. You can:

1. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   nano .env  # Edit with your values
   ```

2. Set environment variables manually:
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

The only required environment variable for basic usage is:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token with permissions to access and transfer repositories

## Logging

The tool logs all operations to both the console and individual log files in the `logs` directory. Each run creates a new log file with a timestamp (e.g., `logs/repo_transfer_20250529_165122.log`), making it easy to track different transfer sessions.

## Testing

The tool includes a comprehensive test suite with 45+ test cases covering all aspects of functionality.

### Setting Up the Testing Environment

1. Create and configure your testing environment:
   ```bash
   # Copy the template environment file
   cp .env.template .env
   
   # Edit the file to set your testing values
   nano .env
   ```

2. Set up test repositories using the provided script:
   ```bash
   # Set up test repositories in your GitHub organizations
   ./setup_test_repos.sh your-org-1 your-org-2
   ```
   
   This script will:
   - Create test repositories with various configurations in both organizations
   - Generate a timestamp suffix for unique repository names
   - Update your .env file with the correct values
   - Create a sample CSV file for batch transfer testing

3. Running tests:
   ```bash
   # Run unit tests only (default)
   ./run_tests.sh
   
   # Run integration tests only
   ./run_tests.sh -i
   
   # Run real execution tests only
   ./run_tests.sh -r
   
   # Run unit tests and integration tests
   ./run_tests.sh -f
   
   # Run all tests (unit, integration, real)
   ./run_tests.sh --all
   ```

For detailed information about running tests, test structure, and available test options, see [test/README.md](test/README.md).

## License

MIT
