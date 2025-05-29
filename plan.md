# Test Plan for GitHub Repository Transfer Tool

## Overview

This document outlines a comprehensive testing strategy for the GitHub Repository Transfer Tool. Since repository transfers are critical operations that can impact organizational assets, thorough testing is essential to ensure reliability, security, and proper handling of all possible scenarios.

## Test Environment Setup

### Available Resources
1. Two GitHub organizations
2. Personal GitHub user account (can be used for testing user vs. organization validation)
3. Ability to create multiple GitHub tokens with different permission levels

### Test Repository Configuration
Create test repositories with various configurations across the two organizations:
   - Public and private repositories
   - Repositories with various sizes (empty, small, large)
   - Repositories with different branch structures
   - Repositories with open issues, pull requests
   - Repositories with GitHub Actions workflows
   - Repositories with GitHub Pages enabled

### Test Environment Variables
- GitHub tokens with different permission scopes:
  - Admin token with full access to both organizations
  - Member token with limited permissions to both organizations
  - Read-only token with minimal permissions
  - Token with access to only one organization
  - Invalid/expired token

## Test Categories

### 1. Authentication Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| AUTH-01 | Valid token with sufficient permissions | Authentication successful | High |
| AUTH-02 | Valid token with insufficient permissions | Authentication successful, but transfer operations fail with appropriate error messages | High |
| AUTH-03 | Expired token | Authentication fails with clear error message | High |
| AUTH-04 | Invalid token format | Authentication fails with clear error message | Medium |
| AUTH-05 | Missing token (environment variable not set) | Script exits with clear error message | High |

### 2. Organization Validation Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| ORG-01 | Valid source organization (Org 1) with admin token | Organization validation successful | High |
| ORG-02 | Valid source organization (Org 1) with member token | Organization validation successful | High |
| ORG-03 | Valid source organization (Org 1) with read-only token | Organization validation fails with appropriate error | High |
| ORG-04 | Non-existent organization name | Organization validation fails with clear error message | High |
| ORG-05 | Valid destination organization (Org 2) with admin token | Organization validation successful | High |
| ORG-06 | Valid destination organization (Org 2) with member token | Organization validation successful | High |
| ORG-07 | Valid destination organization (Org 2) with token that only has access to Org 1 | Organization validation fails with appropriate error | High |
| ORG-08 | User account instead of organization (try to use your personal account as org) | Organization validation fails with clear error message | Medium |
| ORG-09 | Attempt to access Org 2 with token scoped only to Org 1 | Organization validation fails with clear error message | High |

### 3. Repository Validation Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| REPO-01 | Existing repository in source organization | Repository validation successful | High |
| REPO-02 | Non-existent repository in source organization | Repository validation fails with clear error message | High |
| REPO-03 | Repository with same name already exists in destination organization | Transfer fails with appropriate error message | High |
| REPO-04 | Repository with open issues and pull requests | Transfer successful, issues and PRs preserved | Medium |
| REPO-05 | Repository with GitHub Actions workflows | Transfer successful, workflows preserved | Medium |
| REPO-06 | Repository with GitHub Pages enabled | Transfer successful, GitHub Pages configuration preserved | Medium |
| REPO-07 | Repository with branch protection rules | Transfer successful, protection rules preserved | Medium |
| REPO-08 | Empty repository | Transfer successful | Low |
| REPO-09 | Very large repository (>1GB) | Transfer successful but may take longer | Medium |

### 4. Single Transfer Mode Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| SINGLE-01 | Valid source org, repo name, and destination org | Transfer successful | High |
| SINGLE-02 | Missing source org parameter | Script exits with clear error message | Medium |
| SINGLE-03 | Missing repository name parameter | Script exits with clear error message | Medium |
| SINGLE-04 | Missing destination org parameter | Script exits with clear error message | Medium |
| SINGLE-05 | Transfer with dry-run flag | No actual transfer occurs, validation steps executed | High |
| SINGLE-06 | Transfer with verbose flag | Detailed logs printed | Medium |
| SINGLE-07 | Transfer with both dry-run and verbose flags | No actual transfer occurs, detailed logs printed | Medium |

### 5. CSV Batch Mode Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| CSV-01 | Valid CSV file with multiple repositories | All transfers successful | High |
| CSV-02 | CSV file with some valid and some invalid repositories | Valid repositories transferred, invalid ones skipped with errors | High |
| CSV-03 | CSV file with missing required columns | Script exits with clear error message | High |
| CSV-04 | Empty CSV file | Script exits with clear error message | Medium |
| CSV-05 | CSV file with malformed data | Script handles errors gracefully | Medium |
| CSV-06 | Non-existent CSV file | Script exits with clear error message | Medium |
| CSV-07 | CSV with hundreds of repositories | All transfers successful, memory usage stable | Low |
| CSV-08 | CSV transfer with dry-run flag | No actual transfers occur, validation steps executed | High |
| CSV-09 | CSV transfer with verbose flag | Detailed logs printed | Medium |

### 6. Error Handling Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| ERR-01 | Network interruption during transfer | Script handles error gracefully, provides clear message | High |
| ERR-02 | GitHub API rate limit exceeded | Script handles error gracefully, suggests waiting | Medium |
| ERR-03 | GitHub API changes/downtime | Script fails gracefully with clear error message | Medium |
| ERR-04 | Permission changes during execution | Script detects permission issues and fails appropriately | Medium |
| ERR-05 | Unexpected API responses | Script handles unexpected responses gracefully | Medium |

