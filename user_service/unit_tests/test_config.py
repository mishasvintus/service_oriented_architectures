from user_service.app.core.config import DATABASE_URL

def test_database_url():
    assert DATABASE_URL is not None
    assert "postgres" in DATABASE_URL  
