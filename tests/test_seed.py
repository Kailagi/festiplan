from app import seed as seed_module


def test_seed_requires_explicit_confirmation(monkeypatch, capsys):
    def unexpected_database_initialization():
        raise AssertionError("database must not be initialized without confirmation")

    monkeypatch.setattr(seed_module, "initialize_database", unexpected_database_initialization)

    assert seed_module.seed() is False
    assert "ATTENTION" in capsys.readouterr().out


def test_seed_command_cancellation_leaves_database_untouched(monkeypatch, capsys):
    def unexpected_database_initialization():
        raise AssertionError("database must not be initialized after cancellation")

    monkeypatch.setattr(seed_module, "initialize_database", unexpected_database_initialization)
    monkeypatch.setattr("builtins.input", lambda _prompt: "NON")

    seed_module.main()

    assert "Chargement annulé" in capsys.readouterr().out


def test_confirmed_seed_replaces_demo_data(client):
    from app.models import Artist, Concert, Festival, OutboxEvent, Stage

    assert seed_module.seed(confirmed=True) is True

    db = seed_module.SessionLocal()
    try:
        assert db.query(Festival).count() == 1
        assert db.query(Stage).count() == 4
        assert db.query(Artist).count() == 12
        assert db.query(Concert).count() == 14
        assert db.query(OutboxEvent).count() == 0
    finally:
        db.close()
