from openai import OpenAI
import os
from dotenv import load_dotenv
from app.Utils.database_handler import DatabaseHandler

load_dotenv()
db = DatabaseHandler()

api_key = os.getenv('OPENAI_API_KEY')

variables = db.get_variables()

if variables is not None:
    api_key = variables[1]

client = OpenAI(api_key=api_key)

# def get_last_message(report_list: list, customer_name: str):
def get_last_message(report_list, customer_name: str):
    if report_list == []:
        return ""
    report_history = ''
    for report in report_list:
        report_history += '\n' + report[2] # 2 means message column
    
    instruction = f"""
        I need a 300 character work report for our customer, {customer_name}, summarizing the latest update in the project timeline.
        This is the historical report on the progress of this project.
        {report_history}
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
    
    response = client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': f"""
                    Please provide personalized report less than 520 characters.
                """}
            ],
            temperature = 0.7
        )
    response_message = response.choices[0].message.content
    print(response_message)
    print("")
    return response_message