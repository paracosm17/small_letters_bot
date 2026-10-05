import pytest

from tgbot.config import load_config, normalize_database_url


def _base_env(monkeypatch):
    monkeypatch.setenv("APP_SMOKE_MODE", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db:5432/app")


def test_smoke_mode_does_not_require_telegram(monkeypatch):
    _base_env(monkeypatch)
    config = load_config()
    assert config.app.smoke_mode is True
    assert config.tg_bot.token is None


def test_live_mode_requires_https_webhook(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("APP_SMOKE_MODE", "false")
    monkeypatch.setenv("BOT_TOKEN", "not-a-real-token")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "http://example.com")
    monkeypatch.setenv("WEBHOOK_SECRET", "abcdefghijklmnop")
    with pytest.raises(ValueError, match="https"):
        load_config()


def test_database_url_is_normalized():
    assert (
        normalize_database_url("postgresql://u:p@db:5432/app")
        == "postgresql+asyncpg://u:p@db:5432/app"
    )


def test_legacy_admin_ids_are_supported(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("ADMINS", "1,2,3")
    assert load_config().tg_bot.admin_ids == (1, 2, 3)
