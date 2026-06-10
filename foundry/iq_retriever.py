import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def retrieve_creative_knowledge(prompt: str, mood: str, genre: str) -> dict:
    """
    Microsoft Foundry IQ layer — retrieves grounded creative knowledge
    for story, music, and visual domains.
    """

    system_prompt = """You are a creative knowledge retriever (Microsoft Foundry IQ layer).
Given a creative prompt, mood, and genre, return structured creative knowledge.
You MUST respond with ONLY a valid JSON object, no extra text, no markdown, no backticks.
The JSON must have exactly these keys:
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
}"""

    user_message = f"""
Creative prompt: {prompt}
Mood: {mood}
Genre: {genre}

Return only the JSON object with creative knowledge for all three domains.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    knowledge = json.loads(clean)
    return knowledge


if __name__ == "__main__":
    result = retrieve_creative_knowledge(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi"
    )
    print(result)
    