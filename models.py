from enum import auto
from os import pathconf_names
from sqlalchemy.sql.sqltypes import DATETIME
from db import Base
from sqlalchemy import Boolean, LargeBinary, Column, ForeignKey, Float, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship


# Account Class
class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True)

    account = relationship("Account", back_populates="role")


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True,
                        index=True,  autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean)
    role_id = Column(Integer, ForeignKey("roles.role_id"))

    role = relationship("Role", back_populates="account")
    user = relationship("User", back_populates="account")


# User Class
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
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    lastTimeActive = Column(DateTime)

    gender = relationship("Gender", back_populates="user")
    job = relationship("Job", back_populates="user")
    account = relationship("Account", back_populates="user")
    avatar = relationship("Avatar", back_populates="user")
    teacher_status = relationship("TeacherStatus", back_populates="user")
    user_credit = relationship("UserCredit", back_populates="user")
    order_payment = relationship("OrderPayment", back_populates="user")

class Avatar(Base):
    __tablename__ = "avatars"

    avatar_id = Column(Integer, primary_key=True,
                       index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    img = Column(String)

    user = relationship("User", back_populates="avatar")

# Essay Class


class EssayLevel(Base):
    __tablename__ = "levels"

    level_id = Column(Integer, primary_key=True,
                      index=True, autoincrement=True)
    level_name = Column(String)

    type = relationship("EssayType", back_populates="level")


class EssayType(Base):
    __tablename__ = "types"

    type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level_id = Column(Integer, ForeignKey("levels.level_id"))
    type_name = Column(String)
    type_price = Column(Float)

    level = relationship("EssayLevel", back_populates="type")
    essay = relationship("Essay", back_populates="essay_type")


class Essay(Base):
    __tablename__ = "essays"

    essay_id = Column(Integer, primary_key=True,
                      index=True, autoincrement=True)
    title = Column(String)
    content = Column(String)
    type_id = Column(Integer, ForeignKey("types.type_id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    isPublic = Column(Boolean)

    order = relationship("Order", back_populates="essay")
    essay_comment = relationship("EssayComment", back_populates="essay")
    essay_info = relationship("EssayInfo", back_populates="essay")
    essay_type = relationship("EssayType", back_populates="essay")


class EssayComment(Base):
    __tablename__ = "essay_comments"

    comment_id = Column(Integer, primary_key=True,
                        index=True, autoincrement=True)
    essay_id = Column(Integer, ForeignKey("essays.essay_id"))
    sentence_index = Column(Integer)
    comment = Column(String)

    essay = relationship("Essay", back_populates="essay_comment")
# Order class


class Option(Base):
    __tablename__ = "options"

    option_id = Column(Integer, primary_key=True,
                       index=True, autoincrement=True)
    option_type = Column(Integer)
    option_name = Column(String)
    option_price = Column(Float)

    extra_result = relationship("ExtraResult", back_populates="option")


class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String)

    order = relationship("Order", back_populates="status")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True,
                      index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.user_id"))
    teacher_id = Column(Integer, ForeignKey("users.user_id"))
    status_id = Column(Integer, ForeignKey("status.status_id"))
    sent_date = Column(DateTime)
    updated_date = Column(DateTime)
    option_list = Column(String)
    updated_by = Column(Integer, ForeignKey("users.user_id"))
    essay_id = Column(Integer, ForeignKey("essays.essay_id"))
    total_price = Column(Float)
    option_list = Column(String)
    deadline = Column(DateTime)
    is_disabled = Column(Boolean)

    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
    status = relationship("Status", back_populates="order")
    essay = relationship("Essay", back_populates="order")
    rating = relationship("Rating", back_populates="order")
    order_image = relationship("OrderImage", back_populates="order")
    order_payment = relationship("OrderPayment", back_populates="order")


class OrderImage(Base):
    __tablename__ = "order_images"

    image_id = Column(Integer, primary_key=True,
                      index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    img = Column(String)

    order = relationship("Order", back_populates="order_image")


class Rating(Base):
    __tablename__ = "rating"

    rating_id = Column(Integer, primary_key=True,
                       index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    stars = Column(Integer)
    comment = Column(String)

    order = relationship("Order", back_populates="rating")


# Result class


class Result(Base):
    __tablename__ = "results"

    result_id = Column(Integer, primary_key=True,
                       index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    grade = Column(Float)
    grade_comment = Column(String)
    review = Column(String)
    comment = Column(String)
    isCriteria = Column(Boolean)
    isExtra = Column(Boolean)

    order = relationship("Order")
    result_criteria = relationship("ResultCriteria", back_populates="result")
    extra_result = relationship("ExtraResult", back_populates="result")


class Criteria(Base):
    __tablename__ = "criterias"

    criteria_id = Column(Integer, primary_key=True,
                         index=True, autoincrement=True)
    criteria_name = Column(String)

    result_criteria = relationship("ResultCriteria", back_populates="criteria")


class ResultCriteria(Base):
    __tablename__ = "result_criterias"

    resultcriteria_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey("results.result_id"))
    criteria_id = Column(Integer, ForeignKey("criterias.criteria_id"))
    criteria_comment = Column(String)
    criteria_score = Column(Float)

    result = relationship("Result", back_populates="result_criteria")
    criteria = relationship("Criteria", back_populates="result_criteria")


class ExtraResult(Base):
    __tablename__ = "extra_results"

    extraresult_id = Column(Integer, primary_key=True,
                            index=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey("results.result_id"))
    option_id = Column(Integer, ForeignKey("options.option_id"))
    content = Column(String)

    result = relationship("Result", back_populates="extra_result")
    option = relationship("Option", back_populates="extra_result")


# Class NLP


class EssayInfo(Base):
    __tablename__ = "essay_infos"

    info_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    essay_id = Column(Integer, ForeignKey("essays.essay_id"))
    keywords = Column(String)
    num_errors = Column(Integer)
    spelling_errors = Column(String)

    essay = relationship("Essay", back_populates="essay_info")

# class statistics


class TeacherStatus(Base):
    __tablename__ = "teacher_status"

    _id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    level_id = Column(Integer)
    active_essays = Column(Integer)
    
    user = relationship("User", back_populates="teacher_status")
    

# class Payment 

class UserCredit(Base):
    __tablename__ = "user_credits"
    
    _id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    provider = Column(String)
    account_no = Column(String, unique=True)
    expiry_date = Column(Date)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    user = relationship("User", back_populates="user_credit")
    
class OrderPayment(Base):
    __tablename__ = "order_payments"
    
    _id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    total_price = Column(Float)
    payment_type = Column(String)
    paid_by = Column(Integer, ForeignKey("users.user_id"))
    paid_status = Column(String)
    payment_message = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    order = relationship("Order", back_populates="order_payment")
    user = relationship("User", back_populates="order_payment")
    

class FakeBank(Base):
    __tablename__ = "fake_bank"
    _id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    balance = Column(Float)
    
    
class TeacherForm(Base):
    __tablename__ ="teacher_forms"
    _id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    gender_id = Column(Integer)
    email = Column(String, unique=True)
    address = Column(String)
    job_id = Column(Integer)
    phone_number = Column(String)
    date_of_birth = Column(Date)
    level_id = Column(Integer)
    avatar = Column(String)
    cover_letter = Column(String)
    isPassed = Column(Integer)
    submission_date = Column(DateTime)
    process_date = Column(DateTime)