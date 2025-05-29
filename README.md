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

1. Clone this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Testing

The tool includes a comprehensive test suite with 45+ test cases covering all aspects of functionality:

### Running Tests

You can run all tests and generate HTML reports using the provided script:

```bash
./run_tests.sh
```

This will:
1. Create a virtual environment if needed
2. Install required packages for testing
3. Run all tests with code coverage
4. Generate HTML reports in the `test_results` directory

The script has been enhanced to work on various Linux distributions, including Debian/Ubuntu systems.

#### Running Real Execution Tests

The tool includes tests that perform actual repository transfers to verify functionality:

```bash
# Run with the full test suite
./run_tests.sh --real-execution

# Run only the real execution tests
./run_real_tests.sh
```

**Note:** Real execution tests require:
1. A GitHub token with admin access to both test organizations
2. Test repositories created by running `setup_test_repos.sh`
3. Updated organization names in `test/conftest.py`

### Test Structure

- **Unit Tests**: Test individual components in isolation
  - Authentication
  - Organization validation
  - Repository validation
  - Transfer functionality
  - CSV processing
  - Logging

- **Integration Tests**: Test the tool end-to-end

### Setting Up Test Environment

Before running integration tests with real GitHub API:

1. Set up test repositories using the enhanced setup script:
   ```bash
   ./setup_test_repos.sh your-org-1 your-org-2
   ```
   
   This script will:
   - Create test repositories with various configurations:
     - Empty repositories
     - Public and private repositories
     - Repositories with multiple branches
     - Repositories with issues
     - Repositories with GitHub Actions workflows
   - Generate a sample CSV file for batch transfer testing
   - Provide configuration settings for `conftest.py`

2. Update `test/conftest.py` with your organization names and GitHub username:
   ```python
   TEST_ORG_1 = "your-org-1"  # First organization
   TEST_ORG_2 = "your-org-2"  # Second organization
   TEST_USER = "your-username"  # Your GitHub username
   ```

3. Set environment variables for different token permission levels:
   ```bash
   export GITHUB_TEST_INTEGRATION=1
   export GITHUB_TOKEN_ADMIN=your_admin_token
   export GITHUB_TOKEN_MEMBER=your_member_token
   export GITHUB_TOKEN_READONLY=your_readonly_token
   export GITHUB_TOKEN_ORG1=your_org1_only_token
   export GITHUB_TOKEN_ORG2=your_org2_only_token
   ```

For more details, see [test/README.md](test/README.md).

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
