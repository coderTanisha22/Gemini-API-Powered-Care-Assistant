import asyncio
import random
import threading
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any

from .behaviour import get_expected_activity


class ActivitySimulator:
    def __init__(
        self,
        *,
        user_id: str = "care-user-001",
        window_size: int = 180,
        interval_seconds: float = 1.5,
    ) -> None:
        self.user_id = user_id
        self.window_size = window_size
        self.interval_seconds = interval_seconds
        self._events: deque[dict[str, Any]] = deque(maxlen=window_size)
        self._lock = threading.Lock()
        self._running = False
        self._task: asyncio.Task | None = None
        self._rng = random.Random()
        self._boot_reference = datetime.now(timezone.utc)
        self._event_count = 0
        self._last_event_at: str | None = None
        self._scenario = "normal routine"
        self._last_routine_event_at: datetime | None = None
        self._prime_history()

    async def start(self) -> dict[str, Any]:
        if self._running:
            return self.status()

        self._running = True
        self._task = asyncio.create_task(self._run(), name="iot-activity-simulator")
        return self.status()

    async def stop(self) -> dict[str, Any]:
        if not self._running:
            return self.status()

        self._running = False
        task = self._task
        self._task = None

        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        return self.status()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "scenario": self._scenario,
                "event_count": self._event_count,
                "window_size": len(self._events),
                "last_event_at": self._last_event_at,
                "user_id": self.user_id,
            }

    def get_recent_events(self, limit: int | None = None) -> list[dict[str, Any]]:
        with self._lock:
            events = list(self._events)
        return events if limit is None else events[-limit:]

    async def _run(self) -> None:
        try:
            while self._running:
                event = self._generate_event(datetime.now(timezone.utc))
                with self._lock:
                    self._events.append(event)
                    self._event_count += 1
                    self._last_event_at = event["timestamp"]
                await asyncio.sleep(self._rng.uniform(1.0, 2.0))
        except asyncio.CancelledError:
            raise

    def _prime_history(self) -> None:
        now = datetime.now(timezone.utc)
        for offset in range(30, 0, -1):
            event_time = now - timedelta(seconds=offset * self.interval_seconds)
            event = self._generate_event(event_time)
            self._events.append(event)
            self._event_count += 1
            self._last_event_at = event["timestamp"]

    def _generate_event(self, event_time: datetime) -> dict[str, Any]:
        expected = get_expected_activity(event_time)
        scenario = self._select_scenario(event_time)
        self._scenario = scenario

        band_low, band_high = expected["activity_band"]
        location = self._rng.choice(expected["locations"])

        if scenario == "normal routine":
            emit_routine = expected["routine_expected"] and self._should_emit_routine(event_time)
            if emit_routine:
                activity_level = self._bounded_int(max(45, band_low), min(100, band_high + 10))
                event_type = "routine_event"
                self._last_routine_event_at = event_time
            else:
                activity_level = self._bounded_int(band_low, band_high)
                event_type = "movement" if activity_level >= 20 else "idle"
        elif scenario == "inactivity":
            activity_level = self._bounded_int(0, 8)
            event_type = "idle"
            location = expected["rest_location"]
        else:
            irregular_spike = self._event_count % 4 == 0
            if irregular_spike:
                activity_level = self._bounded_int(min(100, band_high + 20), min(100, band_high + 35))
                event_type = "movement"
            else:
                activity_level = self._bounded_int(0, max(12, band_low // 3))
                event_type = "idle"

        return {
            "user_id": self.user_id,
            "timestamp": event_time.isoformat(),
            "activity_level": activity_level,
            "event_type": event_type,
            "location": location,
            "confidence": round(self._rng.uniform(0.82, 0.98), 2),
        }

    def _select_scenario(self, event_time: datetime) -> str:
        elapsed = (event_time - self._boot_reference).total_seconds() % 105
        if elapsed < 55:
            return "normal routine"
        if elapsed < 80:
            return "inactivity"
        return "irregular behavior"

    def _should_emit_routine(self, event_time: datetime) -> bool:
        if self._last_routine_event_at is None:
            return True
        return (event_time - self._last_routine_event_at).total_seconds() >= 18

    def _bounded_int(self, low: int, high: int) -> int:
        low = max(0, min(low, 100))
        high = max(low, min(high, 100))
        return self._rng.randint(low, high)


simulator = ActivitySimulator()
