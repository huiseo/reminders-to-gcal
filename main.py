#!/usr/bin/env python3
"""
Main entry point for Reminders to Google Calendar sync tool.
"""

import argparse
import logging
import sys
from pathlib import Path
import yaml

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from auth import get_authenticated_service
from reminders_reader import RemindersReader
from gcal_writer import GoogleCalendarWriter
from sync_engine import SyncEngine, MappingDatabase


def setup_logging(config: dict):
    """Setup logging configuration."""
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_file = config.get('logging', {}).get('file', 'logs/sync.log')

    # Create logs directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"Error: Config file not found: {config_path}")
        print("Please create config.yaml from the template")
        sys.exit(1)

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def cmd_sync(args, config):
    """Execute sync command."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Starting Reminders to Google Calendar Sync")
    logger.info("=" * 60)

    try:
        # Initialize components
        logger.info("Initializing components...")

        # Database
        db_path = config.get('database', {}).get('path', 'data/mapping.db')
        db = MappingDatabase(db_path)

        # Reminders reader
        logger.info("Connecting to Apple Reminders...")
        reminders_reader = RemindersReader()

        # Google Calendar
        logger.info("Authenticating with Google Calendar...")
        credentials_file = config.get('auth', {}).get('credentials_file', 'credentials.json')
        token_file = config.get('auth', {}).get('token_file', 'data/token.json')
        calendar_id = config.get('google_calendar', {}).get('calendar_id', 'primary')

        service = get_authenticated_service(credentials_file, token_file)
        gcal_writer = GoogleCalendarWriter(service, calendar_id)

        # Sync engine
        logger.info("Starting sync engine...")
        engine = SyncEngine(reminders_reader, gcal_writer, db, config)

        # Check dry-run mode
        dry_run = config.get('sync', {}).get('dry_run', False)
        if dry_run:
            logger.warning("DRY RUN MODE - No changes will be made to Google Calendar")

        # Perform sync
        stats = engine.sync()

        # Print summary
        logger.info("=" * 60)
        logger.info("Sync Complete!")
        logger.info("=" * 60)
        logger.info(f"Total reminders: {stats.total_reminders}")
        logger.info(f"Created: {stats.created}")
        logger.info(f"Updated: {stats.updated}")
        logger.info(f"Deleted: {stats.deleted}")
        logger.info(f"Skipped: {stats.skipped}")
        logger.info(f"Errors: {stats.errors}")
        logger.info("=" * 60)

        return 0 if stats.errors == 0 else 1

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return 1
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return 1


def cmd_list_calendars(args, config):
    """List available reminder calendars."""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Fetching reminder calendars...")
        reader = RemindersReader()
        calendars = reader.get_all_calendars()

        print("\nAvailable Reminder Calendars:")
        print("-" * 40)
        for cal in calendars:
            print(f"  - {cal}")
        print("-" * 40)
        print(f"Total: {len(calendars)} calendar(s)")

        return 0

    except Exception as e:
        logger.error(f"Failed to list calendars: {e}")
        return 1


def cmd_status(args, config):
    """Show sync status and statistics."""
    logger = logging.getLogger(__name__)

    try:
        db_path = config.get('database', {}).get('path', 'data/mapping.db')
        db = MappingDatabase(db_path)

        # Count mappings
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM mappings')
        mapping_count = cursor.fetchone()[0]

        cursor.execute('SELECT sync_time, total_reminders, created, updated, deleted, errors FROM sync_history ORDER BY sync_time DESC LIMIT 5')
        history = cursor.fetchall()

        conn.close()

        # Print status
        print("\nSync Status")
        print("=" * 60)
        print(f"Total mapped reminders: {mapping_count}")
        print("\nRecent sync history:")
        print("-" * 60)

        if history:
            for row in history:
                sync_time, total, created, updated, deleted, errors = row
                print(f"{sync_time}: {total} total, {created} created, {updated} updated, {deleted} deleted, {errors} errors")
        else:
            print("No sync history available")

        print("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync Apple Reminders to Google Calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sync                  # Run sync operation
  %(prog)s list                  # List available reminder calendars
  %(prog)s status                # Show sync status
  %(prog)s --config custom.yaml sync  # Use custom config file
        """
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Sync command
    subparsers.add_parser('sync', help='Sync reminders to Google Calendar')

    # List command
    subparsers.add_parser('list', help='List available reminder calendars')

    # Status command
    subparsers.add_parser('status', help='Show sync status and statistics')

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Setup logging
    setup_logging(config)

    # Execute command
    if args.command == 'sync':
        return cmd_sync(args, config)
    elif args.command == 'list':
        return cmd_list_calendars(args, config)
    elif args.command == 'status':
        return cmd_status(args, config)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
