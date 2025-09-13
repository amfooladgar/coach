# agents/reflector.py
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def reflect_on_day(journal_text: str) -> str:
    """
    Summarize reflections and extract insights from evening journal.
    """
    prompt = f"Summarize this daily reflection into insights and habits:\n{journal_text}"
    return llm.predict(prompt)
