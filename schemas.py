from pydantic import EmailStr
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date,  timedelta, date


#schema class for authorization 
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
    user_id: int
    email: str
    role_id: int
    disabled: Optional[bool] = False 
      
class AccountInDB(Account):
    hashed_password: str
    
class SignUp(BaseModel):
    email: str
    password: str
    name: str
    address: Optional[str] = "Da Nang"
    date_of_birth: date
    gender_id: Optional[int] = 1 
    job_id: Optional[int] = 1
    phone_number: Optional[str] = "123456789"

#schema class for user management
class User(BaseModel):
    user_id: int 
    name: str
    date_of_birth: date
    address: str
    gender_id: Optional[int] = None 
    job_id: Optional[int] = None
    phone_number: Optional[str] = None
    
class Job(BaseModel):
    job_id: int
    job_name: str

class JobResponse(BaseModel):
    status: str 
    totalCount: int
    data: List[Job]

class UserAccount(BaseModel):
    account_id: int
    email: str
    role_id: int
    disabled: Optional[bool] = False 
    info: User 
        
class Gender(BaseModel):
    gender_id: int
    gender_name: str

class GenderResponse(BaseModel):
    status: str 
    totalCount: int
    data: List[Gender]

class UserResponse(BaseModel):
    status: str 
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: int 
    data: List[UserAccount]
        

#schema class for order management 

class EssayInDB(BaseModel):
    title: str 
    content: str  
    type_id: int 
    
class OrderInDB(BaseModel):
    essay: EssayInDB
    option_list: List[int]  

class EssayResponse(BaseModel):
    essay_id: int 
    title: str 
    content: str
    type_id: int 

class OrderResponse(BaseModel):
    status_id: int 
    order_id: int
    student_id: int 
    teacher_id: Optional[int] = None 
    sent_date: str
    updated_date: str 
    updated_by: int 
    essay: EssayResponse
    option_list: List[int]
    total_price: float 



class OrderListResponse(BaseModel):
    status: str
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: Optional[int] = 20 
    data: List[OrderResponse]
    
    
    