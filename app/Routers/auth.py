from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
from app.Utils.Auth import authenticate_user, create_access_token, get_password_hash
from app.Utils.sendgrid import send_mail, send_approve_email
import secrets
import os

import app.Utils.database_handler as crud

from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/signin")
async def signin_for_access_token(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = await authenticate_user(db, email, password)  # This function needs to be updated to use db
    # print("sigin user: ", user.username)
    if not user:
        return JSONResponse(content={"message": "Email or Password are incorrect!"}, status_code=401)
    # if user.approved == 0:
    #     return JSONResponse(content={"message": "This email is not approved!"}, status_code=400)
    access_token = create_access_token(data={"sub": user.username})  # Assuming 'user' is an object
    user_to_return = {'email': user.username, 'hashed_password': user.password}
    return {"access_token": access_token, "token_type": "bearer", "user": user_to_return}

@router.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    print("signup - email: ", email)
    print("signup - password: ", password)
    print("signup - confirm_password: ", confirm_password)
    if password != confirm_password:
        return JSONResponse(content={"success": False}, status_code=400)
    password_in_db = get_password_hash(password)
    # print(password_in_db)
    forgot_password_token = secrets.token_urlsafe()

    user = await crud.get_user_by_email(db, email)
    # print("signup user: ", user)
    
    if not user:
        await send_approve_email(email, db)
        await crud.create_user(db, email, password_in_db, forgot_password_token, 0)
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        return JSONResponse(content={"message": "That email already exists"}, status_code=400)

@router.post("/confirm-email")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    user = await crud.get_user_by_email(db, email)
    print("auth - user", user.username)
    if not user:
        return JSONResponse(content={"message": "This email does not exist!"}, status_code=404)
    else:
        change_password_url = os.getenv('TOKEN_URL') + user.forgot_password_token
        await send_mail(change_password_url, 'Please change your password', email, db)
        return JSONResponse(content={"success": True}, status_code=200)

@router.post("/change-password")
async def change_password(token: str = Form(...), email: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    user = await crud.get_user_by_email(db, email)
    
    if not user:
        return JSONResponse(content={"message": "This email does not exist!"}, status_code=404)
    if token != user.forgot_password_token:
        return JSONResponse(content={"success": False}, status_code=403)
    else:
        password_in_db = get_password_hash(new_password)
        await crud.update_user(db, user.id, password=password_in_db, forgot_password_token=secrets.token_urlsafe())  # Reset the token
        return JSONResponse(content={"success": True}, status_code=200)