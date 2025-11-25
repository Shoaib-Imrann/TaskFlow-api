from sqlalchemy import Column, String, DateTime, Text
from database import Base
from datetime import datetime
import uuid

class TaskDB(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, nullable=True)
    status = Column(String, default="pending")
    priority = Column(String, default="medium")
    dueDate = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)