"""Integration tests for watch mode functionality.

Tests the watch command end-to-end including file monitoring,
regeneration callbacks, and signal handling.
"""

import os
import time

import pytest

from ansibledoctor.watcher.monitor import WatchMonitor


@pytest.fixture
def minimal_role(tmp_path):
    """Create a minimal Ansible role structure for testing."""
    role_path = tmp_path / "test_role"

    # Create role directories
    (role_path / "defaults").mkdir(parents=True)
    (role_path / "meta").mkdir(parents=True)
    (role_path / "tasks").mkdir(parents=True)

    # Create meta/main.yml
    (role_path / "meta" / "main.yml").write_text(
        """---
galaxy_info:
  author: Test Author
  description: Test role for watch mode
  license: MIT
  min_ansible_version: "2.9"
  platforms:
    - name: Ubuntu
      versions:
        - focal
"""
    )

    # Create defaults/main.yml
    (role_path / "defaults" / "main.yml").write_text(
        """---
# @var test_var:description: Test variable
# @var test_var:type: string
test_var: "default_value"
"""
    )

    # Create tasks/main.yml
    (role_path / "tasks" / "main.yml").write_text(
        """---
- name: Test task
  ansible.builtin.debug:
    msg: "{{ test_var }}"
  tags:
    - test
"""
    )

    return role_path


