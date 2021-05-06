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
    tags=["Order"],
    responses={404: {"description": "Not found"}},
)

@router.get("/status")
async def get_order_status(db: Session = Depends(get_db)):
    db_status_list = db.query(models.Status).order_by(models.Status.status_id).all()
    status_list = []
    for db_status in db_status_list:
        status_list.append(schemas.Status(status_id=db_status.status_id, status_name=db_status.status_name))
    
    status_response = schemas.StatusListResponse(
        status = "success",
        totalCount = len(status_list),
        data = status_list
    )
    return status_response 

@router.get("/options")
async def get_order_option(db: Session = Depends(get_db)):
    db_option_list = db.query(models.Option).order_by(models.Option.option_id).all()
    option_list = []
    for db_option in db_option_list:
        option_list.append(schemas.Option(option_id=db_option.option_id,
                                          option_type=db_option.option_type,
                                          option_name=db_option.option_name,
                                          option_price=db_option.option_price))
    
    option_response = schemas.OptionListResponse(
        status="success",
        totalCount = len(option_list),
        data = option_list
    )
    return option_response

@router.get("/levels", 
         response_model = schemas.LevelListResponse)
async def get_essay_level(db: Session = Depends(get_db)):
    db_level_list = db.query(models.EssayLevel).order_by(models.EssayLevel.level_id).all()
    level_list = []
    for db_level in db_level_list:
        level_list.append(schemas.Level(level_id=db_level.level_id,
                                          level_name=db_level.level_name))
    
    level_response = schemas.LevelListResponse(
        status="success",
        totalCount = len(level_list),
        data = level_list
    )
    return level_response

@router.get("/types", 
         response_model = schemas.TypeListResponse)
async def get_essay_type(db: Session = Depends(get_db)):
    db_type_list = db.query(models.EssayType).order_by(models.EssayType.type_id).all()
    type_list = []
    for db_type in db_type_list:
        type_list.append(schemas.Type(type_id=db_type.type_id,
                                       level_id = db_type.level_id,
                                          type_name=db_type.type_name,
                                          type_price=db_type.type_price))
    
    type_response = schemas.TypeListResponse(
        status="success",
        totalCount = len(type_list),
        data = type_list
    )
    return type_response

@router.get("/orders", 
         response_model=schemas.OrderListResponse)
async def get_all_orders(current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    if current_account.role_id == 0:
        db_orders = db.query(models.Order).order_by(models.Order.order_id).all()
    else:
        if current_account.role_id == 1:
            db_orders = db.query(models.Order).filter(models.Order.student_id == current_account.user_id).order_by(models.Order.order_id).all()
        else:
            db_orders = db.query(models.Order).filter(models.Order.teacher_id == current_account.user_id).order_by(models.Order.order_id).all()
    
    
    order_list = []
    for db_order in db_orders:
        db_essay = db_order.essay
        if db_order.status_id == 0:
            continue 
        order_list.append(schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date,
            updated_date = db_order.updated_date,
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price
        ))
    totalCount = len(order_list)

    order_list_response = schemas.OrderListResponse(
        status = "success",
        totalCount = totalCount,
        data = order_list 
        
    )
    return order_list_response

@router.get("/orders/waiting", 
         response_model=schemas.OrderListResponse)
async def get_all_waiting_orders(current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    
    if current_account.role_id == 1:
            raise HTTPException(status_code = 403)

    db_orders = db.query(models.Order).order_by(models.Order.order_id).all()

    
    order_list = []
    for db_order in db_orders:
        db_essay = db_order.essay
        if db_order.status_id != 0:
            continue 
        order_list.append(schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date,
            updated_date = db_order.updated_date,
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price
        ))
    totalCount = len(order_list)

    order_list_response = schemas.OrderListResponse(
        status = "success",
        totalCount = totalCount,
        data = order_list 
        
    )
    return order_list_response

@router.get("/orders/waiting/{order_id}",
         response_model=schemas.OrderResponse)
