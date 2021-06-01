from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status, Query 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from routers.teacher_promo import *
import schemas 
import models 
from typing import Optional, List
from sqlalchemy import desc, schema
from modules import paragraph
#from dependencies import predictor 
from modules import spelling
import json
router = APIRouter(
    tags=["Order"],
    responses={404: {"description": "Not found"}},
)






def get_topic(db_essay:models.Essay, db:Session):
    db_essay_info = db_essay.essay_info
    if not db_essay_info:
        num_error, spelling_errors = spelling.spellCheck(db_essay.content)
        data = json.dumps(spelling_errors)
        topic_predicted = "SCIENE & TECH" 
        db_essay_info = models.EssayInfo(
            essay_id = db_essay.essay_id,
            predicted_topic = topic_predicted,
            num_errors = num_error,
            spelling_errors = data
        )
        db.add(db_essay_info)
        db.commit()
        db.refresh(db_essay_info)
    else:
        return db_essay_info[0]
    return db_essay_info

def convert_type_to_level(db, type_id: int):
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == type_id).first()
    return db_type.level.level_id

def get_user_id(db: Session, order_id: int):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    return db_order.student_id, db_order.teacher_id

def check_user_order(db: Session, order_id: int, user_id: int):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if user_id in [db_order.student_id, db_order.teacher_id]:
        return True 
    return False 

def get_time_left(db, db_order: models.Order):
    time_left = 0
    current_time = datetime.today()
    if db_order.status_id != 0:
        current_time_left =  db_order.deadline - current_time + timedelta(hours=1)
        if current_time_left.days >= 0 :
            time_left = current_time_left.days*24 + (current_time_left.seconds // 3600)
    if (time_left == 0 and db_order.status_id in [1,2]) or (current_time - db_order.sent_date >  timedelta(minutes=30) and (db_order.status_id == 1)):
        db_order.status_id = 4
        db.commit()
        db.refresh(db_order)
    return time_left 
    
def get_order_response(db_order: models.Order, db: Session):
    db_essay = db_order.essay
    deadline = None 
    if db_order.deadline:
        deadline = db_order.deadline.strftime("%m/%d/%Y, %H:%M:%S")
    db_essay_info = get_topic(db_essay, db)
    print(db_essay_info.predicted_topic)
    return schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date.strftime("%m/%d/%Y, %H:%M:%S"),
            updated_date = db_order.updated_date.strftime("%m/%d/%Y, %H:%M:%S"),
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price,
            is_disabled = db_order.is_disabled,
            deadline = deadline,
            time_left = get_time_left(db, db_order),
            topic_name = db_essay_info.predicted_topic
        )

@router.get("/status",
            description="Get all the status in the database")
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
         response_model=schemas.OrderListResponse,
         description='''
         Get all the orders from the database.
         Student Account: get orders with same student_id
         Teacher Account: get orders with same teacher_id 
         Admin: get all the orders
         ''')
