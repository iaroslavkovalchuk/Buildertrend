from sqlalchemy.orm import Session
from sqlalchemy import func

from app.Model.DatabaseModel import Customer, Project, MessageHistory, Report, User, Variables, Status
from datetime import datetime


def get_main_table(db: Session):
    return db.query(
        Customer.id.label('customer_id'),
        Customer.first_name,
        Customer.last_name,
        Project.id.label('project_id'),
        Project.claim_number,
        Project.project_name,
        Project.last_message,
        Project.message_status,
        Project.qued_timestamp,
        Project.sent_timestamp,
        Customer.sending_method,
        Customer.opt_in_status_email,
        Customer.opt_in_status_phone,
        Customer.email,
        Customer.phone,
        Project.phone_sent_success,
        Project.email_sent_success,
    ).outerjoin(Project, Customer.id == Project.customer_id).all()


# Customer CRUD Operations
def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def find_customer_with_phone(db: Session, phone: str):
    phone = phone.replace(" ", "")
    return db.query(Customer).filter(func.replace(Customer.phone, ' ', '') == phone).first()

def insert_customer(db: Session,  manager_name: str, manager_phone: str, manager_email: str, first_name: str, last_name: str, email: str, phone: str, address: str):
    # Check if customer already exists
    existing_customer = db.query(Customer).filter(
        func.lower(Customer.first_name) == func.lower(first_name),
        func.lower(Customer.last_name) == func.lower(last_name)
    ).first()
    
    existing_customer_1 = db.query(Customer).filter(
        func.lower(Customer.first_name) == func.lower(last_name),
        func.lower(Customer.last_name) == func.lower(first_name)
    ).first()

    if existing_customer:
        # If customer exists, update their information and return their ID
        existing_customer.email = email
        existing_customer.phone = phone
        existing_customer.address = address
        existing_customer.manager_name = manager_name
        existing_customer.manager_phone = manager_phone
        existing_customer.manager_email = manager_email
        
        db.add(existing_customer)
        db.commit()
        db.refresh(existing_customer)
        return existing_customer
    elif existing_customer_1:
        # If customer exists, update their information and return their ID
        existing_customer_1.email = email
        existing_customer_1.phone = phone
        existing_customer_1.address = address
        existing_customer.manager_name = manager_name
        existing_customer.manager_phone = manager_phone
        existing_customer.manager_email = manager_email
        db.add(existing_customer_1)
        db.commit()
        db.refresh(existing_customer_1)
        return existing_customer_1
    else:
        # If customer does not exist, insert them and return their ID
        new_customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            sending_method=1,  # Assuming default sending method is 1
            opt_in_status_email=0,
            opt_in_status_phone=0
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)  # Refresh to get the new ID
        return new_customer

def update_customer(db: Session, customer_id: int, first_name: str, last_name: str, email: str, phone: str, address: str):
    db.query(Customer).filter(Customer.id == customer_id).update({
        Customer.first_name: first_name,
        Customer.last_name: last_name,
        Customer.email: email,
        Customer.phone: phone,
        Customer.address: address
    })
    db.commit()

def delete_customer(db: Session, customer_id: int):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    db.delete(customer)
    db.commit()
    
def update_sending_method(db: Session, customer_id: int, method: int):
    customer = db.query(Customer).filter(Customer.id == customer_id).one_or_none()
    if customer:
        customer.sending_method = method
        db.commit()

def update_opt_in_status_email(db: Session, customer_id: int, opt_in_status_email: int):
    db.query(Customer).filter(Customer.id == customer_id).update({
        Customer.opt_in_status_email: opt_in_status_email
    })
    db.commit()
    
def update_opt_in_status_phone(db: Session, customer_id: int, opt_in_status_phone: int):
    db.query(Customer).filter(Customer.id == customer_id).update({
        Customer.opt_in_status_phone: opt_in_status_phone
    })
    db.commit()


# Project CRUD Operations
def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def insert_project(db: Session, claim_number: str, customer_id: int, project_name: str):
    # Check if project already exists
    existing_project = db.query(Project).filter_by(
        claim_number=claim_number,
        customer_id=customer_id,
    ).first()

    if existing_project is None:
        # If project does not exist, insert it
        new_project = Project(
            claim_number=claim_number,
            customer_id=customer_id,
            project_name=project_name
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)  # Refresh to get the new ID
        return new_project
    else:
        # If project exists, return its ID
        return existing_project

def update_project(db: Session, project_id: int, **kwargs):
    db.query(Project).filter(Project.id == project_id).update(kwargs)
    db.commit()

def delete_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    db.delete(project)
    db.commit()

# MessageHistory CRUD Operations
def get_message_history(db: Session, message_history_id: int):
    return db.query(MessageHistory).filter(MessageHistory.id == message_history_id).first()

def create_message_history(db: Session, message: str, project_id: int):
    new_message_history = MessageHistory(message=message, project_id=project_id)
    db.add(new_message_history)
    db.commit()
    db.refresh(new_message_history)
    return new_message_history

def update_message_history(db: Session, message_history_id: int, message: str):
    db.query(MessageHistory).filter(MessageHistory.id == message_history_id).update({MessageHistory.message: message})
    db.commit()

def delete_message_history(db: Session, message_history_id: int):
    message_history = db.query(MessageHistory).filter(MessageHistory.id == message_history_id).first()
    db.delete(message_history)
    db.commit()

