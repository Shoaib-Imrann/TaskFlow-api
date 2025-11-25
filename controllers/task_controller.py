from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.task import Task, TaskCreate, TaskUpdate
from models.task_db import TaskDB
from database import get_db
from datetime import datetime
import uuid

class TaskController:
    @staticmethod
    def get_stats(user_id: str, db: Session = Depends(get_db)) -> dict:
        # Only count parent tasks (exclude subtasks)
        total = db.query(TaskDB).filter(TaskDB.user_id == user_id, TaskDB.parent_task_id == None).count()
        completed = db.query(TaskDB).filter(TaskDB.user_id == user_id, TaskDB.parent_task_id == None, TaskDB.status == "completed").count()
        pending = db.query(TaskDB).filter(TaskDB.user_id == user_id, TaskDB.parent_task_id == None, TaskDB.status == "pending").count()
        in_progress = db.query(TaskDB).filter(TaskDB.user_id == user_id, TaskDB.parent_task_id == None, TaskDB.status == "in-progress").count()
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress
        }
    
    @staticmethod
    def get_all_tasks(
        user_id: str,
        db: Session = Depends(get_db),
        search: str = None,
        category: str = None,
        priority: str = None,
        status: str = None,
        sort_by: str = "createdAt",
        page: int = 1,
        limit: int = 12
    ) -> dict:
        # Only get parent tasks (exclude subtasks)
        query = db.query(TaskDB).filter(
            TaskDB.user_id == user_id,
            TaskDB.parent_task_id == None
        )
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (TaskDB.title.ilike(search_term)) | 
                (TaskDB.description.ilike(search_term))
            )
        
        # Category filter
        if category and category != "all":
            query = query.filter(TaskDB.category == category)
        
        # Priority filter
        if priority and priority != "all":
            query = query.filter(TaskDB.priority == priority)
        
        # Status filter
        if status and status != "all":
            query = query.filter(TaskDB.status == status)
        
        # Sorting
        if sort_by == "dueDate":
            query = query.order_by(TaskDB.dueDate.asc())
        elif sort_by == "priority":
            # Custom priority order: high > medium > low
            priority_order = db.query(TaskDB.id).filter(
                TaskDB.user_id == user_id
            ).order_by(
                db.case(
                    (TaskDB.priority == "high", 1),
                    (TaskDB.priority == "medium", 2),
                    (TaskDB.priority == "low", 3)
                )
            )
            query = query.order_by(
                db.case(
                    (TaskDB.priority == "high", 1),
                    (TaskDB.priority == "medium", 2),
                    (TaskDB.priority == "low", 3)
                )
            )
        else:  # Default: createdAt (newest first)
            query = query.order_by(TaskDB.createdAt.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        tasks = query.offset(offset).limit(limit).all()
        
        return {
            "tasks": [Task.from_orm(task) for task in tasks],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_task_by_id(task_id: str, user_id: str, db: Session = Depends(get_db)) -> Task:
        task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == user_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return Task.from_orm(task)
    
    @staticmethod
    def create_task(task_data: TaskCreate, user_id: str, db: Session = Depends(get_db)) -> Task:
        db_task = TaskDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=task_data.title,
            description=task_data.description or "",
            category=task_data.category,
            status=task_data.status,
            priority=task_data.priority,
            dueDate=task_data.dueDate,
            parent_task_id=task_data.parent_task_id,
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return Task.from_orm(db_task)
    
    @staticmethod
    def update_task(task_id: str, task_updates: TaskUpdate, user_id: str, db: Session = Depends(get_db)) -> Task:
        task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == user_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        update_data = task_updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        task.updatedAt = datetime.now()
        db.commit()
        db.refresh(task)
        return Task.from_orm(task)
    
    @staticmethod
    def delete_task(task_id: str, user_id: str, db: Session = Depends(get_db)) -> bool:
        task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == user_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(task)
        db.commit()
        return True
    
    @staticmethod
    def get_subtasks(parent_task_id: str, user_id: str, db: Session = Depends(get_db)) -> List[Task]:
        # Verify parent task exists and belongs to user
        parent_task = db.query(TaskDB).filter(TaskDB.id == parent_task_id, TaskDB.user_id == user_id).first()
        if not parent_task:
            raise HTTPException(status_code=404, detail="Parent task not found")
        
        # Get all subtasks
        subtasks = db.query(TaskDB).filter(
            TaskDB.parent_task_id == parent_task_id,
            TaskDB.user_id == user_id
        ).order_by(TaskDB.createdAt.desc()).all()
        
        return [Task.from_orm(subtask) for subtask in subtasks]