import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_story(prompt: str, mood: str, genre: str, knowledge: dict) -> dict:
    """
    Generates a short story based on prompt, mood, genre,
    and knowledge retrieved from Foundry IQ.
    """

    full_prompt = f"""You are a master storyteller. 
Use the {knowledge['story_framework']} narrative structure.
Core themes to explore: {', '.join(knowledge['creative_themes'])}.
Write in a {mood.lower()} tone for the {genre.lower()} genre.

Write a short compelling story (300-400 words) based on:
Creative idea: {prompt}

Format your response EXACTLY as:
TITLE: [story title here]

[story text here]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    lines = raw.split('\n')
    title = lines[0].replace("TITLE:", "").strip()
    story = '\n'.join(lines[2:]).strip()

    return {
        "title": title,
        "story": story,
        "word_count": len(story.split()),
        "framework": knowledge['story_framework'],
        "themes": knowledge['creative_themes']
    }


if __name__ == "__main__":
    from foundry.iq_retriever import retrieve_creative_knowledge

    knowledge = retrieve_creative_knowledge(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi"
    )
    result = generate_story(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi",
        knowledge=knowledge
    )
    print(f"Title: {result['title']}")
    print(f"Word count: {result['word_count']}")
    print(f"\n{result['story']}")