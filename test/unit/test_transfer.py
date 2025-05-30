"""
Unit tests for repository transfer functionality in the GitHub Repository Transfer Tool.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os
from pathlib import Path

# Add the parent directory to path to import the module
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from repo_transfer import GitHubRepoTransfer
from test.conftest import TEST_ORG_1, TEST_ORG_2, TEST_REPO, TEST_USER

class TestRepositoryTransfer:
    """Test cases for repository transfer functionality."""

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_successful_transfer(self, mock_get, mock_post, mock_org_success_response, 
                               mock_repo_success_response, mock_transfer_success_response,
                               mock_membership_admin_response):
        """Test successful repository transfer."""
        # Set up successful responses for all API calls in the transfer process
        mock_get.side_effect = [
            mock_org_success_response,   # First org validation
            mock_membership_admin_response,  # First org membership
            mock_org_success_response,   # Second org validation
            mock_membership_admin_response,  # Second org membership
            mock_repo_success_response   # Repo validation
        ]
        mock_post.return_value = mock_transfer_success_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        result = transfer.transfer_repository(TEST_ORG_1, TEST_REPO, TEST_ORG_2)
        
        assert result is True
        assert mock_get.call_count == 5
        mock_post.assert_called_once_with(
            f"https://api.github.com/repos/{TEST_ORG_1}/{TEST_REPO}/transfer",
            json={"new_owner": TEST_ORG_2}
        )

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_transfer_failed_api_error(self, mock_get, mock_post, mock_org_success_response, 
                                     mock_repo_success_response, mock_transfer_failed_response,
                                     mock_membership_admin_response):
        """Test failed repository transfer due to API error."""
        # Set up successful responses for validation but failed transfer
        mock_get.side_effect = [
            mock_org_success_response,   # First org validation
            mock_membership_admin_response,  # First org membership
            mock_org_success_response,   # Second org validation
            mock_membership_admin_response,  # Second org membership
            mock_repo_success_response   # Repo validation
        ]
        mock_post.return_value = mock_transfer_failed_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        result = transfer.transfer_repository(TEST_ORG_1, TEST_REPO, TEST_ORG_2)
        
        assert result is False
        assert mock_get.call_count == 5
        mock_post.assert_called_once()

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_transfer_with_insufficient_permissions(self, mock_get, mock_post, mock_org_success_response, 
                                                 mock_repo_success_response, 
                                                 mock_membership_member_response):
        """Test transfer with insufficient permissions."""
        # Set up responses for validation with member (not admin) permissions
        mock_get.side_effect = [
            mock_org_success_response,   # First org validation
            mock_membership_member_response,  # First org membership - only member, not admin
            mock_org_success_response,   # Second org validation
            mock_membership_member_response,  # Second org membership - only member, not admin
            mock_repo_success_response   # Repo validation
        ]
        
        # GitHub will return a 403 when trying to transfer without admin permissions
        mock_failed_response = MagicMock()
        mock_failed_response.status_code = 403
        mock_failed_response.text = "You need admin access to transfer this repository"
        mock_post.return_value = mock_failed_response
        
        transfer = GitHubRepoTransfer(token="member-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        result = transfer.transfer_repository(TEST_ORG_1, TEST_REPO, TEST_ORG_2)
        
        assert result is False
        assert mock_get.call_count == 5
        mock_post.assert_called_once()

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_transfer_with_network_error(self, mock_get, mock_post, mock_org_success_response, 
                                       mock_repo_success_response, 
                                       mock_membership_admin_response):
        """Test transfer with network error during transfer."""
        # Set up successful responses for validation but network error during transfer
        mock_get.side_effect = [
            mock_org_success_response,   # First org validation
            mock_membership_admin_response,  # First org membership
            mock_org_success_response,   # Second org validation
            mock_membership_admin_response,  # Second org membership
            mock_repo_success_response   # Repo validation
        ]
        mock_post.side_effect = Exception("Network error during transfer")
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        # Override retry parameters to speed up the test
        result = transfer.transfer_repository(TEST_ORG_1, TEST_REPO, TEST_ORG_2, max_retries=1, retry_delay=1)
        
        assert result is False
        assert mock_get.call_count == 5
        
        # With the new retry logic, post will be called up to max_retries times
        assert mock_post.call_count == 1

    @patch('requests.Session.post')
    def test_dry_run_transfer(self, mock_post):
        """Test dry run mode doesn't perform actual transfer."""
        # Create transfer object with dry_run=True
        transfer = GitHubRepoTransfer(token="admin-token", debug=False, dry_run=True)
        transfer._validation_done = True  # Skip validation for this test
        
        result = transfer.transfer_repository(TEST_ORG_1, TEST_REPO, TEST_ORG_2)
        
        # In dry-run mode, the transfer should be "successful" but no API call should be made
        assert result is True
        mock_post.assert_not_called()

    def test_missing_parameters(self):
        """Test transfer with missing parameters."""
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        
        # Test with missing source org
        result = transfer.transfer_repository("", TEST_REPO, TEST_ORG_2)
        assert result is False
        
        # Test with missing repo name
        result = transfer.transfer_repository(TEST_ORG_1, "", TEST_ORG_2)
        assert result is False
        
        # Test with missing destination org
        result = transfer.transfer_repository(TEST_ORG_1, TEST_REPO, "")
        assert result is False
