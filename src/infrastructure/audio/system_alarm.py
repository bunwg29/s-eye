try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None

import time

from core.application.ports.alarm import AlarmPort


class SystemAlarm(AlarmPort):
    def __init__(self, repeat_interval_seconds: float = 0.75) -> None:
        self._active = False
        self._repeat_interval_seconds = max(0.5, min(1.0, repeat_interval_seconds))
        self._last_beep_ts = 0.0

    def trigger(self) -> None:
        now = time.monotonic()
        if self._active and (now - self._last_beep_ts) < self._repeat_interval_seconds:
            return

        self._active = True
        self._last_beep_ts = now
        if winsound is not None:
            winsound.Beep(2200, 250)

    def stop(self) -> None:
        self._active = False
        self._last_beep_ts = 0.0
