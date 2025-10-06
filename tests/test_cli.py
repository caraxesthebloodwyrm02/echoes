def test_cli_imports():
    import app.cli.main as main
    import app.cli.audit as audit

    assert hasattr(main, "app")
    assert hasattr(audit, "app")
