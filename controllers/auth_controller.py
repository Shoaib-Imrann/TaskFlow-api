from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import UserLogin, UserResponse
from models.user_db import UserDB
import jwt
import uuid
import bcrypt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class AuthController:
    @staticmethod
    def signup(credentials: UserLogin, db: Session):
        # Check if user already exists
        existing = db.query(UserDB).filter(UserDB.email == credentials.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user with hashed password
        user = UserDB(
            id=str(uuid.uuid4()),
            email=credentials.email,
            password=hash_password(credentials.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "token": token,
            "user": UserResponse.from_orm(user)
        }
    
    @staticmethod
    def login(credentials: UserLogin, db: Session):
        user = db.query(UserDB).filter(UserDB.email == credentials.email).first()
        
        if not user or not verify_password(credentials.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "token": token,
            "user": UserResponse.from_orm(user)
        }
    
    @staticmethod
    def create_default_user(db: Session):
        existing = db.query(UserDB).filter(UserDB.email == "admin@gmail.com").first()
        if not existing:
            user = UserDB(
                id=str(uuid.uuid4()),
                email="admin@gmail.com",
                password=hash_password("admin@123")
            )
            db.add(user)
            db.commit()
