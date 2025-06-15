from user_service.app.security import hash_password, verify_password, create_access_token, decode_access_token
from datetime import timedelta

def test_password_hashing():
    password = "secret_password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_token_creation_and_decoding():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    decoded_payload = decode_access_token(token)
    assert decoded_payload is not None
    assert decoded_payload.get("sub") == data["sub"]

def test_token_expiration():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    decoded_payload = decode_access_token(token)
    assert decoded_payload is None

def test_hash_password():
    password = "mysecurepassword"
    hashed = hash_password(password)
    assert password != hashed  
    assert len(hashed) > 0  

def test_verify_password():
    password = "mypassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    token = create_access_token({"sub": "123"})
    assert isinstance(token, str)
    assert len(token) > 0 

def test_decode_access_token():
    token = create_access_token({"sub": "123"})
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"

def test_decode_invalid_access_token():
    decoded = decode_access_token("invalid.token.here")
    assert decoded is None  
