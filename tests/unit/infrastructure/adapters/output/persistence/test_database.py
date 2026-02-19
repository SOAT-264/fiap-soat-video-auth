import pytest

from auth_service.infrastructure.adapters.output.persistence import database


@pytest.mark.asyncio
async def test_get_db_commits_on_success(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.committed = False
            self.rolled_back = False

        async def commit(self):
            self.committed = True

        async def rollback(self):
            self.rolled_back = True

    class FakeContextManager:
        def __init__(self, session):
            self.session = session

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    session = FakeSession()
    monkeypatch.setattr(database, "async_session", lambda: FakeContextManager(session))

    gen = database.get_db()
    yielded_session = await anext(gen)
    assert yielded_session is session

    with pytest.raises(StopAsyncIteration):
        await anext(gen)

    assert session.committed is True
    assert session.rolled_back is False


@pytest.mark.asyncio
async def test_get_db_rolls_back_on_exception(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.committed = False
            self.rolled_back = False

        async def commit(self):
            self.committed = True

        async def rollback(self):
            self.rolled_back = True

    class FakeContextManager:
        def __init__(self, session):
            self.session = session

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    session = FakeSession()
    monkeypatch.setattr(database, "async_session", lambda: FakeContextManager(session))

    gen = database.get_db()
    await anext(gen)

    with pytest.raises(RuntimeError):
        await gen.athrow(RuntimeError("boom"))

    assert session.committed is False
    assert session.rolled_back is True


@pytest.mark.asyncio
async def test_init_db_runs_metadata_create_all(monkeypatch):
    called = {"create_all": False}

    class FakeConn:
        async def run_sync(self, fn):
            called["create_all"] = True

    class FakeBegin:
        async def __aenter__(self):
            return FakeConn()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeEngine:
        def begin(self):
            return FakeBegin()

    monkeypatch.setattr(database, "engine", FakeEngine())

    await database.init_db()
    assert called["create_all"] is True
