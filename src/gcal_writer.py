"""
Google Calendar writer module.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleCalendarWriter:
    """Write events to Google Calendar."""

    def __init__(self, service, calendar_id: str = 'primary'):
        """
        Initialize Google Calendar writer.

        Args:
            service: Authenticated Google Calendar API service
            calendar_id: Target calendar ID (default: 'primary')
        """
        self.service = service
        self.calendar_id = calendar_id

    def create_event(
        self,
        summary: str,
        description: str = "",
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        color_id: Optional[str] = None,
        reminder_uuid: Optional[str] = None,
        all_day: bool = False,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a new event in Google Calendar.

        Args:
            summary: Event title
            description: Event description
            start_datetime: Event start time (None = today)
            end_datetime: Event end time (None = start + 1 hour for timed, same day for all-day)
            color_id: Google Calendar color ID (1-11)
            reminder_uuid: Original reminder UUID (stored in extended properties)
            all_day: Whether this is an all-day event

        Returns:
            Created event dict or None on failure
        """
        try:
            # Default to today if no start time
            if start_datetime is None:
                start_datetime = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

            # Default end time
            if end_datetime is None:
                if all_day:
                    end_datetime = start_datetime
                else:
                    end_datetime = start_datetime + timedelta(hours=1)

            # Build event body
            event = {
                'summary': summary,
                'description': description,
            }

            # Add location if provided
            if location:
                event['location'] = location

            # Set start/end time
            if all_day:
                # All-day event uses date format
                event['start'] = {'date': start_datetime.strftime('%Y-%m-%d')}
                event['end'] = {'date': (end_datetime + timedelta(days=1)).strftime('%Y-%m-%d')}
            else:
                # Timed event uses dateTime format with local timezone
                event['start'] = {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Seoul',
                }
                event['end'] = {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Seoul',
                }

            # Add color if specified
            if color_id:
                event['colorId'] = str(color_id)

            # Store reminder UUID in extended properties for tracking
            if reminder_uuid:
                event['extendedProperties'] = {
                    'private': {
                        'reminderUUID': reminder_uuid
                    }
                }

            # Create event
            logger.debug(f"Creating event: {summary}")
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            logger.info(f"Created event: {summary} (ID: {created_event['id']})")
            return created_event

        except HttpError as e:
            logger.error(f"Error creating event '{summary}': {e}")
            return None

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        color_id: Optional[str] = None,
        all_day: bool = False,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update an existing event.

        Args:
            event_id: Google Calendar event ID
            summary: New event title
            description: New event description
            start_datetime: New start time
            end_datetime: New end time
            color_id: New color ID
            all_day: Whether this is an all-day event

        Returns:
            Updated event dict or None on failure
        """
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            # Update fields if provided
            if summary is not None:
                event['summary'] = summary

            if description is not None:
                event['description'] = description

            if start_datetime is not None:
                if all_day:
                    event['start'] = {'date': start_datetime.strftime('%Y-%m-%d')}
                else:
                    event['start'] = {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'Asia/Seoul',
                    }

            if end_datetime is not None:
                if all_day:
                    event['end'] = {'date': (end_datetime + timedelta(days=1)).strftime('%Y-%m-%d')}
                else:
                    event['end'] = {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'Asia/Seoul',
                    }

            if color_id is not None:
                event['colorId'] = str(color_id)

            if location is not None:
                event['location'] = location

            # Update event
            logger.debug(f"Updating event ID: {event_id}")
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            logger.info(f"Updated event: {updated_event.get('summary')} (ID: {event_id})")
            return updated_event

        except HttpError as e:
            logger.error(f"Error updating event '{event_id}': {e}")
            return None

    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event.

        Args:
            event_id: Google Calendar event ID

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Deleting event ID: {event_id}")
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            logger.info(f"Deleted event ID: {event_id}")
            return True

        except HttpError as e:
            logger.error(f"Error deleting event '{event_id}': {e}")
            return False

    def find_event_by_reminder_uuid(self, reminder_uuid: str) -> Optional[Dict]:
        """
        Find an event by its reminder UUID (stored in extended properties).

        Args:
            reminder_uuid: Original reminder UUID

        Returns:
            Event dict or None if not found
        """
        try:
            # Search for events with this reminder UUID
            # Note: privateExtendedProperty search is limited, so we fetch all and filter
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                privateExtendedProperty=f'reminderUUID={reminder_uuid}',
                maxResults=1
            ).execute()

            events = events_result.get('items', [])
            if events:
                logger.debug(f"Found existing event for reminder UUID: {reminder_uuid}")
                return events[0]

            return None

        except HttpError as e:
            logger.error(f"Error searching for event with UUID {reminder_uuid}: {e}")
            return None

    def get_priority_color(self, priority: int, color_map: Dict[str, str]) -> str:
        """
        Map reminder priority to Google Calendar color.

        Args:
            priority: Reminder priority (0=none, 1-4=high, 5=medium, 6-9=low)
            color_map: Dict mapping priority levels to color IDs

        Returns:
            Color ID string
        """
        if priority == 0:
            return color_map.get('none', '1')
        elif 1 <= priority <= 4:
            return color_map.get('high', '11')
        elif priority == 5:
            return color_map.get('medium', '5')
        else:  # 6-9
            return color_map.get('low', '7')

    def batch_create_events(self, events: List[Dict]) -> List[Optional[Dict]]:
        """
        Create multiple events in batch.

        Args:
            events: List of event dicts with fields for create_event()

        Returns:
            List of created event dicts (None for failed creations)
        """
        results = []
        for event_data in events:
            result = self.create_event(**event_data)
            results.append(result)

        return results


def main():
    """Test function."""
    logging.basicConfig(level=logging.INFO)
    print("gcal_writer.py - Run through main sync script")


if __name__ == "__main__":
    main()
