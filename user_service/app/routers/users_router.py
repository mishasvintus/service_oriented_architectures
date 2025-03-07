from fastapi import APIRouter, Depends, HTTPException, status
from user_service.app.schemas.user import UserCreate, UserOut, UserUpdate
from user_service.app.models.user import User
from user_service.app.dependencies import get_current_user
from user_service.app.utils.security import hash_password, verify_password, create_access_token
from user_service.app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users")

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if await User.get_or_none(login=user.login) or await User.get_or_none(email=user.email):
        raise HTTPException(status_code=400, detail="Login or email already registered")
    
    user_obj = await User.create(
        login=user.login,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    return await UserOut.from_tortoise_orm(user_obj)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(login=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_user)):
    return await UserOut.from_tortoise_orm(current_user)

@router.put("/profile", response_model=UserOut)
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    update_data = user_update.model_dump(exclude_unset=True)  # Заменено .dict() на .model_dump()
    await User.filter(id=current_user.id).update(**update_data)
    
    # Обновляем объект из базы данных
    await current_user.refresh_from_db()
    
    return await UserOut.from_tortoise_orm(current_user)