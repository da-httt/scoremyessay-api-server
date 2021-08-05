from pydantic import EmailStr
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date,  timedelta, date
from fastapi import Body 

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
    avatar: Optional[str] = None

#schema class for user management
class User(BaseModel):
    user_id: int 
    name: str
    date_of_birth: date
    address: str
    gender_id: Optional[int] = None 
    job_id: Optional[int] = None
    phone_number: Optional[str] = None

class UserInDB(BaseModel):
    name: str
    address: Optional[str] = "Da Nang"
    date_of_birth: date 
    gender_id: Optional[int] = 1 
    job_id: Optional[int] = 1
    phone_number: Optional[str] = "123456789"
    
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
    
class UserInfo(BaseModel):
    user_id: int 
    email: str 
    name: str
    phone_number: str 
    gender_id: int
    job_id: int 
    date_of_birth: date 
    address: str 
    
        

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
    is_disabled: bool
    deadline: Optional[str] = None 
    time_left: Optional[int] = 0
    keywords: List[str]

class SuggestedOrderResponse(OrderResponse):
    isSuggested: bool 

class SuggestedOrderListResponse(BaseModel):
    status: str
    totalCount: int 
    pageCount: Optional[int] = 1
    currentPage: Optional[int] = 1
    perPage: Optional[int] = 20 
    data: List[SuggestedOrderResponse]
    
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
    order_status_id: int 
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
    
class ListEssayCommentInDB(BaseModel):
    comments: List[EssayCommentInDB]
    
class WordError(BaseModel):
    index: int
    word: str
    sentence: str
    sentence_index: int 
    suggested_word: str 
      
class EssayInfoResponse(BaseModel):
    essay_info_id: int
    essay_id: int
    keywords: List[str]
    number_of_sentences: int 
    average_sentence_length: float 
    number_of_words: int 
    num_errors: int
    spelling_errors: List[WordError]
    
class Deadline(BaseModel):
    total_deadline: int
    today_deadline: int 
    week_deadline: int 
    
    
class UserStatistics(BaseModel):
    user_id: int 
    role_id: int 
    total_orders: int
    total_payment: float 
    total_done: int 
    monthly_orders: int 
    monthly_payment: float 
    gross: Optional[float] = None  
    
class TopUserElement(BaseModel):
    user_id: int
    user_name: str
    image_base64: Optional[str] = None
    order_count: int
    
class TopUser(BaseModel):
    totalCount: int
    top_users: List[TopUserElement]
    
class RecentUser(BaseModel):
    user_id: int
    user_name: str
    image_base64: Optional[str] = None
    
class RecentOrder(BaseModel):
    order_id: int
    essay_type: str
    student_id: int 
    student_name: str 
    total_price: float 
    status_id: int 
    sent_date: datetime
    
class DailyProfit(BaseModel):
    day: date
    total_profit: Optional[float] = 0
    total_orders: Optional[int] = 0 
    
class UploadImage(BaseModel):
    base64: str 
    
class RatingInDB(BaseModel):
    stars: float 
    comment: Optional[str] = None  
    
class Rating(BaseModel):
    rating_id: int
    order_id: int
    student_id: int 
    teacher_id: Optional[int] = None  
    stars: float 
    comment: Optional[str] = None 
    
class OptionInDB(BaseModel):
    option_name: str
    option_price: Optional[float] = Field(
        None, 
        title="The price of the option",
        gt=10000
    )
    option_type: Optional[int] = None 


class EmailSchema(BaseModel):
   email: List[EmailStr]
   
class TeacherForm(BaseModel):
    name: str
    gender_id: int
    email: EmailStr 
    address: str 
    job_id: int 
    phone_number: str 
    date_of_birth: date 
    level_id: int 
    avatar: Optional[str] = None 
    cover_letter: Optional[str] = None 
    
class TeacherStatus(BaseModel):
    teacher_id: int 
    level_id: int 
    active_essays: int 

class TeacherStatusList(BaseModel):
    totalCount: int 
    data: List[TeacherStatus]
    
    
class Invoice(BaseModel):
    order_id: int 
    user_id: int 
    type_id: int 
    level_id: int 
    option_list: List[int]
    total_price: float
    payment_type: str 
    payment_status: str 
    payment_message: str 
    payment_date: datetime 
    
class InvoiceList(BaseModel):
    totalCount: int 
    currentPage: Optional[int]
    pageCount: Optional[int]
    perPage: Optional[int]
    invoices: List[Invoice]
    
class UserCreditCard(BaseModel):
    user_id : int
    provider: Optional[str] = None
    account_no: Optional[str] = None  
    expiry_date: Optional[date] = None  
    
class UserCreditCardInfo(UserCreditCard):
    balance: Optional[float] = 1000000 
    currency: Optional[str] = "VND"
    
    
class UserCreditCardInDB(BaseModel):
    provider: str 
    account_no: str 
    expiry_date: date 
    