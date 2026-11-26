from app.core.rate_limit import SlidingWindowCounter


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_the_limit_is_exceeded_after_enough_events() -> None:
    counter = SlidingWindowCounter(limit=2, window_seconds=60, clock=FakeClock())

    counter.record("1.2.3.4")
    exceeded_after_one = counter.is_exceeded("1.2.3.4")
    counter.record("1.2.3.4")

    assert exceeded_after_one is False
    assert counter.is_exceeded("1.2.3.4") is True


def test_each_key_has_its_own_count() -> None:
    counter = SlidingWindowCounter(limit=1, window_seconds=60, clock=FakeClock())

    counter.record("alice")

    assert counter.is_exceeded("alice") is True
    assert counter.is_exceeded("bob") is False


def test_events_older_than_the_window_are_forgotten() -> None:
    clock = FakeClock()
    counter = SlidingWindowCounter(limit=1, window_seconds=60, clock=clock)
    counter.record("alice")

    clock.now += 61

    assert counter.is_exceeded("alice") is False


def test_reset_forgets_every_event() -> None:
    counter = SlidingWindowCounter(limit=1, window_seconds=60, clock=FakeClock())
    counter.record("alice")

    counter.reset()

    assert counter.is_exceeded("alice") is False