async def get_waiting_order_by_id(order_id:int,
                          current_account: schemas.Account = Depends(get_current_account),
                          db: Session = Depends(get_db)):

    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code = 404)
    
    if current_account.role_id == 1:
            raise HTTPException(status_code = 403)
        
    db_essay = db_order.essay
    return schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date,
            updated_date = db_order.updated_date,
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price
        )


@router.get("/orders/saved", 
         response_model = schemas.OrderListResponse)
async def get_saved_orders(current_account: schemas.Account = Depends(get_current_account),
                           db: Session = Depends(get_db)):
    if current_account.role_id == 0:
        db_orders = db.query(models.Order).order_by(models.Order.order_id).all()
    else:
        if current_account.role_id == 1:
            db_orders = db.query(models.Order).filter(models.Order.student_id == current_account.user_id).order_by(models.Order.order_id).all()
        else:
            raise  HTTPException(status_code=403)
    
    
    order_list = []
    for db_order in db_orders:
        db_essay = db_order.essay
        if db_order.status_id != 0:
            continue 
        order_list.append(schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date,
            updated_date = db_order.updated_date,
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price
        ))
    totalCount = len(order_list)

    order_list_response = schemas.OrderListResponse(
        status = "success",
        totalCount = totalCount,
        data = order_list 
    )
    return order_list_response
         
@router.get("/orders/{order_id}",
         response_model=schemas.OrderResponse)
async def get_order_by_id(order_id:int,
                          current_account: schemas.Account = Depends(get_current_account),
                          db: Session = Depends(get_db)):
    role_id = current_account.role_id
    user_id = current_account.user_id
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code = 404)
    if role_id in [1,2] and user_id not in [db_order.student_id, db_order.teacher_id]:
        raise HTTPException(status_code = 403)
    db_essay = db_order.essay
    return schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date,
            updated_date = db_order.updated_date,
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price
        )

        
@router.post("/orders", 
          response_model=schemas.OrderResponse)
