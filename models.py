from db import Base 
from sqlalchemy import Boolean, Column, ForeignKey, Float, Integer, String, Date, DateTime 
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "roles"
    
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique = True)
    
    account = relationship("Account", back_populates="role")

class Account(Base):
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True,  index=True,  autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    
    role = relationship("Role", back_populates="account")
    user = relationship("User", back_populates="account")


class Job(Base):
    __tablename__ = "jobs"
    
    job_id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, unique=True)
    
    user = relationship("User", back_populates="job")
    
class Gender(Base):
    __tablename__ = "genders"
    
    gender_id = Column(Integer, primary_key=True, index=True)
    gender_name = Column(String, unique=True)
    
    user = relationship("User", back_populates="gender")

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    name = Column(String)
    address = Column(String)
    gender_id = Column(Integer, ForeignKey("genders.gender_id"))
    phone_number = Column(String)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    date_of_birth = Column(Date)
    
    gender = relationship("Gender", back_populates="user")
    job = relationship("Job", back_populates="user")
    account = relationship("Account", back_populates="user")


    
class Essay(Base):
    __tablename__ = "essays"
    
    essay_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    content = Column(String)
    level_id = Column(Integer)
    type_id = Column(Integer)
    
    order = relationship("Order", back_populates="essay")
    
class Status(Base):
    __tablename__ = "status"
    
    status_id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String)
    
    order = relationship("Order", back_populates="status")
    
class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.user_id"))
    teacher_id = Column(Integer, ForeignKey("users.user_id"))
    status_id = Column(Integer, ForeignKey("status.status_id"))
    sent_date = Column(DateTime)
    updated_date = Column(DateTime)
    updated_by = Column(Integer, ForeignKey("users.user_id"))
    essay_id = Column(Integer, ForeignKey("essays.essay_id"))
    total_price = Column(Float, )
    
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
    status = relationship("Status", back_populates="order")
    essay = relationship("Essay", back_populates="order")

