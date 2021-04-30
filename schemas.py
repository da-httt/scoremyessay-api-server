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
class Status(BaseModel):
    status_id: int
    status_name: str

class StatusListResponse(BaseModel):
    status: str
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: Optional[int] = 20 
    data: List[Status]
    
class Option(BaseModel):
    option_id: int
    option_type: int
    option_name: str
    option_price: float

class OptionListResponse(BaseModel):
    status: str
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: Optional[int] = 20 
    data: List[Option]
    
    

class EssayInDB(BaseModel):
    title: str 
    content: str  
    type_id: int 
    
class OrderInDB(BaseModel):
    essay: EssayInDB
    option_list: List[int]  

class OrderUpdate(OrderInDB):
    status_id: int 
    

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
    
class Level(BaseModel):
    level_id: int
    level_name: str

class LevelListResponse(BaseModel):
    status: str
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: Optional[int] = 20 
    data: List[Level]
    
class Type(BaseModel):
    type_id: int
    level_id: int
    type_name: str
    type_price: float

class TypeListResponse(BaseModel):
    status: str
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: Optional[int] = 20 
    data: List[Type]

class CriteriaResponse(BaseModel):
    result_id: int
    criteria_id: int 
    criteria_name: str 
    criteria_comment: Optional[str] = None
    criteria_score: Optional[str] = None  
    
class ExtraResponse(BaseModel):
    result_id: int
    option_id: int 
    option_name: str
    content: Optional[str] = None
    
class ResultResponse(BaseModel):
    result_id: int 
    isCriteria: bool
    isExtra: bool
    grade: Optional[float] = None 
    grade_comment: Optional[str] = None  
    review: Optional[str] = None 
    comment: Optional[str] = None  
    criteria_results: Optional[List[CriteriaResponse]] = None 
    extra_results: Optional[List[ExtraResponse]] = None 


    
class CriteriaListResponse(BaseModel):
    criteria_id: int 
    criteria_name: str 

class CriteriaResultInDB(BaseModel):
    criteria_id: int 
    criteria_comment: Optional[str] = None 
    criteria_score: Optional[float] = None 

class ExtraResultInDB(BaseModel):
    option_id: int 
    content: Optional[str] = None 
    
class ResultInDB(BaseModel):
    grade: Optional[float] = None 
    grade_comment: Optional[str] = None  
    review: Optional[str] = None  
    comment: Optional[str] = None  
    criteria_results: Optional[List[CriteriaResultInDB]] = None 
    extra_results: Optional[List[ExtraResultInDB]] = None 
    
#Essay Comment 

class EssayComment(BaseModel):
    sentence_index: int 
    sentence: str 
    comment: Optional[str] = None 
    
class EssayCommentResponse(EssayResponse):
    essay_comments: List[EssayComment]
    
    
class EssayCommentInDB(BaseModel):
    sentence_index: int 
    comment: Optional[str] = None 
    
    