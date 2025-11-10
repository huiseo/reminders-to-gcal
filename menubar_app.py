#!/usr/bin/env python3
"""
Reminders to Google Calendar - Menu Bar App
"""

import rumps
import os
import sys
import subprocess
import threading
import fcntl
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
# When running as PyInstaller bundle, use _MEIPASS for code, Resources for data
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    BUNDLE_DIR = Path(sys._MEIPASS)
    # Use Resources directory for persistent data (outside the executable)
    APP_DIR = Path(sys.executable).parent.parent / 'Resources'
else:
    # Running as script
    BUNDLE_DIR = Path(__file__).parent
    APP_DIR = BUNDLE_DIR

sys.path.insert(0, str(BUNDLE_DIR / 'src'))

from auth import get_authenticated_service
from reminders_reader import RemindersReader
from gcal_writer import GoogleCalendarWriter
from sync_engine import SyncEngine, MappingDatabase
import yaml

# Setup logging
logger = logging.getLogger(__name__)


class RemindersToGCalApp(rumps.App):
    """Menu bar app for syncing reminders to Google Calendar."""

    def __init__(self):
        # Use icon from bundle directory
        icon_path = str(BUNDLE_DIR / "icon.icns") if (BUNDLE_DIR / "icon.icns").exists() else None
        super(RemindersToGCalApp, self).__init__(
            "R→GCal",
            icon=icon_path,
            quit_button=None
        )

        self.config_path = APP_DIR / 'config.yaml'
        self.prefs_path = Path.home() / '.reminders-to-gcal-prefs.json'
        self.syncing = False
        self.last_sync_time = None
        self.last_sync_stats = None
        self.auto_sync_timer = None

        # Load preferences
        self.load_preferences()

        # Setup menu
        self.last_sync_item = rumps.MenuItem('Last Sync: Never', callback=None)
        self.menu = [
            rumps.MenuItem('Sync Now', callback=self.sync_now),
            self.last_sync_item,
            rumps.separator,
            rumps.MenuItem('Preferences...', callback=self.show_preferences),
            rumps.separator,
            rumps.MenuItem('View Logs', callback=self.view_logs),
            rumps.MenuItem('Open Reminders', callback=self.open_reminders),
            rumps.MenuItem('Open Google Calendar', callback=self.open_gcal),
            rumps.separator,
            rumps.MenuItem('Help', callback=self.show_help),
            rumps.MenuItem('About', callback=self.show_about),
            rumps.MenuItem('Quit', callback=self.quit_app),
        ]

        # Load last sync time
        self.update_last_sync_display()

        # Start auto-sync timer if enabled
        self.start_auto_sync()

    def sync_now(self, _):
        """Manually trigger sync."""
        if self.syncing:
            rumps.alert("Sync in Progress", "A sync operation is already running.")
            return

        # Run sync in background thread
        thread = threading.Thread(target=self._run_sync)
        thread.daemon = True
        thread.start()

    def _run_sync(self):
        """Run sync operation in background."""
        self.syncing = True
        self.title = "R→GCal ⟳"
        logger.info("Starting manual sync operation")

        try:
            # Load config
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
            except (IOError, OSError) as e:
                raise FileNotFoundError(f"Config file not found: {self.config_path}") from e
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in config file: {e}") from e

            # Initialize components
            db_path = APP_DIR / config.get('database', {}).get('path', 'data/mapping.db')
            db = MappingDatabase(str(db_path))

            reminders_reader = RemindersReader()

            credentials_file = APP_DIR / config.get('auth', {}).get('credentials_file', 'credentials.json')
            token_file = APP_DIR / config.get('auth', {}).get('token_file', 'data/token.json')
            calendar_id = config.get('google_calendar', {}).get('calendar_id', 'primary')

            service = get_authenticated_service(str(credentials_file), str(token_file))
            gcal_writer = GoogleCalendarWriter(service, calendar_id)

            # Sync
            engine = SyncEngine(reminders_reader, gcal_writer, db, config)
            stats = engine.sync()

            # Update status
            self.last_sync_time = datetime.now()
            self.last_sync_stats = stats
            self.update_last_sync_display()
            logger.info(f"Sync completed: {stats}")

            # Show notification if enabled
            if self.preferences.get('show_notifications', True):
                if stats.errors == 0:
                    rumps.notification(
                        title="Sync Complete",
                        subtitle=f"{stats.created} created, {stats.updated} updated",
                        message=f"Total: {stats.total_reminders} reminders"
                    )
                else:
                    rumps.notification(
                        title="Sync Complete with Errors",
                        subtitle=f"{stats.errors} errors occurred",
                        message="Check logs for details"
                    )

        except FileNotFoundError as e:
            logger.error(f"Configuration error: {e}")
            self.handle_config_error(str(e))
        except Exception as e:
            logger.error(f"Sync error: {e}", exc_info=True)
            self.handle_sync_error(str(e))
        finally:
            self.syncing = False
            self.title = "R→GCal"
            logger.info("Sync operation finished")

    def update_last_sync_display(self):
        """Update last sync time in menu."""
        if self.last_sync_time:
            time_str = self.last_sync_time.strftime('%H:%M')
            if self.last_sync_stats:
                stats = self.last_sync_stats
                status = f"Last: {time_str} ({stats.created}↑ {stats.updated}↻ {stats.deleted}↓)"
            else:
                status = f"Last Sync: {time_str}"
        else:
            status = "Last Sync: Never"

        # Update menu item using the stored reference
        self.last_sync_item.title = status

    def view_logs(self, _):
        """Open log file in Console app."""
        log_path = APP_DIR / 'logs' / 'sync.log'
        if log_path.exists():
            subprocess.run(['open', '-a', 'Console', str(log_path)])
        else:
            rumps.alert("No Logs", "Log file not found.")

    def open_reminders(self, _):
        """Open Reminders app."""
        subprocess.run(['open', '-a', 'Reminders'])

    def open_gcal(self, _):
        """Open Google Calendar in browser."""
        subprocess.run(['open', 'https://calendar.google.com'])

    def show_about(self, _):
        """Show about dialog."""
        rumps.alert(
            title="Reminders to Google Calendar",
            message=(
                "Version 1.0\n\n"
                "Automatically sync your Mac/iPhone Reminders\n"
                "to Google Calendar.\n\n"
                "© 2025"
            )
        )

    def load_preferences(self):
        """Load user preferences."""
        default_prefs = {
            'auto_sync_enabled': False,
            'auto_sync_interval': 60,  # minutes
            'launch_at_login': False,
            'show_notifications': True,
            'sync_completed_reminders': True
        }

        if self.prefs_path.exists():
            try:
                with open(self.prefs_path, 'r') as f:
                    self.preferences = {**default_prefs, **json.load(f)}
            except (json.JSONDecodeError, IOError, OSError) as e:
                logger.warning(f"Error loading preferences: {e}. Using defaults.")
                self.preferences = default_prefs
        else:
            self.preferences = default_prefs

    def save_preferences(self):
        """Save user preferences."""
        try:
            with open(self.prefs_path, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except (IOError, OSError) as e:
            logger.error(f"Error saving preferences: {e}")
            rumps.alert("Error", f"Failed to save preferences:\n\n{str(e)}")

    def start_auto_sync(self):
        """Start automatic sync timer."""
        if self.auto_sync_timer:
            self.auto_sync_timer.stop()
            self.auto_sync_timer = None

        if self.preferences.get('auto_sync_enabled'):
            interval = self.preferences.get('auto_sync_interval', 60) * 60  # Convert to seconds
            self.auto_sync_timer = rumps.Timer(self.auto_sync_callback, interval)
            self.auto_sync_timer.start()

    def auto_sync_callback(self, _):
        """Callback for automatic sync."""
        if not self.syncing:
            self.sync_now(None)

    def show_preferences(self, _):
        """Show preferences window."""
        # Create preferences window using AppleScript
        prefs = self.preferences

        # Auto sync interval options
        interval_options = {
            '15 minutes': 15,
            '30 minutes': 30,
            '1 hour': 60,
            '2 hours': 120,
            'Manual only': 0
        }

        current_interval = prefs.get('auto_sync_interval', 60)
        interval_text = next((k for k, v in interval_options.items() if v == current_interval), '1 hour')

        # Show dialog with current settings
        response = rumps.Window(
            title='Preferences',
            message='Auto-sync interval:',
            default_text=str(current_interval),
            ok='Save',
            cancel='Cancel',
            dimensions=(320, 100)
        ).run()

        if response.clicked:
            try:
                new_interval = int(response.text)
                if new_interval < 0:
                    new_interval = 0

                self.preferences['auto_sync_interval'] = new_interval
                self.preferences['auto_sync_enabled'] = new_interval > 0
                self.save_preferences()
                self.start_auto_sync()

                rumps.notification(
                    title="Preferences Saved",
                    subtitle="Settings updated",
                    message=f"Auto-sync: {'Enabled' if new_interval > 0 else 'Disabled'}"
                )
            except ValueError:
                rumps.alert("Invalid Input", "Please enter a valid number of minutes.")

    def toggle_launch_at_login(self):
        """Toggle launch at login setting."""
        try:
            bundle_id = "com.reminders-to-gcal.app"
            enabled = not self.preferences.get('launch_at_login', False)

            # Use osascript to set login item
            if enabled:
                script = f'''
                tell application "System Events"
                    make login item at end with properties {{path:"/Applications/Reminders to GCal.app", hidden:false}}
                end tell
                '''
            else:
                script = f'''
                tell application "System Events"
                    delete login item "Reminders to GCal"
                end tell
                '''

            subprocess.run(['osascript', '-e', script], capture_output=True)

            self.preferences['launch_at_login'] = enabled
            self.save_preferences()

            return True
        except Exception as e:
            logger.error(f"Error toggling launch at login: {e}")
            return False

    def handle_config_error(self, error_msg):
        """Handle configuration errors with recovery options."""
        response = rumps.alert(
            title="Configuration Error",
            message=f"Missing file: {error_msg}\n\nWhat would you like to do?",
            ok="View Guide",
            cancel="Cancel",
            other="Open App Folder"
        )

        if response == 1:  # View Guide
            subprocess.run(['open', str(APP_DIR / 'DMG_INSTALL_GUIDE.md')])
        elif response == 0:  # Open App Folder
            subprocess.run(['open', '-R', str(APP_DIR)])

    def handle_sync_error(self, error_msg):
        """Handle sync errors with recovery options."""
        response = rumps.alert(
            title="Sync Error",
            message=f"An error occurred:\n\n{error_msg}\n\nWhat would you like to do?",
            ok="Retry",
            cancel="Cancel",
            other="Re-authenticate"
        )

        if response == 1:  # Retry
            self.sync_now(None)
        elif response == 0:  # Re-authenticate
            self.reset_authentication()

    def reset_authentication(self):
        """Reset Google authentication."""
        try:
            token_file = APP_DIR / 'data' / 'token.json'
            if token_file.exists():
                token_file.unlink()

            rumps.alert(
                "Authentication Reset",
                "Google authentication has been reset.\n\n"
                "Please run sync again to re-authenticate."
            )
        except Exception as e:
            rumps.alert("Error", f"Failed to reset authentication:\n\n{str(e)}")

    def show_help(self, _):
        """Show help menu."""
        response = rumps.alert(
            title="Help",
            message="Choose an option:",
            ok="User Guide",
            cancel="Cancel",
            other="Report Issue"
        )

        if response == 1:  # User Guide
            guide_path = APP_DIR / 'DMG_INSTALL_GUIDE.md'
            if guide_path.exists():
                subprocess.run(['open', str(guide_path)])
            else:
                subprocess.run(['open', 'https://github.com/yourusername/reminders-to-gcal'])
        elif response == 0:  # Report Issue
            subprocess.run(['open', 'https://github.com/yourusername/reminders-to-gcal/issues'])

    def quit_app(self, _):
        """Quit the application."""
        if self.auto_sync_timer:
            self.auto_sync_timer.stop()
        rumps.quit_application()


if __name__ == "__main__":
    # Setup logging
    log_dir = APP_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'menubar_app.log'),
            logging.StreamHandler()
        ]
    )

    # Check if already running (single instance)
    lock_file = Path.home() / '.reminders-to-gcal.lock'
    lock_fp = open(lock_file, 'w')

    try:
        # Try to acquire exclusive lock
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # Another instance is already running
        logger.info("Reminders to GCal is already running. Exiting.")
        lock_fp.close()
        sys.exit(0)

    # Change to app directory
    os.chdir(APP_DIR)

    # Start app
    try:
        logger.info("Starting Reminders to GCal menubar app")
        app = RemindersToGCalApp()
        app.run()
    finally:
        # Release lock on exit
        logger.info("Shutting down Reminders to GCal")
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)
        lock_fp.close()
        if lock_file.exists():
            lock_file.unlink()
