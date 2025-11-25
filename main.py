from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import task_routes, auth_routes, ai_routes
from database import engine, Base, SessionLocal
from controllers.auth_controller import AuthController
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables with error handling
try:
    Base.metadata.create_all(bind=engine)
    print("Database connected successfully")
except Exception as e:
    print(f"Database connection failed: {e}")
    print("API will start but database operations may fail")

app = FastAPI()

CLIENT_URL = os.getenv("CLIENT_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api/auth")
app.include_router(ai_routes.router, prefix="/api/ai")

@app.get("/")
def root():
    return {"message": "Backend up and ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
