from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from .schemas import UserCreate, UserOut, UserUpdate
from .models import User
from .security import hash_password, verify_password, create_access_token, decode_access_token
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from .kafka_producer import kafka_producer

router = APIRouter(prefix="/users")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

# --- Роуты ---
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if await User.get_or_none(login=user.login) or await User.get_or_none(email=user.email):
        raise HTTPException(status_code=400, detail="Login or email already registered")
    
    hashed_pass = hash_password(user.password)
    user_obj = await User.create(
        login=user.login,
        email=user.email,
        password_hash=hashed_pass
    )
    
    kafka_producer.send_user_registration_event(user_obj.id, user_obj.created_at)
    
    return user_obj

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(login=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    update_data = user_update.model_dump(exclude_unset=True)  
    
    allowed_fields = {"first_name", "last_name", "phone", "email", "date_of_birth"}

    for field in update_data:
        if field not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"Field '{field}' cannot be updated")

    await current_user.update_from_dict(update_data).save()
    return current_user

@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(current_user: User = Depends(get_current_user)):
    await current_user.delete()
    return {"message": "User deleted successfully"} 