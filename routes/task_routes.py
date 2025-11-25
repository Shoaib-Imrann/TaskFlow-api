from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from models.task import Task, TaskCreate, TaskUpdate
from controllers.task_controller import TaskController
from database import get_db
from middleware.jwt_middleware import verify_token

router = APIRouter()

@router.get("/tasks/stats")
async def get_stats(db: Session = Depends(get_db), user=Depends(verify_token)):
    return TaskController.get_stats(user["user_id"], db)

@router.get("/tasks")
async def get_all_tasks(
    search: str = None,
    category: str = None,
    priority: str = None,
    status: str = None,
    sort_by: str = "createdAt",
    page: int = 1,
    limit: int = 12,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return TaskController.get_all_tasks(
        user["user_id"], db, search, category, priority, status, sort_by, page, limit
    )

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str, db: Session = Depends(get_db), user=Depends(verify_token)):
    return TaskController.get_task_by_id(task_id, user["user_id"], db)

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), user=Depends(verify_token)):
    return TaskController.create_task(task, user["user_id"], db)

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_updates: TaskUpdate, db: Session = Depends(get_db), user=Depends(verify_token)):
    return TaskController.update_task(task_id, task_updates, user["user_id"], db)

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db), user=Depends(verify_token)):
    TaskController.delete_task(task_id, user["user_id"], db)
    return {"message": "Task deleted successfully"}