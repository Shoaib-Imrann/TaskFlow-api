from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime, date

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    status: Literal["pending", "in-progress", "completed"] = "pending"
    priority: Literal["low", "medium", "high"] = "medium"
    dueDate: Optional[str] = None
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('dueDate')
    def validate_due_date(cls, v):
        if v:
            try:
                due_date = datetime.strptime(v, '%Y-%m-%d').date()
                if due_date < date.today():
                    raise ValueError('Due date cannot be in the past')
            except ValueError as e:
                if 'past' in str(e):
                    raise e
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    status: Optional[Literal["pending", "in-progress", "completed"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    dueDate: Optional[str] = None
    
    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    @validator('dueDate')
    def validate_due_date(cls, v):
        if v:
            try:
                due_date = datetime.strptime(v, '%Y-%m-%d').date()
                if due_date < date.today():
                    raise ValueError('Due date cannot be in the past')
            except ValueError as e:
                if 'past' in str(e):
                    raise e
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str
    priority: str
    dueDate: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True