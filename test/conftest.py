"""
Shared fixtures and configurations for the GitHub Repository Transfer Tool tests.
"""
import os
import pytest
import requests
from unittest.mock import MagicMock, patch
import logging
import sys

# Constants for testing
TEST_ORG_1 = "nova-iris"  # Replace with your actual first org name
TEST_ORG_2 = "baohtruong"  # Replace with your actual second org name
TEST_USER = "trongtruong2509"  # Replace with your GitHub username
TEST_REPO = "example-repo-2"  # Replace with a test repository name

# Skip all logging tests by default
def pytest_collection_modifyitems(items):
    """Skip all test_logging.py tests by default."""
    for item in items:
        if "test_logging" in item.nodeid:
            item.add_marker(pytest.mark.skip(reason="Logging tests disabled by default"))

# Create token fixtures with different permission levels
@pytest.fixture
def admin_token():
    """Token with admin access to both organizations."""
    return os.environ.get("GITHUB_TOKEN_ADMIN", "mock-admin-token")

@pytest.fixture
def member_token():
    """Token with member access to both organizations."""
    return os.environ.get("GITHUB_TOKEN_MEMBER", "mock-member-token")

@pytest.fixture
def readonly_token():
    """Token with read-only access to both organizations."""
    return os.environ.get("GITHUB_TOKEN_READONLY", "mock-readonly-token")

@pytest.fixture
def org1_only_token():
    """Token with access only to org1."""
    return os.environ.get("GITHUB_TOKEN_ORG1", "mock-org1-token")

@pytest.fixture
def org2_only_token():
    """Token with access only to org2."""
    return os.environ.get("GITHUB_TOKEN_ORG2", "mock-org2-token")

@pytest.fixture
def invalid_token():
    """Invalid token for testing authentication failures."""
    return "invalid-token"

# Mocked API responses
@pytest.fixture
def mock_successful_auth_response():
    """Mock a successful authentication response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": TEST_USER}
    return mock_response

@pytest.fixture
def mock_failed_auth_response():
    """Mock a failed authentication response."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Bad credentials"
    return mock_response

@pytest.fixture
def mock_org_success_response():
    """Mock a successful organization response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": TEST_ORG_1, "type": "Organization"}
    return mock_response

@pytest.fixture
def mock_org_not_found_response():
    """Mock a not found organization response."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    return mock_response

@pytest.fixture
def mock_user_account_response():
    """Mock a user account (not organization) response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": TEST_USER, "type": "User"}
    return mock_response

@pytest.fixture
def mock_repo_success_response():
    """Mock a successful repository response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": TEST_REPO, "full_name": f"{TEST_ORG_1}/{TEST_REPO}"}
    return mock_response

@pytest.fixture
def mock_repo_not_found_response():
    """Mock a not found repository response."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    return mock_response

@pytest.fixture
def mock_transfer_success_response():
    """Mock a successful transfer response."""
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {"name": TEST_REPO, "full_name": f"{TEST_ORG_2}/{TEST_REPO}"}
    return mock_response

@pytest.fixture
def mock_transfer_failed_response():
    """Mock a failed transfer response."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "You need admin access to transfer this repository"
    return mock_response

@pytest.fixture
def mock_membership_admin_response():
    """Mock an admin membership response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"role": "admin", "state": "active"}
    return mock_response

@pytest.fixture
def mock_membership_member_response():
    """Mock a member membership response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"role": "member", "state": "active"}
    return mock_response

@pytest.fixture
def mock_membership_not_found_response():
    """Mock a not found membership response."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    return mock_response

# Create a sample CSV file for testing
@pytest.fixture
def sample_csv_path(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = "source_org,repo_name,dest_org\n"
    csv_content += f"{TEST_ORG_1},repo-1,{TEST_ORG_2}\n"
    csv_content += f"{TEST_ORG_1},repo-2,{TEST_ORG_2}\n"
    csv_content += f"{TEST_ORG_2},repo-3,{TEST_ORG_1}\n"
    csv_content += f"nonexistent-org,repo-4,{TEST_ORG_2}\n"
    csv_content += f"{TEST_ORG_1},nonexistent-repo,{TEST_ORG_2}\n"
    
    csv_file = tmp_path / "test_repos.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)

@pytest.fixture
def invalid_csv_path(tmp_path):
    """Create an invalid CSV file for testing."""
    csv_content = "source,repository,destination\n"  # Wrong column names
    csv_content += f"{TEST_ORG_1},repo-1,{TEST_ORG_2}\n"
    
    csv_file = tmp_path / "invalid_test_repos.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)

@pytest.fixture
def empty_csv_path(tmp_path):
    """Create an empty CSV file for testing."""
    csv_content = "source_org,repo_name,dest_org\n"  # Headers only
    
    csv_file = tmp_path / "empty_test_repos.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)

# Disable actual logging during tests
@pytest.fixture(autouse=True)
def disable_logging():
    """Disable logging during tests."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
