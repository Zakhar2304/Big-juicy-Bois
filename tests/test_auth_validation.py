from app.auth.validation import clean_email, clean_password, validate_auth_form


def test_email_ok() -> None:
    assert clean_email("  User@Mail.com ") == "user@mail.com"


def test_email_bad() -> None:
    try:
        clean_email("not-an-email")
        assert False
    except ValueError:
        pass


def test_register_password() -> None:
    assert validate_auth_form("a@b.co", "garden12", confirm="garden12", registering=True)[1] == "garden12"


def test_register_mismatch() -> None:
    try:
        clean_password("garden12", confirm="garden99", registering=True)
        assert False
    except ValueError:
        pass
