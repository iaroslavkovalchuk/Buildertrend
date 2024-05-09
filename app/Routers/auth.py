from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

# from app.Models.UserModel import SignInModel, SignUpModel
from app.Utils.Auth import authenticate_user, create_access_token, get_password_hash
from fastapi import HTTPException, status
from app.Utils.database_handler import DatabaseHandler
from app.Utils.sendgrid import send_mail
import secrets
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

db = DatabaseHandler()

@router.post("/signin")
def signin_for_access_token(email: str = Form(...), password: str = Form(...)):
    user = authenticate_user(email, password)
    print(user)
    if not user:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Incorrect username or password",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        return JSONResponse(content={"success": False}, status_code=401)
    email = user[1]
    hashed_password = user[2]
    
    access_token = create_access_token(data={"sub": email}) # email
    print(access_token)
    user_to_return = {'email': email, 'hashed_password': hashed_password} # hashed password
    return {"access_token": access_token, "token_type": "bearer", "user": user_to_return}


@router.post("/signup")
def signup(email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return False
    password_in_db = get_password_hash(password)
    forgot_password_token = secrets.token_urlsafe()

    print("password_in_db: ", password_in_db)
    user = db.get_user(email)
    if not user:
        print(email, password_in_db)
        db.insert_user(email, password_in_db, forgot_password_token)
        return True
    else:
        return "That email alrealy exist"
        # raise ValueError("That email alrealy exist")

@router.post("/confirm-email")
def forgot_password(email: str = Form(...)):
    user = db.get_user(email)
    if not user:
        return "This email is not exist!"
    else:
        change_password = os.getenv('TOKEN_URL') + user[3]
        print(change_password)
        send_mail(change_password, 'Please change your password', email)
        return JSONResponse(content={"success": True}, status_code=200)


@router.post("/change-password")
def change_password(token: str = Form(...), email: str = Form(...), new_password: str = Form(...)):
    print(token)
    user = db.get_user(email)
    
    if not user:
        return "This email is not exist!"
    if token != user[3]:
        return JSONResponse(content={"success": False}, status_code=303)
    else:
        password_in_db = get_password_hash(new_password)
        db.update_user(email, password_in_db, token)
        return JSONResponse(content={"success": True}, status_code=200)