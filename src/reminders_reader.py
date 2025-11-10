"""
Apple Reminders reader using EventKit framework.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import EventKit
from Foundation import NSDate, NSPredicate

logger = logging.getLogger(__name__)


class Reminder:
    """Represents a reminder from Apple Reminders."""

    def __init__(self, ek_reminder):
        """
        Initialize from EventKit reminder.

        Args:
            ek_reminder: EKReminder object from EventKit
        """
        self.uuid = str(ek_reminder.calendarItemIdentifier())
        self.title = str(ek_reminder.title()) if ek_reminder.title() else "Untitled"
        self.notes = str(ek_reminder.notes()) if ek_reminder.notes() else ""
        self.completed = bool(ek_reminder.isCompleted())
        self.completion_date = self._convert_date(ek_reminder.completionDate())
        self.due_date = self._convert_date(ek_reminder.dueDateComponents())
        self.priority = int(ek_reminder.priority())
        self.calendar_title = str(ek_reminder.calendar().title()) if ek_reminder.calendar() else "Unknown"
        self.creation_date = self._convert_date(ek_reminder.creationDate())
        self.modification_date = self._convert_date(ek_reminder.lastModifiedDate())

        # Extract location from alarms
        self.location = self._extract_location(ek_reminder)

    @staticmethod
    def _extract_location(ek_reminder) -> Optional[str]:
        """
        Extract location from reminder alarms.

        Args:
            ek_reminder: EKReminder object from EventKit

        Returns:
            Location string or None
        """
        try:
            alarms = ek_reminder.alarms()
            if alarms:
                for alarm in alarms:
                    # Check for location-based alarm
                    structured_location = alarm.structuredLocation()
                    if structured_location:
                        title = structured_location.title()
                        if title:
                            return str(title)
        except Exception as e:
            logger.debug(f"Error extracting location: {e}")
        return None

    @staticmethod
    def _convert_date(date_obj) -> Optional[datetime]:
        """
        Convert NSDate or NSDateComponents to Python datetime.

        Args:
            date_obj: NSDate or NSDateComponents object

        Returns:
            Python datetime or None
        """
        if date_obj is None:
            return None

        # Handle NSDateComponents (used for due dates)
        if hasattr(date_obj, 'date'):
            date_obj = date_obj.date()

        # Handle NSDate
        if isinstance(date_obj, NSDate):
            timestamp = date_obj.timeIntervalSince1970()
            return datetime.fromtimestamp(timestamp)

        return None

    def to_dict(self) -> Dict:
        """Convert reminder to dictionary."""
        return {
            'uuid': self.uuid,
            'title': self.title,
            'notes': self.notes,
            'completed': self.completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'calendar_title': self.calendar_title,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'modification_date': self.modification_date.isoformat() if self.modification_date else None,
            'location': self.location,
        }

    def __repr__(self):
        return f"Reminder(title='{self.title}', uuid='{self.uuid}', completed={self.completed})"


class RemindersReader:
    """Read reminders from Apple Reminders app using EventKit."""

    def __init__(self):
        """Initialize EventKit event store."""
        self.event_store = EventKit.EKEventStore.alloc().init()
        self._request_access()

    def _request_access(self):
        """Request access to reminders."""
        # Check current authorization status
        auth_status = EventKit.EKEventStore.authorizationStatusForEntityType_(
            EventKit.EKEntityTypeReminder
        )

        if auth_status == EventKit.EKAuthorizationStatusNotDetermined:
            logger.info("Requesting access to Reminders...")
            # Request access (this will show a system dialog)
            granted = [False]  # Use list to modify in closure

            def completion_handler(granted_val, error):
                granted[0] = granted_val
                if error:
                    logger.error(f"Error requesting access: {error}")

            self.event_store.requestAccessToEntityType_completion_(
                EventKit.EKEntityTypeReminder,
                completion_handler
            )

            # Note: In a real app, this would be async. For CLI, we assume user grants permission.
            import time
            time.sleep(1)  # Give time for dialog to appear

        elif auth_status == EventKit.EKAuthorizationStatusAuthorized:
            logger.info("Access to Reminders already granted")
        elif auth_status == EventKit.EKAuthorizationStatusDenied:
            raise PermissionError(
                "Access to Reminders denied. Please enable in System Settings > "
                "Privacy & Security > Reminders"
            )
        elif auth_status == EventKit.EKAuthorizationStatusRestricted:
            raise PermissionError("Access to Reminders is restricted by system policy")

    def get_all_calendars(self) -> List[str]:
        """
        Get list of all reminder calendars (lists).

        Returns:
            List of calendar names
        """
        calendars = self.event_store.calendarsForEntityType_(EventKit.EKEntityTypeReminder)
        return [str(cal.title()) for cal in calendars]

    def fetch_reminders(self, calendar_names: Optional[List[str]] = None) -> List[Reminder]:
        """
        Fetch reminders from specified calendars.

        Args:
            calendar_names: List of calendar names to fetch from (None = all calendars)

        Returns:
            List of Reminder objects
        """
        # Get calendars to query
        all_calendars = self.event_store.calendarsForEntityType_(EventKit.EKEntityTypeReminder)

        if calendar_names:
            calendars = [
                cal for cal in all_calendars
                if str(cal.title()) in calendar_names
            ]
            if not calendars:
                logger.warning(f"No calendars found matching: {calendar_names}")
                return []
        else:
            calendars = list(all_calendars)

        logger.info(f"Fetching reminders from {len(calendars)} calendar(s)")

        # Fetch incomplete reminders
        incomplete_predicate = self.event_store.predicateForIncompleteRemindersWithDueDateStarting_ending_calendars_(
            None,  # Start date (None = no limit)
            None,  # End date (None = no limit)
            calendars
        )

        # Fetch completed reminders
        completed_predicate = self.event_store.predicateForCompletedRemindersWithCompletionDateStarting_ending_calendars_(
            None,  # Start date (None = no limit)
            None,  # End date (None = no limit)
            calendars
        )

        # Collect reminders
        all_reminders = []

        # Note: fetchRemindersMatchingPredicate is async in real usage
        # For simplicity, we use a synchronous approach here
        def fetch_with_predicate(predicate, label):
            reminders_found = []

            def completion_handler(ek_reminders):
                if ek_reminders:
                    reminders_found.extend(ek_reminders)

            self.event_store.fetchRemindersMatchingPredicate_completion_(
                predicate,
                completion_handler
            )

            # Wait for completion (in real app, use proper async handling)
            import time
            time.sleep(0.5)

            logger.info(f"Found {len(reminders_found)} {label} reminders")
            return reminders_found

        incomplete = fetch_with_predicate(incomplete_predicate, "incomplete")
        completed = fetch_with_predicate(completed_predicate, "completed")

        # Convert to Reminder objects
        for ek_reminder in incomplete + completed:
            try:
                reminder = Reminder(ek_reminder)
                all_reminders.append(reminder)
            except Exception as e:
                logger.error(f"Error processing reminder: {e}")

        logger.info(f"Total reminders fetched: {len(all_reminders)}")
        return all_reminders


def main():
    """Test function."""
    logging.basicConfig(level=logging.INFO)

    reader = RemindersReader()

    # List all calendars
    print("\nAvailable calendars:")
    for cal in reader.get_all_calendars():
        print(f"  - {cal}")

    # Fetch all reminders
    print("\nFetching all reminders...")
    reminders = reader.fetch_reminders()

    print(f"\nFound {len(reminders)} reminders:")
    for reminder in reminders[:5]:  # Show first 5
        print(f"  - {reminder}")


if __name__ == "__main__":
    main()
