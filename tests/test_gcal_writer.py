"""
Unit tests for gcal_writer module.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gcal_writer import GoogleCalendarWriter


class TestGoogleCalendarWriter(unittest.TestCase):
    """Test GoogleCalendarWriter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock()
        self.calendar_id = 'test-calendar-id'
        self.writer = GoogleCalendarWriter(self.mock_service, self.calendar_id)

    def test_initialization(self):
        """Test GoogleCalendarWriter initialization."""
        self.assertEqual(self.writer.service, self.mock_service)
        self.assertEqual(self.writer.calendar_id, self.calendar_id)

    def test_get_priority_color_default(self):
        """Test default priority color mapping."""
        # No custom colors
        result = self.writer.get_priority_color(1, {})
        self.assertEqual(result, '11')  # High priority = red

        result = self.writer.get_priority_color(5, {})
        self.assertEqual(result, '5')   # Medium priority = yellow

        result = self.writer.get_priority_color(9, {})
        self.assertEqual(result, '7')   # Low priority = '7'

    def test_get_priority_color_custom(self):
        """Test custom priority color mapping."""
        custom_colors = {
            'high': '9',
            'medium': '3',
            'low': '7'
        }

        result = self.writer.get_priority_color(1, custom_colors)
        self.assertEqual(result, '9')

        result = self.writer.get_priority_color(5, custom_colors)
        self.assertEqual(result, '3')

        result = self.writer.get_priority_color(9, custom_colors)
        self.assertEqual(result, '7')

    def test_create_event_success(self):
        """Test successful event creation."""
        # Mock API response
        mock_events = Mock()
        mock_insert = Mock()
        mock_execute = Mock(return_value={'id': 'created-event-123'})

        mock_insert.execute = mock_execute
        mock_events.insert.return_value = mock_insert
        self.mock_service.events.return_value = mock_events

        # Create event
        result = self.writer.create_event(
            summary='Test Event',
            description='Test Description',
            start_datetime=datetime(2025, 1, 15, 10, 0),
            end_datetime=datetime(2025, 1, 15, 11, 0),
            color_id='11',
            reminder_uuid='test-uuid-123'
        )

        # Verify API was called
        mock_events.insert.assert_called_once()
        self.assertEqual(result['id'], 'created-event-123')

    def test_create_all_day_event(self):
        """Test creating all-day event."""
        mock_events = Mock()
        mock_insert = Mock()
        mock_execute = Mock(return_value={'id': 'all-day-event-456'})

        mock_insert.execute = mock_execute
        mock_events.insert.return_value = mock_insert
        self.mock_service.events.return_value = mock_events

        # Create all-day event
        result = self.writer.create_event(
            summary='All Day Event',
            description='',
            start_datetime=datetime(2025, 1, 20),
            end_datetime=datetime(2025, 1, 20),
            all_day=True
        )

        # Verify event was created
        self.assertEqual(result['id'], 'all-day-event-456')

        # Verify insert was called with date format
        call_args = mock_events.insert.call_args
        event_body = call_args[1]['body']

        # All-day events should use 'date' not 'dateTime'
        self.assertIn('date', event_body['start'])
        self.assertNotIn('dateTime', event_body['start'])

    def test_create_event_with_location(self):
        """Test creating event with location."""
        mock_events = Mock()
        mock_insert = Mock()
        mock_execute = Mock(return_value={'id': 'event-with-location-789'})

        mock_insert.execute = mock_execute
        mock_events.insert.return_value = mock_insert
        self.mock_service.events.return_value = mock_events

        # Create event with location
        result = self.writer.create_event(
            summary='Meeting',
            description='Team meeting',
            start_datetime=datetime(2025, 1, 25, 14, 0),
            end_datetime=datetime(2025, 1, 25, 15, 0),
            location='Conference Room A'
        )

        # Verify location was included
        call_args = mock_events.insert.call_args
        event_body = call_args[1]['body']
        self.assertEqual(event_body['location'], 'Conference Room A')

    def test_create_event_api_error(self):
        """Test handling API error during event creation."""
        mock_events = Mock()
        mock_insert = Mock()
        mock_insert.execute.side_effect = Exception('API Error')

        mock_events.insert.return_value = mock_insert
        self.mock_service.events.return_value = mock_events

        # Create event should return None on error
        result = self.writer.create_event(
            summary='Test Event',
            start_datetime=datetime.now(),
            end_datetime=datetime.now()
        )

        self.assertIsNone(result)

    def test_update_event_success(self):
        """Test successful event update."""
        mock_events = Mock()

        # Mock get() to return existing event
        mock_get = Mock()
        existing_event = {
            'id': 'existing-event-id',
            'summary': 'Old Title',
            'description': 'Old description',
            'start': {'dateTime': '2025-01-15T10:00:00'},
            'end': {'dateTime': '2025-01-15T11:00:00'}
        }
        mock_get.execute.return_value = existing_event
        mock_events.get.return_value = mock_get

        # Mock update()
        mock_update = Mock()
        mock_update.execute.return_value = {'id': 'updated-event-123'}
        mock_events.update.return_value = mock_update

        self.mock_service.events.return_value = mock_events

        # Update event
        result = self.writer.update_event(
            event_id='existing-event-id',
            summary='Updated Event',
            description='Updated description',
            start_datetime=datetime(2025, 2, 1, 10, 0),
            end_datetime=datetime(2025, 2, 1, 11, 0)
        )

        # Verify API was called
        mock_events.get.assert_called_once()
        mock_events.update.assert_called_once()
        self.assertIsNotNone(result)

    def test_update_event_api_error(self):
        """Test handling API error during event update."""
        mock_events = Mock()
        mock_get = Mock()
        mock_get.execute.side_effect = Exception('Get failed')

        mock_events.get.return_value = mock_get
        self.mock_service.events.return_value = mock_events

        # Update should return None on error
        result = self.writer.update_event(
            event_id='event-id',
            summary='Test',
            start_datetime=datetime.now(),
            end_datetime=datetime.now()
        )

        self.assertIsNone(result)

    def test_delete_event_success(self):
        """Test successful event deletion."""
        mock_events = Mock()
        mock_delete = Mock()
        mock_delete.execute.return_value = None

        mock_events.delete.return_value = mock_delete
        self.mock_service.events.return_value = mock_events

        # Delete event
        result = self.writer.delete_event('event-to-delete')

        # Verify API was called
        mock_events.delete.assert_called_once_with(
            calendarId=self.calendar_id,
            eventId='event-to-delete'
        )
        self.assertTrue(result)

    def test_delete_event_api_error(self):
        """Test handling API error during event deletion."""
        mock_events = Mock()
        mock_delete = Mock()
        mock_delete.execute.side_effect = Exception('Delete failed')

        mock_events.delete.return_value = mock_delete
        self.mock_service.events.return_value = mock_events

        # Delete should return False on error
        result = self.writer.delete_event('event-id')
        self.assertFalse(result)


    def test_create_event_without_end_datetime(self):
        """Test creating event without explicit end time."""
        mock_events = Mock()
        mock_insert = Mock()
        mock_execute = Mock(return_value={'id': 'no-end-event-999'})

        mock_insert.execute = mock_execute
        mock_events.insert.return_value = mock_insert
        self.mock_service.events.return_value = mock_events

        start = datetime(2025, 4, 1, 10, 0)

        # Create event without end_datetime (should default to start + 1 hour)
        result = self.writer.create_event(
            summary='Quick Event',
            start_datetime=start,
            end_datetime=None
        )

        # Verify event was created
        self.assertIsNotNone(result)

        # Verify end time was set
        call_args = mock_events.insert.call_args
        event_body = call_args[1]['body']
        self.assertIn('end', event_body)


if __name__ == '__main__':
    unittest.main()
