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
from contextlib import asynccontextmanager

import requests
import logging
import logging.config
from datetime import datetime, timedelta
import logging

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


@app.get("/")
async def health_checker():
    return {"status": "success"}

async def init():
    print("--------------dd--------------")
    async with AsyncSessionLocal() as db:
        variables = await crud.get_variables(db)
        if variables is None:
            crud.create_variables(db)
            
        status = await crud.get_status(db)
        if status is None:
            crud.create_status(db)

async def main():
    await create_tables()
    await init()


# def run_scheduler():
#     # Calculate the time for the second job to start 1.5 hours after the first job
#     first_job_time = datetime.now()
#     second_job_start_time = (first_job_time + timedelta(hours=0.5)).strftime("%H:%M")

#     # Schedule jobs to run every 3 hours
#     schedule.every(3).hours.do(job, source="BuilderTrend")
#     schedule.every(3).hours.at(second_job_start_time).do(job, source="Xactanalysis")

#     # Run the scheduler in an infinite loop
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


async def job_scheduler():  
    async def schedule_job(source, initial_delay=0):  
        await asyncio.sleep(initial_delay)  # Initial delay before starting the job loop  
        while True:  
            await job(source=source)  
            await asyncio.sleep(3 * 3600)  # Sleep for 3 hours  
    
    # Schedule the first job immediately  
    first_task = asyncio.create_task(schedule_job("BuilderTrend"))  
    
    # Schedule the second job to start after 30 minutes  
    second_task = asyncio.create_task(schedule_job("Xactanalysis", initial_delay=30 * 60))  

    await asyncio.gather(first_task, second_task)  

@app.on_event("startup")  
async def on_startup():  
    await main()  
    asyncio.create_task(job_scheduler())  

if __name__ == "__main__":
     # Run asynchronous tasks
    asyncio.run(main())
    
    # Run the scheduler in a separate thread
    # import threading
    # scheduler_thread = threading.Thread(target=run_scheduler)
    # scheduler_thread.start()

    # Run Uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
