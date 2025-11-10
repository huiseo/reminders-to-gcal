"""
Google Calendar OAuth authentication module.
"""

import os
import logging
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarAuth:
    """Handle Google Calendar OAuth authentication."""

    def __init__(self, credentials_file: str, token_file: str):
        """
        Initialize authentication handler.

        Args:
            credentials_file: Path to Google OAuth credentials JSON file
            token_file: Path to store/load OAuth token
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.creds = None

    def authenticate(self) -> Credentials:
        """
        Authenticate with Google Calendar API.

        Returns:
            Google OAuth credentials

        Raises:
            FileNotFoundError: If credentials file is missing
            Exception: If authentication fails
        """
        # Check if credentials file exists
        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                "Please download it from Google Cloud Console:\n"
                "1. Go to https://console.cloud.google.com/\n"
                "2. Create a project or select existing one\n"
                "3. Enable Google Calendar API\n"
                "4. Create OAuth 2.0 credentials (Desktop app)\n"
                "5. Download JSON and save as 'credentials.json'"
            )

        # Load existing token if available
        if self.token_file.exists():
            logger.info("Loading existing OAuth token")
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_file), SCOPES
            )

        # Refresh or obtain new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Refreshing expired OAuth token")
                self.creds.refresh(Request())
            else:
                logger.info("Starting OAuth flow (browser will open)")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save the token for future use
            logger.info(f"Saving OAuth token to {self.token_file}")
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())

            # Set secure permissions (readable/writable by owner only)
            os.chmod(self.token_file, 0o600)

        logger.info("Authentication successful")
        return self.creds

    def get_calendar_service(self):
        """
        Get authenticated Google Calendar API service.

        Returns:
            Google Calendar API service object
        """
        if not self.creds:
            self.authenticate()

        logger.debug("Building Google Calendar service")
        return build('calendar', 'v3', credentials=self.creds)


def get_authenticated_service(credentials_file: str, token_file: str):
    """
    Convenience function to get authenticated Google Calendar service.

    Args:
        credentials_file: Path to Google OAuth credentials JSON file
        token_file: Path to store/load OAuth token

    Returns:
        Google Calendar API service object
    """
    auth = GoogleCalendarAuth(credentials_file, token_file)
    return auth.get_calendar_service()
