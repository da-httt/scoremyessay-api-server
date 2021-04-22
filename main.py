from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from schemas import Account, AccountInDB, Order, OrderCreate, AccountLogin, Token, TokenData, User, SignUp, Job, Gender, UserAccount
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
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    account = get_account(db, email=token_data.email)
    if account is None:
        raise credentials_exception
    
    print("see role: " + account.role.role_name)
    schema_account = Account(
        account_id=account.account_id,
        email=account.email,
        role_id=account.role_id,
        disabled=account.disabled)
    return schema_account 

async def create_account(db: Session, new_account: SignUp):
    
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
async def get_current_active_account(account: Account = Depends(get_current_account)):
    print("Getting info..")
    if account.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    print(account)
    return account

@app.post("/token", response_model=Token, tags=['Authentication'])
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

@app.post("/login", response_model=Token, tags=['Authentication'])
async def login_for_access_token(account_login: AccountLogin, db: Session = Depends(get_db)):
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

@app.post("/signup", response_model=Account, tags=['Authentication'])
async def signup_for_new_account(new_account: SignUp,
                                db: Session = Depends(get_db)):
    
    if get_account(db, new_account.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_account, _ = await create_account(db, new_account)
    return Account(account_id=db_account.account_id,
                   email = db_account.email,
                   disabled = db_account.disabled,
                   role_id=db_account.role_id)
    



@app.get("/accounts/me", response_model=Account, tags=['Authentication'])
async def read_account_me(current_account: Account = Depends(get_current_active_account)):
    return current_account


@app.get("/jobs", response_model= List[Job], tags=['Authentication'])
async def read_job_list(db: Session=Depends(get_db)):
    db_job_list = db.query(models.Job).all()
    job_list = []
    for db_job in db_job_list:
        job_list.append(Job(job_id=db_job.job_id, job_name=db_job.job_name))
    
    return job_list

@app.get("/genders", response_model= List[Gender], tags=['Authentication'])
async def read_gender_list(db: Session=Depends(get_db)):
    db_gender_list = db.query(models.Gender).all()
    gender_list = []
    for db_gender in db_gender_list:
        gender_list.append(Gender(gender_id=db_gender.gender_id, gender_name=db_gender.gender_name))
    
    return gender_list


# User route 

@app.get("/users/me", 
         response_model=User, 
         description = "Get the user information of current account",
         tags = ["User"])
async def read_user_information(current_account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.account_id == current_account.account_id).first()
    return User(
        email = current_account.email,
        name =  db_user.name,
        date_of_birth =  db_user.date_of_birth,
        address = db_user.address,
        gender = db_user.gender_id,
        job = db_user.job_id,
        phone_number = db_user.phone_number 
    )
    
@app.get("/users",
         response_model = List[UserAccount],
         description = "Get the all user information in database",
         tags = ["User"])
async def read_all_users(current_account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    if current_account.role_id != 3:
        raise HTTPException(status_code=403, detail="Only Admin can access this api")
    
    db_user_list = db.query(models.User).all()
    user_list = []
    for db_user in db_user_list:
        user_list.append(UserAccount(
            user_id = db_user.user_id,
            account_id = db_user.account.account_id,
            role_id = db_user.account.role_id,
            email = db_user.account.email,
            name =  db_user.name,
            date_of_birth =  db_user.date_of_birth,
            address = db_user.address,
            gender_id = db_user.gender_id,
            job_id = db_user.job_id,
            phone_number = db_user.phone_number,
            disabled = db_user.account.disabled
            
        ))
    return user_list
        

@app.put("/users/{user_id}", tags=["User"])
async def update_user():
    pass 

@app.delete("/users/{user_id}", tags=["User"])
async def delete_user():
    pass 


#Order 

@app.get("/orders", tags = ["Order"])
async def get_all_orders():
    pass

@app.get("/orders/students/{user_id}",
         response_model=List[Order],
        tags = ["Order"])
async def get_all_orders_by_studentid(user_id:int, current_account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    db_order_list = db.query(models.Order).filter(models.Order.student_id == user_id)
    order_list = []
    for db_order in db_order_list:
        order_list.append(Order(
            **db_order.__dict__
        ))
    return order_list 

@app.get("/orders/teachers/{user_id}",
         response_model=List[Order],
        tags = ["Order"])
async def get_all_orders_by_teacherid(user_id:int, current_account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    db_order_list = db.query(models.Order).filter(models.Order.teacher_id == user_id)
    order_list = []
    for db_order in db_order_list:
        order_list.append(Order(
            **db_order.__dict__
        ))
    return order_list 
    

@app.get("/orders/{order_id}", tags=["Order"])
async def get_order_by_id():
    pass 

"""@app.post("/orders", tags = ["Order"])
async def create_order(new_order: OrderCreate, current_account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    if current_account.role_id == 2:
        raise HTTPException(status_code=403)
    order = create_new_order(db, new_order)
"""
@app.put("/orders/{order_id}", tags=["Order"])
async def update_order():
    pass 

@app.delete("/orders/{order_id}", tags=["Order"])
async def delete_order():
    pass 

