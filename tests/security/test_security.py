from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    hashed = hash_password("Rahasia123!")
    assert hashed != "Rahasia123!"
    assert verify_password("Rahasia123!", hashed)


def test_create_access_token():
    token = create_access_token("user@example.com")
    assert token.count(".") == 2
