from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from controllers.ai_controller import AIController
from database import get_db
from middleware.jwt_middleware import verify_token

router = APIRouter()

@router.get("/summary")
async def get_ai_summary(db: Session = Depends(get_db), user=Depends(verify_token)):
    try:
        return AIController.generate_weekly_summary(user["user_id"], db)
    except Exception as e:
        print(f"AI Summary Error: {str(e)}")
        raise
