from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_last_message(report_list: list, customer_name: str):
    if report_list == []:
        return ""
    report_history = ''
    for report in report_list:
        report_history += '\n' + report[2] # 2 means message column
    
    instruction = f"""
        I need to create a personalized and comprehensive work report for our customer, {customer_name}.
        The important thing is that the length of this report shouldn't more than 400 characters.
        The report should be a synthesis of the historical reports we have on the progress of their project.
        Focus on the most recent data in the historical timeline here emphazie and focus on the most recent update in the historical timeline.
        {report_history}
        
        It should not reference individual employees but rather present the collective efforts of our team.

        Please include the following elements in a fluid and cohesive narrative:

        - A brief introduction that sets the context for the report and acknowledges the ongoing partnership with the customer.
        - An overview of the project's objectives and the progress made to date, drawing on the key points from the historical reports.
        - A summary of the results achieved, focusing on milestones, deliverables, and any quantifiable metrics that illustrate the project's advancement.
        - Any notable challenges that were encountered and the strategic approaches taken by our team to address them, ensuring continuous progress.
        - A forward-looking statement that outlines the next steps and expected outcomes, reinforcing our commitment to meeting the project's goals and the customer's expectations.
        - A conclusion that emphasizes the value we place on the customer's business and our dedication to delivering high-quality results.
        - Please craft the report to be professional, engaging, and reflective of our company's brand and values. The language should be clear, concise, and geared towards reinforcing the customer's confidence in our capabilities and services.
    """
    
    response = client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': f"""
                    Please provide personalized report less than 400 characters.
                """}
            ],
            seed=2425,
            temperature = 0.7
        )
    response_message = response.choices[0].message.content
    print(response_message)
    print("")
    return response_message