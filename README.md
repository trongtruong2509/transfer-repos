# GitHub Repository Transfer Tool

A Python-based tool to automate validation and transfer of repositories between GitHub organizations.

## 🔄 Repository Transfer Workflow

This tool is designed with a pull request-based workflow for safe, validated repository transfers.

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

### Step-by-Step Guide:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/repo-transfer-tool.git
   cd repo-transfer-tool
   ```

2. **Create a New Branch**
   ```bash
   git checkout -b transfer-repos-YYYYMMDD
   ```

3. **Update Transfer List**
   - Edit the `transfer_repos.csv` file to include ONLY the repositories you want to transfer
   - Format must be: `source_org,repo_name,dest_org` (one repository per line)
   ```csv
   source_org,repo_name,dest_org
   organization_1,repo-to-transfer,organization_2
   organization_3,another-repo,organization_4
   ```

4. **Commit and Push**
   ```bash
   git add transfer_repos.csv
   git commit -m "Add repositories for transfer"
   git push -u origin transfer-repos-YYYYMMDD
   ```

5. **Open a Pull Request**
   - Go to the repository on GitHub and create a pull request
   - This will automatically trigger validation workflows

6. **Review Validation Results**
   - The PR will show results from automatic validation as comments
   - Check the workflow logs and validation artifacts
   - Make any necessary corrections to the CSV file if issues are found

7. **Execute the Transfer**
   - Once validation passes and your PR has been approved
   - Comment `apply transfer` on the PR
   - This will trigger the actual repository transfer process
   - Results will be posted as comments on the PR

8. **Verify the Transfer**
   - Check the status report in the PR comments
   - Verify repositories have been transferred correctly in GitHub


## Installation and run locally

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
- `--auto-approve`: Skip confirmation prompts (useful for automation)

### Example Usage

1. Transfer a single repository:
   ```bash
   python repo_transfer.py --source-org my-source-org --repo-name my-repo --dest-org my-dest-org
   ```

2. Transfer multiple repositories using a CSV file:
   ```bash
   python repo_transfer.py --csv transfer_repos.csv
   ```

3. Perform a dry run (no actual transfers):
   ```bash
   python repo_transfer.py --csv transfer_repos.csv --dry-run
   ```

## GitHub Actions Workflow Details

This tool is integrated with GitHub Actions to automate repository transfers via Pull Requests.

### Two-Phase Workflow for Safety

The repository transfer process is split into two phases for safety:

#### 1. Validation Phase (`repo-transfer-pr.yml`)
- **Trigger**: Automatically runs when a PR updates `transfer_repos.csv`
- **Actions**:
  - Validates CSV format and checks for substantial changes
  - Validates repository existence in source organizations
  - Runs automated tests to ensure tool functionality
  - Performs a dry-run simulation of all transfers
  - Generates detailed validation report
- **Result**: Posts validation results as a PR comment with detailed status

#### 2. Execution Phase (`repo-transfer-comment-execution.yml`)
- **Trigger**: Manually initiated by commenting `apply transfer` on a PR
- **Safety Checks**:
  - Verifies the PR has at least one approval
  - Confirms all required status checks have passed
  - Only proceeds if all validation checks passed
- **Actions**:
  - Executes the actual repository transfers
  - Monitors progress and logs transfer details
  - Generates a comprehensive transfer report
- **Result**: Posts transfer results as a PR comment with success/failure status

### Security and Permissions

The transfer tool requires GitHub tokens with:
- Admin access to source organizations
- Admin access to destination organizations
- Permission to create repositories in destination organizations

These permissions are stored as repository secrets and are only used by the GitHub Actions workflows.

### CSV Format

The `transfer_repos.csv` file should contain the following columns:

```csv
source_org,repo_name,dest_org
nova-iris,test-repo-1,baohtruong
nova-iris,test-repo-2,baohtruong
baohtruong,test-repo-3,nova-iris
```

## Usage (Command Line)

If you prefer to use the tool directly from the command line instead of the PR workflow:

### Environment Setup

Before running the tool, you need to set up your GitHub API token as an environment variable:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
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
