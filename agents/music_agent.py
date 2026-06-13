import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from utils.llm_provider import generate_completion

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__),
        '..',
        '.env'
    )
)

MUSIC_STYLE_GUIDES = {
    "Rock": {
        "structure": "Verse / Chorus / Verse / Chorus / Bridge / Chorus",
        "traits": "Power chords, anthemic chorus, electric guitar riffs, driving drums, rebellious tone",
        "instruments": ["Electric Guitar", "Bass Guitar", "Drums", "Vocals"]
    },
    "Jazz": {
        "structure": "Intro / A section / B section / Improvisation / Outro",
        "traits": "Syncopated rhythms, blue notes, swing feel, scat-style phrasing, sophisticated chord substitutions",
        "instruments": ["Saxophone", "Double Bass", "Piano", "Brushed Drums"]
    },
    "Hip-hop": {
        "structure": "Intro / Verse 1 (16 bars) / Hook / Verse 2 (16 bars) / Hook / Outro",
        "traits": "Bar counting, internal rhyme schemes, flow variations, punch lines, beat drops, storytelling",
        "instruments": ["808 Bass", "Sampler", "Hi-hats", "Trap Drums"]
    },
    "Pop": {
        "structure": "Verse / Pre-Chorus / Chorus / Verse / Pre-Chorus / Chorus / Bridge / Chorus",
        "traits": "Catchy hook, simple relatable lyrics, repetitive chorus, upbeat energy, radio-friendly",
        "instruments": ["Synthesizer", "Electric Piano", "Bass", "Programmed Drums"]
    },
    "Classical": {
        "structure": "Exposition / Development / Recapitulation / Coda",
        "traits": "Operatic phrasing, Latin or poetic language, dramatic dynamics, orchestral imagery, themes and variations",
        "instruments": ["String Orchestra", "Piano", "Choir", "Woodwinds"]
    },
    "Electronic": {
        "structure": "Intro / Build-up / Drop / Break / Build-up / Drop / Outro",
        "traits": "Minimal repetitive lyrics, hypnotic phrases, build tension and release, synth textures, drop moment",
        "instruments": ["Synthesizer", "808", "Arpeggiator", "Vocoder"]
    },
    "R&B": {
        "structure": "Verse / Pre-Chorus / Chorus / Verse / Chorus / Bridge / Outro",
        "traits": "Melismatic vocal runs, smooth soulful groove, emotional vulnerability, rich harmonies, sensual tone",
        "instruments": ["Rhodes Piano", "Bass Guitar", "Soul Drums", "Backing Vocals"]
    },
    "Folk": {
        "structure": "Verse / Chorus / Verse / Chorus / Bridge / Final Verse",
        "traits": "Storytelling verses, poetic imagery, acoustic warmth, simple honest emotions, narrative arc",
        "instruments": ["Acoustic Guitar", "Banjo", "Harmonica", "Upright Bass"]
    },
    "Metal": {
        "structure": "Intro Riff / Verse / Chorus / Verse / Chorus / Solo / Breakdown / Chorus",
        "traits": "Heavy breakdowns, aggressive imagery, double bass drumming, power and intensity, dark themes",
        "instruments": ["Distorted Guitar", "7-string Bass", "Double Bass Drums", "Screaming Vocals"]
    },
    "Blues": {
        "structure": "12-bar Blues x3 / Bridge / 12-bar Blues",
        "traits": "Call and response, bent notes, suffering and resilience themes, raw emotion, repetition with variation",
        "instruments": ["Blues Guitar", "Harmonica", "Upright Bass", "Snare Drums"]
    },
    "Reggae": {
        "structure": "Intro / Verse / Chorus / Verse / Chorus / Dub Break / Chorus",
        "traits": "Offbeat rhythms, social consciousness, repetitive hooks, laid-back groove, uplifting message",
        "instruments": ["Rhythm Guitar", "Bass", "Organ", "Reggae Drums"]
    },
    "Country": {
        "structure": "Verse / Chorus / Verse / Chorus / Bridge / Chorus",
        "traits": "Storytelling, heartfelt emotion, rural imagery, twang, relatable everyday themes",
        "instruments": ["Acoustic Guitar", "Steel Guitar", "Fiddle", "Country Drums"]
    },
}


