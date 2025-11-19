"""Unit tests for WatchMonitor and FileChangeHandler (TDD RED phase for T017).

Tests cover:
- File modifications in monitored directories
- New files created
- Excluded patterns (ignored files)
- Config file changes
"""

from pathlib import Path
from unittest.mock import Mock, patch
import time

import pytest

from ansibledoctor.watcher.monitor import WatchMonitor
from ansibledoctor.watcher.handler import FileChangeHandler


class TestFileChangeHandler:
    """Test suite for FileChangeHandler class."""

    def test_handler_calls_callback_on_file_modification(self):
        """Handler should call callback when monitored file is modified."""
        callback = Mock()
        handler = FileChangeHandler(callback, debounce_delay=0.05)
        
        # Create mock event for file modification
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = "/role/defaults/main.yml"
        
        handler.on_modified(mock_event)
        
        # Wait for debounce
        time.sleep(0.1)
        
        # Callback should be called
        assert callback.call_count == 1

    def test_handler_ignores_directory_events(self):
        """Handler should ignore directory modification events."""
        callback = Mock()
        handler = FileChangeHandler(callback, debounce_delay=0.05)
        
        # Create mock event for directory
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = "/role/defaults"
        
        handler.on_modified(mock_event)
        time.sleep(0.1)
        
        # Callback should not be called
        assert callback.call_count == 0

    def test_handler_ignores_excluded_patterns(self):
        """Handler should ignore files matching exclude patterns."""
        callback = Mock()
        handler = FileChangeHandler(
            callback,
            debounce_delay=0.05,
            exclude_patterns=["*.pyc", "__pycache__", ".git"]
        )
        
        # Test .pyc file
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = "/role/test.pyc"
        
        handler.on_modified(mock_event)
        time.sleep(0.1)
        
        assert callback.call_count == 0

    def test_handler_processes_yaml_files(self):
        """Handler should process YAML file changes."""
        callback = Mock()
        handler = FileChangeHandler(callback, debounce_delay=0.05)
        
        yaml_files = [
            "/role/defaults/main.yml",
            "/role/vars/main.yaml",
            "/role/tasks/install.yml",
            "/role/.ansibledoctor.yml"
        ]
        
        for yaml_file in yaml_files:
            mock_event = Mock()
            mock_event.is_directory = False
            mock_event.src_path = yaml_file
            
            handler.on_modified(mock_event)
        
        time.sleep(0.1)
        
        # Should trigger callback (debounced to single call)
        assert callback.call_count >= 1

    def test_handler_debounces_multiple_changes(self):
        """Multiple rapid changes should debounce to single callback."""
        callback = Mock()
        handler = FileChangeHandler(callback, debounce_delay=0.1)
        
        # Trigger 5 changes rapidly
        for i in range(5):
            mock_event = Mock()
            mock_event.is_directory = False
            mock_event.src_path = f"/role/defaults/var{i}.yml"
            handler.on_modified(mock_event)
            time.sleep(0.02)
        
        time.sleep(0.15)
        
        # Should be called only once due to debouncing
        assert callback.call_count == 1


class TestWatchMonitor:
    """Test suite for WatchMonitor class."""

    @pytest.fixture
    def temp_role_dir(self, tmp_path):
        """Create temporary role directory structure."""
        role_dir = tmp_path / "test-role"
        role_dir.mkdir()
        
        # Create role subdirectories
        (role_dir / "defaults").mkdir()
        (role_dir / "vars").mkdir()
        (role_dir / "tasks").mkdir()
        (role_dir / "meta").mkdir()
        
        # Create sample files
        (role_dir / "defaults" / "main.yml").write_text("---\nvar1: value1\n")
        (role_dir / "tasks" / "main.yml").write_text("---\n- name: Task\n")
        
        return role_dir

    def test_monitor_initializes_with_role_path(self, temp_role_dir):
        """WatchMonitor should initialize with valid role path."""
        callback = Mock()
        monitor = WatchMonitor(temp_role_dir, callback)
        
        assert monitor.role_path == temp_role_dir
        assert monitor.callback == callback

    def test_monitor_starts_and_stops_cleanly(self, temp_role_dir):
        """WatchMonitor should start and stop without errors."""
        callback = Mock()
        monitor = WatchMonitor(temp_role_dir, callback)
        
        monitor.start()
        assert monitor.is_running()
        
        time.sleep(0.2)
        
        monitor.stop()
        time.sleep(0.1)
        assert not monitor.is_running()

    def test_monitor_detects_file_modification(self, temp_role_dir):
        """WatchMonitor should detect when monitored files are modified."""
        callback = Mock()
        monitor = WatchMonitor(temp_role_dir, callback, debounce_delay=0.1)
        
        monitor.start()
        time.sleep(0.2)
        
        # Modify a file
        defaults_file = temp_role_dir / "defaults" / "main.yml"
        defaults_file.write_text("---\nvar1: modified\n")
        
        # Wait for detection and debounce
        time.sleep(0.5)
        
        monitor.stop()
        
        # Callback should have been triggered
        assert callback.call_count >= 1

    def test_monitor_detects_new_file_creation(self, temp_role_dir):
        """WatchMonitor should detect when new files are created."""
        callback = Mock()
        monitor = WatchMonitor(temp_role_dir, callback, debounce_delay=0.1)
        
        monitor.start()
        time.sleep(0.2)
        
        # Create new file
        new_file = temp_role_dir / "vars" / "new.yml"
        new_file.write_text("---\nnew_var: value\n")
        
        time.sleep(0.5)
        monitor.stop()
        
        assert callback.call_count >= 1

    def test_monitor_respects_exclude_patterns(self, temp_role_dir):
        """WatchMonitor should ignore files matching exclude patterns."""
        callback = Mock()
        monitor = WatchMonitor(
            temp_role_dir,
            callback,
            exclude_patterns=["*.tmp", "test_*"],
            debounce_delay=0.1
        )
        
        monitor.start()
        time.sleep(0.2)
        
        # Create excluded file
        excluded_file = temp_role_dir / "test_temp.tmp"
        excluded_file.write_text("temporary")
        
        time.sleep(0.5)
        monitor.stop()
        
        # Should not trigger callback
        assert callback.call_count == 0

    def test_monitor_watches_config_file_changes(self, temp_role_dir):
        """WatchMonitor should detect .ansibledoctor.yml changes."""
        callback = Mock()
        monitor = WatchMonitor(temp_role_dir, callback, debounce_delay=0.1)
        
        monitor.start()
        time.sleep(0.2)
        
        # Create/modify config file
        config_file = temp_role_dir / ".ansibledoctor.yml"
        config_file.write_text("output_format: html\n")
        
        time.sleep(0.5)
        monitor.stop()
        
        assert callback.call_count >= 1
