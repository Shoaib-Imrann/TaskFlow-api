from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.user import UserLogin
from controllers.auth_controller import AuthController
from database import get_db

router = APIRouter()

@router.post("/signup")
async def signup(credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthController.signup(credentials, db)

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthController.login(credentials, db)