async def create_order(new_order: schemas.OrderInDB,
                       status_id: int, 
                       current_account: schemas.Account = Depends(get_current_account),
                       db: Session = Depends(get_db)):
    if not current_account.role_id == 1:
        raise  HTTPException(status_code=403, detail="Permission Not Found with role id =" + str(current_account.role_id) )
    
    sent_date = date.today().strftime("%Y/%m/%d")
    updated_date = sent_date
    updated_by = current_account.user_id
    student_id = current_account.user_id 
    
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == new_order.essay.type_id).first()
    db_optionlist = db.query(models.Option).all()
    
    if not db_type:
        raise HTTPException(status_code=400, detail="Type ID not found") 
    
    db_essay = models.Essay(
            title=new_order.essay.title,
            content=new_order.essay.content,
            type_id=new_order.essay.type_id,
            
    )
    db.add(db_essay)
    db.commit()
    db.refresh(db_essay)
    
    total_price = 0
    for option_id in new_order.option_list:
        total_price += db_optionlist[option_id].option_price 
    total_price += db_type.type_price 
        
    db_order = models.Order(
        student_id = current_account.user_id,
        status_id = status_id,
        sent_date = sent_date,
        updated_date = sent_date,
        updated_by = current_account.user_id,
        essay_id = db_essay.essay_id,
        option_list = '-'.join(str(item) for item in new_order.option_list),
        total_price = total_price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    create_order_response = schemas.OrderResponse(
        status_id = db_order.status_id,
        order_id = db_order.order_id,
        student_id = db_order.student_id,
        teacher_id = db_order.teacher_id,
        sent_date = sent_date,
        updated_date = sent_date,
        updated_by = db_order.student_id,
        essay = schemas.EssayResponse(
            essay_id = db_essay.essay_id,
            title = db_essay.title,
            content = db_essay.content,
            type_id = db_essay.type_id
        ),
        option_list = [int(item) for item in db_order.option_list.split("-")],
        total_price = db_order.total_price
    )
    return create_order_response

@router.put("/oders/saved/{order_id}",
         response_model=schemas.OrderResponse)
async def update_order(order_id: int,
                       updated_order: schemas.OrderUpdate,
                       current_account: schemas.Account = Depends(get_current_account),
                       db: Session = Depends(get_db)):
    
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first() 
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == updated_order.essay.type_id).first()
    db_optionlist = db.query(models.Option).order_by(models.Option.option_id).all()
    
    if not db_order:
        raise HTTPException(status_code=404)
    
    if current_account.role_id == 1 and current_account.user_id != db_order.student_id:
        raise HTTPException(status_code = 403)
    
    if current_account.role_id == 1 and db_order.status_id != 0:
        raise HTTPException(status_code = 403, detail="You can not change the order!")

    db_status_list = db.query(models.Status).all()
    if updated_order.status_id not in [db_status.status_id for db_status in db_status_list]:
        raise HTTPException(status_code = 400)
    
    updated_date = date.today().strftime("%Y/%m/%d")
    
    db_order.status_id = updated_order.status_id 
    db_order.updated_by = current_account.user_id 
    db_order.updated_date = updated_date
    db_order.essay.title = updated_order.essay.title 
    db_order.essay.content = updated_order.essay.content
    db_order.essay.type_id = updated_order.essay.type_id
    db_order.option_list = '-'.join(str(item) for item in updated_order.option_list)
    
    total_price = 0
    for option_id in updated_order.option_list:
        total_price += db_optionlist[option_id].option_price 
    total_price += db_type.type_price 
    
    db_order.total_price = total_price
    
    db.commit()
    db.refresh(db_order)
    db_essay = db_order.essay 
    update_order_response = schemas.OrderResponse(
        status_id = db_order.status_id,
        order_id = db_order.order_id,
        student_id = db_order.student_id,
        teacher_id = db_order.teacher_id,
        sent_date = db_order.sent_date,
        updated_date = db_order.updated_date,
        updated_by = db_order.updated_by,
        essay = schemas.EssayResponse(
            essay_id = db_essay.essay_id,
            title = db_essay.title,
            content = db_essay.content,
            type_id = db_essay.type_id
        ),
        option_list = [int(item) for item in db_order.option_list.split("-")],
        total_price = db_order.total_price
    )
    return update_order_response




@router.put("/orders/assign/{order_id}", 
         response_model=schemas.OrderResponse)
async def assign_teacher_order(order_id:int,
                                current_account: schemas.Account = Depends(get_current_account),
                               db: Session = Depends(get_db),
                               teacher_id: Optional[int] = None):
    
    if current_account.role_id == 1:
        raise HTTPException(status_code=403, detail="Student accounts are not allowed!")
    if current_account.role_id == 0:
        if not teacher_id:
            raise HTTPException(status_code=400, detail="Admin must provide a teacher_id!")
    else:
        teacher_id = current_account.user_id
    
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="order_id not found")
    if db_order.status_id != 1:
        raise HTTPException(status_code=405, detail="The order is not available or was taken")
    db_order.teacher_id = teacher_id
    db_order.status_id = 2
    db.commit()
    db.refresh(db_order)
    db_essay = db_order.essay 
    update_order_response = schemas.OrderResponse(
        status_id = db_order.status_id,
        order_id = db_order.order_id,
        student_id = db_order.student_id,
        teacher_id = db_order.teacher_id,
        sent_date = db_order.sent_date,
        updated_date = db_order.updated_date,
        updated_by = db_order.updated_by,
        essay = schemas.EssayResponse(
            essay_id = db_essay.essay_id,
            title = db_essay.title,
            content = db_essay.content,
            type_id = db_essay.type_id
        ),
        option_list = [int(item) for item in db_order.option_list.split("-")],
        total_price = db_order.total_price
    )
    return update_order_response
    
    
