# Environment Configuration

The GitHub Repository Transfer Tool supports configuration through environment variables and a `.env` file. This approach offers flexibility and security for managing sensitive information like API tokens.

## Using the .env File

A template `.env.template` file is provided. To get started:

1. Copy the template to create your `.env` file:
   ```bash
   cp .env.template .env
   ```

2. Edit the `.env` file with your specific settings:
   ```bash
   nano .env  # or use any text editor
   ```

## Available Configuration Variables

The following environment variables can be set:

| Variable | Description | Required For |
|----------|-------------|------------|
| `GITHUB_TOKEN` | Your GitHub Personal Access Token | All operations |
| `TEST_ORG_1` | First organization name for testing | Real execution tests |
| `TEST_ORG_2` | Second organization name for testing | Real execution tests |
| `TEST_USER` | Your GitHub username | Real execution tests |
| `TEST_REPO` | Repository name used in tests | Real execution tests |
| `GITHUB_TEST_INTEGRATION` | Set to "1" to enable real API integration tests | Integration tests |
| `GITHUB_TEST_REAL_EXECUTION` | Set to "1" to enable actual repository transfers | Real execution tests |

## Automatic Configuration

The `setup_test_repos.sh` script can automatically update your `.env` file with the correct values:

```bash
./setup_test_repos.sh
```

When run without parameters, the script will:
1. Use values from your existing `.env` file if present
2. Ask for your GitHub token if not already set
3. Detect your GitHub username
4. Offer to save all values back to the `.env` file

## Manual Environment Variables

Instead of using a `.env` file, you can also set the variables directly in your shell:

```bash
export GITHUB_TOKEN=your_token_here
export TEST_ORG_1=your_first_org
export TEST_ORG_2=your_second_org
export TEST_USER=your_username
./run_tests.sh -r
```

This method is useful for CI/CD environments or when you don't want to create a `.env` file.