# Report CRUD Operations

def insert_report(db: Session, project_id: int, message: str = "", timestamp: str = ""):
    # If no timestamp is provided, use the current UTC time
    if timestamp is None:
        timestamp = ""

    # Check if a report with the same project_id, message, and timestamp already exists
    existing_report = db.query(Report).filter_by(project_id=project_id, message=message, timestamp=timestamp).first()

    if existing_report is None:
        # If it does not exist, create a new Report instance
        new_report = Report(project_id=project_id, message=message, timestamp=timestamp)
        db.add(new_report)
        db.commit()
        db.refresh(new_report)  # Refresh to get the new ID if needed
        return new_report
    else:
        # If a report already exists, return its ID
        print('||||||||||||||||||||||')
        return existing_report
    
def update_report(db: Session, report_id: int, message: str):
    db.query(Report).filter(Report.id == report_id).update({Report.message: message})
    db.commit()

def delete_report(db: Session, report_id: int):
    report = db.query(Report).filter(Report.id == report_id).first()
    db.delete(report)
    db.commit()

# User CRUD Operations
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.username == email).first()

def create_user(db: Session, username: str, password: str, forgot_password_token: str):
    new_user = User(username=username, password=password, forgot_password_token=forgot_password_token)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, **kwargs):
    db.query(User).filter(User.id == user_id).update(kwargs)
    db.commit()

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()

# Variables CRUD Operations
def get_variables(db: Session):
    return db.query(Variables).first()

def create_variables(db: Session):
    new_variables = Variables(openAIKey="", twilioPhoneNumber="", twilioAccountSID="", twilioAuthToken="", sendgridEmail="", sendgridApiKey="", prompts="", timer=0)
    db.add(new_variables)
    db.commit()
    db.refresh(new_variables)
    return new_variables    


def update_variables(db: Session, variables_id: int, **kwargs):
    db.query(Variables).filter(Variables.id == variables_id).update(kwargs)
    db.commit()

def delete_variables(db: Session, variables_id: int):
    variables = db.query(Variables).filter(Variables.id == variables_id).first()
    db.delete(variables)
    db.commit()

def set_project_message(db: Session, project_id: int, message: str):
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project:
        project.last_message = message
        db.commit()

def insert_message_history(db: Session, message: str, project_id: int):
    new_message_history = MessageHistory(message=message, project_id=project_id, sent_time=datetime.utcnow())
    db.add(new_message_history)
    db.commit()
    db.refresh(new_message_history)  # Refresh to get the new ID if needed
    return new_message_history


def get_message_history_by_project_id_as_list(db: Session, project_id: int):
    results = db.query(MessageHistory).filter(MessageHistory.project_id == project_id).all()
    # Convert the instances to dictionaries, excluding any non-column attributes like '_sa_instance_state'
    return results

def get_message_history_by_project_id(db: Session, project_id: int):
    messages = db.query(MessageHistory).filter(MessageHistory.project_id == project_id).all()
    result = ''
    for message in messages:
        result += f"{message.sent_time}\n{message.message}\n---------------\n"
    return result.rstrip('---------------\n')

def get_message_history_by_customer_id(db: Session, customer_id):
    projects = db.query(Project).filter(Project.customer_id == customer_id).all()
    # print("projects--------------: ", projects)
    
    result = ''
    for project in projects:
        print(project.id)
        result += get_message_history_by_project_id(db, project.id)
    print(result)
    return result.rstrip('---------------\n')

def set_project_status(db: Session, project_id: int, message_status: int, qued_timestamp):
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project:
        project.message_status = message_status
        project.qued_timestamp = qued_timestamp
        db.commit()

def set_project_sent(db: Session, project_id: int, message_status: int, sent_timestamp):
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project:
        project.message_status = message_status
        project.sent_timestamp = sent_timestamp
        db.commit()

    

def get_reports_by_project_id(db: Session, project_id: int):
    return db.query(Report).filter(Report.project_id == project_id).all()


def get_all_projects(db: Session):
    return db.query(Project).all()


def check_duplicate_message(db: Session, message: str):
    return db.query(MessageHistory).filter(MessageHistory.message == message).first() is not None

def update_project_sent_status(db: Session, project_id: int, phone_sent_success: bool, email_sent_success: bool):
    db.query(Project).filter(Project.id == project_id).update({
        Project.phone_sent_success: phone_sent_success,
        Project.email_sent_success: email_sent_success
    })
    db.commit()

def set_db_update_status(db: Session, status_id: int, db_update_status: int):
    db.query(Status).filter(Status.id == status_id).update({
        Status.db_update_status : db_update_status
    })
    db.commit()
    
# Status CRUD Operations
def get_status(db: Session):
    return db.query(Status).first()

def update_status(db: Session, status_id, **kwargs):
    db.query(Status).filter(Status.id == status_id).update(kwargs)
    db.commit()
    
def update_rerun_status(db: Session, status_id, project_total, project_current):
    db.query(Status).filter(Status.id == status_id).update({
        Status.project_total: project_total,
        Status.project_current: project_current
    })
    db.commit()
    

def create_status(db: Session):
    new_status = Status(db_update_status=0, buildertrend_total=0, buildertrend_current=0, xactanalysis_total=0, xactanalysis_current=0, project_total=0, project_current=0)
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return new_status    

