"""
Unit tests for retry logic in the GitHub Repository Transfer Tool.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os
import json
from pathlib import Path

# Add the parent directory to path to import the module
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from repo_transfer import GitHubRepoTransfer
from test.conftest import TEST_ORG_1, TEST_ORG_2, TEST_REPO, TEST_USER

class TestRetryLogic:
    """Test cases for retry logic functionality."""

    @patch('requests.Session.post')
    def test_retry_on_operation_in_progress(self, mock_post, mock_sleep):
        """Test retry logic when a 'previous operation in progress' error occurs."""
        # Create a mock response for the "operation in progress" error
        operation_in_progress_response = MagicMock()
        operation_in_progress_response.status_code = 422
        operation_in_progress_response.text = json.dumps({
            "message": "Validation Failed",
            "errors": [
                {
                    "resource": "Repository",
                    "code": "unprocessable",
                    "field": "data",
                    "message": "Failed to transfer repository. A previous repository operation is still in progress."
                }
            ],
            "documentation_url": "https://docs.github.com/rest/repos/repos#transfer-a-repository",
            "status": "422"
        })
        
        # Create a successful response for the final attempt
        success_response = MagicMock()
        success_response.status_code = 202
        success_response.json.return_value = {"name": TEST_REPO, "full_name": f"{TEST_ORG_2}/{TEST_REPO}"}
        
        # Set up post to fail with "operation in progress" twice, then succeed
        mock_post.side_effect = [
            operation_in_progress_response,  # First attempt
            operation_in_progress_response,  # Second attempt
            success_response                  # Third attempt
        ]
        
        # Create transfer object and skip validation
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer._validation_done = True  # Skip validation for this test
        
        # Call the method with retry parameters
        result = transfer.transfer_repository(
            TEST_ORG_1, TEST_REPO, TEST_ORG_2, 
            max_retries=3, retry_delay=10
        )
        
        # Verify the result and call counts
        assert result is True
        assert mock_post.call_count == 3
        
        # Verify sleep was called with the right delay
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([call(10), call(10)])

    @patch('requests.Session.post')
    def test_no_retry_on_other_errors(self, mock_post, mock_sleep):
        """Test that retry doesn't happen for other types of errors."""
        # Create a mock response for a permission error
        permission_error_response = MagicMock()
        permission_error_response.status_code = 403
        permission_error_response.text = "You need admin access to transfer this repository"
        
        # Set up post to fail with permission error
        mock_post.return_value = permission_error_response
        
        # Create transfer object and skip validation
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer._validation_done = True  # Skip validation for this test
        
        # Call the method with retry parameters
        result = transfer.transfer_repository(
            TEST_ORG_1, TEST_REPO, TEST_ORG_2, 
            max_retries=3, retry_delay=10
        )
        
        # Verify the result and call counts
        assert result is False
        assert mock_post.call_count == 1
        
        # Verify sleep was not called
        assert mock_sleep.call_count == 0

    @patch('requests.Session.post')
    def test_retry_limit_reached(self, mock_post, mock_sleep):
        """Test behavior when retry limit is reached."""
        # Create a mock response for the "operation in progress" error
        operation_in_progress_response = MagicMock()
        operation_in_progress_response.status_code = 422
        operation_in_progress_response.text = json.dumps({
            "message": "Validation Failed",
            "errors": [
                {
                    "resource": "Repository",
                    "code": "unprocessable",
                    "field": "data",
                    "message": "Failed to transfer repository. A previous repository operation is still in progress."
                }
            ],
            "documentation_url": "https://docs.github.com/rest/repos/repos#transfer-a-repository",
            "status": "422"
        })
        
        # Set up post to always fail with "operation in progress"
        mock_post.return_value = operation_in_progress_response
        
        # Create transfer object and skip validation
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer._validation_done = True  # Skip validation for this test
        
        # Call the method with limited retries
        result = transfer.transfer_repository(
            TEST_ORG_1, TEST_REPO, TEST_ORG_2, 
            max_retries=2, retry_delay=5
        )
        
        # Verify the result and call counts
        assert result is False
        assert mock_post.call_count == 2  # Initial try + 1 retry
        
        # Verify sleep was called once
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_once_with(5)

    @patch('requests.Session.post')
    def test_retry_on_exception(self, mock_post, mock_sleep):
        """Test retry logic when an exception occurs during the API call."""
        # Set up post to raise an exception, then succeed
        success_response = MagicMock()
        success_response.status_code = 202
        success_response.json.return_value = {"name": TEST_REPO, "full_name": f"{TEST_ORG_2}/{TEST_REPO}"}
        
        mock_post.side_effect = [
            Exception("Network error"),  # First attempt fails
            success_response             # Second attempt succeeds
        ]
        
        # Create transfer object and skip validation
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer._validation_done = True  # Skip validation for this test
        
        # Call the method with retry parameters
        result = transfer.transfer_repository(
            TEST_ORG_1, TEST_REPO, TEST_ORG_2, 
            max_retries=3, retry_delay=5
        )
        
        # Verify the result and call counts
        assert result is True
        assert mock_post.call_count == 2
        
        # Verify sleep was called
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_once_with(5)

    def test_no_retries_in_dry_run(self, mock_sleep):
        """Test that no retries happen in dry-run mode."""
        # Create transfer object with dry_run=True
        transfer = GitHubRepoTransfer(token="admin-token", debug=False, dry_run=True)
        transfer._validation_done = True  # Skip validation for this test
        
        # Call the method with retry parameters
        result = transfer.transfer_repository(
            TEST_ORG_1, TEST_REPO, TEST_ORG_2, 
            max_retries=3, retry_delay=5
        )
        
        # Verify the result and that no sleep was called
        assert result is True
        assert mock_sleep.call_count == 0
