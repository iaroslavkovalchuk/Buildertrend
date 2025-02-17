from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import logging.config
import logging

from app.Utils.regular_update import job
from app.Utils.regular_send import send_sms_via_phone_number
from app.Routers import dashboard
from app.Routers import auth
from app.Routers import socket
import app.Utils.database_handler as crud
from database import AsyncSessionLocal, create_tables

app = FastAPI()

# Disable all SQLAlchemy logging
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(socket.router, prefix="/api/v1")

@app.get("/")
async def health_checker():
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