def generate_music(
    prompt: str,
    mood: str,
    genre: str,
    knowledge: dict,
    music_style: str = "Pop"
) -> dict:

    style_guide = MUSIC_STYLE_GUIDES.get(
        music_style,
        MUSIC_STYLE_GUIDES["Pop"]
    )

    tempo = knowledge["music_mood"].get(
        "tempo",
        "Moderate"
    )

    instruments = knowledge["music_mood"].get(
        "instruments",
        style_guide["instruments"]
    )

    chord_progression = knowledge["music_mood"].get(
        "chord_progression",
        "Am - F - C - G"
    )

    full_prompt = f"""
You are a world-class {music_style} songwriter and music producer.

Creative idea: {prompt}
Story mood: {mood}
Story genre: {genre}
Music style: {music_style}

Music style characteristics:
- Structure: {style_guide['structure']}
- Style traits: {style_guide['traits']}
- Key instruments: {', '.join(style_guide['instruments'])}
- Tempo feel: {tempo}
- Chord progression: {chord_progression}
- Creative themes: {', '.join(knowledge.get('creative_themes', ['Discovery', 'Wonder']))}

Write a complete {music_style} song.

Format EXACTLY as:

SONG_TITLE: [title here]

GENRE_STYLE: [describe this specific style in 1-2 sentences]

LYRICS:
{style_guide['structure'].replace(' / ', chr(10))}

[Write actual lyrics]

PRODUCTION_NOTES:
[2-3 sentences of production advice]
"""

    response = generate_completion(
        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        max_tokens=1000
    )

    raw = response["content"].strip()

    song_title = ""
    genre_style = ""
    production_notes = ""
    lyrics_lines = []
    current_section = ""

    for line in raw.split("\n"):

        if line.startswith("SONG_TITLE:"):
            song_title = line.replace(
                "SONG_TITLE:",
                ""
            ).strip()

        elif line.startswith("GENRE_STYLE:"):
            genre_style = line.replace(
                "GENRE_STYLE:",
                ""
            ).strip()
            current_section = "style"

        elif line.startswith("LYRICS:"):
            current_section = "lyrics"

        elif line.startswith("PRODUCTION_NOTES:"):
            current_section = "production"
            production_notes = line.replace(
                "PRODUCTION_NOTES:",
                ""
            ).strip()

        elif current_section == "lyrics":
            lyrics_lines.append(line)

        elif current_section == "production" and line.strip():
            production_notes += " " + line.strip()

        elif current_section == "style" and line.strip():
            genre_style += " " + line.strip()

    return {
        "song_title": song_title,
        "genre_style": genre_style,
        "lyrics": "\n".join(lyrics_lines).strip(),
        "production_notes": production_notes,
        "tempo": tempo,
        "instruments": style_guide["instruments"],
        "chord_progression": chord_progression,
        "music_style": music_style,
        "structure": style_guide["structure"],
        "provider": response["provider"]
    }


if __name__ == "__main__":

    knowledge = {
        "story_framework": "Hero's Journey",
        "music_mood": {
            "tempo": "Slow",
            "instruments": ["Guitar"],
            "chord_progression": "Am - F - C - G"
        },
        "visual_style": {
            "art_style": "Digital Art",
            "color_palette": ["Blue"],
            "lighting": "Low Key",
            "visual_references": ["Cinematic"]
        },
        "creative_themes": [
            "Isolation",
            "Discovery",
            "Wonder"
        ]
    }

    result = generate_music(
        "A lonely astronaut finds music on Mars",
        "Mysterious",
        "Sci-fi",
        knowledge,
        "Rock"
    )

    print(f"Provider: {result['provider']}")
    print(f"Song: {result['song_title']}")
    print(result["lyrics"][:300])