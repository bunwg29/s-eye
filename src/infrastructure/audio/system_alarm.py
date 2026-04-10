try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None

from core.application.ports.alarm import AlarmPort


class SystemAlarm(AlarmPort):
    def __init__(self) -> None:
        self._active = False

    def trigger(self) -> None:
        if self._active:
            return
        self._active = True
        if winsound is not None:
            winsound.Beep(2200, 250)

    def stop(self) -> None:
        self._active = False
