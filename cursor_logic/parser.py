import json
import datetime
import os
import time
from openai import OpenAI

def get_ai_prompt(text: str) -> str:
    """
    Generates the prompt for the AI to parse the task.
    """
    # Get today's date to provide context to the AI for relative dates like "tomorrow"
    today = datetime.date.today().isoformat()

    prompt = f"""
    You are an intelligent task parser. Your job is to analyze free-text input and extract structured task information.

    Today's date is {today}.

    Analyze the following user input:
    "{text}"

    Extract the following information and return it as a valid JSON object with the specified keys.
    - "title": The main action of the task. Keep the title as complete as possible unless other fields are EXPLICITLY mentioned.
    - "due_date": The target completion date in YYYY-MM-DD format. If no date is mentioned, return null.
    - "priority": An integer from 1 (normal) to 4 (most urgent). If not mentioned, default to 1.
    - "project": The primary category for the task. If not mentioned, return null.
    - "section": A sub-category within the project. If not mentioned, return null.

    Example Input: "Review Q2 budget proposals by next Wednesday, high priority, for the 'Finance' team under 'Budgets'"
    Example Output:
    {{
      "title": "Review Q2 budget proposals for the 'Finance' team under 'Budgets'",
      "due_date": "YYYY-MM-DD", # Replace with the calculated date for next Wednesday
      "priority": 3,
      "project": "Finance",
      "section": "Budgets"
    }}

    Now, parse the user's text.
    """
    return prompt

def parse_task_with_openai_assistant(text: str):
    """
    Uses an OpenAI Assistant to parse the task string.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

    if not api_key or not assistant_id:
        print("Error: OPENAI_API_KEY or OPENAI_ASSISTANT_ID not set in .env file.")
        return None

    client = OpenAI(api_key=api_key)

    try:
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            assistant_message = messages.data[0].content[0].text.value
            
            if assistant_message.startswith("```json"):
                assistant_message = assistant_message.strip("```json\n").strip("```")

            return json.loads(assistant_message)
        else:
            print(f"OpenAI run failed with status: {run.status}")
            return None

    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return None

def parse_task_with_ai(text: str):
    """
    Parses a task string using an AI model and returns a structured dictionary.
    """
    return parse_task_with_openai_assistant(text) 