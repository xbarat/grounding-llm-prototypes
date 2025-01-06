from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Any
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.username)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=str(user.username)
    )

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """Handle OAuth2 form-based login"""
    return await authenticate_user(form_data.username, form_data.password, db)

@router.post("/login", response_model=Token)
async def login_json(
    login_data: LoginData,
    db: Session = Depends(get_db)
) -> Any:
    """Handle JSON-based login"""
    return await authenticate_user(login_data.username, login_data.password, db)

async def authenticate_user(username: str, password: str, db: Session) -> Token:
    """Common authentication logic"""
    # Find user
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    setattr(user, 'last_login', datetime.utcnow())
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.username)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=str(user.username)
    ) 