from auth_service.infrastructure.config.settings import get_settings


def test_get_settings_is_cached():
    get_settings.cache_clear()
    settings_1 = get_settings()
    settings_2 = get_settings()

    assert settings_1 is settings_2


def test_get_settings_reads_environment(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret")

    settings = get_settings()
    assert settings.JWT_SECRET == "unit-test-secret"

    get_settings.cache_clear()
