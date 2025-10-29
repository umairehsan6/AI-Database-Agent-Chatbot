import os 
from pathlib import Path
from django.conf import settings 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

GEMINI_MODEL = "gemini-2.5-flash"
temperature = 0

def load_prompt():
    prompt_path = Path(settings.BASE_DIR) / 'agent' / 'prompt.txt'
    with open(prompt_path, 'r') as file:
        return file.read()
    
def process_command(user_input , api_key=None):
    try:
        if not api_key:
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "":
            return {'error': 'GEMINI_API_KEY is not set in environment variables or settings.'}
        llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=temperature, google_api_key=api_key)

        system_prompt = load_prompt()
        full_prompt = f"{system_prompt}\nUser Input: {user_input}\n\n JSON Response:"
        messages = [
            HumanMessage(content=full_prompt)
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return {'error': f'Error processing command: {str(e)}'}
    
def get_agent_response(user_input):
    return process_command(user_input)