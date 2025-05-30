# GitHub Actions Repository Transfer

This directory contains GitHub Actions workflows for automating repository transfers between GitHub organizations.

## Available Workflows

1. **Repository Transfer PR Workflow** (`repo-transfer-pr.yml`)
   - Triggered on pull requests to the `main` branch
   - Runs tests and performs a dry-run of repository transfers
   - Uses `transfer_repos.csv` as input

2. **Repository Transfer Production Workflow** (`repo-transfer-production.yml`)
   - Triggered when changes to `transfer_repos.csv` are merged to `main`
   - Performs actual repository transfers after manual approval
   - Uploads transfer logs as artifacts

## Required Secrets

Configure these secrets in your GitHub repository settings:

| Secret Name | Description |
|-------------|-------------|
| `GITHUB_TOKEN_ADMIN` | GitHub token with admin access to organizations |
| `GITHUB_TOKEN_MEMBER` | GitHub token with member access (for testing) |
| `GITHUB_TOKEN_READONLY` | GitHub token with read-only access (for testing) |
| `GITHUB_TOKEN_ORG1` | Token for source organization |
| `GITHUB_TOKEN_ORG2` | Token for destination organization |

## Required Variables

Configure these variables in your GitHub repository settings:

| Variable Name | Description |
|---------------|-------------|
| `TEST_ORG_1` | Name of the first test organization |
| `TEST_ORG_2` | Name of the second test organization |
| `TEST_USER` | GitHub username for testing |
| `TRANSFER_APPROVERS` | Comma-separated list of GitHub usernames who can approve transfers |

## Workflow Process

### Pull Request Workflow

1. Developer creates a PR with changes to `transfer_repos.csv`
2. GitHub Actions runs unit and integration tests
3. If tests pass, a dry-run of transfers is performed
4. Logs are uploaded as artifacts for review

### Production Workflow

1. PR is merged to `main`
2. GitHub Actions runs a final dry-run verification
3. A manual approval is required before proceeding
4. After approval, actual transfers are executed
5. Logs are uploaded as artifacts

## Security Considerations

- GitHub tokens should have the minimum required permissions
- Manual approval step ensures transfers are intentional
- All actions are logged for audit purposes

## Customization

To customize these workflows, edit the YAML files in this directory or modify the `.github/workflow.config` file.
