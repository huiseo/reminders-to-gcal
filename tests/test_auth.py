"""
Unit tests for auth module.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from auth import GoogleCalendarAuth, get_authenticated_service


class TestGoogleCalendarAuth(unittest.TestCase):
    """Test GoogleCalendarAuth class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.credentials_file = Path(self.temp_dir) / 'credentials.json'
        self.token_file = Path(self.temp_dir) / 'token.json'

        # Create dummy credentials file
        self.credentials_file.write_text('{"installed": {}}')

    def tearDown(self):
        """Clean up test fixtures."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()
        if self.token_file.exists():
            self.token_file.unlink()
        Path(self.temp_dir).rmdir()

    def test_initialization(self):
        """Test GoogleCalendarAuth initialization."""
        auth = GoogleCalendarAuth(
            str(self.credentials_file),
            str(self.token_file)
        )

        self.assertEqual(auth.credentials_file, self.credentials_file)
        self.assertEqual(auth.token_file, self.token_file)
        self.assertIsNone(auth.creds)

    def test_missing_credentials_file(self):
        """Test error when credentials file is missing."""
        nonexistent = Path(self.temp_dir) / 'nonexistent.json'
        auth = GoogleCalendarAuth(str(nonexistent), str(self.token_file))

        with self.assertRaises(FileNotFoundError) as context:
            auth.authenticate()

        self.assertIn("Credentials file not found", str(context.exception))

    @patch('auth.Credentials')
    def test_load_existing_token(self, mock_credentials):
        """Test loading existing valid token."""
        # Create token file
        self.token_file.write_text('{"token": "test"}')

        # Mock credentials
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        auth = GoogleCalendarAuth(
            str(self.credentials_file),
            str(self.token_file)
        )

        result = auth.authenticate()

        # Verify token was loaded
        mock_credentials.from_authorized_user_file.assert_called_once()
        self.assertEqual(result, mock_creds)

    @patch('auth.InstalledAppFlow')
    @patch('auth.Credentials')
    def test_oauth_flow_for_new_token(self, mock_credentials, mock_flow):
        """Test OAuth flow when no token exists."""
        # Mock credentials
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = False
        mock_creds.refresh_token = None
        mock_credentials.from_authorized_user_file.return_value = None

        # Mock flow
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        # Mock creds.to_json()
        mock_creds.to_json.return_value = '{"token": "new"}'
        mock_creds.valid = True

        auth = GoogleCalendarAuth(
            str(self.credentials_file),
            str(self.token_file)
        )

        result = auth.authenticate()

        # Verify OAuth flow was initiated
        mock_flow.from_client_secrets_file.assert_called_once()
        mock_flow_instance.run_local_server.assert_called_once()

        # Verify token was saved
        self.assertTrue(self.token_file.exists())

    @patch('auth.Request')
    @patch('auth.Credentials')
    def test_refresh_expired_token(self, mock_credentials, mock_request):
        """Test refreshing expired token."""
        # Create token file
        self.token_file.write_text('{"token": "expired"}')

        # Mock expired credentials with refresh token
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token_value'
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # After refresh, mark as valid
        def refresh_side_effect(request):
            mock_creds.valid = True

        mock_creds.refresh.side_effect = refresh_side_effect
        mock_creds.to_json.return_value = '{"token": "refreshed"}'

        auth = GoogleCalendarAuth(
            str(self.credentials_file),
            str(self.token_file)
        )

        result = auth.authenticate()

        # Verify token was refreshed
        mock_creds.refresh.assert_called_once()
        self.assertEqual(result, mock_creds)

    def test_token_file_permissions(self):
        """Test that token file has secure permissions after creation."""
        # Mock successful authentication
        with patch('auth.Credentials') as mock_credentials, \
             patch('auth.InstalledAppFlow') as mock_flow:

            mock_creds = Mock()
            mock_creds.valid = True
            mock_creds.to_json.return_value = '{"token": "test"}'

            mock_flow_instance = Mock()
            mock_flow_instance.run_local_server.return_value = mock_creds
            mock_flow.from_client_secrets_file.return_value = mock_flow_instance

            mock_credentials.from_authorized_user_file.return_value = None

            auth = GoogleCalendarAuth(
                str(self.credentials_file),
                str(self.token_file)
            )

            auth.authenticate()

            # Check file permissions (should be 0o600 = owner read/write only)
            if self.token_file.exists():
                stat_info = os.stat(self.token_file)
                permissions = stat_info.st_mode & 0o777
                self.assertEqual(permissions, 0o600)

    @patch('auth.build')
    def test_get_calendar_service(self, mock_build):
        """Test getting calendar service."""
        with patch('auth.Credentials') as mock_credentials:
            mock_creds = Mock()
            mock_creds.valid = True
            mock_credentials.from_authorized_user_file.return_value = mock_creds

            # Create token file
            self.token_file.write_text('{"token": "test"}')

            auth = GoogleCalendarAuth(
                str(self.credentials_file),
                str(self.token_file)
            )

            service = auth.get_calendar_service()

            # Verify build was called with correct parameters
            mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_creds)


class TestGetAuthenticatedService(unittest.TestCase):
    """Test get_authenticated_service convenience function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.credentials_file = Path(self.temp_dir) / 'credentials.json'
        self.token_file = Path(self.temp_dir) / 'token.json'

        # Create dummy credentials file
        self.credentials_file.write_text('{"installed": {}}')
        self.token_file.write_text('{"token": "test"}')

    def tearDown(self):
        """Clean up test fixtures."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()
        if self.token_file.exists():
            self.token_file.unlink()
        Path(self.temp_dir).rmdir()

    @patch('auth.build')
    @patch('auth.Credentials')
    def test_get_authenticated_service(self, mock_credentials, mock_build):
        """Test convenience function returns service."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        mock_service = Mock()
        mock_build.return_value = mock_service

        result = get_authenticated_service(
            str(self.credentials_file),
            str(self.token_file)
        )

        self.assertEqual(result, mock_service)


if __name__ == '__main__':
    unittest.main()
