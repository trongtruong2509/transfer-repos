"""
Unit tests for repository validation in the GitHub Repository Transfer Tool.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add the parent directory to path to import the module
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from repo_transfer import GitHubRepoTransfer
from test.conftest import TEST_ORG_1, TEST_ORG_2, TEST_REPO

class TestRepositoryValidation:
    """Test cases for repository validation."""

    @patch('requests.Session.get')
    def test_valid_repo(self, mock_get, mock_repo_success_response):
        """Test validation of existing repository with correct owner."""
        mock_get.return_value = mock_repo_success_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_repo_access(TEST_ORG_1, TEST_REPO)
        
        assert result is True
        mock_get.assert_called_once_with(f"https://api.github.com/repos/{TEST_ORG_1}/{TEST_REPO}")

    @patch('requests.Session.get')
    def test_repo_not_found(self, mock_get, mock_repo_not_found_response):
        """Test validation of non-existent repository."""
        mock_get.return_value = mock_repo_not_found_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_repo_access(TEST_ORG_1, "non-existent-repo")
        
        assert result is False
        mock_get.assert_called_once_with(f"https://api.github.com/repos/{TEST_ORG_1}/non-existent-repo")

    @patch('requests.Session.get')
    def test_repo_wrong_owner(self, mock_get, mock_repo_wrong_owner_response):
        """Test validation of a repository owned by a different org than expected."""
        mock_get.return_value = mock_repo_wrong_owner_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_repo_access(TEST_ORG_1, TEST_REPO)
        
        assert result is False
        mock_get.assert_called_once_with(f"https://api.github.com/repos/{TEST_ORG_1}/{TEST_REPO}")

    @patch('requests.Session.get')
    def test_network_error_during_repo_validation(self, mock_get):
        """Test handling of network errors during repository validation."""
        mock_get.side_effect = Exception("Network error")
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_repo_access(TEST_ORG_1, TEST_REPO)
        
        assert result is False
        mock_get.assert_called_once_with(f"https://api.github.com/repos/{TEST_ORG_1}/{TEST_REPO}")

    @patch('requests.Session.get')
    def test_insufficient_permissions_for_repo(self, mock_get):
        """Test handling of insufficient permissions to access a repository."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Resource not accessible by integration"
        mock_get.return_value = mock_response
        
        transfer = GitHubRepoTransfer(token="readonly-token", debug=False)
        result = transfer.validate_repo_access(TEST_ORG_1, "private-repo")
        
        assert result is False
        mock_get.assert_called_once_with(f"https://api.github.com/repos/{TEST_ORG_1}/private-repo")
