import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')
def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment variables")
        return False
    print("API Key found:", api_key)
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=api_key)
        messages = [
            HumanMessage(content="What is the capital of France?")
        ]
        response = llm.invoke(messages)

        print("Response from Gemini:", response.content)
        return True
    except Exception as e:
        print("Error initializing ChatGoogleGenerativeAI:", str(e))
        return False

if __name__ == "__main__":
    test_gemini()