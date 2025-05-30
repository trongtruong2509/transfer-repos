# GitHub Repository Transfer Workflow Guide

This document explains how to use the repository transfer workflows to validate and execute GitHub repository transfers.

## Overview

The repository transfer system consists of two main workflows:

1. **Repository Transfer PR Validation** - Validates repository transfers in PRs
2. **Repository Transfer Comment Execution** - Executes actual transfers via PR comments

## Workflow Process

### Step 1: Create a PR with Repository Transfer Changes

1. Create a branch from `main`
2. Edit the `transfer_repos.csv` file to add repositories for transfer
3. Submit a Pull Request

### Step 2: Validate the Transfers

When a PR is created or updated, the `repo-transfer-pr.yml` workflow will:

- Run tests to validate the code
- Check that repositories exist and are accessible
- Perform a dry-run validation of the transfers
- Add a comment to the PR with validation results

### Step 3: Execute the Transfers

After validation is successful and the PR has been approved, you can:

**Option 1: Execute directly from the PR**
1. Get at least one approval on the PR
2. Comment `apply transfer` on the PR
3. The `repo-transfer-comment-execution.yml` workflow will execute the transfers
4. A comment with results will be added to the PR

**Option 2: Merge and execute later**
1. Merge the PR to `main`
2. The transfers will be ready to execute manually via the workflow dispatch

## Troubleshooting

If you encounter issues:

1. Check the workflow logs for detailed error messages
2. Verify that the GitHub token has sufficient permissions
3. Ensure repositories exist and are accessible

## Security Considerations

- Transfers require approval before execution
- The workflow uses GitHub's GITHUB_TOKEN with limited permissions
- Sensitive operations require manual approval
