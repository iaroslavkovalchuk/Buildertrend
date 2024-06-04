from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.Utils.regular_update import job
from app.Utils.regular_send import send_sms_via_phone_number
from app.Routers import dashboard
from app.Routers import auth
import app.Utils.database_handler as crud
from database import AsyncSessionLocal, create_tables
import uvicorn
import schedule
import time
import asyncio

import requests
import logging
import logging.config
from datetime import datetime, timedelta
app = FastAPI()


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

# send_sms_via_phone_number("+13205471980", "How are you, @rayleigh!")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.get("/")
async def health_checker():
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    asyncio.run(create_tables())

    
    db = AsyncSessionLocal()
    
    variables = crud.get_variables(db)
    if variables is None:
        crud.create_variables(db)
        
    status = crud.get_status(db)
    if status is None:
        crud.create_status(db)
    
    schedule.every(3).hours.do(job, source="BuilderTrend")

    # Calculate the time for the second job to start 1.5 hours after the first job
    first_job_time = datetime.now()
    second_job_start_time = (first_job_time + timedelta(hours=1.5)).strftime("%H:%M")

    # Schedule the second job function to run every 3 hours starting 1.5 hours from now
    schedule.every(3).hours.at(second_job_start_time).do(job, source="Xactanalysis")

    # Run the scheduler in an infinite loop
    while True:
        schedule.run_pending()
        time.sleep(1)

    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
