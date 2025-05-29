# GitHub Repository Transfer Tool - Tests

This directory contains the test suite for the GitHub Repository Transfer Tool.

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

You can run all tests and generate a comprehensive HTML report using the provided script:

```bash
./run_tests.sh
```

This will:
1. Create a virtual environment if needed
2. Install required packages
3. Run all tests with coverage
4. Generate HTML reports

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

# Run only real execution tests that perform actual transfers
pytest test/real_execution -v
```

### Running Tests with Shortcuts

The `run_tests.sh` script provides shortcuts for running different test suites:

```bash
# Run standard tests (skipping real tests)
./run_tests.sh

# Run full tests including real integration tests
./run_tests.sh -f

# Run only real execution tests
./run_tests.sh -r

# Run only real execution tests with dedicated script
./run_real_tests.sh
```

## Setting Up Test Repositories

Before running integration tests with real GitHub API, you need to set up test repositories:

```bash
./setup_test_repos.sh your-org-1 your-org-2
```

This script will create test repositories in your organizations with different configurations.

## Test Environment Variables

For real integration tests, you need to set the following environment variables:

```bash
# Set to 1 to run real integration tests against GitHub API
export GITHUB_TEST_INTEGRATION=1

# Set to 1 to run real execution tests that perform actual transfers
export GITHUB_TEST_REAL_EXECUTION=1

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
