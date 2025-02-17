from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.Model.DatabaseModel import Customer, Project, MessageHistory, Report, User, Variables, Status
from datetime import datetime
from app.Model.MainTable import MainTableModel
from sqlalchemy.orm import Session

# Utility Functions for Asynchronous Execution

# Main Table Retrieval
async def get_main_table(db: AsyncSession):
    stmt = (
        select(
            Customer.id,
            Customer.last_message,
            Customer.message_status,
            Customer.qued_timestamp,
            Customer.sent_timestamp,
            Customer.sent_success,
            Customer.image_url,
            Customer.phone_numbers,
            Customer.num_sent,
            Customer.created_at
        )
    )
    result = await db.execute(stmt)
    return result.all()

# Customer CRUD Operations
async def get_customer(db: AsyncSession, customer_id: int):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def find_customer_with_phone(db: AsyncSession, phone: str):
    phone = phone.replace(" ", "")
    stmt = select(Customer).filter(func.replace(Customer.phone, ' ', '') == phone)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def insert_customer(db: AsyncSession, item: MainTableModel):
    new_customer = Customer(
        last_message=item.last_message,
        message_status=item.message_status,
        qued_timestamp=item.qued_timestamp,
        sent_timestamp=item.sent_timestamp,
        sent_success=item.sent_success,
        image_url=item.image_url,
        phone_numbers=item.phone_numbers,
        num_sent=item.num_sent,
        created_at=item.created_at
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

async def update_customer(db: AsyncSession, customer_id: int, item: MainTableModel):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    existing_customer = result.scalar_one_or_none()
    
    if existing_customer:
        existing_customer.last_message = item.last_message
        existing_customer.message_status = item.message_status
        existing_customer.qued_timestamp = item.qued_timestamp
        existing_customer.sent_timestamp = item.sent_timestamp
        existing_customer.sent_success = item.sent_success
        existing_customer.image_url = item.image_url
        existing_customer.phone_numbers = item.phone_numbers
        existing_customer.num_sent = item.num_sent
        existing_customer.created_at = item.created_at
        await db.commit()
        return existing_customer
    return None

async def delete_customer(db: AsyncSession, customer_id: int):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer:
        await db.delete(customer)
        await db.commit()
        return True
    return False

async def restore_customer(db: AsyncSession, customer_id: int):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer:
        customer.is_deleted = 0
        await db.commit()
        return customer
    return None

async def update_sending_method(db: AsyncSession, customer_id: int, method: int):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer:
        customer.sending_method = method
        await db.commit()
        return customer
    return None

async def update_opt_in_status_email(db: AsyncSession, customer_id: int, opt_in_status_email: int):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer:
        customer.opt_in_status_email = opt_in_status_email
        await db.commit()
        return customer
    return None

async def update_opt_in_status_phone(db: AsyncSession, customer_id: int, opt_in_status_phone: int):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer:
        customer.opt_in_status_phone = opt_in_status_phone
        await db.commit()
        return customer
    return None

# Project CRUD Operations
async def get_project(db: AsyncSession, project_id: int):
    stmt = select(Project).filter(Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def insert_project(db: AsyncSession, claim_number: str, customer_id: int, project_name: str):
    stmt = select(Project).filter_by(claim_number=claim_number, customer_id=customer_id)
    result = await db.execute(stmt)
    existing_project = result.scalar_one_or_none()

    if existing_project is None:
        new_project = Project(
            claim_number=claim_number,
            customer_id=customer_id,
            project_name=project_name,
        )
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        return new_project
    return existing_project

async def update_project(db: AsyncSession, project_id: int, **kwargs):
    stmt = select(Project).filter(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project:
        for key, value in kwargs.items():
            setattr(project, key, value)
        await db.commit()
        return project
    return None

async def delete_project(db: AsyncSession, project_id: int):
    stmt = select(Project).filter(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project:
        await db.delete(project)
        await db.commit()
        return True
    return False

# MessageHistory CRUD Operations
async def get_message_history(db: AsyncSession, message_history_id: int):
    stmt = select(MessageHistory).filter(MessageHistory.id == message_history_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_message_history(db: AsyncSession):
    stmt = select(MessageHistory)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_message_history(db: AsyncSession, message: str, project_id: int):
    new_message_history = MessageHistory(message=message, project_id=project_id, sent_time=datetime.utcnow())
    db.add(new_message_history)
    await db.commit()
    await db.refresh(new_message_history)
    return new_message_history

async def update_message_history(db: AsyncSession, message_history_id: int, message: str):
    stmt = select(MessageHistory).filter(MessageHistory.id == message_history_id)
    result = await db.execute(stmt)
    message_history = result.scalar_one_or_none()

    if message_history:
        message_history.message = message
        await db.commit()
        return message_history
    return None

async def delete_message_history(db: AsyncSession, message_history_id: int):
    stmt = select(MessageHistory).filter(MessageHistory.id == message_history_id)
    result = await db.execute(stmt)
    message_history = result.scalar_one_or_none()

    if message_history:
        await db.delete(message_history)
        await db.commit()
        return True
    return False

# Report CRUD Operations
async def insert_report(db: AsyncSession, project_id: int, message: str = "", timestamp: str = ""):
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    stmt = select(Report).filter_by(project_id=project_id, message=message, timestamp=timestamp)
    result = await db.execute(stmt)
    existing_report = result.scalar_one_or_none()

    if existing_report is None:
        new_report = Report(project_id=project_id, message=message, timestamp=timestamp)
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        return new_report
    return existing_report

async def update_report(db: AsyncSession, report_id: int, message: str):
    stmt = select(Report).filter(Report.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if report:
        report.message = message
        await db.commit()
        return report
    return None

async def delete_report(db: AsyncSession, report_id: int):
    stmt = select(Report).filter(Report.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if report:
        await db.delete(report)
        await db.commit()
        return True
    return False

# User CRUD Operations
async def get_user(db: AsyncSession, user_id: int):
    stmt = select(User).filter(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).filter(User.username == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, username: str, password: str, forgot_password_token: str, approved: int):
    new_user = User(username=username, password=password, forgot_password_token=forgot_password_token, approved=approved)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user(db: AsyncSession, user_id: int, **kwargs):
    stmt = select(User).filter(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await db.commit()
        return user
    return None

async def delete_user(db: AsyncSession, user_id: int):
    stmt = select(User).filter(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False

# Variables CRUD Operations
async def get_variables(db: Session):
    stmt = select(Variables)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_variables(db: AsyncSession):
    new_variables = Variables(openAIKey="", twilioPhoneNumber="", twilioAccountSID="", twilioAuthToken="", sendgridEmail="", sendgridApiKey="", prompts="", timer=0)
    db.add(new_variables)
    await db.commit()
    await db.refresh(new_variables)
    return new_variables

async def update_variables(db: AsyncSession, variables_id: int, **kwargs):
    stmt = select(Variables).filter(Variables.id == variables_id)
    result = await db.execute(stmt)
    variables = result.scalar_one_or_none()

    if variables:
        for key, value in kwargs.items():
            setattr(variables, key, value)
        await db.commit()
        return variables
    return None

async def delete_variables(db: AsyncSession, variables_id: int):
    stmt = select(Variables).filter(Variables.id == variables_id)
    result = await db.execute(stmt)
    variables = result.scalar_one_or_none()

    if variables:
        await db.delete(variables)
        await db.commit()
        return True
    return False

async def set_project_message(db: AsyncSession, project_id: int, message: str):
    stmt = select(Project).filter(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project:
        project.last_message = message
        await db.commit()
        return project
    return None

async def insert_message_history(db: AsyncSession, message: str, project_id: int):
    new_message_history = MessageHistory(message=message, project_id=project_id, sent_time=datetime.utcnow())
    db.add(new_message_history)
    await db.commit()
    await db.refresh(new_message_history)
    return new_message_history

async def get_message_history_by_project_id_as_list(db: AsyncSession, project_id: int):
    stmt = select(MessageHistory).filter(MessageHistory.project_id == project_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_message_history_by_project_id(db: AsyncSession, project_id: int):
    stmt = select(MessageHistory).filter(MessageHistory.project_id == project_id)
    result = await db.execute(stmt)
    messages = result.scalars().all()

    formatted_messages = ''
    print("messages --: ", messages)
    for message in messages:
        formatted_messages += f"{message.sent_time}\n{message.message}\n---------------\n"
    return formatted_messages.rstrip('---------------\n')

async def get_message_history_by_history_id(db: AsyncSession, history_id: int):
    stmt = select(MessageHistory).filter(MessageHistory.id == history_id)
    result = await db.execute(stmt)
    messages = result.scalars().all()

    formatted_messages = ''
    print("messages --: ", messages)
    for message in messages:
        formatted_messages += f"{message.sent_time}\n{message.message}\n---------------\n"
    return formatted_messages.rstrip('---------------\n')

async def get_message_history_by_customer_id(db: AsyncSession, customer_id: int):
    stmt = select(Project).filter(Project.customer_id == customer_id)
    result = await db.execute(stmt)
    projects = result.scalars().all()

    formatted_messages = ''
    for project in projects:
        project_messages = await get_message_history_by_project_id(db, project.id)
        formatted_messages += project_messages
    return formatted_messages.rstrip('---------------\n')

async def set_project_status(db: AsyncSession, project_id: int, message_status: int, qued_timestamp):
    stmt = select(Project).filter(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project:
        project.message_status = message_status
        project.qued_timestamp = qued_timestamp
        await db.commit()
        return project
    return None

async def set_project_sent(db: AsyncSession, project_id: int, message_status: int, sent_timestamp):
    stmt = select(Project).filter(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project:
        project.message_status = message_status
        project.sent_timestamp = sent_timestamp
        await db.commit()
        return project
    return None

async def get_reports_by_project_id(db: AsyncSession, project_id: int):
    stmt = select(Report).filter(Report.project_id == project_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_all_projects(db: AsyncSession):
    stmt = select(Project)
    result = await db.execute(stmt)
    return result.scalars().all()

async def check_duplicate_message(db: AsyncSession, message: str):
    stmt = select(MessageHistory).filter(MessageHistory.message == message)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None

async def update_sent_status(db: AsyncSession, customer_id: int, sent_success: bool):
    stmt = select(Customer).filter(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer and sent_success:
        customer.num_sent += 1
        await db.commit()

async def set_db_update_status(db: AsyncSession, status_id: int, db_update_status: int):
    stmt = select(Status).filter(Status.id == status_id)
    result = await db.execute(stmt)
    status = result.scalar_one_or_none()

    if status:
        status.db_update_status = db_update_status
        await db.commit()
        return status
    return None

# Status CRUD Operations
async def get_status(db: AsyncSession):
    stmt = select(Status)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_status(db: AsyncSession, status_id, **kwargs):
    stmt = select(Status).filter(Status.id == status_id)
    result = await db.execute(stmt)
    status = result.scalar_one_or_none()

    if status:
        for key, value in kwargs.items():
            setattr(status, key, value)
        await db.commit()
        return status
    return None

async def update_rerun_status(db: AsyncSession, status_id, project_total, project_current):
    stmt = select(Status).filter(Status.id == status_id)
    result = await db.execute(stmt)
    status = result.scalar_one_or_none()

    if status:
        status.project_total = project_total
        status.project_current = project_current
        await db.commit()
        return status
    return None

async def create_status(db: AsyncSession):
    new_status = Status(db_update_status=0, buildertrend_total=0, buildertrend_current=0, xactanalysis_total=0, xactanalysis_current=0, project_total=0, project_current=0)
    db.add(new_status)
    await db.commit()
    await db.refresh(new_status)
    return new_status