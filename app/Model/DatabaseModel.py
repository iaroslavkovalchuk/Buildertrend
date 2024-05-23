from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'tbl_customer'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(255))
    address = Column(String(255))
    sending_method = Column(Integer)
    opt_in_status_email = Column(Integer)
    opt_in_status_phone = Column(Integer)

    projects = relationship('Project', backref='customer')

class Project(Base):
    __tablename__ = 'tbl_project'

    id = Column(Integer, primary_key=True)
    claim_number = Column(String(255))
    customer_id = Column(Integer, ForeignKey('tbl_customer.id'))
    project_name = Column(String(255))
    last_message = Column(String(255))
    message_status = Column(String(255))
    qued_timestamp = Column(DateTime)
    sent_timestamp = Column(DateTime)
    phone_sent_success = Column(Boolean)
    email_sent_success = Column(Boolean)

    message_history = relationship('MessageHistory', backref='project')

class MessageHistory(Base):
    __tablename__ = 'tbl_message_history'

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    project_id = Column(Integer, ForeignKey('tbl_project.id'))
    sent_time = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = 'tbl_report'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('tbl_project.id'))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = 'tbl_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    forgot_password_token = Column(String(255))

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
    db_update_status = Column(Integer)