async def get_all_orders(current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    if current_account.role_id == 0:
        db_orders = db.query(models.Order).order_by(desc(models.Order.order_id)).all()
    else:
        if current_account.role_id == 1:
            db_orders = db.query(models.Order).filter(models.Order.student_id == current_account.user_id).order_by(models.Order.order_id).all()
        else:
            db_orders = db.query(models.Order).filter(models.Order.teacher_id == current_account.user_id).order_by(models.Order.order_id).all()
    
    
    order_list = []
    for db_order in db_orders:
        if (db_order.status_id == 0 or db_order.is_disabled):
            continue
        order_list.append(get_order_response(db_order, db))
    totalCount = len(order_list)

    order_list_response = schemas.OrderListResponse(
        status = "success",
        totalCount = totalCount,
        data = order_list 
        
    )
    return order_list_response

@router.get("/orders/waiting", 
         response_model=schemas.OrderListResponse,
         description='''
         For Teacher/Admin Account.
         Get all the orders from the students if they are not taken by anyone.
         ''')
async def get_all_waiting_orders(current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    
    if current_account.role_id == 1:
            raise HTTPException(status_code = 403)

    db_orders = db.query(models.Order).order_by(models.Order.order_id).all()
    db_teacher_status = db.query(models.TeacherStatus).filter(models.TeacherStatus.teacher_id == current_account.user_id).first()
    
    order_list = []
    print("get waiting order")
    for db_order in db_orders:
        if db_order.status_id != 1 or db_order.is_disabled or convert_type_to_level(db, db_order.essay.type_id) != db_teacher_status.level_id :
            continue
        order_list.append(get_order_response(db_order, db))
    totalCount = len(order_list)

    order_list_response = schemas.OrderListResponse(
        status = "success",
        totalCount = totalCount,
        data = order_list 
        
    )
    return order_list_response

@router.get("/orders/waiting/{order_id}",
         response_model=schemas.OrderResponse,
         description='''
         For Teacher/Admin Account.
         Receive specific information of an order from waiting list.
         ''')
async def get_waiting_order_by_id(order_id:int,
                          current_account: schemas.Account = Depends(get_current_account),
                          db: Session = Depends(get_db)):

    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    db_teacher_status = db.query(models.TeacherStatus).filter(models.TeacherStatus.teacher_id == current_account.user_id).first()
    if convert_type_to_level(db, db_order.essay.type_id) != db_teacher_status.level_id:
        raise HTTPException(status_code=403, detail="Teacher's level doesn't match")
    if not db_order or db_order.is_disabled:
        raise HTTPException(status_code = 404, detail="Order not found")
    
    if current_account.role_id == 1:
            raise HTTPException(status_code = 403)

    return get_order_response(db_order, db)


@router.get("/orders/saved", 
         response_model = schemas.OrderListResponse,
         description='''
         For Student/Admin Account.
         Get all saved orders created by specific students.
         If used by Admin, get all saved order by all students.
         ''')
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
        if db_order.status_id != 0 or db_order.is_disabled:
            continue 
        order_list.append(get_order_response(db_order, db))
    totalCount = len(order_list)

    order_list_response = schemas.OrderListResponse(
        status = "success",
        totalCount = totalCount,
        data = order_list 
    )
    return order_list_response
         
@router.get("/orders/{order_id}",
         response_model=schemas.OrderResponse,
         description='''
         For Teacher/Student/Admin Account.
         Get specific information of an order that has the same student_id or teacher_id.
         ''')
async def get_order_by_id(order_id:int,
                          current_account: schemas.Account = Depends(get_current_account),
                          db: Session = Depends(get_db)):
    role_id = current_account.role_id
    user_id = current_account.user_id
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order or db_order.is_disabled:
        raise HTTPException(status_code = 404)
    if role_id in [1,2] and user_id not in [db_order.student_id, db_order.teacher_id]:
        raise HTTPException(status_code = 403)

    return get_order_response(db_order, db)

        
@router.post("/orders", 
          response_model=schemas.OrderResponse,
          description='''
          For Student/Admin account.
          Create a new order.
          ''')
async def create_order(new_order: schemas.OrderInDB,
                       status_id: int, 
                       current_account: schemas.Account = Depends(get_current_account),
                       db: Session = Depends(get_db)):
    if not current_account.role_id in [0,1]:
        raise  HTTPException(status_code=403, detail="Permission Not Found with role id =" + str(current_account.role_id) )
    
    if status_id not in [0,1]:
        raise HTTPException(status_code=400, detail="Wrong status id!")
    
    sent_date = datetime.today()
    updated_date = sent_date
    updated_by = current_account.user_id
    student_id = current_account.user_id 
    
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == new_order.essay.type_id).first()
    db_optionlist = db.query(models.Option).all()
    
    if not db_type:
        raise HTTPException(status_code=400, detail="Type ID not found") 
    if status_id == 1:
        if not if_any_teacher_left(level_id=convert_type_to_level(db, new_order.essay.type_id)):
            raise HTTPException(status_code=408, detail="All Teachers are busy")
    
    db_essay = models.Essay(
            title=new_order.essay.title,
            content=new_order.essay.content,
            type_id=new_order.essay.type_id,
            
    )
    db.add(db_essay)
    db.commit()
    db.refresh(db_essay)
    
    total_price = 0
    deadline_hour = 0
    for option_id in new_order.option_list:
        total_price += db_optionlist[option_id].option_price
        if db_optionlist[option_id].option_type == 1:
            deadline_hour = int(db_optionlist[option_id].option_name)
    total_price += db_type.type_price
    
    #Set deadline 
    if status_id == 0:
        deadline = None 
    else: 
        deadline = datetime.today() + timedelta(hours=deadline_hour)
        
    db_order = models.Order(
        student_id = current_account.user_id,
        status_id = status_id,
        sent_date = sent_date,
        updated_date = sent_date,
        updated_by = current_account.user_id,
        essay_id = db_essay.essay_id,
        option_list = '-'.join(str(item) for item in new_order.option_list),
        total_price = total_price,
        is_disabled = False,
        deadline = deadline 
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    

    return get_order_response(db_order, db)

@router.put("/orders/saved/{order_id}",
         response_model=schemas.OrderResponse,
         description='''
         For student/admin account 
         Get the specific information of a saved order created by student.
         ''')
async def update_order(order_id: int,
                       updated_order: schemas.OrderUpdate,
                       current_account: schemas.Account = Depends(get_current_account),
                       db: Session = Depends(get_db)):
    
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first() 
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == updated_order.essay.type_id).first()
    db_optionlist = db.query(models.Option).order_by(models.Option.option_id).all()
    
    if not db_order or db_order.is_disabled:
        raise HTTPException(status_code=404)
    
    if current_account.role_id == 1 and current_account.user_id != db_order.student_id:
        raise HTTPException(status_code = 403, detail="This order doesn't belong to you!")
    
    if current_account.role_id == 1 and db_order.status_id != 0:
        raise HTTPException(status_code = 403, detail="You can not change the order!")

    db_status_list = db.query(models.Status).all()
    if updated_order.status_id not in [db_status.status_id for db_status in db_status_list]:
        raise HTTPException(status_code = 400)
    
    updated_date = datetime.today()
    
    if updated_order.status_id == 1:
        if not if_any_teacher_left(level_id=convert_type_to_level(db, updated_order.essay.type_id)):
            raise HTTPException(status_code=408, detail="All Teachers are busy")
    
    
    db_order.status_id = updated_order.status_id 
    db_order.updated_by = current_account.user_id 
    db_order.updated_date = updated_date
    db_order.essay.title = updated_order.essay.title 
    db_order.essay.content = updated_order.essay.content
    db_order.essay.type_id = updated_order.essay.type_id
    db_order.option_list = '-'.join(str(item) for item in updated_order.option_list)
    
    total_price = 0
    deadline = 0
    for option_id in updated_order.option_list:
        total_price += db_optionlist[option_id].option_price
        for db_option in db_optionlist:
            if db_option.option_id == option_id:
                if db_option.option_type == 1:
                    deadline_hour = int(db_option.option_name) 
    total_price += db_type.type_price 
    time_left = 0
    #Set deadline 
    if updated_order.status_id == 0:
        deadline = None 
    else: 
        print("update_order")
        deadline = datetime.today() + timedelta(hours=deadline_hour)
        
    db_order.total_price = total_price
    db_order.deadline = deadline

    
    db.commit()
    db.refresh(db_order)
    
    return get_order_response(db_order, db)




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
    
    db_teacher_status = db.query(models.TeacherStatus).filter(models.TeacherStatus.teacher_id == teacher_id).first()
    if if_max_essays(db_teacher_status):
        raise HTTPException(status_code=405, detail="the teacher has reached maximum essays")
    
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order or db_order.is_disabled:
        raise HTTPException(status_code=404, detail="order_id not found")
    if db_order.status_id != 1:
        raise HTTPException(status_code=405, detail="The order is not available or was taken")
    
    updated_date = datetime.today()
    db_order.updated_date = updated_date 
    db_order.teacher_id = teacher_id
    db_order.status_id = 2
    db.commit()
    db.refresh(db_order)
    
    change_current_scoring_essay(db, db_teacher_status, increase=True)
    
    return get_order_response(db_order, db)
    
    
@router.delete("/orders/saved/{order_id}")
async def delete_saved_order(order_id: int,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first() 

    if not db_order or db_order.status_id != 0:
        raise HTTPException(status_code=404)
    
    if current_account.user_id != db_order.student_id and current_account.role_id != 0:
        raise HTTPException(status_code=403)
    updated_date = datetime.today()
    db_order.updated_date = updated_date 
    
    db_order.is_disabled = not db_order.is_disabled
    db.commit()
    db.refresh(db_order)

    return get_order_response(db_order, db)

@router.delete("/orders/{order_id}",
               description="Disable the paid order if student decide to cancel it, or the order is not taken before the deadline")
async def delete_order(order_id: int,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first() 

    if not db_order or db_order.status_id in [0,3,4]:
        raise HTTPException(status_code=404)
    
    if current_account.user_id != db_order.student_id and current_account.role_id != 0:
        raise HTTPException(status_code=403)
    updated_date = datetime.today()
    db_order.updated_date = updated_date 
    db_order.status_id = 4
    db.commit()
    db.refresh(db_order)

    return get_order_response(db_order, db)
    
@router.get("/orders/image/{order_id}")
async def get_order_image(order_id:int,
                          current_account: schemas.Account = Depends(get_current_account),
                          db: Session = Depends(get_db)):
    db_order_img = db.query(models.OrderImage).filter(models.OrderImage.order_id == order_id).first()
    if not db_order_img:
        db_order_img = models.OrderImage(order_id=order_id)
        db.add(db_order_img)
        db.commit()
        db.refresh(db_order_img)
    return {
        "order_id": db_order_img.order_id,
        "image_base64": db_order_img.img 
    }


@router.put("/orders/image/{order_id}")
async def upload_order_image(order_id:int,
                          order_image: schemas.UploadImage,
                          current_account: schemas.Account = Depends(get_current_account),
                          db: Session = Depends(get_db)):
    db_order_img = db.query(models.OrderImage).filter(models.OrderImage.order_id == order_id).first()
    if not db_order_img:
        db_order_img = models.OrderImage(order_id=order_id)
        db.add(db_order_img)
        db.commit()
        db.refresh(db_order_img)
    db_order_img.img = order_image.base64
    db.commit()
    db.refresh(db_order_img)
    return {
        "order_id": db_order_img.order_id,
        "image_base64": db_order_img.img 
    }


@router.post("/ratings/{order_id}")
async def create_order_rating(order_id: int,
                              rating_in_db: schemas.RatingInDB,
                              current_account: schemas.Account  = Depends(get_current_account),
                              db: Session = Depends(get_db)):
    if current_account.role_id == 2:
        raise HTTPException(status_code=403)

    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found!")
    
    if db_order.status_id != 3:
        raise HTTPException(status_code=409, detail="Order not done yet!")
    
    db_rating = db.query(models.Rating).filter(models.Rating.order_id==order_id).first()
    
    if db_rating:
        raise HTTPException(status_code=409, detail="Rating already exists!")
    
    try:
        db_rating = models.Rating(
            order_id = order_id,
            stars = rating_in_db.stars,
            comment = rating_in_db.comment
        )
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
    except RuntimeError: 
        raise HTTPException(status_code=500)
    
    
    return schemas.Rating(
            rating_id = db_rating.rating_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            order_id = db_rating.order_id,
            stars = db_rating.stars,
            comment = db_rating.comment
    )

@router.get("/ratings/{order_id}",
             response_model = schemas.Rating)
async def get_order_rating(order_id: int,
                              current_account: schemas.Account  = Depends(get_current_account),
                              db: Session = Depends(get_db)):

    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found!")
    
    if current_account.user_id not in [db_order.student_id, db_order.teacher_id] and current_account.role_id != 0:
        raise HTTPException(status_code=403)

    
    db_rating = db.query(models.Rating).filter(models.Rating.order_id==order_id).first()
    
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found!!")
    
    return schemas.Rating(
            rating_id = db_rating.rating_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            order_id = db_rating.order_id,
            stars = db_rating.stars,
            comment = db_rating.comment
    )  
    
@router.get("/ratings")
async def get_rating_list(current_account: schemas.Account  = Depends(get_current_account),
                          student_id: int = Query(None, description="Get rating list by student id"),
                            db: Session = Depends(get_db)):

    db_rating_list = []
    db_rating_list = db.query(models.Rating).\
                            order_by(models.Rating.rating_id.desc()).\
                            all()
    
    rating_list = []
    for db_rating in db_rating_list:
        if current_account.role_id != 0 :
            if not check_user_order(db, db_rating.order_id, current_account.user_id):
                continue
        student_id, teacher_id = get_user_id(db, db_rating.order_id)
        print(student_id)
        print(teacher_id)
        rating_list.append(schemas.Rating(
            rating_id = db_rating.rating_id,
            student_id = student_id,
            teacher_id = teacher_id, 
            order_id = db_rating.order_id,
            stars = db_rating.stars,
            comment = db_rating.comment 
        ))
    
    return {
        "totalCount": len(db_rating_list),
        "data": rating_list 
    }

@router.put("/ratings/{order_id}",
            response_model = schemas.Rating,
            description="Admin API")
async def update_order_rating(order_id: int,
                              rating_in_db: schemas.RatingInDB,
                              current_account: schemas.Account  = Depends(get_current_account),
                              db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)

    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if db_order.status_id != 3:
        raise HTTPException(status_code=409, detail="Order not done yet!")
    else:
        db_rating.stars = rating_in_db.stars
        db_rating.comment = rating_in_db.comment
        db.commit()
        db.refresh(db_rating)
    
    
    return schemas.Rating(
            rating_id = db_rating.rating_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            order_id = db_rating.order_id,
            stars = db_rating.stars,
            comment = db_rating.comment
    )
    
@router.get("/ratings/teacher/{user_id}",
            description="Admin API")
async def get_teacher_rating(user_id: int,
                              current_account: schemas.Account  = Depends(get_current_account),
                              db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user or db_user.account.role_id  in [0,1]:
        raise HTTPException(status_code=404)
    
    db_user_order = db.query(models.Order).filter(models.Order.teacher_id == user_id).all()

    rating_response = {
        "teacher_id": db_user.user_id,
        "teacher_name": db_user.name,
        "average_rating": 0
    }
    
    if len(db_user_order) == 0:
        return rating_response
    
    rating_list = [] 
    for db_order in db_user_order:
        if db_order.rating != []:
            rating_list.append(db_order.rating[0].stars)
    
    if len(rating_list) == 0:
        return rating_response
    else:
        rating_response['average_rating'] = sum(rating_list)/len(rating_list)
        return rating_response 

