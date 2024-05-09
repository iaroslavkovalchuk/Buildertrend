from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.Utils.regular_update import job
from app.Utils.regular_send import send_sms_via_phone_number
from app.Routers import dashboard
from app.Routers import auth

import uvicorn
import schedule
import time
import threading
import requests

app = FastAPI()

origins = ["*"]

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
    try:
        # schedule.every(12).hours.do(job) # schedule the job every 10 minutes
        # t = threading.Thread(target=run_schedule) # run the schedule in a separate thread
        # t.start()
        job()
    except:
        print("reqular DB update error!")
    uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)