import os
import sys
import json

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        '..'
    )
)

from dotenv import load_dotenv
from utils.llm_provider import generate_completion

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__),
        '..',
        '.env'
    )
)


def retrieve_creative_knowledge(
    prompt: str,
    mood: str,
    genre: str
) -> dict:
    """
    Creative Knowledge Engine

    Generates structured creative guidance
    for story, music and visual agents.
    """

    system_prompt = """
You are a Creative Knowledge Engine.

Given a creative prompt, mood and genre,
return structured creative guidance.

You MUST respond with ONLY a valid JSON object.

NO markdown.
NO explanations.
NO backticks.

The JSON must have EXACTLY this structure:

{
  "story_framework": "string",
  "music_mood": {
    "tempo": "string",
    "instruments": ["string", "string", "string"],
    "chord_progression": "string"
  },
  "visual_style": {
    "art_style": "string",
    "color_palette": ["string", "string", "string"],
    "lighting": "string",
    "visual_references": ["string", "string"]
  },
  "creative_themes": ["string", "string", "string"]
}
"""

    user_message = f"""
Creative Prompt:
{prompt}

Mood:
{mood}

Genre:
{genre}

Return ONLY the JSON object.
"""

    response = generate_completion(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.7,
        max_tokens=800
    )

    raw = response["content"].strip()

    clean = (
        raw
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        knowledge = json.loads(clean)

    except Exception as e:

        print("JSON Parse Error")
        print(clean)

        raise Exception(
            f"Creative Knowledge Engine failed: {e}"
        )

    knowledge["provider"] = response["provider"]

    return knowledge


if __name__ == "__main__":

    result = retrieve_creative_knowledge(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi"
    )

    print(
        f"Provider: {result['provider']}"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )