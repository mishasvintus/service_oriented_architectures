from user_service.app.utils.security import hash_password, verify_password, create_access_token, decode_access_token

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
