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

models.Base.metadata.create_all(bind=engine)

#Define secret key and algorithm
SECRET_KEY = "b8f93afd6ae4f16427e475cb090a23671e6e9f00dc5fbd603c1469355f575854"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000


#Initialize app
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
        
#Define CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Define authenticate function
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_account(db: Session, email: str):
    print("checking email with " + email)
    return db.query(models.Account).filter(models.Account.email == email).first()


def authenticate_account(db: Session, email: str, password: str):
    account = get_account(db, email)
    if not account:
        print("Account not found!")
        return False 
    if not verify_password(password, account.hashed_password):
        print("Wrong password")
        return False 
    return account

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt 


async def get_current_account(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") 
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    account = get_account(db, email=token_data.email)
    if account is None:
        raise credentials_exception
    
    print("see role: " + account.role.role_name)
    schema_account = schemas.Account(
        user_id = account.user[0].user_id,
        account_id=account.account_id,
        email=account.email,
        role_id=account.role_id,
        disabled=account.disabled)
    return schema_account 

async def create_account(db: Session, new_account: schemas.SignUp):
    
    hashed_password = get_password_hash(new_account.password)
    db_account = models.Account(email=new_account.email, 
                                hashed_password=hashed_password, 
                                disabled=False, 
                                role_id=1)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    db_user = models.User(account_id=db_account.account_id,
                          name = new_account.name,
                          address = new_account.address,
                          gender_id = new_account.gender_id,
                          job_id = new_account.job_id,
                          phone_number = new_account.phone_number,
                          date_of_birth = new_account.date_of_birth
                         )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_account, db_user
    
"""#Define Order Function 
async def create_new_order(db: Session, order: OrderCreate, db_account: models.Account):
    if db.query(models.Order).filter(models.Order.essay_id == order.essay_id):
        raise HTTPException(status_code=400, detail="Essay already registered")
    db_order = models.Order(**order.dict(), )

    """

#Authentication Route 
async def get_current_active_account(account: schemas.Account = Depends(get_current_account)):
    print("Getting info..")
    if account.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    print(account)
    return account

@app.post("/token", response_model=schemas.Token, tags=['Authentication'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account = authenticate_account(db, form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=schemas.Token, tags=['Authentication'])
async def login_for_access_token(account_login: schemas.AccountLogin, db: Session = Depends(get_db)):
    account = authenticate_account(db, account_login.username, account_login.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", response_model=schemas.Account, tags=['Authentication'])
async def signup_for_new_account(new_account: schemas.SignUp,
                                db: Session = Depends(get_db)):
    
    if get_account(db, new_account.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not db.query(models.Role).filter(models.Job.job_id == new_account.job_id).first():
        raise HTTPException(status_code=400, detail="role_id not found")
    
    if not db.query(models.Gender).filter(models.Gender.gender_id == new_account.gender_id).first():
        raise HTTPException(status_code=400, detail="gender_id not found")
    
    
    db_account, _ = await create_account(db, new_account)
    return schemas.Account(account_id=db_account.account_id,
                   user_id = db_account.user[0].user_id,
                   email = db_account.email,
                   disabled = db_account.disabled,
                   role_id=db_account.role_id)
    



@app.get("/accounts/me", response_model=schemas.Account, tags=['Authentication'])
async def read_account_me(current_account: schemas.Account = Depends(get_current_active_account)):
    return current_account


@app.get("/jobs", response_model= schemas.JobResponse, tags=['User'])
async def read_job_list(db: Session=Depends(get_db)):
    db_job_list = db.query(models.Job).all()
    job_list = []
    for db_job in db_job_list:
        job_list.append(schemas.Job(job_id=db_job.job_id, job_name=db_job.job_name))
    
    job_response = schemas.JobResponse(
        status = "success",
        totalCount = len(job_list),
        data = job_list
    )
    return job_response

@app.get("/genders", response_model= schemas.GenderResponse, tags=['User'])
async def read_gender_list(db: Session=Depends(get_db)):
    db_gender_list = db.query(models.Gender).all()
    gender_list = []
    for db_gender in db_gender_list:
        gender_list.append(schemas.Gender(gender_id=db_gender.gender_id, gender_name=db_gender.gender_name))
    
    gender_response = schemas.GenderResponse(
        status = "success",
        totalCount = len(gender_list),
        data = gender_list
    )
    return gender_response


# User route 

@app.get("/users/me", 
         response_model=schemas.UserAccount, 
         description = "Get the user information of current account",
         tags = ["User"])
async def read_user_information(current_account: schemas.Account = Depends(get_current_account), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.account_id == current_account.account_id).first()
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
    
@app.get("/users",
         response_model = schemas.UserResponse,
         description = "Get the all user information in database",
         tags = ["User"])
async def read_all_users(current_account: schemas.Account = Depends(get_current_account), db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403, detail="Only Admin can access this api")
    
    db_user_list = db.query(models.User).all()
    user_list = []
    for db_user in db_user_list:
        user_list.append(schemas.UserAccount(
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
            
        ))
    user_response = schemas.UserResponse(
        status = "success", 
        totalCount = len(user_list),
        perPage = len(user_list),
        data = user_list
    )
    return user_response 
        

@app.put("/users/{user_id}", tags=["User"])
async def update_user():
    pass 

@app.delete("/users/{user_id}", tags=["User"])
async def delete_user():
    pass 

#Order Management 

@app.get("/status", tags=["Order"])
async def get_order_status(db: Session = Depends(get_db)):
    db_status_list = db.query(models.Status).all()
    status_list = []
    for db_status in db_status_list:
        status_list.append(schemas.Status(status_id=db_status.status_id, status_name=db_status.status_name))
    
    status_response = schemas.StatusListResponse(
        status = "success",
        totalCount = len(status_list),
        data = status_list
    )
    return status_response 

@app.get("/options", tags=["Order"])
async def get_order_option(db: Session = Depends(get_db)):
    db_option_list = db.query(models.Option).all()
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
    
    

@app.get("/orders", 
         response_model=schemas.OrderListResponse,
         tags=["Order"])
async def get_all_orders(current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    if current_account.role_id == 0:
        db_orders = db.query(models.Order).all()
    else:
        if current_account.role_id == 1:
            db_orders = db.query(models.Order).filter(models.Order.student_id == current_account.user_id).all()
        else:
            db_orders = db.query(models.Order).filter(models.Order.teacher_id == current_account.user_id).all()
    
    
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
        

@app.get("/orders/saved", 
         response_model = schemas.OrderListResponse,
         tags=["Order"])
async def get_saved_orders(current_account: schemas.Account = Depends(get_current_account),
                           db: Session = Depends(get_db)):
    if current_account.role_id == 0:
        db_orders = db.query(models.Order).all()
    else:
        if current_account.role_id == 1:
            db_orders = db.query(models.Order).filter(models.Order.student_id == current_account.user_id).all()
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
         


@app.post("/orders", 
          response_model=schemas.OrderResponse,
          tags=["Order"])
async def create_order(new_order: schemas.OrderInDB,
                       status_id: int, 
                       current_account: schemas.Account = Depends(get_current_account),
                       db: Session = Depends(get_db)):
    if not current_account.role_id == 1:
        raise  HTTPException(status_code=403, detail="Permission Not Found")
    
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
        total_price += db_optionlist[0].option_price 
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
    
@app.put("/orders/assign/{order_id}", 
         response_model=schemas.OrderResponse,
         tags=["Order"])
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
    
    
