from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hashing():
    password = "minhasenha123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("senhaerrada", hashed)


def test_token_creation_and_decode():
    token = create_access_token({"sub": "42", "role": "client"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_invalid_token():
    payload = decode_token("token.invalido.aqui")
    assert payload is None
