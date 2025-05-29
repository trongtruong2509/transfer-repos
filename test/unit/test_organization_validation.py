"""
Unit tests for organization validation in the GitHub Repository Transfer Tool.
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
from test.conftest import TEST_ORG_1, TEST_ORG_2, TEST_USER

class TestOrganizationValidation:
    """Test cases for organization validation."""

    @patch('requests.Session.get')
    def test_valid_org_admin_access(self, mock_get, mock_org_success_response, mock_membership_admin_response):
        """Test validation of organization with admin access."""
        # Set up the response sequence for the org and membership checks
        mock_get.side_effect = [mock_org_success_response, mock_membership_admin_response]
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        result = transfer.validate_org_access(TEST_ORG_1)
        
        assert result is True
        assert mock_get.call_count == 2
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_1}")
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_1}/memberships/{TEST_USER}")

    @patch('requests.Session.get')
    def test_valid_org_member_access(self, mock_get, mock_org_success_response, mock_membership_member_response):
        """Test validation of organization with member access."""
        # Set up the response sequence for the org and membership checks
        mock_get.side_effect = [mock_org_success_response, mock_membership_member_response]
        
        transfer = GitHubRepoTransfer(token="member-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        result = transfer.validate_org_access(TEST_ORG_1)
        
        assert result is True
        assert mock_get.call_count == 2
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_1}")
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_1}/memberships/{TEST_USER}")

    @patch('requests.Session.get')
    def test_org_not_found(self, mock_get, mock_org_not_found_response):
        """Test validation of non-existent organization."""
        mock_get.return_value = mock_org_not_found_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_org_access("non-existent-org")
        
        assert result is False
        mock_get.assert_called_once_with("https://api.github.com/orgs/non-existent-org")

    @patch('requests.Session.get')
    def test_user_not_org_member(self, mock_get, mock_org_success_response, mock_membership_not_found_response):
        """Test validation when user is not a member of the organization."""
        # Set up the response sequence for the org and membership checks
        mock_get.side_effect = [mock_org_success_response, mock_membership_not_found_response]
        
        transfer = GitHubRepoTransfer(token="non-member-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        result = transfer.validate_org_access(TEST_ORG_1)
        
        assert result is False
        assert mock_get.call_count == 2
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_1}")
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_1}/memberships/{TEST_USER}")

    @patch('requests.Session.get')
    def test_user_account_not_org(self, mock_get, mock_user_account_response):
        """Test validation when providing a user account instead of an organization."""
        mock_get.return_value = mock_user_account_response
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_org_access(TEST_USER)
        
        assert result is False
        mock_get.assert_called_once_with(f"https://api.github.com/orgs/{TEST_USER}")

    @patch('requests.Session.get')
    def test_network_error_during_org_validation(self, mock_get):
        """Test handling of network errors during organization validation."""
        mock_get.side_effect = Exception("Network error")
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        result = transfer.validate_org_access(TEST_ORG_1)
        
        assert result is False
        mock_get.assert_called_once_with(f"https://api.github.com/orgs/{TEST_ORG_1}")

    @patch('requests.Session.get')
    def test_token_without_org_access(self, mock_get, mock_org_success_response, mock_membership_not_found_response):
        """Test validation with a token that doesn't have access to the organization."""
        # Set up the response sequence for the org and membership checks
        mock_get.side_effect = [mock_org_success_response, mock_membership_not_found_response]
        
        transfer = GitHubRepoTransfer(token="org1-only-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        result = transfer.validate_org_access(TEST_ORG_2)
        
        assert result is False
        assert mock_get.call_count == 2
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_2}")
        mock_get.assert_any_call(f"https://api.github.com/orgs/{TEST_ORG_2}/memberships/{TEST_USER}")
