from fastapi import FastAPI, Depends
from typing import Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import schema
from database import SessionLocal, db_engine
import models

SECRET_KEY = "9066487c8a7e5fd807c345ad783a9518fd6b1c0f7e2cbaf064ef6dc9357150fa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

models.Base.metadata.create_all(bind=db_engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
db = SessionLocal()


def get_user(username: str):
    return db.query(models.User).filter(models.User.username == username)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return get_user(username)
    except:
        return None


@app.post("/register")
async def register(user_info: schema.User):
    user = models.User(username=user_info.username, password=user_info.password)
    db.add(user)
    db.commit()
    return user_info


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    username = get_current_user(token)
    if username:
        user = get_user(username)
        if user:
            return {"Logged out"}
    return {"Failed"}
