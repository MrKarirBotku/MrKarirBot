from app.workers.jobs import CYCLE_LOCK_KEY, run_locked_job_cycle


class FakeRedis:
    def __init__(self, acquired: bool) -> None:
        self.acquired = acquired
        self.released = False

    async def set(self, key, value, *, ex, nx):
        assert key == CYCLE_LOCK_KEY
        assert ex >= 300
        assert nx is True
        return self.acquired

    async def eval(self, script, number_of_keys, key, token):
        assert script
        assert number_of_keys == 1
        assert key == CYCLE_LOCK_KEY
        assert token
        self.released = True
        return 1


async def test_locked_job_cycle_runs_and_releases_lock() -> None:
    client = FakeRedis(acquired=True)
    calls = 0

    async def cycle() -> None:
        nonlocal calls
        calls += 1

    assert await run_locked_job_cycle(client, cycle) is True
    assert calls == 1
    assert client.released is True


async def test_locked_job_cycle_skips_when_lock_is_held() -> None:
    client = FakeRedis(acquired=False)
    calls = 0

    async def cycle() -> None:
        nonlocal calls
        calls += 1

    assert await run_locked_job_cycle(client, cycle) is False
    assert calls == 0
    assert client.released is False
