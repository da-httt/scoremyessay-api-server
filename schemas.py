from pydantic import EmailStr
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, date

class AccountLogin(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str 
    
class TokenData(BaseModel):
    email: Optional[str] = None 

class Account(BaseModel):
    account_id: int
    email: str
    role_id: int
    disabled: Optional[bool] = False 
      
class AccountInDB(Account):
    hashed_password: str

class User(BaseModel):
    email: str
    name: str
    date_of_birth: date
    address: str
    gender_id: Optional[int] = None 
    job_id: Optional[int] = None
    phone_number: Optional[str] = None
    
class SignUp(BaseModel):
    email: str
    password: str
    name: str
    address: Optional[str] = None
    date_of_birth: date
    gender_id: Optional[int] = None 
    job_id: Optional[int] = None
    phone_number: Optional[str] = None
        
class Job(BaseModel):
    job_id: int
    job_name: str

class UserAccount(User):
    account_id: int
    user_id: int 
    role_id: int 
    disabled: bool
        
class Gender(BaseModel):
    gender_id: int
    gender_name: str
    
class Order(BaseModel):
    order_id: int 
    essay_id: int
    student_id: int 
    teacher_id: int 
    sent_date: datetime 
    updated_date: datetime 
    updated_by: int 
    total_price: float 
    status_id: int 

class Essay(BaseModel):
    essay_id: int
    title: str 
    content: str 
    level_id: int
    type_id: int 
    
    
class OrderCreate(BaseModel):
    essay_id: int
    student_id: int 
    teacher_id: int 
    total_price: float 
    status_id: int 
    
    
    