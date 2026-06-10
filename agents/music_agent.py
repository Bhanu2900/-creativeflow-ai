import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
os.environ.setdefault("GROQ_API_KEY", "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")
os.environ.setdefault("GITHUB_TOKEN", "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")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_music(prompt: str, mood: str, genre: str, knowledge: dict) -> dict:
    music_info = knowledge['music_mood']
# Handle both flat and nested formats
    tempo = music_info.get('tempo', 'Moderate')
    instruments = music_info.get('instruments', ['Piano', 'Guitar'])
    chord_progression = music_info.get('chord_progression', 'Am - F - C - G')

    full_prompt = f"""You are a professional music composer and lyricist.
Based on this creative idea: {prompt}
Mood: {mood}
Genre: {genre}
Tempo: {tempo}
Instruments: {', '.join(instruments)}
Chord progression: {chord_progression}

Create a complete music direction. Format EXACTLY as:

SONG_TITLE: [title here]
GENRE_STYLE: [describe the music style in 1-2 sentences]
LYRICS:
[Verse 1]
[4 lines]
[Chorus]
[4 lines]
[Verse 2]
[4 lines]
PRODUCTION_NOTES: [2-3 sentences on how to produce this track]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    print("RAW RESPONSE:\n", raw)

    song_title = ""
    genre_style = ""
    production_notes = ""
    lyrics_lines = []
    current_section = ""

    for line in raw.split('\n'):
        if line.startswith("SONG_TITLE:"):
            song_title = line.replace("SONG_TITLE:", "").strip()
        elif line.startswith("GENRE_STYLE:"):
            genre_style = line.replace("GENRE_STYLE:", "").strip()
        elif line.startswith("LYRICS:"):
            current_section = "lyrics"
        elif line.startswith("PRODUCTION_NOTES:"):
            current_section = "production"
            production_notes = line.replace("PRODUCTION_NOTES:", "").strip()
        elif current_section == "lyrics":
            lyrics_lines.append(line)
        elif current_section == "production" and line.strip():
            production_notes += " " + line.strip()

    return {
        "song_title": song_title,
        "genre_style": genre_style,
        "lyrics": '\n'.join(lyrics_lines).strip(),
        "production_notes": production_notes,
        "tempo": tempo,
"instruments": instruments,
"chord_progression": chord_progression
    }


if __name__ == "__main__":
    from foundry.iq_retriever import retrieve_creative_knowledge

    print("Step 1: Getting knowledge...")
    knowledge = retrieve_creative_knowledge(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi"
    )
    print("Step 2: Generating music...")
    result = generate_music(
        prompt="A lonely astronaut finds music on Mars",
        mood="Mysterious",
        genre="Sci-fi",
        knowledge=knowledge
    )
    print(f"\nSong Title: {result['song_title']}")
    print(f"Style: {result['genre_style']}")
    print(f"Tempo: {result['tempo']}")
    print(f"Chords: {result['chord_progression']}")
    print(f"\nLyrics:\n{result['lyrics']}")
    print(f"\nProduction Notes: {result['production_notes']}")