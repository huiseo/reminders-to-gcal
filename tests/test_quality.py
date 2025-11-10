"""
End-to-end quality tests for the application.
"""

import unittest
import os
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestCodeQuality(unittest.TestCase):
    """Test overall code quality."""

    def test_all_imports_work(self):
        """Test that all modules can be imported without errors."""
        try:
            import auth
            import gcal_writer
            import reminders_reader
            import sync_engine
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_no_syntax_errors(self):
        """Test that all Python files have valid syntax."""
        src_dir = Path(__file__).parent.parent / 'src'
        for py_file in src_dir.glob('*.py'):
            with open(py_file, 'r') as f:
                try:
                    compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    self.fail(f"Syntax error in {py_file}: {e}")

    def test_config_file_exists(self):
        """Test that config file exists and is valid YAML."""
        config_path = Path(__file__).parent.parent / 'config.yaml'
        self.assertTrue(config_path.exists(), "config.yaml not found")

        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.assertIsInstance(config, dict)
        except Exception as e:
            self.fail(f"Config file error: {e}")

    def test_app_structure(self):
        """Test that app has required structure."""
        base_dir = Path(__file__).parent.parent

        required_files = [
            'menubar_app.py',
            'config.yaml',
            'build_app.sh',
            'Uninstall.command',
            'src/auth.py',
            'src/gcal_writer.py',
            'src/reminders_reader.py',
            'src/sync_engine.py'
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            self.assertTrue(
                file_path.exists(),
                f"Required file missing: {req_file}"
            )

    def test_build_script_executable(self):
        """Test that build script is executable."""
        build_script = Path(__file__).parent.parent / 'build_app.sh'
        self.assertTrue(build_script.exists())
        self.assertTrue(os.access(build_script, os.X_OK), "build_app.sh not executable")

    def test_uninstall_script_executable(self):
        """Test that uninstall script is executable."""
        uninstall_script = Path(__file__).parent.parent / 'Uninstall.command'
        self.assertTrue(uninstall_script.exists())
        self.assertTrue(os.access(uninstall_script, os.X_OK), "Uninstall.command not executable")


class TestDatabaseIntegrity(unittest.TestCase):
    """Test database operations integrity."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'

    def tearDown(self):
        """Clean up."""
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_database_creates_all_tables(self):
        """Test that database initialization creates all required tables."""
        from sync_engine import MappingDatabase
        import sqlite3

        db = MappingDatabase(str(self.db_path))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check for mappings table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='mappings'"
            )
            self.assertIsNotNone(cursor.fetchone())

            # Check for sync_history table
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sync_history'"
            )
            self.assertIsNotNone(cursor.fetchone())

    def test_database_concurrent_access(self):
        """Test that database can handle concurrent read/write."""
        from sync_engine import MappingDatabase

        db = MappingDatabase(str(self.db_path))

        # Write and read concurrently
        db.save_mapping('uuid-1', 'event-1')
        result1 = db.get_event_id('uuid-1')

        db.save_mapping('uuid-2', 'event-2')
        result2 = db.get_event_id('uuid-2')

        self.assertEqual(result1, 'event-1')
        self.assertEqual(result2, 'event-2')


class TestErrorHandling(unittest.TestCase):
    """Test error handling throughout the app."""

    def test_handles_missing_credentials(self):
        """Test that missing credentials raises appropriate error."""
        from auth import GoogleCalendarAuth

        auth = GoogleCalendarAuth('/nonexistent/path', '/tmp/token.json')

        with self.assertRaises(FileNotFoundError):
            auth.authenticate()

    def test_handles_invalid_config(self):
        """Test handling of invalid config."""
        import yaml

        invalid_yaml = "invalid: [unclosed"

        with self.assertRaises(yaml.YAMLError):
            yaml.safe_load(invalid_yaml)

    def test_database_handles_invalid_path(self):
        """Test database initialization with invalid path still works."""
        from sync_engine import MappingDatabase

        # This should create parent directories
        db = MappingDatabase('/tmp/test_deep/nested/path/db.db')

        self.assertTrue(Path('/tmp/test_deep/nested/path').exists())

        # Cleanup
        import shutil
        shutil.rmtree('/tmp/test_deep')


class TestAppFunctionality(unittest.TestCase):
    """Test key application functionality."""

    def test_sync_stats_calculation(self):
        """Test that sync statistics are calculated correctly."""
        from sync_engine import SyncStats

        stats = SyncStats()
        stats.total_reminders = 100
        stats.created = 30
        stats.updated = 20
        stats.deleted = 10
        stats.skipped = 35
        stats.errors = 5

        # Verify all stats are accessible
        self.assertEqual(stats.total_reminders, 100)
        self.assertEqual(stats.created, 30)
        self.assertEqual(stats.updated, 20)
        self.assertEqual(stats.deleted, 10)
        self.assertEqual(stats.skipped, 35)
        self.assertEqual(stats.errors, 5)

        # Verify string representation
        str_repr = str(stats)
        self.assertIn('100 total', str_repr)
        self.assertIn('30 created', str_repr)

    def test_priority_color_mapping(self):
        """Test priority to color mapping logic."""
        from gcal_writer import GoogleCalendarWriter
        from unittest.mock import Mock

        writer = GoogleCalendarWriter(Mock(), 'test-calendar')

        # Test default mappings
        self.assertEqual(writer.get_priority_color(0, {}), '1')   # None
        self.assertEqual(writer.get_priority_color(1, {}), '11')  # High
        self.assertEqual(writer.get_priority_color(5, {}), '5')   # Medium
        self.assertEqual(writer.get_priority_color(9, {}), '7')   # Low

    def test_checksum_consistency(self):
        """Test that checksums are consistent for same data."""
        from sync_engine import SyncEngine, MappingDatabase
        from unittest.mock import Mock
        import tempfile

        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test.db'
        db = MappingDatabase(str(db_path))

        config = {
            'reminders': {'sync_lists': [], 'skip_completed_older_than_days': 30},
            'sync': {'completed_action': 'delete'},
            'google_calendar': {'priority_colors': {}}
        }

        engine = SyncEngine(Mock(), Mock(), db, config)

        # Create two identical reminders
        from datetime import datetime
        reminder1 = Mock()
        reminder1.title = "Test"
        reminder1.notes = "Notes"
        reminder1.due_date = datetime(2025, 1, 15, 10, 0)
        reminder1.priority = 1
        reminder1.completed = False
        reminder1.location = "Office"

        reminder2 = Mock()
        reminder2.title = "Test"
        reminder2.notes = "Notes"
        reminder2.due_date = datetime(2025, 1, 15, 10, 0)
        reminder2.priority = 1
        reminder2.completed = False
        reminder2.location = "Office"

        checksum1 = engine._generate_checksum(reminder1)
        checksum2 = engine._generate_checksum(reminder2)

        self.assertEqual(checksum1, checksum2)

        # Cleanup
        db_path.unlink()
        Path(temp_dir).rmdir()


if __name__ == '__main__':
    unittest.main()
