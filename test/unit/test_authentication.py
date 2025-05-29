"""
Unit tests for authentication functionality in the GitHub Repository Transfer Tool.
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

class TestAuthentication:
    """Test cases for token validation and authentication."""

    @patch('requests.Session.get')
    def test_valid_token(self, mock_get, mock_successful_auth_response):
        """Test that a valid token authenticates successfully."""
        mock_get.return_value = mock_successful_auth_response
        
        transfer = GitHubRepoTransfer(token="valid-token", debug=False)
        result = transfer.validate_token()
        
        assert result is True
        assert transfer.user_login == mock_successful_auth_response.json()["login"]
        mock_get.assert_called_once_with("https://api.github.com/user")

    @patch('requests.Session.get')
    def test_invalid_token(self, mock_get, mock_failed_auth_response):
        """Test that an invalid token fails authentication."""
        mock_get.return_value = mock_failed_auth_response
        
        transfer = GitHubRepoTransfer(token="invalid-token", debug=False)
        result = transfer.validate_token()
        
        assert result is False
        assert transfer.user_login is None
        mock_get.assert_called_once_with("https://api.github.com/user")

    @patch('requests.Session.get')
    def test_expired_token(self, mock_get, mock_failed_auth_response):
        """Test that an expired token fails authentication."""
        mock_get.return_value = mock_failed_auth_response
        
        transfer = GitHubRepoTransfer(token="expired-token", debug=False)
        result = transfer.validate_token()
        
        assert result is False
        mock_get.assert_called_once_with("https://api.github.com/user")

    @patch('requests.Session.get')
    def test_network_error_during_auth(self, mock_get):
        """Test handling of network errors during authentication."""
        mock_get.side_effect = Exception("Network error")
        
        transfer = GitHubRepoTransfer(token="valid-token", debug=False)
        result = transfer.validate_token()
        
        assert result is False
        assert transfer.user_login is None
        mock_get.assert_called_once_with("https://api.github.com/user")

    @patch('os.environ.get')
    def test_missing_token_env_variable(self, mock_env_get):
        """Test handling of missing environment variable."""
        mock_env_get.return_value = None
        
        # This test needs to patch sys.exit to prevent the script from exiting
        # and sys.argv to set specific command line arguments
        with patch('sys.exit') as mock_exit, \
             patch('sys.argv', ['repo_transfer.py', '--source-org', 'test-org', '--repo-name', 'test-repo', '--dest-org', 'dest-org']):
            # We can't import main directly as it would try to run
            # So we import it within the patch context
            from repo_transfer import main
            main()
            # Check that sys.exit was called with 1
            assert mock_exit.call_count >= 1
            assert mock_exit.call_args_list[0] == ((1,),)
