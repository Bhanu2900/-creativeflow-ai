import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
os.environ.setdefault("GROQ_API_KEY", "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")
os.environ.setdefault("GITHUB_TOKEN", "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")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_visual(prompt: str, mood: str, genre: str, knowledge: dict) -> dict:
    visual_info = knowledge['visual_style']
    art_style = visual_info.get('art_style', 'Digital Art')
    color_palette = visual_info.get('color_palette', ['Blue', 'Black', 'Silver'])
    lighting = visual_info.get('lighting', 'Dramatic')
    visual_references = visual_info.get('visual_references', ['Cinematic', 'Epic'])

    full_prompt = f"""You are a world-class visual art director and concept artist.
Based on this creative idea: {prompt}
Mood: {mood}
Genre: {genre}
Art Style: {art_style}
Color Palette: {', '.join(color_palette)}
Lighting: {lighting}
Visual References: {', '.join(visual_references)}

Create a detailed visual concept. Format EXACTLY as:

SCENE_TITLE: [title here]
SCENE_DESCRIPTION: [2-3 sentences describing the main scene]
COLOR_STORY: [describe the color mood and palette in 2 sentences]
KEY_VISUAL_ELEMENTS: [list 4 specific visual elements, one per line, starting with -]
IMAGE_PROMPT: [a detailed single paragraph prompt that could be used with an AI image generator]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    scene_title = ""
    scene_description = ""
    color_story = ""
    key_elements = []
    image_prompt = ""
    current_section = ""

    for line in raw.split('\n'):
        if line.startswith("SCENE_TITLE:"):
            scene_title = line.replace("SCENE_TITLE:", "").strip()
        elif line.startswith("SCENE_DESCRIPTION:"):
            scene_description = line.replace("SCENE_DESCRIPTION:", "").strip()
            current_section = "description"
        elif line.startswith("COLOR_STORY:"):
            color_story = line.replace("COLOR_STORY:", "").strip()
            current_section = "color"
        elif line.startswith("KEY_VISUAL_ELEMENTS:"):
            current_section = "elements"
        elif line.startswith("IMAGE_PROMPT:"):
            image_prompt = line.replace("IMAGE_PROMPT:", "").strip()
            current_section = "image"
        elif current_section == "elements" and line.strip().startswith("-"):
            key_elements.append(line.strip())
        elif current_section == "image" and line.strip():
            image_prompt += " " + line.strip()
        elif current_section == "description" and line.strip():
            scene_description += " " + line.strip()
        elif current_section == "color" and line.strip():
            color_story += " " + line.strip()

    return {
        "scene_title": scene_title,
        "scene_description": scene_description,
        "color_story": color_story,
        "key_elements": key_elements,
        "image_prompt": image_prompt,
        "art_style": art_style,
        "color_palette": color_palette,
        "lighting": lighting
    }


if __name__ == "__main__":
    knowledge = {
        "story_framework": "Hero's Journey",
        "music_mood": {
            "tempo": "Slow",
            "instruments": ["Synthesizer", "Piano", "Theremin"],
            "chord_progression": "Am - F - C - G"
        },
        "visual_style": {
            "art_style": "Digital Art",
            "color_palette": ["Deep Red", "Dark Blue", "Muted Gray"],
            "lighting": "Low Key",
            "visual_references": ["Interstellar", "Blade Runner"]
        },
        "creative_themes": ["Isolation", "Discovery", "Wonder"]
    }

    print("Step 1: Using hardcoded knowledge...")
    print("Step 2: Generating visual concept...")
    result = generate_visual(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi",
        knowledge=knowledge
    )
    print(f"\nScene Title: {result['scene_title']}")
    print(f"Description: {result['scene_description']}")
    print(f"Color Story: {result['color_story']}")
    print(f"\nKey Visual Elements:")
    for el in result['key_elements']:
        print(el)
    print(f"\nImage Prompt:\n{result['image_prompt']}")