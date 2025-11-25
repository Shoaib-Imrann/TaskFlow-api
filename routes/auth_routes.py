from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.user import UserLogin
from controllers.auth_controller import AuthController
from database import get_db
from middleware.jwt_middleware import verify_token

router = APIRouter()

# Public routes
@router.post("/signup")
async def signup(credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthController.signup(credentials, db)

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthController.login(credentials, db)

# Protected routes
@router.get("/me")
async def get_current_user(db: Session = Depends(get_db), user=Depends(verify_token)):
    return AuthController.get_user_by_id(user["user_id"], db)
