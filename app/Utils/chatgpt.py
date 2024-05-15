from sqlalchemy.orm import Session
from database import SessionLocal
import app.Utils.database_handler as crud
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

openai_api_key = os.getenv('OPENAI_API_KEY')

standard_prompts = """
    Focus on:
    Introduction acknowledging our role as their contractor.
    Overview of project objectives and recent progress.
    Summary of milestones, deliverables, and key metrics.
    Notable challenges and solutions.
    Next steps and expected outcomes.
    Conclusion emphasizing our commitment and appreciation.
    When there are no new work orders or changes, focus on notable challenges, solutions, next steps, and appreciation.

    The report should be professional, engaging, and reflect our brand. Exclude individual employee references.
"""

# Function to retrieve API key and prompts from the database
def get_api_key_and_prompts(db: Session):
    variables = crud.get_variables(db)
    api_key = ''
    main_prompts = ''
    if variables:
        api_key = variables.openAIKey or openai_api_key
        main_prompts = variables.prompts or standard_prompts
    else:
        api_key = openai_api_key
        main_prompts = standard_prompts
    return api_key, main_prompts

# Function to get the last message using OpenAI
def get_last_message(db: Session, report_list, customer_name: str):
    api_key, main_prompts = get_api_key_and_prompts(db)
    print("chatgpt - main_prompts: ", api_key, main_prompts)
    client = OpenAI(api_key=api_key)
    # return
    if not report_list:
        return ""

    report_history = '\n'.join(report.message for report in report_list)  # 2 means message column

      
    print("chatgpt - main_prompts: ", main_prompts)
    
    instruction = f"""
        I need a 300 character work report for our customer, {customer_name}, summarizing the latest update in the project timeline.
        This is the historical report on the progress of this project.
        {report_history}
        -----------------------------
        {main_prompts}
    """
    
    response = client.chat.completions.create(
        model='gpt-4-0125-preview',
        max_tokens=2000,
        messages=[
            {'role': 'system', 'content': instruction},
            {'role': 'user', 'content': f"Please provide a personalized report less than 520 characters."}
        ],
        temperature=0.7
    )
    response_message = response.choices[0].message.content
    
    print("chatgpt - response_message: ", response_message)
    
    return response_message