"""
Unit tests for sync_engine module.
"""

import unittest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from sync_engine import MappingDatabase, SyncEngine, SyncStats


class TestSyncStats(unittest.TestCase):
    """Test SyncStats dataclass."""

    def test_sync_stats_initialization(self):
        """Test SyncStats initializes with correct defaults."""
        stats = SyncStats()
        self.assertEqual(stats.total_reminders, 0)
        self.assertEqual(stats.created, 0)
        self.assertEqual(stats.updated, 0)
        self.assertEqual(stats.deleted, 0)
        self.assertEqual(stats.skipped, 0)
        self.assertEqual(stats.errors, 0)

    def test_sync_stats_str(self):
        """Test SyncStats string representation."""
        stats = SyncStats(
            total_reminders=10,
            created=5,
            updated=3,
            deleted=1,
            skipped=1,
            errors=0
        )
        result = str(stats)
        self.assertIn("10 total", result)
        self.assertIn("5 created", result)
        self.assertIn("3 updated", result)


class TestMappingDatabase(unittest.TestCase):
    """Test MappingDatabase class."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_mapping.db'
        self.db = MappingDatabase(str(self.db_path))

    def tearDown(self):
        """Clean up test database."""
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_database_initialization(self):
        """Test database is created and tables exist."""
        self.assertTrue(self.db_path.exists())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check mappings table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='mappings'"
            )
            self.assertIsNotNone(cursor.fetchone())

            # Check sync_history table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sync_history'"
            )
            self.assertIsNotNone(cursor.fetchone())

    def test_save_and_get_mapping(self):
        """Test saving and retrieving mappings."""
        reminder_uuid = "test-uuid-123"
        event_id = "gcal-event-456"

        # Save mapping
        self.db.save_mapping(reminder_uuid, event_id)

        # Retrieve mapping
        retrieved_id = self.db.get_event_id(reminder_uuid)
        self.assertEqual(retrieved_id, event_id)

    def test_get_event_id_nonexistent(self):
        """Test getting event ID for non-existent reminder."""
        result = self.db.get_event_id("nonexistent-uuid")
        self.assertIsNone(result)

    def test_delete_mapping(self):
        """Test deleting a mapping."""
        reminder_uuid = "test-uuid-789"
        event_id = "gcal-event-012"

        # Save then delete
        self.db.save_mapping(reminder_uuid, event_id)
        self.db.delete_mapping(reminder_uuid)

        # Verify deleted
        result = self.db.get_event_id(reminder_uuid)
        self.assertIsNone(result)

    def test_get_all_reminder_uuids(self):
        """Test getting all reminder UUIDs."""
        # Add multiple mappings
        mappings = {
            "uuid-1": "event-1",
            "uuid-2": "event-2",
            "uuid-3": "event-3"
        }

        for uuid, event_id in mappings.items():
            self.db.save_mapping(uuid, event_id)

        # Get all UUIDs
        uuids = self.db.get_all_reminder_uuids()

        self.assertEqual(len(uuids), 3)
        for uuid in mappings.keys():
            self.assertIn(uuid, uuids)

    def test_save_mapping_with_checksum(self):
        """Test saving mapping with checksum."""
        reminder_uuid = "test-uuid-checksum"
        event_id = "gcal-event-checksum"
        checksum = "abc123"

        self.db.save_mapping(
            reminder_uuid,
            event_id,
            checksum=checksum
        )

        # Verify saved
        result = self.db.get_event_id(reminder_uuid)
        self.assertEqual(result, event_id)

    def test_save_sync_stats(self):
        """Test saving sync statistics."""
        stats = SyncStats(
            total_reminders=20,
            created=10,
            updated=5,
            deleted=2,
            errors=1
        )

        self.db.save_sync_stats(stats)

        # Verify saved in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sync_history')
            result = cursor.fetchone()

            self.assertIsNotNone(result)
            self.assertEqual(result[2], 20)  # total_reminders
            self.assertEqual(result[3], 10)  # created
            self.assertEqual(result[4], 5)   # updated
            self.assertEqual(result[5], 2)   # deleted


class TestSyncEngine(unittest.TestCase):
    """Test SyncEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_sync.db'
        self.db = MappingDatabase(str(self.db_path))

        # Create mocks
        self.mock_reminders_reader = Mock()
        self.mock_gcal_writer = Mock()

        # Test config
        self.config = {
            'reminders': {
                'sync_lists': [],
                'skip_completed_older_than_days': 30
            },
            'sync': {
                'completed_action': 'delete'
            },
            'google_calendar': {
                'priority_colors': {}
            }
        }

        self.engine = SyncEngine(
            self.mock_reminders_reader,
            self.mock_gcal_writer,
            self.db,
            self.config
        )

    def tearDown(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_generate_checksum(self):
        """Test checksum generation."""
        reminder = Mock()
        reminder.title = "Test Reminder"
        reminder.notes = "Test notes"
        reminder.due_date = datetime.now()
        reminder.priority = 1
        reminder.completed = False
        reminder.location = "Test Location"

        checksum1 = self.engine._generate_checksum(reminder)
        checksum2 = self.engine._generate_checksum(reminder)

        # Same reminder should generate same checksum
        self.assertEqual(checksum1, checksum2)

        # Different reminder should generate different checksum
        reminder.title = "Different Title"
        checksum3 = self.engine._generate_checksum(reminder)
        self.assertNotEqual(checksum1, checksum3)

    def test_should_skip_old_completed_reminder(self):
        """Test skipping old completed reminders."""
        reminder = Mock()
        reminder.completed = True
        reminder.completion_date = datetime.now().replace(year=2020)

        result = self.engine._should_skip_reminder(reminder)
        self.assertTrue(result)

    def test_should_not_skip_recent_completed_reminder(self):
        """Test not skipping recent completed reminders."""
        reminder = Mock()
        reminder.completed = True
        reminder.completion_date = datetime.now()

        result = self.engine._should_skip_reminder(reminder)
        self.assertFalse(result)

    def test_should_not_skip_incomplete_reminder(self):
        """Test not skipping incomplete reminders."""
        reminder = Mock()
        reminder.completed = False
        reminder.completion_date = None

        result = self.engine._should_skip_reminder(reminder)
        self.assertFalse(result)

    def test_sync_create_new_event(self):
        """Test creating a new event for reminder."""
        reminder = Mock()
        reminder.uuid = "new-reminder-uuid"
        reminder.title = "New Reminder"
        reminder.notes = "Notes"
        reminder.due_date = datetime.now()
        reminder.priority = 1
        reminder.completed = False
        reminder.location = "Office"
        reminder.modification_date = datetime.now()

        # Mock gcal_writer to return success
        self.mock_gcal_writer.create_event.return_value = {
            'id': 'new-event-123'
        }
        self.mock_gcal_writer.get_priority_color.return_value = None

        # Sync the reminder
        self.engine._sync_reminder(reminder)

        # Verify create_event was called
        self.mock_gcal_writer.create_event.assert_called_once()

        # Verify mapping was saved
        event_id = self.db.get_event_id(reminder.uuid)
        self.assertEqual(event_id, 'new-event-123')

        # Verify stats
        self.assertEqual(self.engine.stats.created, 1)

    def test_sync_update_existing_event(self):
        """Test updating an existing event."""
        reminder = Mock()
        reminder.uuid = "existing-reminder-uuid"
        reminder.title = "Updated Reminder"
        reminder.notes = "Updated notes"
        reminder.due_date = datetime.now()
        reminder.priority = 1
        reminder.completed = False
        reminder.location = "Home"
        reminder.modification_date = datetime.now()

        # Pre-save mapping
        self.db.save_mapping(reminder.uuid, "existing-event-456")

        # Mock gcal_writer
        self.mock_gcal_writer.update_event.return_value = True
        self.mock_gcal_writer.get_priority_color.return_value = None

        # Sync the reminder
        self.engine._sync_reminder(reminder)

        # Verify update_event was called
        self.mock_gcal_writer.update_event.assert_called_once()

        # Verify stats
        self.assertEqual(self.engine.stats.updated, 1)

    def test_sync_delete_completed_event(self):
        """Test deleting a completed reminder's event."""
        reminder = Mock()
        reminder.uuid = "completed-reminder-uuid"
        reminder.title = "Completed Reminder"
        reminder.notes = ""
        reminder.due_date = datetime.now()
        reminder.priority = 1
        reminder.completed = True
        reminder.completion_date = datetime.now()
        reminder.location = None

        # Pre-save mapping
        self.db.save_mapping(reminder.uuid, "completed-event-789")

        # Mock gcal_writer
        self.mock_gcal_writer.delete_event.return_value = True

        # Sync the reminder
        self.engine._sync_reminder(reminder)

        # Verify delete_event was called
        self.mock_gcal_writer.delete_event.assert_called_once_with("completed-event-789")

        # Verify mapping was deleted
        event_id = self.db.get_event_id(reminder.uuid)
        self.assertIsNone(event_id)

        # Verify stats
        self.assertEqual(self.engine.stats.deleted, 1)


if __name__ == '__main__':
    unittest.main()
