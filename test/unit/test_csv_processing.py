"""
Unit tests for CSV file processing in the GitHub Repository Transfer Tool.
"""
import pytest
import os
from unittest.mock import patch, MagicMock, call
import sys
from pathlib import Path

# Add the parent directory to path to import the module
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from repo_transfer import GitHubRepoTransfer
from test.conftest import TEST_ORG_1, TEST_ORG_2, TEST_USER

class TestCSVProcessing:
    """Test cases for CSV file processing."""

    @patch.object(GitHubRepoTransfer, 'transfer_repository')
    @patch.object(GitHubRepoTransfer, 'validate_token')
    def test_valid_csv_processing(self, mock_validate_token, mock_transfer, sample_csv_path):
        """Test processing of a valid CSV file."""
        # Set up successful token validation
        mock_validate_token.return_value = True
        
        # Set up successful transfers for the first 3 repos and failed for the last 2
        mock_transfer.side_effect = [True, True, True, False, False]
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        successful, total = transfer.process_csv_file(sample_csv_path)
        
        assert successful == 3
        assert total == 5
        assert mock_validate_token.call_count == 1
        assert mock_transfer.call_count == 5

    @patch.object(GitHubRepoTransfer, 'validate_token')
    def test_csv_file_not_found(self, mock_validate_token):
        """Test handling of non-existent CSV file."""
        # Set up successful token validation
        mock_validate_token.return_value = True
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        
        successful, total = transfer.process_csv_file("non_existent_file.csv")
        
        assert successful == 0
        assert total == 0
        assert mock_validate_token.call_count == 1

    @patch.object(GitHubRepoTransfer, 'validate_token')
    def test_invalid_csv_format(self, mock_validate_token, invalid_csv_path):
        """Test handling of CSV with invalid format (missing required columns)."""
        # Set up successful token validation
        mock_validate_token.return_value = True
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        
        successful, total = transfer.process_csv_file(invalid_csv_path)
        
        assert successful == 0
        assert total == 0
        assert mock_validate_token.call_count == 1

    @patch.object(GitHubRepoTransfer, 'validate_token')
    def test_empty_csv(self, mock_validate_token, empty_csv_path):
        """Test handling of empty CSV file (headers only)."""
        # Set up successful token validation
        mock_validate_token.return_value = True
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        
        successful, total = transfer.process_csv_file(empty_csv_path)
        
        assert successful == 0
        assert total == 0
        assert mock_validate_token.call_count == 1

    @patch.object(GitHubRepoTransfer, 'transfer_repository')
    @patch.object(GitHubRepoTransfer, 'validate_token')
    def test_csv_processing_with_exception(self, mock_validate_token, mock_transfer, sample_csv_path):
        """Test handling of exceptions during CSV processing."""
        # Set up successful token validation
        mock_validate_token.return_value = True
        
        # Set up successful transfer for first repo, then an exception
        mock_transfer.side_effect = [True, Exception("Unexpected error")]
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        successful, total = transfer.process_csv_file(sample_csv_path)
        
        assert successful == 1
        assert total == 2
        assert mock_validate_token.call_count == 1
        assert mock_transfer.call_count == 2

    @patch.object(GitHubRepoTransfer, 'transfer_repository')
    @patch.object(GitHubRepoTransfer, 'validate_token')
    def test_csv_dry_run(self, mock_validate_token, mock_transfer, sample_csv_path):
        """Test CSV processing in dry-run mode."""
        # Set up successful token validation
        mock_validate_token.return_value = True
        
        # All transfers "succeed" in dry-run mode
        mock_transfer.return_value = True
        
        transfer = GitHubRepoTransfer(token="admin-token", debug=False, dry_run=True)
        transfer.user_login = TEST_USER  # Set user_login directly for the test
        
        successful, total = transfer.process_csv_file(sample_csv_path)
        
        assert successful == 5
        assert total == 5
        assert mock_validate_token.call_count == 1
        assert mock_transfer.call_count == 5
