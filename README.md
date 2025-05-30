# GitHub Repository Transfer Tool

A Python-based tool to automate validation and transfer of repositories between GitHub organizations.

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
   # Run standard tests (skipping real tests)
   ./run_tests.sh
   
   # Run full tests including real integration tests
   ./run_tests.sh -f
   
   # Run only real execution tests
   ./run_tests.sh -r
   ```

For detailed information about running tests, test structure, and available test options, see [test/README.md](test/README.md).

## License

MIT
