"""Debouncer for rate-limiting file change events.

Feature 003 - US2: Watch Mode Auto-Regeneration
T019: Debouncer class using threading.Timer
"""

import threading
from typing import Callable


class Debouncer:
    """Debounce rapid function calls to avoid excessive executions.

    Uses threading.Timer to delay function execution until a quiet period
    (no calls for specified delay). Subsequent calls reset the timer.

    Attributes:
        callback: Function to call after quiet period
        delay: Delay in seconds before executing callback
        _timer: Active timer instance (or None)

    Example:
        >>> def process_change():
        ...     print("Processing change...")
        >>> debouncer = Debouncer(process_change, delay=0.5)
        >>> debouncer.trigger()  # Start timer
        >>> debouncer.trigger()  # Reset timer (callback not yet called)
        >>> debouncer.trigger()  # Reset timer again
        >>> # ... after 0.5 seconds of quiet ...
        >>> # Output: "Processing change..." (called once)

    Feature: US2 - Watch Mode Auto-Regeneration (T019)
    """

    def __init__(self, callback: Callable[[], None], delay: float = 0.5):
        """Initialize debouncer.

        Args:
            callback: Function to call after quiet period
            delay: Delay in seconds before calling callback (default: 0.5)
        """
        self.callback = callback
        self.delay = delay
        self._timer: threading.Timer | None = None

    def trigger(self) -> None:
        """Trigger debounced callback.

        If timer is active, cancels it. Starts new timer with specified delay.
        Callback will execute if no additional calls occur within delay period.
        """
        # Cancel existing timer if present
        if self._timer is not None:
            self._timer.cancel()

        # Start new timer
        self._timer = threading.Timer(self.delay, self.callback)
        self._timer.start()

    def clear(self) -> None:
        """Cancel pending callback execution.

        Cancels active timer if present. Callback will not execute.
        """
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
