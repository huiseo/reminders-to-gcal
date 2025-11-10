"""
Sync engine for coordinating reminders to Google Calendar sync.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SyncStats:
    """Statistics for a sync operation."""
    total_reminders: int = 0
    created: int = 0
    updated: int = 0
    deleted: int = 0
    skipped: int = 0
    errors: int = 0

    def __str__(self):
        return (
            f"Sync Stats: {self.total_reminders} total, "
            f"{self.created} created, {self.updated} updated, "
            f"{self.deleted} deleted, {self.skipped} skipped, "
            f"{self.errors} errors"
        )


class MappingDatabase:
    """SQLite database for tracking reminder-to-event mappings."""

    def __init__(self, db_path: str):
        """
        Initialize mapping database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mappings (
                    reminder_uuid TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    last_synced TIMESTAMP NOT NULL,
                    last_modified TIMESTAMP,
                    checksum TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_time TIMESTAMP NOT NULL,
                    total_reminders INTEGER,
                    created INTEGER,
                    updated INTEGER,
                    deleted INTEGER,
                    errors INTEGER
                )
            ''')

            conn.commit()
        logger.debug(f"Database initialized at {self.db_path}")

    def get_event_id(self, reminder_uuid: str) -> Optional[str]:
        """Get event ID for a reminder UUID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT event_id FROM mappings WHERE reminder_uuid = ?', (reminder_uuid,))
            result = cursor.fetchone()
            return result[0] if result else None

    def save_mapping(
        self,
        reminder_uuid: str,
        event_id: str,
        last_modified: Optional[datetime] = None,
        checksum: Optional[str] = None
    ):
        """Save or update a reminder-to-event mapping."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO mappings (reminder_uuid, event_id, last_synced, last_modified, checksum)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                reminder_uuid,
                event_id,
                datetime.now(),
                last_modified,
                checksum
            ))

            conn.commit()
        logger.debug(f"Saved mapping: {reminder_uuid} -> {event_id}")

    def delete_mapping(self, reminder_uuid: str):
        """Delete a mapping."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM mappings WHERE reminder_uuid = ?', (reminder_uuid,))
            conn.commit()
        logger.debug(f"Deleted mapping for {reminder_uuid}")

    def get_all_reminder_uuids(self) -> Set[str]:
        """Get all reminder UUIDs currently in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT reminder_uuid FROM mappings')
            results = cursor.fetchall()
            return {row[0] for row in results}

    def get_last_modified(self, reminder_uuid: str) -> Optional[datetime]:
        """Get last modification time for a reminder."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT last_modified FROM mappings WHERE reminder_uuid = ?', (reminder_uuid,))
            result = cursor.fetchone()

            if result and result[0]:
                return datetime.fromisoformat(result[0])
            return None

    def save_sync_stats(self, stats: SyncStats):
        """Save sync statistics to history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO sync_history (sync_time, total_reminders, created, updated, deleted, errors)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                stats.total_reminders,
                stats.created,
                stats.updated,
                stats.deleted,
                stats.errors
            ))

            conn.commit()


class SyncEngine:
    """Synchronize reminders to Google Calendar."""

    def __init__(
        self,
        reminders_reader,
        gcal_writer,
        db: MappingDatabase,
        config: Dict
    ):
        """
        Initialize sync engine.

        Args:
            reminders_reader: RemindersReader instance
            gcal_writer: GoogleCalendarWriter instance
            db: MappingDatabase instance
            config: Configuration dict
        """
        self.reminders_reader = reminders_reader
        self.gcal_writer = gcal_writer
        self.db = db
        self.config = config
        self.stats = SyncStats()

    def _generate_checksum(self, reminder) -> str:
        """Generate a checksum for a reminder to detect changes."""
        # Simple checksum based on key fields (including location)
        data = f"{reminder.title}|{reminder.notes}|{reminder.due_date}|{reminder.priority}|{reminder.completed}|{reminder.location}"
        return str(hash(data))

    def _should_skip_reminder(self, reminder) -> bool:
        """Determine if a reminder should be skipped."""
        # Skip old completed reminders
        skip_days = self.config.get('reminders', {}).get('skip_completed_older_than_days', 30)

        if skip_days > 0 and reminder.completed and reminder.completion_date:
            cutoff = datetime.now() - timedelta(days=skip_days)
            if reminder.completion_date < cutoff:
                logger.debug(f"Skipping old completed reminder: {reminder.title}")
                return True

        return False

    def _sync_reminder(self, reminder):
        """Sync a single reminder."""
        if self._should_skip_reminder(reminder):
            self.stats.skipped += 1
            return

        # Check if mapping exists
        event_id = self.db.get_event_id(reminder.uuid)
        current_checksum = self._generate_checksum(reminder)

        # Prepare event data
        color_id = self.gcal_writer.get_priority_color(
            reminder.priority,
            self.config.get('google_calendar', {}).get('priority_colors', {})
        )

        # Determine if all-day event
        all_day = reminder.due_date is not None and reminder.due_date.hour == 0

        if reminder.completed:
            # Handle completed reminder
            completed_action = self.config.get('sync', {}).get('completed_action', 'delete')

            if event_id and completed_action == 'delete':
                # Delete the event
                if self.gcal_writer.delete_event(event_id):
                    self.db.delete_mapping(reminder.uuid)
                    self.stats.deleted += 1
                else:
                    self.stats.errors += 1
            else:
                self.stats.skipped += 1

        elif event_id:
            # Check if update needed
            last_modified = self.db.get_last_modified(reminder.uuid)

            if reminder.modification_date and last_modified:
                if reminder.modification_date <= last_modified:
                    # No changes needed
                    self.stats.skipped += 1
                    return

            # Update existing event
            logger.debug(f"Updating reminder: {reminder.title}")
            result = self.gcal_writer.update_event(
                event_id=event_id,
                summary=reminder.title,
                description=reminder.notes,
                start_datetime=reminder.due_date,
                end_datetime=reminder.due_date,
                color_id=color_id,
                all_day=all_day,
                location=reminder.location
            )

            if result:
                self.db.save_mapping(
                    reminder.uuid,
                    event_id,
                    reminder.modification_date,
                    current_checksum
                )
                self.stats.updated += 1
            else:
                self.stats.errors += 1

        else:
            # Create new event
            logger.debug(f"Creating new event for reminder: {reminder.title}")
            result = self.gcal_writer.create_event(
                summary=reminder.title,
                description=reminder.notes,
                start_datetime=reminder.due_date,
                end_datetime=reminder.due_date,
                color_id=color_id,
                reminder_uuid=reminder.uuid,
                all_day=all_day,
                location=reminder.location
            )

            if result:
                self.db.save_mapping(
                    reminder.uuid,
                    result['id'],
                    reminder.modification_date,
                    current_checksum
                )
                self.stats.created += 1
            else:
                self.stats.errors += 1

    def _cleanup_deleted_reminders(self, current_reminder_uuids: Set[str]):
        """Delete events for reminders that no longer exist."""
        db_uuids = self.db.get_all_reminder_uuids()
        deleted_uuids = db_uuids - current_reminder_uuids

        for uuid in deleted_uuids:
            event_id = self.db.get_event_id(uuid)
            if event_id:
                logger.debug(f"Deleting event for removed reminder: {uuid}")
                if self.gcal_writer.delete_event(event_id):
                    self.db.delete_mapping(uuid)
                    self.stats.deleted += 1
                else:
                    self.stats.errors += 1

    def sync(self) -> SyncStats:
        """
        Perform full sync operation.

        Returns:
            SyncStats object with operation statistics
        """
        logger.info("Starting sync operation")
        self.stats = SyncStats()

        try:
            # Fetch reminders
            sync_lists = self.config.get('reminders', {}).get('sync_lists', [])
            calendar_names = sync_lists if sync_lists else None

            reminders = self.reminders_reader.fetch_reminders(calendar_names)
            self.stats.total_reminders = len(reminders)

            logger.info(f"Fetched {len(reminders)} reminders")

            # Track current UUIDs
            current_uuids = {r.uuid for r in reminders}

            # Sync each reminder
            for reminder in reminders:
                try:
                    self._sync_reminder(reminder)
                except Exception as e:
                    logger.error(f"Error syncing reminder '{reminder.title}': {e}")
                    self.stats.errors += 1

            # Cleanup deleted reminders
            self._cleanup_deleted_reminders(current_uuids)

            # Save stats
            self.db.save_sync_stats(self.stats)

            logger.info(f"Sync complete: {self.stats}")
            return self.stats

        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            raise


def main():
    """Test function."""
    logging.basicConfig(level=logging.INFO)
    print("sync_engine.py - Run through main sync script")


if __name__ == "__main__":
    main()
