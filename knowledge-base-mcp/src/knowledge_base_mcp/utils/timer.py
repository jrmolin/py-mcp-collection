from datetime import UTC, datetime
from typing import Self

from pydantic import BaseModel, Field, PrivateAttr, computed_field


class RunningTimer(BaseModel):
    name: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), exclude=True)

    def stop(self) -> "FinishedTimer":
        return FinishedTimer(name=self.name, start_time=self.start_time)


class Timer(RunningTimer):
    pass


class FinishedTimer(RunningTimer):
    end_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), exclude=True)

    def _duration(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    @computed_field()
    def duration(self) -> float:
        return self._duration()


class TimerGroup(BaseModel):
    name: str = Field(description="The name of the timer group")

    _running_timer: RunningTimer | None = PrivateAttr(default=None)
    _finished_timers: list[FinishedTimer] = PrivateAttr(default_factory=list)

    def start_timer(self, name: str) -> Self:
        if self._running_timer is not None:
            msg = f"A timer is already running for {name}"
            raise ValueError(msg)

        new_timer = RunningTimer(name=name)
        self._running_timer = new_timer

        return self

    def stop_timer(self) -> Self:
        if self._running_timer is None:
            msg = f"No running timer found for {self.name}"
            raise ValueError(msg)

        self._finished_timers.append(self._running_timer.stop())
        self._running_timer = None

        return self

    def merge(self, other: "TimerGroup") -> Self:
        """Merge another timer group into this one."""

        self._finished_timers.extend(other._finished_timers)
        return self

    @computed_field()
    def times(self) -> dict[str, float]:
        return {timer.name: timer._duration() for timer in self._finished_timers}

    @computed_field()
    def total_duration(self) -> float:
        return sum(timer._duration() for timer in self._finished_timers)

    def wall_clock_time(self) -> float:
        if not self._finished_timers:
            return 0

        minimum_start_time = min(timer.start_time for timer in self._finished_timers)
        maximum_end_time = max(timer.end_time for timer in self._finished_timers)

        return (maximum_end_time - minimum_start_time).total_seconds()