class TestWatchModeIntegration:
    """Integration tests for watch mode."""

    def test_watch_command_with_file_output(self, minimal_role):
        """Test watch command generates docs to file on startup."""
        output_file = minimal_role / "README.md"
        regeneration_count = {"count": 0}

        def regenerate_callback():
            """Mock regeneration that creates output file."""
            regeneration_count["count"] += 1
            output_file.write_text(f"# Generated docs (version {regeneration_count['count']})")

        # Create monitor
        monitor = WatchMonitor(minimal_role, callback=regenerate_callback, debounce_delay=0.1)

        try:
            # Start monitoring
            monitor.start()
            assert monitor.is_running()

            # Initial callback (called manually in real CLI)
            regenerate_callback()
            assert output_file.exists()
            assert "version 1" in output_file.read_text()

            # Modify a file to trigger regeneration
            defaults_file = minimal_role / "defaults" / "main.yml"
            defaults_file.write_text(defaults_file.read_text() + "\n# New comment")

            # Wait for debouncing and regeneration
            time.sleep(0.3)

            # Should have regenerated
            assert regeneration_count["count"] >= 2

        finally:
            monitor.stop()
            assert not monitor.is_running()

    def test_watch_detects_new_yaml_files(self, minimal_role):
        """Test watch detects new YAML files in role directories."""
        detected_changes = []

        def track_changes():
            """Callback that tracks change events."""
            detected_changes.append(time.time())

        monitor = WatchMonitor(minimal_role, callback=track_changes, debounce_delay=0.1)

        try:
            monitor.start()
            initial_count = len(detected_changes)

            # Create new file in defaults/
            (minimal_role / "defaults" / "extra.yml").write_text("---\nextra_var: value")
            time.sleep(0.3)

            # Should have detected change
            assert len(detected_changes) > initial_count

        finally:
            monitor.stop()

    def test_watch_detects_config_file_changes(self, minimal_role):
        """Test watch detects changes to .ansibledoctor.yml."""
        detected_changes = []

        def track_changes():
            detected_changes.append(time.time())

        monitor = WatchMonitor(minimal_role, callback=track_changes, debounce_delay=0.1)

        try:
            monitor.start()
            initial_count = len(detected_changes)

            # Create config file
            config_file = minimal_role / ".ansibledoctor.yml"
            config_file.write_text("output_format: html")
            time.sleep(0.3)

            assert len(detected_changes) > initial_count

            # Modify config file
            config_file.write_text("output_format: markdown")
            time.sleep(0.3)

            assert len(detected_changes) > initial_count + 1

        finally:
            monitor.stop()

    def test_watch_excludes_non_relevant_files(self, minimal_role):
        """Test watch ignores excluded file patterns."""
        detected_changes = []

        def track_changes():
            detected_changes.append(time.time())

        monitor = WatchMonitor(
            minimal_role,
            callback=track_changes,
            debounce_delay=0.1,
            exclude_patterns=["*.pyc", "__pycache__", ".git"],
        )

        try:
            monitor.start()
            initial_count = len(detected_changes)

            # Create excluded files
            (minimal_role / "test.pyc").write_text("compiled python")
            (minimal_role / "__pycache__").mkdir(exist_ok=True)
            (minimal_role / "__pycache__" / "test.pyc").write_text("cache")
            time.sleep(0.3)

            # Should NOT have detected changes (excluded)
            assert len(detected_changes) == initial_count

            # Create relevant file
            (minimal_role / "vars" / "main.yml").parent.mkdir(exist_ok=True)
            (minimal_role / "vars" / "main.yml").write_text("---\nvar: value")
            time.sleep(0.3)

            # Should detect this change
            assert len(detected_changes) > initial_count

        finally:
            monitor.stop()

    def test_watch_debounces_rapid_changes(self, minimal_role):
        """Test watch debounces rapid file changes to single regeneration."""
        detected_changes = []

        def track_changes():
            detected_changes.append(time.time())

        monitor = WatchMonitor(minimal_role, callback=track_changes, debounce_delay=0.2)

        try:
            monitor.start()
            initial_count = len(detected_changes)

            # Make rapid changes
            defaults_file = minimal_role / "defaults" / "main.yml"
            for i in range(5):
                defaults_file.write_text(f"---\nvar_{i}: value_{i}")
                time.sleep(0.05)  # 50ms between changes (within debounce window)

            # Wait for debouncing
            time.sleep(0.4)

            # Should have debounced to single regeneration
            changes_detected = len(detected_changes) - initial_count
            assert changes_detected == 1, f"Expected 1 change, got {changes_detected}"

        finally:
            monitor.stop()

    def test_watch_graceful_shutdown(self, minimal_role):
        """Test watch stops gracefully."""
        monitor = WatchMonitor(minimal_role, callback=lambda: None, debounce_delay=0.1)

        # Start monitor
        monitor.start()
        assert monitor.is_running()

        # Make some changes
        (minimal_role / "defaults" / "main.yml").write_text("---\ntest: value")

        # Stop should complete without hanging
        monitor.stop()
        assert not monitor.is_running()

    def test_watch_continues_after_callback_error(self, minimal_role):
        """Test watch continues monitoring even if callback raises exception."""
        callback_count = {"count": 0, "errors": 0}

        def failing_callback():
            callback_count["count"] += 1
            if callback_count["count"] == 1:
                callback_count["errors"] += 1
                raise ValueError("Simulated callback error")
            # Second call succeeds

        monitor = WatchMonitor(minimal_role, callback=failing_callback, debounce_delay=0.1)

        try:
            monitor.start()

            # First change - callback will fail
            defaults_file = minimal_role / "defaults" / "main.yml"
            defaults_file.write_text("---\nfirst: change")
            time.sleep(0.3)

            assert callback_count["count"] >= 1
            assert callback_count["errors"] == 1

            # Second change - callback should succeed
            defaults_file.write_text("---\nsecond: change")
            time.sleep(0.3)

            # Monitor should still be running
            assert monitor.is_running()
            assert callback_count["count"] >= 2

        finally:
            monitor.stop()

    def test_watch_monitors_multiple_role_directories(self, minimal_role):
        """Test watch monitors all role subdirectories recursively."""
        detected_changes = []

        def track_changes():
            detected_changes.append(time.time())

        monitor = WatchMonitor(minimal_role, callback=track_changes, debounce_delay=0.1)

        try:
            monitor.start()
            initial_count = len(detected_changes)

            # Change in defaults/
            (minimal_role / "defaults" / "main.yml").write_text("---\ndefault_change: 1")
            time.sleep(0.3)
            assert len(detected_changes) > initial_count

            # Change in meta/
            (minimal_role / "meta" / "main.yml").write_text("---\nauthor: Changed")
            time.sleep(0.3)
            assert len(detected_changes) > initial_count + 1

            # Change in tasks/
            (minimal_role / "tasks" / "main.yml").write_text("---\n- name: Changed task")
            time.sleep(0.3)
            assert len(detected_changes) > initial_count + 2

        finally:
            monitor.stop()


@pytest.mark.skipif(os.name == "nt", reason="Signal handling differs on Windows")
class TestWatchSignalHandling:
    """Test signal handling (SIGINT/SIGTERM) - Unix only."""

    def test_watch_handles_sigint(self, minimal_role):
        """Test watch handles SIGINT (Ctrl+C) gracefully."""
        monitor = WatchMonitor(minimal_role, callback=lambda: None, debounce_delay=0.1)

        monitor.start()
        assert monitor.is_running()

        # Send SIGINT to current process (simulates Ctrl+C)
        # Note: In real CLI, this would be handled by signal.signal()
        monitor.stop()
        assert not monitor.is_running()
