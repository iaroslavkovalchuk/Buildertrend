from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'tbl_customer'

    id = Column(Integer, primary_key=True)
    last_message = Column(Text)
    message_status = Column(Integer)
    qued_timestamp = Column(DateTime)
    sent_timestamp = Column(DateTime)
    sent_success = Column(Integer)
    image_url = Column(String(255))
    phone_numbers = Column(JSON)
    num_sent = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = 'tbl_project'

    id = Column(Integer, primary_key=True)
    claim_number = Column(String(255))
    customer_id = Column(Integer, ForeignKey('tbl_customer.id'))
    project_name = Column(String(255))
    last_message = Column(Text)
    message_status = Column(Integer)
    qued_timestamp = Column(DateTime)
    sent_timestamp = Column(DateTime)
    phone_sent_success = Column(Boolean)
    email_sent_success = Column(Boolean)

class MessageHistory(Base):
    __tablename__ = 'tbl_message_history'

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    project_id = Column(Integer)
    sent_time = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = 'tbl_report'    

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('tbl_project.id'))
    message = Column(Text)
    timestamp = Column(String(255))

class User(Base):
    __tablename__ = 'tbl_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    forgot_password_token = Column(String(255))
    approved = Column(Integer)

class Variables(Base):
    __tablename__ = 'tbl_variables'

    id = Column(Integer, primary_key=True)
    openAIKey = Column(String(255))
    twilioPhoneNumber = Column(String(255))
    twilioAccountSID = Column(String(255))
    twilioAuthToken = Column(String(255))
    sendgridEmail = Column(String(255))
    sendgridApiKey = Column(String(255))
    prompts = Column(Text)
    timer = Column(Integer)

class Status(Base):
    __tablename__ = 'tbl_status'

    id = Column(Integer, primary_key=True)
    db_update_status = Column(Integer)
    buildertrend_total = Column(Integer)
    buildertrend_current = Column(Integer)
    xactanalysis_total = Column(Integer)
    xactanalysis_current = Column(Integer)
    project_total = Column(Integer)
    project_current = Column(Integer)
