"""Unit tests for Debouncer class (TDD RED phase for T016).

Tests cover:
- Single file change triggers callback after quiet period
- Burst of changes debounces to single callback
- Multiple files changing simultaneously debounce correctly
- clear() cancels pending callback
"""

import time
from unittest.mock import Mock

from ansibledoctor.watcher.debouncer import Debouncer


class TestDebouncer:
    """Test suite for Debouncer class."""

    def test_single_change_triggers_callback_after_delay(self):
        """Single file change should trigger callback after quiet period (500ms)."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.1)  # 100ms for faster tests

        debouncer.trigger()

        # Callback should not be called immediately
        assert callback.call_count == 0

        # Wait for delay period
        time.sleep(0.15)

        # Callback should be called once
        assert callback.call_count == 1

    def test_burst_of_changes_debounces_to_single_callback(self):
        """Burst of 10 changes should debounce to single callback."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.1)

        # Trigger 10 times rapidly
        for _ in range(10):
            debouncer.trigger()
            time.sleep(0.01)  # 10ms between triggers

        # Wait for delay period
        time.sleep(0.15)

        # Callback should be called only once despite 10 triggers
        assert callback.call_count == 1

    def test_multiple_files_changing_debounces_correctly(self):
        """Multiple files changing simultaneously should debounce correctly."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.1)

        # Simulate 3 files changing in quick succession
        debouncer.trigger()
        time.sleep(0.05)
        debouncer.trigger()
        time.sleep(0.05)
        debouncer.trigger()

        # Wait for delay period
        time.sleep(0.15)

        # Callback should be called only once
        assert callback.call_count == 1

    def test_clear_cancels_pending_callback(self):
        """clear() should cancel pending callback before it executes."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.1)

        debouncer.trigger()

        # Cancel before delay expires
        time.sleep(0.05)
        debouncer.clear()

        # Wait past original delay
        time.sleep(0.1)

        # Callback should never be called
        assert callback.call_count == 0

    def test_trigger_after_clear_works_correctly(self):
        """Trigger after clear should schedule new callback."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.1)

        # First trigger then clear
        debouncer.trigger()
        time.sleep(0.05)
        debouncer.clear()

        # New trigger after clear
        debouncer.trigger()
        time.sleep(0.15)

        # Callback should be called once (from second trigger)
        assert callback.call_count == 1

    def test_consecutive_triggers_restart_timer(self):
        """Each trigger should restart the delay timer."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.1)

        # First trigger
        debouncer.trigger()

        # Trigger again before delay expires (restarts timer)
        time.sleep(0.08)
        debouncer.trigger()

        # Wait only 0.12s total (would have expired if timer didn't restart)
        time.sleep(0.05)

        # Callback should not be called yet (timer restarted)
        assert callback.call_count == 0

        # Wait for full delay from second trigger
        time.sleep(0.08)

        # Now callback should be called
        assert callback.call_count == 1

    def test_debouncer_with_zero_delay(self):
        """Debouncer with zero delay should call callback immediately."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.0)

        debouncer.trigger()

        # Small sleep to allow thread to execute
        time.sleep(0.05)

        # Callback should be called
        assert callback.call_count == 1

    def test_callback_receives_no_arguments(self):
        """Callback should be called without arguments."""
        callback = Mock()
        debouncer = Debouncer(callback, delay=0.05)

        debouncer.trigger()
        time.sleep(0.1)

        # Verify callback was called with no arguments
        callback.assert_called_once_with()
