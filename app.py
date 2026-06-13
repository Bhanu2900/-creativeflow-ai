import os
import sys
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Load keys from Streamlit secrets (deployment) or .env (local)
# Load keys safely
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except Exception:
    load_dotenv()
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN

from foundry.iq_retriever import retrieve_creative_knowledge
from agents.story_agent import generate_story
from agents.music_agent import generate_music
from agents.visual_agent import generate_visual
from utils.exporter import export_to_docx

st.set_page_config(
    page_title="CreativeFlow AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme Map ─────────────────────────────────────────────────
THEMES = {
    ("Epic", "Sci-fi"):        {"bg":"#0d0d2b","card":"#13134a","accent":"#4f46e5","text":"#c7d2fe","sub":"#6366f1","name":"Cosmic Indigo","emoji":"🚀","pinterest":"epic+sci-fi+space+concept+art+indigo+futuristic"},
    ("Mysterious", "Sci-fi"):  {"bg":"#0a0f1e","card":"#0f172a","accent":"#38bdf8","text":"#bae6fd","sub":"#0ea5e9","name":"Deep Space","emoji":"🌌","pinterest":"mysterious+sci-fi+dark+space+blue+concept+art"},
    ("Epic", "Fantasy"):       {"bg":"#1a0f00","card":"#2d1a00","accent":"#f59e0b","text":"#fde68a","sub":"#d97706","name":"Golden Kingdom","emoji":"⚔️","pinterest":"epic+fantasy+golden+kingdom+concept+art+warrior"},
    ("Mysterious", "Fantasy"): {"bg":"#071a10","card":"#0d2b1a","accent":"#10b981","text":"#a7f3d0","sub":"#059669","name":"Enchanted Forest","emoji":"🌿","pinterest":"mysterious+fantasy+enchanted+forest+green+magic"},
    ("Dark", "Thriller"):      {"bg":"#0a0a0a","card":"#141414","accent":"#dc2626","text":"#fca5a5","sub":"#ef4444","name":"Noir Shadow","emoji":"🔪","pinterest":"noir+thriller+dark+shadow+red+cinematic+art"},
    ("Romantic", "Romance"):   {"bg":"#1a0a12","card":"#2d1020","accent":"#ec4899","text":"#fbcfe8","sub":"#db2777","name":"Rose Velvet","emoji":"🌹","pinterest":"romantic+rose+velvet+pink+aesthetic+dreamy+art"},
    ("Calm", "Historical"):    {"bg":"#1a1508","card":"#2a2010","accent":"#b45309","text":"#fde68a","sub":"#d97706","name":"Aged Parchment","emoji":"📜","pinterest":"historical+parchment+vintage+sepia+calm+aesthetic"},
    ("Playful", "Fantasy"):    {"bg":"#0f0a1e","card":"#1a1030","accent":"#a855f7","text":"#e9d5ff","sub":"#9333ea","name":"Rainbow Realm","emoji":"🦄","pinterest":"playful+fantasy+colorful+magical+whimsical+art"},
    ("Dark", "Horror"):        {"bg":"#0f0000","card":"#1a0000","accent":"#b91c1c","text":"#fecaca","sub":"#dc2626","name":"Blood Moon","emoji":"🩸","pinterest":"horror+dark+blood+moon+gothic+atmospheric+art"},
    ("Calm", "Sci-fi"):        {"bg":"#080f1a","card":"#0f1829","accent":"#06b6d4","text":"#a5f3fc","sub":"#0891b2","name":"Soft Nebula","emoji":"🌠","pinterest":"calm+sci-fi+nebula+soft+cyan+space+aesthetic"},
    ("Epic", "Historical"):    {"bg":"#120a00","card":"#1e1000","accent":"#92400e","text":"#fcd34d","sub":"#b45309","name":"Bronze Age","emoji":"🏛️","pinterest":"epic+historical+bronze+ancient+civilization+art"},
    ("Romantic", "Fantasy"):   {"bg":"#120818","card":"#1e0d28","accent":"#c026d3","text":"#f0abfc","sub":"#a21caf","name":"Twilight Bloom","emoji":"🌸","pinterest":"romantic+fantasy+twilight+purple+bloom+dreamy"},
    ("Playful", "Romance"):    {"bg":"#0f0a10","card":"#1e1025","accent":"#f472b6","text":"#fce7f3","sub":"#ec4899","name":"Cotton Candy","emoji":"🍭","pinterest":"playful+romantic+pastel+cotton+candy+cute+art"},
    ("Calm", "Romance"):       {"bg":"#100a12","card":"#1a1020","accent":"#e879f9","text":"#fae8ff","sub":"#d946ef","name":"Lavender Dusk","emoji":"💜","pinterest":"calm+romantic+lavender+dusk+soft+purple+aesthetic"},
    ("Dark", "Fantasy"):       {"bg":"#08080f","card":"#10101a","accent":"#7c3aed","text":"#ddd6fe","sub":"#6d28d9","name":"Shadow Realm","emoji":"🌑","pinterest":"dark+fantasy+shadow+realm+purple+gothic+concept"},
    ("Mysterious", "Thriller"):{"bg":"#0a0a10","card":"#141420","accent":"#6366f1","text":"#e0e7ff","sub":"#4f46e5","name":"Midnight Cipher","emoji":"🕵️","pinterest":"mysterious+thriller+midnight+cipher+dark+purple"},
    ("Epic", "Romance"):       {"bg":"#1a0810","card":"#2a1020","accent":"#f43f5e","text":"#ffe4e6","sub":"#e11d48","name":"Crimson Epic","emoji":"❤️‍🔥","pinterest":"epic+romance+crimson+passionate+dramatic+art"},
    ("Calm", "Fantasy"):       {"bg":"#081510","card":"#0f2018","accent":"#34d399","text":"#d1fae5","sub":"#10b981","name":"Serene Glade","emoji":"🍃","pinterest":"calm+fantasy+serene+glade+green+peaceful+nature"},
}

DEFAULT_THEME = {"bg":"#0f0f13","card":"#1a1a24","accent":"#a78bfa","text":"#e9d5ff","sub":"#7c3aed","name":"Creative Universe","emoji":"✨","pinterest":"creative+concept+art+aesthetic"}

MUSIC_STYLE_EMOJIS = {
    "Rock":"🎸","Jazz":"🎷","Hip-hop":"🎤","Pop":"🎵","Classical":"🎻",
    "Electronic":"🎹","R&B":"🎶","Folk":"🪕","Metal":"🤘","Blues":"🎺",
    "Reggae":"🌴","Country":"🤠"
}

def get_theme(mood, genre):
    return THEMES.get((mood, genre), DEFAULT_THEME)

def apply_theme(t):
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t['bg']} !important; }}
        [data-testid="stSidebar"] {{
            background-color: #0f0f13 !important;
            border-right: 1px solid #2a2a3a !important;
        }}
        [data-testid="stSidebar"] * {{ color: #e0e0e0 !important; }}
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] textarea {{
            background-color: #1a1a24 !important;
            border-color: #2a2a3a !important;
            color: #e0e0e0 !important;
        }}
        .cf-card {{
            background: {t['card']};
            border: 1px solid {t['accent']}44;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {t['card']};
            border-radius: 10px;
            padding: 4px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {t['accent']}44 !important;
            color: {t['text']} !important;
        }}
        [data-testid="stMetric"] {{
            background: {t['card']};
            border: 1px solid {t['accent']}33;
            border-radius: 10px;
            padding: 12px;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {t['accent']} !important;
            border-color: {t['accent']} !important;
            color: white !important;
        }}
        .cf-badge {{
            display: inline-block;
            background: {t['accent']}22;
            border: 1px solid {t['accent']}44;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 12px;
            color: {t['accent']};
        }}
        .cf-platform-btn {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            margin: 4px;
            border: 1px solid {t['accent']}44;
            background: {t['card']};
            color: {t['text']} !important;
        }}
        .cf-pinterest-btn {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
            background: #e60023;
            color: white !important;
            border: none;
        }}
        .cf-music-style-badge {{
            display: inline-block;
            background: {t['accent']}33;
            color: {t['accent']};
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }}
        .stApp h1, .stApp h2, .stApp h3 {{ color: {t['text']} !important; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='margin:0'>✨ CreativeFlow AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px;opacity:.6;margin-top:4px'>Powered by Creative Knowledge Engine</p>", unsafe_allow_html=True)
    st.divider()

    prompt = st.text_area("💡 Your Creative Idea", placeholder="e.g. A lonely astronaut finds music on Mars...", max_chars=300, height=120)
    mood = st.selectbox("🎭 Mood", ["Mysterious","Calm","Epic","Dark","Romantic","Playful"])
    genre = st.selectbox("📚 Story Genre", ["Sci-fi","Fantasy","Romance","Thriller","Historical","Horror"])

    theme = get_theme(mood, genre)
    apply_theme(theme)

    st.markdown(f"""
    <div style='background:{theme["accent"]}22;border:1px solid {theme["accent"]}44;border-radius:10px;padding:10px;margin:8px 0;text-align:center'>
        <span style='font-size:20px'>{theme["emoji"]}</span>
        <p style='margin:4px 0 0;font-size:13px;color:{theme["accent"]};font-weight:600'>{theme["name"]}</p>
        <p style='margin:0;font-size:11px;opacity:.6'>{mood} × {genre}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("**🎵 Music Style**")
    music_style = st.selectbox("", [
        "Rock","Jazz","Hip-hop","Pop","Classical",
        "Electronic","R&B","Folk","Metal","Blues","Reggae","Country"
    ], label_visibility="collapsed")

    music_emoji = MUSIC_STYLE_EMOJIS.get(music_style, "🎵")
    st.markdown(f"""
    <div style='background:#1a1a24;border:1px solid #2a2a3a;border-radius:8px;padding:8px;text-align:center;margin-top:4px'>
        <span style='font-size:18px'>{music_emoji}</span>
        <span style='font-size:12px;color:#a0a0c0;margin-left:6px'>{music_style} style selected</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("**🎯 What to Generate**")
    gen_story  = st.checkbox("📖 Story", value=True)
    gen_music  = st.checkbox("🎵 Music direction", value=True)
    gen_visual = st.checkbox("🎨 Visual concept", value=True)

    st.divider()
    generate_btn = st.button("✨ Generate Creative Universe", type="primary", use_container_width=True)

    st.divider()
    pinterest_url = f"https://pinterest.com/search/pins/?q={theme['pinterest']}"
    st.markdown(f"""
    <div style='text-align:center'>
        <p style='font-size:12px;opacity:.5;margin-bottom:6px'>Get visual inspiration</p>
        <a href='{pinterest_url}' target='_blank' class='cf-pinterest-btn'>📌 Search Pinterest</a>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:32px 0 8px'>
    <div style='font-size:48px'>{theme['emoji']}</div>
    <h1 style='font-size:42px;font-weight:700;color:{theme["text"]};margin:8px 0'>CreativeFlow AI</h1>
    <p style='color:{theme["sub"]};font-size:16px'>Turn one idea into a story, music, and visual concept</p>
</div>
<div style='text-align:center;margin-bottom:24px'>
    <span class='cf-badge'>⚡ {theme["name"]} — Multi-Agent Creative Generation Active</span>
</div>
""", unsafe_allow_html=True)

if not generate_btn and 'story_result' not in st.session_state:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='cf-card' style='text-align:center'>
            <div style='font-size:32px'>📖</div>
            <h3>Story</h3>
            <p style='font-size:13px;opacity:.6'>A structured narrative using proven frameworks</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='cf-card' style='text-align:center'>
            <div style='font-size:32px'>{music_emoji}</div>
            <h3>Music — {music_style}</h3>
            <p style='font-size:13px;opacity:.6'>Lyrics, tempo, instruments and production notes</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='cf-card' style='text-align:center'>
            <div style='font-size:32px'>🎨</div>
            <h3>Visual</h3>
            <p style='font-size:13px;opacity:.6'>Scene concept + image prompt for AI art tools</p>
        </div>""", unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────
if generate_btn:
    if not prompt:
        st.warning("Please enter a creative idea in the sidebar first!")
    else:
        progress = st.progress(0, text="🔍 Foundry IQ retrieving creative knowledge...")
        try:
            knowledge = retrieve_creative_knowledge(prompt, mood, genre)
            progress.progress(20, text="✅ Knowledge retrieved!")
        except Exception as e:
            knowledge = {
                "story_framework": "Hero's Journey",
                "music_mood": {"tempo":"Moderate","instruments":["Piano","Synthesizer","Strings"],"chord_progression":"Am - F - C - G"},
                "visual_style": {"art_style":"Digital Art","color_palette":["Deep Blue","Silver","Black"],"lighting":"Dramatic","visual_references":["Cinematic","Epic"]},
                "creative_themes": ["Discovery","Wonder","Connection"]
            }

        story_result = music_result = visual_result = None

        if gen_story:
            progress.progress(40, text="📖 Writing your story...")
            story_result = generate_story(prompt, mood, genre, knowledge)
        if gen_music:
            progress.progress(60, text=f"{music_emoji} Composing {music_style} music...")
            music_result = generate_music(prompt, mood, genre, knowledge, music_style)
        if gen_visual:
            progress.progress(80, text="🎨 Creating visual concept...")
            visual_result = generate_visual(prompt, mood, genre, knowledge)

        progress.progress(100, text="✅ Your creative universe is ready!")

        st.session_state.update({
            'story_result': story_result,
            'music_result': music_result,
            'visual_result': visual_result,
            'prompt': prompt,
            'mood': mood,
            'genre': genre,
            'theme': theme,
            'music_style': music_style,
            'music_emoji': music_emoji,
        })

# ── Results ───────────────────────────────────────────────────
if 'story_result' in st.session_state:
    story_result  = st.session_state.get('story_result')
    music_result  = st.session_state.get('music_result')
    visual_result = st.session_state.get('visual_result')
    t             = st.session_state.get('theme', theme)
    saved_style   = st.session_state.get('music_style', music_style)
    saved_emoji   = st.session_state.get('music_emoji', music_emoji)
    saved_mood    = st.session_state.get('mood', mood)
    saved_genre   = st.session_state.get('genre', genre)
    saved_theme   = st.session_state.get('theme', theme)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 Story", f"{saved_emoji} Music", "🎨 Visual", "📌 Inspiration", "📤 Export"])

    # ── Story Tab ──
    with tab1:
        if story_result:
            st.markdown(f"<div class='cf-card'><h2>{story_result['title']}</h2><p>{story_result['story'].replace(chr(10),'<br>')}</p></div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Framework", story_result['framework'])
            c2.metric("Words", story_result['word_count'])
            c3.metric("Genre", saved_genre)
            st.markdown("**🚀 Continue your story:**")
            st.markdown("""
            <a href='https://aistudio.google.com/generate-video' target='_blank' class='cf-platform-btn'>🎬 Veo 3 — Google AI Studio</a>
            <a href='https://docs.google.com' target='_blank' class='cf-platform-btn'>📝 Google Docs</a>
            <a href='https://medium.com/new-story' target='_blank' class='cf-platform-btn'>✍️ Publish on Medium</a>
            """, unsafe_allow_html=True)
        else:
            st.info("Story was not generated. Enable Story in the sidebar and regenerate.")

    # ── Music Tab ──
    with tab2:
        if music_result:
            st.markdown(f"""
            <div class='cf-card'>
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap'>
                    <h2 style='margin:0'>{music_result['song_title']}</h2>
                    <span class='cf-music-style-badge'>{saved_emoji} {saved_style}</span>
                </div>
                <p style='opacity:.7;margin:0'>{music_result['genre_style']}</p>
                <p style='font-size:12px;opacity:.4;margin-top:6px'>Structure: {music_result.get('structure','')}</p>
            </div>
            """, unsafe_allow_html=True)

            c1,c2,c3 = st.columns(3)
            c1.metric("Tempo", music_result['tempo'])
            c2.metric("Chords", music_result['chord_progression'])
            c3.metric("Style", saved_style)

            st.markdown(f"**{saved_emoji} Lyrics:**")
            st.code(music_result['lyrics'], language=None)
            st.markdown(f"**🎛️ Production Notes:** {music_result['production_notes']}")

            st.markdown("**🎼 Instruments:**")
            instruments_html = " ".join([f"<span style='background:{t['accent']}22;color:{t['accent']};padding:4px 12px;border-radius:20px;font-size:12px;margin:2px;display:inline-block'>{i}</span>" for i in music_result['instruments']])
            st.markdown(instruments_html, unsafe_allow_html=True)

            st.markdown("**🚀 Turn your lyrics into music:**")
            st.markdown(f"""
            <a href='https://suno.com' target='_blank' class='cf-platform-btn'>🎵 Suno AI</a>
            <a href='https://udio.com' target='_blank' class='cf-platform-btn'>🎶 Udio</a>
            <a href='https://www.soundraw.io' target='_blank' class='cf-platform-btn'>🎸 Soundraw</a>
            <a href='https://www.musicfy.lol' target='_blank' class='cf-platform-btn'>🎤 Musicfy</a>
            """, unsafe_allow_html=True)
        else:
            st.info("Music was not generated. Enable Music direction in the sidebar and regenerate.")

    # ── Visual Tab ──
    with tab3:
        if visual_result:
            st.markdown(f"<div class='cf-card'><h2>{visual_result['scene_title']}</h2><p>{visual_result['scene_description']}</p></div>", unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("**🎨 Color Story:**")
                st.write(visual_result['color_story'])
                palette = visual_result.get('color_palette', [])
                st.markdown(" ".join([f"<span style='background:{c.lower().replace(' ','')}; padding:4px 12px; border-radius:20px; font-size:12px; margin:2px; display:inline-block; border:1px solid rgba(255,255,255,.2); color:white'>{c}</span>" for c in palette]), unsafe_allow_html=True)
            with c2:
                st.markdown("**🖼️ Key Elements:**")
                for el in visual_result['key_elements']:
                    st.write(el)
            st.markdown("**📋 Image Prompt (copy to DALL-E / Midjourney / Firefly):**")
            st.code(visual_result['image_prompt'], language=None)
            st.markdown("**🚀 Generate your visual:**")
            st.markdown("""
            <a href='https://firefly.adobe.com' target='_blank' class='cf-platform-btn'>🔥 Adobe Firefly</a>
            <a href='https://ideogram.ai' target='_blank' class='cf-platform-btn'>🎨 Ideogram AI</a>
            <a href='https://www.midjourney.com' target='_blank' class='cf-platform-btn'>🌌 Midjourney</a>
            <a href='https://aistudio.google.com/generate-video' target='_blank' class='cf-platform-btn'>🎬 Veo 3 — Google AI Studio</a>
            """, unsafe_allow_html=True)
        else:
            st.info("Visual was not generated. Enable Visual concept in the sidebar and regenerate.")

    # ── Inspiration Tab ──
    with tab4:
        pinterest_search  = f"https://pinterest.com/search/pins/?q={saved_theme['pinterest']}"
        visual_ref_query  = "+".join(visual_result['key_elements'][0].replace("-","").strip().split()[:3]) if visual_result and visual_result['key_elements'] else saved_theme['pinterest']
        pinterest_specific= f"https://pinterest.com/search/pins/?q={visual_ref_query}+{saved_mood}+{saved_genre}+concept+art"
        pinterest_music   = f"https://pinterest.com/search/pins/?q={saved_style}+music+aesthetic+{saved_mood}"

        st.markdown(f"<div class='cf-card'><h2>📌 Get Inspired on Pinterest</h2><p>Explore visuals that match your {saved_theme['name']} universe</p></div>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class='cf-card' style='text-align:center'>
                <div style='font-size:28px'>🎨</div>
                <h3>Theme Mood Board</h3>
                <p style='font-size:12px;opacity:.6'>{saved_mood} × {saved_genre} concept art and color palettes</p>
                <a href='{pinterest_search}' target='_blank' class='cf-pinterest-btn'>📌 Open Pinterest</a>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='cf-card' style='text-align:center'>
                <div style='font-size:28px'>🖼️</div>
                <h3>Scene Reference</h3>
                <p style='font-size:12px;opacity:.6'>Visual references for your specific scene</p>
                <a href='{pinterest_specific}' target='_blank' class='cf-pinterest-btn'>📌 Open Pinterest</a>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class='cf-card' style='text-align:center'>
                <div style='font-size:28px'>{saved_emoji}</div>
                <h3>{saved_style} Aesthetic</h3>
                <p style='font-size:12px;opacity:.6'>{saved_style} music visuals and album art inspiration</p>
                <a href='{pinterest_music}' target='_blank' class='cf-pinterest-btn'>📌 Open Pinterest</a>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**🔍 More inspiration sources:**")
        st.markdown(f"""
        <a href='https://www.artstation.com/search?q={saved_mood}+{saved_genre}&sort_by=relevance' target='_blank' class='cf-platform-btn'>🎭 ArtStation</a>
        <a href='https://unsplash.com/s/photos/{saved_mood}-{saved_genre}' target='_blank' class='cf-platform-btn'>📷 Unsplash</a>
        <a href='https://www.behance.net/search/projects?search={saved_mood}+{saved_genre}+concept+art' target='_blank' class='cf-platform-btn'>💼 Behance</a>
        <a href='https://dribbble.com/search/{saved_mood}+{saved_genre}' target='_blank' class='cf-platform-btn'>🏀 Dribbble</a>
        """, unsafe_allow_html=True)

    # ── Export Tab ──
    with tab5:
        st.markdown("<div class='cf-card'><h2>📤 Export Your Creative Universe</h2></div>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**📦 Included:**")
            if story_result:  st.write(f"✅ Story: *{story_result['title']}*")
            if music_result:  st.write(f"✅ Music ({saved_style}): *{music_result['song_title']}*")
            if visual_result: st.write(f"✅ Visual: *{visual_result['scene_title']}*")
        with c2:
            st.markdown("**ℹ️ Details:**")
            st.write(f"Prompt: {st.session_state.get('prompt','')[:60]}...")
            st.write(f"Theme: {t['emoji']} {t['name']}")
            st.write(f"Mood × Genre: {saved_mood} × {saved_genre}")
            st.write(f"Music Style: {saved_emoji} {saved_style}")

        st.markdown("")
        if st.button("📄 Generate Word Document", type="primary", use_container_width=True):
            with st.spinner("Creating your document..."):
                path = export_to_docx(
                    st.session_state.get('prompt',''),
                    st.session_state.get('mood',''),
                    st.session_state.get('genre',''),
                    story_result, music_result, visual_result
                )
            with open(path,"rb") as f:
                st.download_button(
                    label="⬇️ Download Your Creative Universe",
                    data=f,
                    file_name="creativeflow_output.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )