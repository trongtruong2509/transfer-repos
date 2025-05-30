# Repository Transfer Workflow Guide

This guide explains how to use the Repository Transfer Tool with GitHub Actions to automate repository transfers between GitHub organizations.

## Prerequisites

Before you begin, ensure you have:

1. Admin access to both source and destination GitHub organizations
2. Proper GitHub tokens with required permissions
3. The necessary GitHub secrets and variables configured in the repository settings

## Workflow Overview

The Repository Transfer Tool is integrated with GitHub Actions to provide an automated workflow:

1. Create a PR with changes to `transfer_repos.csv`
2. GitHub Actions runs tests automatically
3. If tests pass, a dry-run of the transfers is performed
4. Review the dry-run logs in the workflow artifacts
5. After merging the PR, you can manually run the actual transfers

## Step 1: Configure GitHub Secrets and Variables

Go to your repository settings and configure the following:

### Secrets
- `GITHUB_TOKEN_ADMIN`: GitHub token with admin access to organizations
- `GITHUB_TOKEN_MEMBER`: GitHub token with member access
- `GITHUB_TOKEN_READONLY`: GitHub token with read-only access
- `GITHUB_TOKEN_ORG1`: Token for source organization
- `GITHUB_TOKEN_ORG2`: Token for destination organization

### Variables
- `TEST_ORG_1`: Name of the first test organization
- `TEST_ORG_2`: Name of the second test organization
- `TEST_USER`: GitHub username for testing
- `TEST_REPO_SUFFIX`: Suffix for test repositories (optional)
- `TEST_REPO`: Name of the test repository (optional)

## Step 2: Prepare the Transfer CSV

Edit the `transfer_repos.csv` file to list the repositories you want to transfer. The file must have the following format:

```csv
source_org,repo_name,dest_org
nova-iris,test-repo-1,baohtruong
nova-iris,test-repo-2,baohtruong
baohtruong,test-repo-3,nova-iris
```

## Step 3: Create a Pull Request

1. Create a new branch
2. Update the `transfer_repos.csv` file with your transfer list
3. Commit and push your changes
4. Create a pull request to the `main` branch
5. Fill in the PR template with details about your transfer request

## Step 4: Review the Workflow Results

After creating the PR, GitHub Actions will automatically:

1. Run tests to verify the tool is working correctly
2. Validate the CSV format and check if all repositories exist
3. Perform a dry-run of the transfers if validation passes
4. Upload the dry-run logs as artifacts
5. Add a detailed comment to the PR with validation and dry-run results

Review the workflow results, validation outputs, and the dry-run logs to ensure everything is correct.

## Step 5: Merge the PR and Run Actual Transfers

If the dry-run looks good:

1. Merge the PR
2. Run the actual transfers using one of these methods:
   - Manually through the command line
   - Create a new workflow dispatch event to trigger the transfers

## Manual Transfer Command

To manually run the actual transfers after the PR is merged:

```bash
# First, clone the repository if you don't have it locally
git clone https://github.com/your-org/your-repo.git
cd your-repo

# Make sure you have the latest changes
git pull

# Set your GitHub token
export GITHUB_TOKEN=your_github_token

# Run the transfer
python repo_transfer.py --csv transfer_repos.csv --auto-approve
```

## Troubleshooting

If you encounter issues:

1. Check the workflow logs for error messages
2. Verify that your GitHub tokens have the necessary permissions
3. Ensure all repositories exist in their source organizations
4. Confirm you have admin access to both source and destination organizations

For more detailed information, refer to the [GitHub Actions documentation](.github/GITHUB_ACTIONS.md) and the [README.md](README.md) file.