### 7. Logging Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| LOG-01 | Check log file creation | Log file created with correct naming format | Medium |
| LOG-02 | Check log content with successful transfers | Logs contain all necessary information | Medium |
| LOG-03 | Check log content with failed transfers | Logs contain detailed error information | High |
| LOG-04 | Check console output formatting | Console output is well-formatted with appropriate colors | Low |
| LOG-05 | Check debug mode logging | Debug mode provides extensive information | Medium |

### 8. Cross-Organization Transfer Tests

| ID | Test Case | Expected Result | Priority |
|----|-----------|----------------|----------|
| CROSS-01 | Transfer from Org 1 to Org 2 with admin token | Transfer successful | High |
| CROSS-02 | Transfer from Org 2 to Org 1 with admin token | Transfer successful | High |
| CROSS-03 | Transfer from Org 1 to Org 2 with member token | Transfer successful if member has necessary permissions | High |
| CROSS-04 | Transfer from Org 1 to personal user account | Transfer successful if user has necessary permissions | Medium |
| CROSS-05 | Transfer from personal user account to Org 1 | Transfer successful if user has necessary permissions | Medium |

## Automated Testing Strategy

1. **Unit Tests**:
   - Test validation functions in isolation
   - Mock GitHub API responses to test various scenarios
   - Test CSV parsing and error handling

2. **Integration Tests**:
   - Test end-to-end flow with real GitHub API (using test accounts)
   - Test with limited number of repositories to avoid rate limits

3. **Load Testing**:
   - Test with a large number of repositories to ensure stability
   - Monitor memory usage and performance

## Manual Testing Checklist

For each major release, perform the following manual tests:

1. Verify all console outputs are clear and helpful
2. Verify color coding works as expected in different terminals
3. Check log files for completeness and readability
4. Verify dry-run mode doesn't perform actual transfers
5. Check permissions on transferred repositories to ensure they match expectations
6. Verify webhook configurations are properly transferred
7. Test on different operating systems (Windows, macOS, Linux)

## Testing Matrix for Available Resources

Given the limited number of organizations (2) and your personal account, we'll create a testing matrix to maximize test coverage:

### Organization Matrix
- **Org 1**: Primary test organization 
- **Org 2**: Secondary test organization
- **Personal Account**: For testing user vs. organization scenarios

### Token Permission Matrix
| Token | Access to Org 1 | Access to Org 2 | Permission Level |
|-------|----------------|----------------|------------------|
| Token A | Yes | Yes | Admin |
| Token B | Yes | Yes | Member |
| Token C | Yes | No | Admin |
| Token D | No | Yes | Admin |
| Token E | Yes | Yes | Read-only |
| Token F | Invalid/Expired | - | - |

### Repository Configuration Matrix
Create the following types of repositories in both organizations:

| Repo Type | In Org 1 | In Org 2 | In Personal Account |
|-----------|---------|---------|---------------------|
| Empty repo | ✓ | ✓ | ✓ |
| Public repo with content | ✓ | ✓ | ✓ |
| Private repo with content | ✓ | ✓ | ✓ |
| Repo with open issues/PRs | ✓ | - | - |
| Repo with GitHub Actions | ✓ | - | - |
| Repo with branch protection | - | ✓ | - |

## Test Automation Implementation

For automated testing with limited resources, we'll focus on:

1. **pytest** for unit and integration tests
2. **pytest-mock** for mocking GitHub API responses to simulate additional organizations or error conditions
3. **pytest-parametrize** to run the same tests with different combinations of organizations and tokens

```python
# Example test file structure
test_repo_transfer/
    test_authentication.py       # Test different token scenarios
    test_organization_validation.py  # Test org validation with different tokens
    test_repository_validation.py    # Test repo access validation
    test_single_transfer.py      # Test single repo transfers
    test_csv_transfer.py         # Test batch transfers via CSV
    test_error_handling.py       # Test error conditions
    conftest.py                  # Contains fixtures and test configuration
```

## Test Data Management

1. Create test repositories in both organizations with the configurations defined in the matrix
2. Prepare a sample CSV file with the following test cases:
   - Valid repositories from Org 1 to Org 2
   - Valid repositories from Org 2 to Org 1
   - Non-existent repositories
   - Repositories with special characters in names
   - Mix of public and private repositories
3. Store test tokens securely in environment variables or .env files (do not commit to repository)
4. Create a cleanup script to reset the test environment after each test run:

```bash
#!/bin/bash
# Example cleanup script to recreate test repositories
# Run this after a full test cycle to reset the environment

# Set your GitHub token
export GITHUB_TOKEN=your_admin_token

# Recreate test repositories in Org 1
gh repo delete org1/test-empty --yes || true
gh repo create org1/test-empty --private

gh repo delete org1/test-public --yes || true
gh repo create org1/test-public --public
# Add initial content to test-public

# Continue for all test repositories...
```

## Reporting

After each test run:
1. Generate a test report showing passed/failed tests
2. Document any issues found with detailed steps to reproduce
3. Include screenshots for UI-related issues (especially console color output)
4. Track issues in GitHub Issues for follow-up

## Conclusion

This test plan adapts to the available resources (2 organizations and a personal account) while still providing comprehensive test coverage. By creating multiple tokens with different permission levels and establishing a clear test matrix, we can efficiently validate the repository transfer tool's functionality across all critical scenarios.

The plan covers 45+ test cases across multiple categories, with a focus on the most critical operations: authentication, organization validation, and the actual transfer process. By following this test plan, you can ensure the repository transfer tool performs reliably in your environment.
