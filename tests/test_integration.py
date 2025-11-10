"""
Integration tests for the complete sync workflow.
"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from sync_engine import MappingDatabase, SyncEngine
from gcal_writer import GoogleCalendarWriter


class TestEndToEndSync(unittest.TestCase):
    """Test complete sync workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_integration.db'
        self.db = MappingDatabase(str(self.db_path))

        # Create mock services
        self.mock_reminders_reader = Mock()
        self.mock_gcal_service = Mock()
        self.calendar_id = 'test-calendar'

        # Config
        self.config = {
            'reminders': {
                'sync_lists': [],
                'skip_completed_older_than_days': 30
            },
            'sync': {
                'completed_action': 'delete'
            },
            'google_calendar': {
                'calendar_id': self.calendar_id,
                'priority_colors': {}
            }
        }

    def tearDown(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_full_sync_workflow_create_new_events(self):
        """Test complete workflow: fetch reminders → create events → save mappings."""
        # Mock reminders
        mock_reminder1 = Mock()
        mock_reminder1.uuid = 'reminder-1'
        mock_reminder1.title = 'Buy groceries'
        mock_reminder1.notes = 'Milk, bread, eggs'
        mock_reminder1.due_date = datetime(2025, 1, 20, 15, 0)
        mock_reminder1.priority = 1
        mock_reminder1.completed = False
        mock_reminder1.location = 'Supermarket'
        mock_reminder1.modification_date = datetime.now()

        mock_reminder2 = Mock()
        mock_reminder2.uuid = 'reminder-2'
        mock_reminder2.title = 'Doctor appointment'
        mock_reminder2.notes = 'Annual checkup'
        mock_reminder2.due_date = datetime(2025, 1, 25, 10, 0)
        mock_reminder2.priority = 5
        mock_reminder2.completed = False
        mock_reminder2.location = 'Hospital'
        mock_reminder2.modification_date = datetime.now()

        self.mock_reminders_reader.fetch_reminders.return_value = [
            mock_reminder1,
            mock_reminder2
        ]

        # Mock Google Calendar API
        mock_events = Mock()
        mock_events.insert.return_value.execute.side_effect = [
            {'id': 'gcal-event-1'},
            {'id': 'gcal-event-2'}
        ]
        self.mock_gcal_service.events.return_value = mock_events

        # Create gcal_writer and sync_engine
        gcal_writer = GoogleCalendarWriter(self.mock_gcal_service, self.calendar_id)
        engine = SyncEngine(
            self.mock_reminders_reader,
            gcal_writer,
            self.db,
            self.config
        )

        # Execute sync
        stats = engine.sync()

        # Verify results
        self.assertEqual(stats.total_reminders, 2)
        self.assertEqual(stats.created, 2)
        self.assertEqual(stats.updated, 0)
        self.assertEqual(stats.deleted, 0)
        self.assertEqual(stats.errors, 0)

        # Verify mappings were saved
        self.assertEqual(self.db.get_event_id('reminder-1'), 'gcal-event-1')
        self.assertEqual(self.db.get_event_id('reminder-2'), 'gcal-event-2')

    def test_full_sync_workflow_update_existing_events(self):
        """Test updating existing events when reminders change."""
        # Pre-save mappings
        self.db.save_mapping('reminder-3', 'gcal-event-3')

        # Mock updated reminder
        mock_reminder = Mock()
        mock_reminder.uuid = 'reminder-3'
        mock_reminder.title = 'Updated title'
        mock_reminder.notes = 'Updated notes'
        mock_reminder.due_date = datetime(2025, 2, 1, 14, 0)
        mock_reminder.priority = 1
        mock_reminder.completed = False
        mock_reminder.location = 'New location'
        mock_reminder.modification_date = datetime.now()

        self.mock_reminders_reader.fetch_reminders.return_value = [mock_reminder]

        # Mock Google Calendar API
        mock_events = Mock()

        # Mock get() to return existing event
        existing_event = {
            'id': 'gcal-event-3',
            'summary': 'Old title',
            'description': '',
            'start': {'dateTime': '2025-01-15T10:00:00'},
            'end': {'dateTime': '2025-01-15T11:00:00'}
        }
        mock_events.get.return_value.execute.return_value = existing_event
        mock_events.update.return_value.execute.return_value = {'id': 'gcal-event-3'}
        self.mock_gcal_service.events.return_value = mock_events

        # Create services and sync
        gcal_writer = GoogleCalendarWriter(self.mock_gcal_service, self.calendar_id)
        engine = SyncEngine(
            self.mock_reminders_reader,
            gcal_writer,
            self.db,
            self.config
        )

        stats = engine.sync()

        # Verify update occurred
        self.assertEqual(stats.updated, 1)
        self.assertEqual(stats.created, 0)

    def test_full_sync_workflow_delete_completed_events(self):
        """Test deleting events for completed reminders."""
        # Pre-save mapping
        self.db.save_mapping('reminder-4', 'gcal-event-4')

        # Mock completed reminder
        mock_reminder = Mock()
        mock_reminder.uuid = 'reminder-4'
        mock_reminder.title = 'Completed task'
        mock_reminder.notes = ''
        mock_reminder.due_date = datetime(2025, 1, 15, 10, 0)
        mock_reminder.priority = 1
        mock_reminder.completed = True
        mock_reminder.completion_date = datetime.now()
        mock_reminder.location = None

        self.mock_reminders_reader.fetch_reminders.return_value = [mock_reminder]

        # Mock Google Calendar API
        mock_events = Mock()
        mock_events.delete.return_value.execute.return_value = None
        self.mock_gcal_service.events.return_value = mock_events

        # Create services and sync
        gcal_writer = GoogleCalendarWriter(self.mock_gcal_service, self.calendar_id)
        engine = SyncEngine(
            self.mock_reminders_reader,
            gcal_writer,
            self.db,
            self.config
        )

        stats = engine.sync()

        # Verify deletion
        self.assertEqual(stats.deleted, 1)

        # Verify mapping was removed
        self.assertIsNone(self.db.get_event_id('reminder-4'))

    def test_full_sync_workflow_cleanup_deleted_reminders(self):
        """Test cleanup of events for deleted reminders."""
        # Pre-save mappings for reminders that no longer exist
        self.db.save_mapping('old-reminder-1', 'old-event-1')
        self.db.save_mapping('old-reminder-2', 'old-event-2')

        # Mock empty reminder list (all reminders deleted)
        self.mock_reminders_reader.fetch_reminders.return_value = []

        # Mock Google Calendar API
        mock_events = Mock()
        mock_events.delete.return_value.execute.return_value = None
        self.mock_gcal_service.events.return_value = mock_events

        # Create services and sync
        gcal_writer = GoogleCalendarWriter(self.mock_gcal_service, self.calendar_id)
        engine = SyncEngine(
            self.mock_reminders_reader,
            gcal_writer,
            self.db,
            self.config
        )

        stats = engine.sync()

        # Verify cleanup
        self.assertEqual(stats.deleted, 2)

        # Verify mappings were removed
        self.assertIsNone(self.db.get_event_id('old-reminder-1'))
        self.assertIsNone(self.db.get_event_id('old-reminder-2'))

    def test_full_sync_workflow_mixed_operations(self):
        """Test sync with mixed create/update/delete operations."""
        # Pre-save some mappings
        self.db.save_mapping('existing-reminder', 'existing-event')
        self.db.save_mapping('to-delete', 'deleted-event')

        # Mock reminders: 1 existing (to update), 1 new (to create)
        mock_existing = Mock()
        mock_existing.uuid = 'existing-reminder'
        mock_existing.title = 'Updated'
        mock_existing.notes = 'Updated'
        mock_existing.due_date = datetime.now()
        mock_existing.priority = 1
        mock_existing.completed = False
        mock_existing.location = None
        mock_existing.modification_date = datetime.now()

        mock_new = Mock()
        mock_new.uuid = 'new-reminder'
        mock_new.title = 'New'
        mock_new.notes = 'New'
        mock_new.due_date = datetime.now()
        mock_new.priority = 1
        mock_new.completed = False
        mock_new.location = None
        mock_new.modification_date = datetime.now()

        self.mock_reminders_reader.fetch_reminders.return_value = [
            mock_existing,
            mock_new
        ]

        # Mock Google Calendar API
        mock_events = Mock()

        # Mock get() for update
        existing_event = {
            'id': 'existing-event',
            'summary': 'Old',
            'description': '',
            'start': {'dateTime': '2025-01-15T10:00:00'},
            'end': {'dateTime': '2025-01-15T11:00:00'}
        }
        mock_events.get.return_value.execute.return_value = existing_event
        mock_events.update.return_value.execute.return_value = {'id': 'existing-event'}
        mock_events.insert.return_value.execute.return_value = {'id': 'new-event'}
        mock_events.delete.return_value.execute.return_value = None
        self.mock_gcal_service.events.return_value = mock_events

        # Create services and sync
        gcal_writer = GoogleCalendarWriter(self.mock_gcal_service, self.calendar_id)
        engine = SyncEngine(
            self.mock_reminders_reader,
            gcal_writer,
            self.db,
            self.config
        )

        stats = engine.sync()

        # Verify mixed operations
        self.assertEqual(stats.total_reminders, 2)
        self.assertEqual(stats.created, 1)
        self.assertEqual(stats.updated, 1)
        self.assertEqual(stats.deleted, 1)  # 'to-delete' was cleaned up


class TestDatabasePersistence(unittest.TestCase):
    """Test database persistence across sessions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'persistent.db'

    def tearDown(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_database_persistence(self):
        """Test that database persists data across instances."""
        # Create database and save data
        db1 = MappingDatabase(str(self.db_path))
        db1.save_mapping('test-uuid', 'test-event-id')

        # Close and reopen database
        del db1
        db2 = MappingDatabase(str(self.db_path))

        # Verify data persists
        result = db2.get_event_id('test-uuid')
        self.assertEqual(result, 'test-event-id')


if __name__ == '__main__':
    unittest.main()
