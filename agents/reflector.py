# agents/reflector.py
import os
import json
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

def reflect_on_day(journal_text: str, config: dict = None) -> dict:
    """
    Summarize the reflection into structured JSON with optional mood/gratitude.
    Config may enable:
      - agents.reflector.mood_tracking (bool)
      - agents.reflector.gratitude_prompt (bool)

    Returns a dict with keys: summary, insights, actions, mood?, gratitude?
    """

    # Base schema
    schema = {
        "summary": "2-3 sentence summary",
        "insights": ["bullet insight 1", "bullet insight 2"],
        "actions": ["action 1 for tomorrow", "action 2 for tomorrow"]
    }

    # Extend schema depending on config
    if config:
        refl_cfg = config.get("agents", {}).get("reflector", {})
        if refl_cfg.get("mood_tracking", False):
            schema["mood"] = "integer 1-10 (self-rated mood for today)"
        if refl_cfg.get("gratitude_prompt", False):
            schema["gratitude"] = "one thing you feel grateful for today"

    prompt = f"""
    You are the Reflector. Analyze this journal entry and output ONLY valid JSON.
    Follow this schema exactly:

    {json.dumps(schema, indent=2)}

    Journal Entry:
    {journal_text}
    """

    result = llm.invoke(prompt)

    # LangChain returns an object with .content
    raw_text = getattr(result, "content", str(result)).strip()

    # Remove accidental code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[len("json"):].strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Reflector did not return valid JSON.\nGot:\n{raw_text}") from e

    # Normalize fields into strings (DB safe)
    reflection = {
        "summary": parsed.get("summary", "").strip(),
        "insights": "\n".join(parsed.get("insights", [])),
        "actions": "\n".join(parsed.get("actions", [])),
    }

    if "mood" in parsed:
        reflection["mood"] = str(parsed["mood"])
    if "gratitude" in parsed:
        reflection["gratitude"] = parsed["gratitude"].strip()

    return reflection
