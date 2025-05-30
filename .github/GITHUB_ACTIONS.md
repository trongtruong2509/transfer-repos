# GitHub Actions Integration Guide

This document provides detailed information about the GitHub Actions workflow for the Repository Transfer Tool.

## Overview

The GitHub Actions workflow automates the process of validating and testing repository transfers through pull requests. The workflow consists of two main jobs:

1. **Test Job**: Runs unit and integration tests to ensure the tool is working correctly
2. **Dry-Run Job**: Performs a simulated transfer (dry-run) of repositories listed in the `transfer_repos.csv` file

## Workflow Trigger

The workflow is triggered when:
- A pull request is opened, synchronized, or reopened to the `main` branch
- The changes don't only affect markdown files or the `.gitignore` file

## Required Secrets

You must configure the following secrets in your GitHub repository settings:

| Secret Name | Description |
|-------------|-------------|
| `GITHUB_TOKEN_ADMIN` | GitHub token with admin access to organizations |
| `GITHUB_TOKEN_MEMBER` | GitHub token with member access (for testing) |
| `GITHUB_TOKEN_READONLY` | GitHub token with read-only access (for testing) |
| `GITHUB_TOKEN_ORG1` | Token for source organization |
| `GITHUB_TOKEN_ORG2` | Token for destination organization |

## Required Variables

You should also configure these variables in your GitHub repository settings:

| Variable Name | Description |
|---------------|-------------|
| `TEST_ORG_1` | Name of the first test organization |
| `TEST_ORG_2` | Name of the second test organization |
| `TEST_USER` | GitHub username for testing |
| `TEST_REPO_SUFFIX` | Suffix for test repositories (optional) |
| `TEST_REPO` | Name of the test repository (optional) |

## Workflow Jobs

### Test Job

The test job performs the following steps:
1. Checks out the code from the repository
2. Sets up Python 3.12
3. Installs dependencies from `requirements.txt` and testing libraries
4. Configures environment variables using repository secrets and variables
5. Runs unit tests in the `test/unit/` directory
6. Runs integration tests in the `test/integration/` directory

### Dry-Run Job

If the tests pass, the dry-run job performs these steps:
1. Checks out the code from the repository
2. Sets up Python 3.12
3. Installs dependencies from `requirements.txt`
4. Runs the repository transfer tool in dry-run mode with the repositories listed in `transfer_repos.csv`
5. Uploads the dry-run logs as an artifact for review

## Artifacts

The workflow generates and uploads the following artifacts:
- **repo-transfer-logs**: Contains the dry-run logs for the repository transfers

## Local Testing

To test the workflow locally before creating a pull request:

1. Install [act](https://github.com/nektos/act) to run GitHub Actions locally
2. Create a `.secrets` file with your GitHub tokens
3. Run the workflow locally:
   ```bash
   act pull_request -s GITHUB_TOKEN_ADMIN=your_token -s GITHUB_TOKEN_MEMBER=your_token ...
   ```

## Customizing the Workflow

You can customize the workflow by editing the `.github/workflows/repo-transfer-pr.yml` file. Common customizations include:
- Changing the trigger events
- Adding more tests or validation steps
- Configuring notifications for workflow results
- Adding approval steps before actual transfers

## Security Considerations

- GitHub tokens should have the minimum required permissions
- Never store tokens directly in the workflow file
- Consider using GitHub's OIDC provider for more secure token handling
