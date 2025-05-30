# GitHub Repository Transfer Tool - Tests

This directory contains the test suite for the GitHub Repository Transfer Tool.

## Setting Up the Test Environment

Before running tests, you need to set up your test environment:

1. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   nano .env  # Edit with your values
   ```

2. Configure the testing section in the `.env` file:
   - Set `GITHUB_TOKEN` to your GitHub Personal Access Token
   - Set `TEST_ORG_1` and `TEST_ORG_2` to your GitHub organization names
   - Set `TEST_USER` to your GitHub username
   - Configure additional test tokens if needed

3. Set up test repositories using the enhanced setup script:
   ```bash
   ./setup_test_repos.sh your-org-1 your-org-2
   ```
   
   This script will:
   - Create test repositories with various configurations in both organizations
   - Generate a timestamp suffix for unique repository names
   - Update your .env file with the correct values
   - Create a sample CSV file for batch transfer testing

## Test Structure

The test suite is organized as follows:

- `unit/`: Unit tests that test individual components in isolation
  - `test_authentication.py`: Tests for token validation
  - `test_organization_validation.py`: Tests for organization validation
  - `test_repository_validation.py`: Tests for repository validation
  - `test_transfer.py`: Tests for repository transfer functionality
  - `test_csv_processing.py`: Tests for CSV file processing
  - `test_logging.py`: Tests for logging functionality

- `integration/`: Integration tests that test the tool end-to-end
  - `test_integration.py`: End-to-end tests with real or mocked GitHub API

- `real_execution/`: Real-world execution tests that perform actual repository transfers
  - `test_real_execution.py`: Tests that execute actual repository transfers (not dry-run)

- `fixtures/`: Shared test fixtures (via conftest.py)

## Running Tests

The tool includes a comprehensive test suite with 45+ test cases covering all aspects of functionality:

### Using the Test Script

You can run all tests and generate a comprehensive HTML report using the provided script:

```bash
# Run standard tests (skipping real tests)
./run_tests.sh

# Run full tests including real integration tests
./run_tests.sh -f

# Run only real execution tests
./run_tests.sh -r

# Run full tests and real execution tests
./run_tests.sh -f -r
```

This will:
1. Create a virtual environment if needed
2. Install required packages
3. Run all tests with coverage
4. Generate HTML reports

The script has been enhanced to work on various Linux distributions, including Debian/Ubuntu systems.

### Running Specific Tests

To run specific test files or test cases:

```bash
# Activate virtual environment
source venv/bin/activate

# Run a specific test file
pytest test/unit/test_authentication.py -v

# Run a specific test case
pytest test/unit/test_authentication.py::TestAuthentication::test_valid_token -v

# Run tests with a specific marker
pytest -m "not integration" -v
```

## Setting Up Test Environment

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

### Running Real Execution Tests

The tool includes tests that perform actual repository transfers to verify functionality:

```bash
# Run only real execution tests
./run_tests.sh -r

# Alternative dedicated script for real execution tests
./run_real_tests.sh
```

**Note:** Real execution tests require:
1. A GitHub token with admin access to both test organizations
2. Test repositories created by running `setup_test_repos.sh`
3. Updated organization names in `test/conftest.py`

## Test Environment Variables

The following environment variables are used for testing:

| Variable | Description | Required For |
|----------|-------------|------------|
| `GITHUB_TOKEN` | Your GitHub Personal Access Token | All operations |
| `TEST_ORG_1` | First organization name for testing | Real execution tests |
| `TEST_ORG_2` | Second organization name for testing | Real execution tests |
| `TEST_USER` | Your GitHub username | Real execution tests |
| `TEST_REPO_SUFFIX` | Timestamp suffix for unique repo names | Real execution tests |
| `TEST_REPO` | Repository name used in tests | Real execution tests |
| `GITHUB_TEST_INTEGRATION` | Set to "1" to enable real API integration tests | Integration tests |
| `GITHUB_TEST_REAL_EXECUTION` | Set to "1" to enable actual repository transfers | Real execution tests |
| `GITHUB_TOKEN_ADMIN` | Admin access token | Permission tests |
| `GITHUB_TOKEN_MEMBER` | Member access token | Permission tests |
| `GITHUB_TOKEN_READONLY` | Read-only access token | Permission tests |
| `GITHUB_TOKEN_ORG1` | Token with access to org1 only | Permission tests |
| `GITHUB_TOKEN_ORG2` | Token with access to org2 only | Permission tests |

You can set these variables in the `.env` file or directly in your shell environment:

```bash
# Set to 1 to run real integration tests against GitHub API
export GITHUB_TEST_INTEGRATION=1

# Different tokens for testing various permission levels
export GITHUB_TOKEN_ADMIN=your_admin_token
export GITHUB_TOKEN_MEMBER=your_member_token
export GITHUB_TOKEN_READONLY=your_readonly_token
export GITHUB_TOKEN_ORG1=your_org1_only_token
export GITHUB_TOKEN_ORG2=your_org2_only_token
```

## Test Reports

After running tests, reports are available in the `test_results` directory:
- HTML Test Report: `test_results/report.html`
- Coverage Report: `test_results/coverage/index.html`

## Continuous Integration

This test suite is designed to work well in CI/CD environments. For GitHub Actions, see the example workflow in the main README.md.
