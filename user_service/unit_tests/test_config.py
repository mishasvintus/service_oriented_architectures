from user_service.app.config import DATABASE_URL
import os

def test_database_url_is_set():
    assert DATABASE_URL is not None
    assert "test_db" in DATABASE_URL or "postgres" in os.environ.get("DATABASE_URL", "")
