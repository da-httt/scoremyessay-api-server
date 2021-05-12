from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 
from typing import Optional, List
from sqlalchemy import func
router = APIRouter(
    tags=["Statistics"],
    responses={404: {"description": "Not found"}},
)

def get_user_account(db_user: Session):
    return schemas.UserAccount(
            account_id = db_user.account.account_id,
            role_id = db_user.account.role_id,
            email = db_user.account.email,
            disabled = db_user.account.disabled,
            info = schemas.User(user_id = db_user.user_id,
                        name =  db_user.name,
                        date_of_birth =  db_user.date_of_birth,
                        address = db_user.address,
                        gender_id = db_user.gender_id,
                        job_id = db_user.job_id,
                        phone_number = db_user.phone_number)
            
        )
    
@router.get("/statistics/me",
            response_model = schemas.UserStatistics,
            description="Get current user's statistics: total/monthly orders, total/monthly payment")
async def get_current_statistic(current_account: schemas.Account = Depends(get_current_account),
                                db: Session = Depends(get_db)):
    user_id = current_account.user_id
    user_role_id = current_account.role_id
    db_order_list = []
    
    if user_role_id == 1:
        db_order_list = db.query(models.Order).filter(models.Order.student_id == user_id).all()
    elif user_role_id == 2:
        db_order_list = db.query(models.Order).filter(models.Order.teacher_id == user_id).all()
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
            

@router.get("/statistics/recent_users")
async def get_users_statistic(current_account: schemas.Account = Depends(get_current_account),
                                  db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_user_list = db.query(models.User).\
                    order_by(models.User.user_id.desc()).\
                        limit(10).\
                            all()
    recent_users = []
    for db_user in db_user_list:
        recent_users.append(schemas.RecentUser(
            user_id = db_user.user_id,
            user_name = db_user.name
        ))
    return recent_users
        
@router.get("/statistics/recent_orders",
            response_model = List[schemas.RecentOrder])
async def get_users_statistic(current_account: schemas.Account = Depends(get_current_account),
                                  db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_order_list = db.query(models.Order).\
                    filter(models.Order.status_id != 0).\
                    order_by(models.Order.order_id.desc()).\
                        limit(10).\
                            all()
    recent_orders = []
    for db_order in db_order_list:
        recent_orders.append(schemas.RecentOrder(
            order_id = db_order.order_id,
            essay_type = db_order.essay.essay_type.type_name,
            student_id = db_order.student.user_id,
            student_name = db_order.student.name,
            total_price = db_order.total_price, 
            status_id = db_order.status_id 
        ))
    return recent_orders
             

@router.get("/statistics/top_user",
            response_model=schemas.TopUser)
async def get_top_users_statistic(current_account: schemas.Account = Depends(get_current_account),
                                  db: Session = Depends(get_db)):
    count_ = func.count(models.Order.student_id)
    db_user_count = db.query(models.Order.student_id, count_).\
                            group_by(models.Order.student_id).\
                            order_by(count_.desc()).\
                            limit(10).\
                            all()
    top_users = []
    for db_user_index in db_user_count:
        db_user = db.query(models.User).filter(models.User.user_id == db_user_index[0]).first()
        top_users.append(schemas.TopUserElement(
            user_id = db_user.user_id,
            user_name = db_user.name,
            order_count = db_user_index[1]
        ))
    
    return schemas.TopUser(
        totalCount = len(db_user_count),
        top_users = top_users
    )

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

@router.get("/statistics/profit/days")
async def get_daily_profit(current_account:schemas.Account = Depends(get_current_account),
                           db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    count_ = func.count(models.Order.sent_date)
    
    db_order_list = db.query(models.Order).\
                    order_by(models.Order.sent_date.desc()).\
                    all()
    daily_profit_list = []
    j = 0
    
    
    for i in range(0,30):
        total_profit = 0
        total_orders = 0 
        current_date = datetime.today().date() - timedelta(days=i)
        daily_profit_list.append(schemas.DailyProfit(
            day = current_date,
            total_profit = total_profit, 
            total_orders = total_orders 
        ))
    
    for db_order in db_order_list:
        for daily_profit in daily_profit_list:
            if db_order.sent_date.date() == daily_profit.day:
                daily_profit.total_profit += db_order.total_price 
                daily_profit.total_orders += 1
    
    
    return {
        "totalDay": len(daily_profit_list),
        "daily_profit": daily_profit_list
    }
    
