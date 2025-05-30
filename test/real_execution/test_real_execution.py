"""
Real-world execution tests for the GitHub Repository Transfer Tool.

These tests perform actual repository transfers (not dry-run) using repositories
created by the setup_test_repos.sh script.

To run these tests, you need:
1. GITHUB_TOKEN environment variable with admin access to both test organizations
2. Run setup_test_repos.sh first to create the test repositories
3. Set GITHUB_TEST_REAL_EXECUTION=1 environment variable
"""
import pytest
import os
import sys
import csv
import time
import subprocess
from pathlib import Path

# Add the parent directory to path to import the module
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from repo_transfer import GitHubRepoTransfer
from test.conftest import TEST_ORG_1, TEST_ORG_2, TEST_USER, TEST_REPO_SUFFIX

# Check if we should run real execution tests
RUN_REAL_EXECUTION = os.environ.get("GITHUB_TEST_REAL_EXECUTION") == "1"

@pytest.fixture(scope="module")
def github_token():
    """Get GitHub token from environment."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token and RUN_REAL_EXECUTION:
        pytest.fail("GITHUB_TOKEN environment variable is required for real execution tests")
    return token

@pytest.fixture(scope="module")
def setup_test_repos():
    """Run setup_test_repos.sh script to create test repositories."""
    if not RUN_REAL_EXECUTION:
        return

    # Check if the script exists
    script_path = Path(__file__).parent.parent.parent / "setup_test_repos.sh"
    if not script_path.exists():
        pytest.fail(f"Setup script not found: {script_path}")

    # Make the script executable
    try:
        os.chmod(script_path, 0o755)
    except Exception as e:
        pytest.fail(f"Failed to make setup script executable: {e}")

    # Run the script without arguments to use values from .env
    print(f"Running setup script: {script_path}")
    process = subprocess.run(
        [str(script_path)],
        capture_output=True,
        text=True,
        env=os.environ.copy()  # Pass current environment variables including TEST_ORG_1, TEST_ORG_2
    )

    if process.returncode != 0:
        pytest.fail(f"Setup script failed: {process.stderr}")

    print("Setup script output:")
    print(process.stdout)

    # Give GitHub API some time to process the repository creations
    time.sleep(5)
    return True

@pytest.fixture(scope="module")
def temp_csv_file(tmp_path_factory):
    """Create a temporary CSV file for real testing."""
    if not RUN_REAL_EXECUTION:
        return None
    
    # Create a directory for CSV files
    csv_dir = tmp_path_factory.mktemp("csv_files")
    csv_path = csv_dir / "real_test_repos.csv"
    
    # Create CSV with a subset of test repos to transfer
    with open(csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["source_org", "repo_name", "dest_org"])
        writer.writerow([TEST_ORG_1, f"test-with-branches-org1-{TEST_REPO_SUFFIX}", TEST_ORG_2])
        writer.writerow([TEST_ORG_1, f"test-with-issues-org1-{TEST_REPO_SUFFIX}", TEST_ORG_2])
        writer.writerow([TEST_ORG_1, f"test-with-actions-org1-{TEST_REPO_SUFFIX}", TEST_ORG_2])
    
    return str(csv_path)

@pytest.mark.skipif(not RUN_REAL_EXECUTION, reason="Skipping real execution tests")
class TestRealExecution:
    """Tests that perform actual repository transfers."""
    
    def test_real_setup_completed(self, setup_test_repos):
        """Verify that the setup script ran successfully."""
        assert setup_test_repos is True
        
    def test_real_single_transfer(self, github_token, setup_test_repos):
        """Test transferring a single repository for real."""
        # Create the transfer instance - NOT in dry run mode
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Use the unique repository name with timestamp suffix
        repo_name = f"test-empty-org1-{TEST_REPO_SUFFIX}"
        
        # Transfer a repository from org1 to org2
        result = transfer.process_single_transfer(TEST_ORG_1, repo_name, TEST_ORG_2)
        assert result is True
        
        # Verify the repository was transferred by checking access
        # We need to wait a bit for the transfer to complete
        time.sleep(5)
        assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Transfer it back to restore the initial state
        transfer.process_single_transfer(TEST_ORG_2, repo_name, TEST_ORG_1)
        time.sleep(5)
    
    def test_real_public_repo_transfer(self, github_token, setup_test_repos):
        """Test transferring a public repository for real."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Use the unique repository name with timestamp suffix
        repo_name = f"test-public-org1-{TEST_REPO_SUFFIX}"
        
        # Transfer a public repository from org1 to org2
        result = transfer.process_single_transfer(TEST_ORG_1, repo_name, TEST_ORG_2)
        assert result is True
        
        # Verify the repository was transferred
        time.sleep(5)
        assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Transfer it back
        transfer.process_single_transfer(TEST_ORG_2, repo_name, TEST_ORG_1)
        time.sleep(5)
    
    def test_real_private_repo_transfer(self, github_token, setup_test_repos):
        """Test transferring a private repository for real."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Use the unique repository name with timestamp suffix
        repo_name = f"test-private-org1-{TEST_REPO_SUFFIX}"
        
        # Transfer a private repository from org1 to org2
        result = transfer.process_single_transfer(TEST_ORG_1, repo_name, TEST_ORG_2)
        assert result is True
        
        # Verify the repository was transferred
        time.sleep(5)
        assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Transfer it back
        transfer.process_single_transfer(TEST_ORG_2, repo_name, TEST_ORG_1)
        time.sleep(5)
    
    def test_real_repo_with_branches_transfer(self, github_token, setup_test_repos):
        """Test transferring a repository with multiple branches."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Use the unique repository name with timestamp suffix
        repo_name = f"test-with-branches-org1-{TEST_REPO_SUFFIX}"
        
        # Transfer repository with branches from org1 to org2
        result = transfer.process_single_transfer(TEST_ORG_1, repo_name, TEST_ORG_2)
        assert result is True
        
        # Verify the repository was transferred
        time.sleep(5)
        assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Transfer it back
        transfer.process_single_transfer(TEST_ORG_2, repo_name, TEST_ORG_1)
        time.sleep(5)
    
    def test_real_repo_with_issues_transfer(self, github_token, setup_test_repos):
        """Test transferring a repository with issues."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Use the unique repository name with timestamp suffix
        repo_name = f"test-with-issues-org1-{TEST_REPO_SUFFIX}"
        
        # Transfer repository with issues from org1 to org2
        result = transfer.process_single_transfer(TEST_ORG_1, repo_name, TEST_ORG_2)
        assert result is True
        
        # Verify the repository was transferred
        time.sleep(5)
        assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Transfer it back
        transfer.process_single_transfer(TEST_ORG_2, repo_name, TEST_ORG_1)
        time.sleep(5)
    
    def test_real_repo_with_actions_transfer(self, github_token, setup_test_repos):
        """Test transferring a repository with GitHub Actions."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Use the unique repository name with timestamp suffix
        repo_name = f"test-with-actions-org1-{TEST_REPO_SUFFIX}"
        
        # Transfer repository with GitHub Actions from org1 to org2
        result = transfer.process_single_transfer(TEST_ORG_1, repo_name, TEST_ORG_2)
        assert result is True
        
        # Verify the repository was transferred
        time.sleep(5)
        assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Transfer it back
        transfer.process_single_transfer(TEST_ORG_2, repo_name, TEST_ORG_1)
        time.sleep(5)
    
    def test_real_csv_batch_transfer(self, github_token, setup_test_repos, temp_csv_file):
        """Test transferring multiple repositories using a CSV file."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Create a list of repositories with unique names
        repo_names = [
            f"test-with-branches-org1-{TEST_REPO_SUFFIX}",
            f"test-with-issues-org1-{TEST_REPO_SUFFIX}",
            f"test-with-actions-org1-{TEST_REPO_SUFFIX}"
        ]
        
        # Process the CSV file
        successful, total = transfer.process_csv_file(temp_csv_file)
        
        # Verify all transfers were successful
        assert successful == 3
        assert total == 3
        
        # Wait for transfers to complete
        time.sleep(10)
        
        # Verify the repositories were transferred
        for repo_name in repo_names:
            assert transfer.validate_repo_access(TEST_ORG_2, repo_name) is True
        
        # Create a CSV to transfer repositories back
        reverse_csv_path = Path(temp_csv_file).parent / "reverse_transfer.csv"
        with open(reverse_csv_path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["source_org", "repo_name", "dest_org"])
            for repo_name in repo_names:
                writer.writerow([TEST_ORG_2, repo_name, TEST_ORG_1])
        
        # Transfer them back
        successful, total = transfer.process_csv_file(str(reverse_csv_path))
        assert successful == 3
        assert total == 3
        
        # Wait for transfers to complete
        time.sleep(10)
        
        # Verify they were transferred back
        for repo_name in repo_names:
            assert transfer.validate_repo_access(TEST_ORG_1, repo_name) is True

    def test_real_error_handling_nonexistent_repo(self, github_token):
        """Test handling of transfers with nonexistent repositories."""
        transfer = GitHubRepoTransfer(token=github_token, debug=True, dry_run=False)
        
        # Try to transfer a nonexistent repository
        result = transfer.process_single_transfer(TEST_ORG_1, "nonexistent-repo", TEST_ORG_2)
        
        # Should fail gracefully
        assert result is False
