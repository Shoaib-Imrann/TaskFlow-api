import os
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.task_db import TaskDB
from fastapi import HTTPException

class AIController:
    _cache = {}
    _cache_duration = 300  # 5 minutes
    
    @staticmethod
    def invalidate_cache(user_id: str):
        """Invalidate cache for a specific user"""
        cache_key = f"{user_id}_summary"
        if cache_key in AIController._cache:
            del AIController._cache[cache_key]
    
    @staticmethod
    def generate_weekly_summary(user_id: str, db: Session):
        # Check cache first
        cache_key = f"{user_id}_summary"
        now = datetime.now().timestamp()
        if cache_key in AIController._cache:
            cached_data, cached_time = AIController._cache[cache_key]
            if now - cached_time < AIController._cache_duration:
                return cached_data
        
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        week_ago = datetime.now() - timedelta(days=7)
        
        completed = db.query(TaskDB).filter(
            TaskDB.user_id == user_id,
            TaskDB.status == "completed",
            TaskDB.updatedAt >= week_ago,
            TaskDB.parent_task_id == None
        ).all()
        
        pending = db.query(TaskDB).filter(
            TaskDB.user_id == user_id,
            TaskDB.status.in_(["pending", "in-progress"]),
            TaskDB.parent_task_id == None
        ).all()
        
        overdue = [t for t in pending if t.dueDate and datetime.fromisoformat(t.dueDate.replace('Z', '+00:00')) < datetime.now()]
        
        prompt = f"""Generate a brief weekly productivity summary (3-4 sentences max):

Completed this week: {len(completed)} tasks
{chr(10).join(f"- {t.title}" for t in completed[:5])}

Pending: {len(pending)} tasks ({len(overdue)} overdue)
{chr(10).join(f"- {t.title}" for t in pending[:5])}

Provide: 1) Progress overview, 2) Top priority, 3) Brief motivation."""

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"AI API error: {response.text}")
        
        data = response.json()
        summary = data["candidates"][0]["content"]["parts"][0]["text"]
        
        result = {
            "summary": summary,
            "stats": {
                "completed_this_week": len(completed),
                "pending": len(pending),
                "overdue": len(overdue)
            }
        }
        
        # Cache result
        AIController._cache[cache_key] = (result, now)
        return result
