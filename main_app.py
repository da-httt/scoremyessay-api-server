from datetime import datetime, date, timedelta
from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import schemas
from sqlalchemy.orm import Session
from db import SessionLocal, engine 
import models
from fastapi.middleware.cors import CORSMiddleware
from modules import paragraph
from routers import authentication
app = FastAPI()


app.include_router(authentication.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}