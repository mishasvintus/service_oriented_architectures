from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.fastapi import register_tortoise
from app.core.config import DATABASE_URL
from app.models.user import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await User.get_or_none(id=payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

def init_db(app):
    register_tortoise(
        app,
        db_url=DATABASE_URL,
        modules={"models": ["app.models.user"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )