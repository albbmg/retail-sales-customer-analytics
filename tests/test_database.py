import pytest

from retail_analytics.database import DatabaseConfigError, DatabaseSettings


def test_database_settings_read_environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "analytics_test")
    monkeypatch.setenv("POSTGRES_USER", "tester")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_HOST", "db.example")
    monkeypatch.setenv("POSTGRES_PORT", "5544")

    settings = DatabaseSettings.from_environment()

    assert settings.database == "analytics_test"
    assert settings.user == "tester"
    assert settings.password == "secret"
    assert settings.host == "db.example"
    assert settings.port == 5544
    assert settings.connect_kwargs()["dbname"] == "analytics_test"


@pytest.mark.parametrize("port", ["abc", "0", "65536"])
def test_database_settings_reject_invalid_port(monkeypatch, port):
    monkeypatch.setenv("POSTGRES_PORT", port)

    with pytest.raises(DatabaseConfigError, match="POSTGRES_PORT"):
        DatabaseSettings.from_environment()
