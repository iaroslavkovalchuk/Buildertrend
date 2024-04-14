from fastapi import FastAPI, APIRouter
import os
from dotenv import load_dotenv

from app.Utils.database_handler import DatabaseHandler

load_dotenv()

router = APIRouter()


# @router.get('/notification')
# def get_notification():

