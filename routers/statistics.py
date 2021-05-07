from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 
from typing import Optional, List

router = APIRouter(
    tags=["Statistics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/statistics/me",
            response_model = schemas.UserStatistics,
            description="Get current user's statistics: total/monthly orders, total/monthly payment")
async def get_current_statistic(current_account: schemas.Account = Depends(get_current_account),
                                db: Session = Depends(get_db)):
    user_id = current_account.user_id
    user_role_id = current_account.role_id
    db_order_list = db.query(models.Order).filter(models.Order.student_id == user_id).all()
    total_orders = 0
    total_payment = 0
    total_done = 0
    monthly_orders = 0
    monthly_payment = 0
    last_month_payment = 0
    gross = None 
    current_month = datetime.today().date().month
    last_month = current_month - 1
    for db_order in db_order_list:
        if db_order.status_id in [1,2,3,4]:
            total_orders += 1
            total_payment += db_order.total_price 
            if db_order.status_id == 3:
                total_done += 1
            if db_order.sent_date.date().month == current_month:
                monthly_orders += 1
                monthly_payment += db_order.total_price
            if db_order.sent_date.date().month == last_month:
                last_month_payment += db_order.total_price
    
    if last_month_payment > 0:
        gross = (monthly_payment / last_month_payment)*100
    
    return schemas.UserStatistics(
        user_id = user_id,
        role_id = user_role_id,
        total_orders = total_orders,
        total_payment = total_payment,
        total_done = total_done,
        monthly_orders = monthly_orders,
        monthly_payment = monthly_payment,
        gross = gross 
    )
            

            
        
    
    


@router.get("/statistics/users")
async def get_users_statistic():
    pass 

@router.get("/statistics/top")
async def get_top_users_statistic():
    pass 

@router.get("/statistics/top")
async def get_top_users_statistic():
    pass 


@router.get("/deadlines",
            response_model=schemas.Deadline)
async def get_user_deadlines(current_account: schemas.Account = Depends(get_current_account),
                              db: Session = Depends(get_db)):
    
    user_role_id = current_account.role_id
    user_id = current_account.user_id
    db_order_list = []

    if user_role_id == 1:
        db_order_list = db.query(models.Order).filter(models.Order.student_id == user_id).all()
    elif user_role_id == 2:
        db_order_list = db.query(models.Order).filter(models.Order.teacher_id == user_id).all()
        
    today_deadline = 0
    week_deadline = 0
    total_deadline  = 0
    
    
    for db_order in db_order_list:
        if db_order.status_id in [0,3,4]:
            continue
        if db_order.deadline.date().isocalendar()[1] == datetime.today().date().isocalendar()[1]:
            week_deadline +=1
        if db_order.deadline.date() == datetime.today().date():
            today_deadline +=1 
        if db_order.status_id == 2:
            total_deadline += 1
        if db_order.status_id == 1 and user_role_id == 1:
            total_deadline += 1
            
    
    return schemas.Deadline(
        total_deadline = total_deadline,
        today_deadline = today_deadline,
        week_deadline = week_deadline
    )

