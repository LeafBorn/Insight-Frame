import streamlit as st
from dotenv import load_dotenv
from utils.audio_processor import process_youtube_audio
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

st.set_page_config(
    page_title="INSIGHT FRAME",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PALETTE (Sofia-style) ────────────────────────────────────────────────
LIME    = "#f5ffdc"
MINT    = "#9FE3D8"   
PINK    = "#F5A8C9"   
PURPLE  = "#7B2FBE"  
LPURPLE = "#C084FC"   
BLACK   = "#111111"
WHITE   = "#FFFFFF"
CREAM   = "#FFFDE7"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Nunito:wght@700;800;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background: {LIME} !important;
    font-family: 'Nunito', sans-serif;
    color: {BLACK};
}}

[data-testid="stAppViewContainer"] > .main {{ padding: 0 !important; }}
[data-testid="block-container"] {{ padding: 1.5rem 2rem 4rem 2rem !important; max-width: 100% !important; }}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: {MINT} !important;
    border-right: 3px solid {BLACK} !important;
}}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] [data-testid="stSidebarContent"],
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {{
    padding: 0 !important;
    margin: 0 !important;
    background: {MINT} !important;
}}
[data-testid="stSidebar"] * {{ color: {BLACK} !important; }}

[data-testid="stSidebar"] .stTextInput > div > div > input {{
    background: {WHITE} !important;
    border: 3px solid {BLACK} !important;
    border-radius: 12px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
    box-shadow: 4px 4px 0 {BLACK} !important;
    color: {BLACK} !important;
    outline: none !important;
}}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {{
    box-shadow: 5px 5px 0 {PURPLE} !important;
    border-color: {PURPLE} !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div {{
    background: {WHITE} !important;
    border: 3px solid {BLACK} !important;
    border-radius: 12px !important;
    box-shadow: 4px 4px 0 {BLACK} !important;
}}
[data-testid="stSidebar"] label {{
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: {PURPLE} !important;
    color: {WHITE} !important;
    border: 3px solid {BLACK} !important;
    border-radius: 50px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.06em !important;
    padding: 12px 20px !important;
    box-shadow: 4px 4px 0 {BLACK} !important;
    transition: all 0.12s ease !important;
    width: 100% !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {PINK} !important;
    color: {BLACK} !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0 {BLACK} !important;
}}
[data-testid="stSidebar"] .stButton > button:active {{
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 {BLACK} !important;
}}

/* ── MAIN BUTTONS ── */
.stButton > button {{
    background: {PINK} !important;
    color: {BLACK} !important;
    border: 3px solid {BLACK} !important;
    border-radius: 50px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    box-shadow: 4px 4px 0 {BLACK} !important;
    transition: all 0.12s ease !important;
}}
.stButton > button:hover {{
    background: {PURPLE} !important;
    color: {WHITE} !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0 {BLACK} !important;
}}

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 3px solid {BLACK} !important;
    gap: 6px !important;
    background: transparent !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    background: {WHITE} !important;
    border: 3px solid {BLACK} !important;
    border-bottom: none !important;
    border-radius: 12px 12px 0 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: {BLACK} !important;
    padding: 10px 16px !important;
    box-shadow: 3px 0px 0 {BLACK} !important;
    transition: background 0.1s !important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    background: {PURPLE} !important;
    color: {WHITE} !important;
}}
[data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {{
    background: {PINK} !important;
}}

/* ── PROGRESS ── */
[data-testid="stProgress"] > div > div > div > div {{
    background: {PURPLE} !important;
    border-radius: 50px !important;
}}
[data-testid="stProgress"] > div > div {{
    border: 2px solid {BLACK} !important;
    border-radius: 50px !important;
    background: {WHITE} !important;
}}

/* ── ALERTS ── */
[data-testid="stAlert"] {{
    border-radius: 14px !important;
    border: 3px solid {BLACK} !important;
    box-shadow: 4px 4px 0 {BLACK} !important;
    font-family: 'Space Mono', monospace !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-track {{ background: {LIME}; }}
::-webkit-scrollbar-thumb {{ background: {PURPLE}; border-radius: 4px; }}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] textarea {{
    border: 3px solid {BLACK} !important;
    border-radius: 14px !important;
    font-family: 'Space Mono', monospace !important;
    background: {WHITE} !important;
    color: {BLACK} !important;
    box-shadow: 4px 4px 0 {BLACK} !important;
}}
[data-testid="stChatInput"] button {{
    background: {PURPLE} !important;
    border-radius: 10px !important;
    border: 2px solid {BLACK} !important;
}}

/* Hide user chat bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    display: none !important;
}}

/* ── SPINNER ── */
[data-testid="stSpinner"] > div {{ color: {PURPLE} !important; }}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer {{ visibility: hidden !important; }}

header {{ 
    visibility: visible !important;
    background: transparent !important;
}}

[data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}}
</style>
""", unsafe_allow_html=True)


# ─── COMPONENTS ─────────────────────────────────────────────────────────────────

def card(content_html: str, bg: str = WHITE, shadow_color: str = BLACK,
         radius: str = "16px", border: str = BLACK, padding: str = "22px 24px",
         extra_style: str = ""):
    st.markdown(f"""
    <div style="
        background: {bg};
        border: 3px solid {border};
        border-radius: {radius};
        box-shadow: 5px 5px 0 {shadow_color};
        padding: {padding};
        margin-bottom: 18px;
        {extra_style}
    ">{content_html}</div>
    """, unsafe_allow_html=True)


def pill_tag(text: str, bg: str = PURPLE, color: str = WHITE):
    return f"""<span style="
        background:{bg};color:{color};
        border:2px solid {BLACK};border-radius:50px;
        font-family:'Space Mono',monospace;font-size:10px;font-weight:700;
        letter-spacing:0.08em;text-transform:uppercase;
        padding:3px 12px;display:inline-block;
        box-shadow:2px 2px 0 {BLACK};margin-right:6px;
    ">{text}</span>"""


def section_header(emoji: str, text: str, bg: str = PURPLE, color: str = WHITE):
    st.markdown(f"""
    <div style="
        display:inline-flex;align-items:center;gap:10px;
        background:{bg};color:{color};
        border:3px solid {BLACK};border-radius:50px;
        font-family:'Space Mono',monospace;font-size:12px;font-weight:700;
        letter-spacing:0.06em;text-transform:uppercase;
        padding:8px 20px;
        box-shadow:4px 4px 0 {BLACK};
        margin:20px 0 14px 0;
    ">{emoji} {text}</div>
    """, unsafe_allow_html=True)


def status_pill(label: str, bg: str = WHITE, color: str = BLACK, blink: bool = False):
    anim = "animation:blink 0.9s step-end infinite;" if blink else ""
    st.markdown(f"""
    <style>@keyframes blink{{50%{{opacity:0;}}}}</style>
    <div style="
        background:{bg};color:{color};
        border:3px solid {BLACK};border-radius:50px;
        font-family:'Space Mono',monospace;font-size:12px;font-weight:700;
        letter-spacing:0.1em;text-transform:uppercase;
        padding:9px 20px;display:inline-flex;align-items:center;gap:10px;
        box-shadow:4px 4px 0 {BLACK};margin-bottom:20px;
    ">
        <span style="width:10px;height:10px;background:{color};border-radius:50%;{anim}"></span>
        {label}
    </div>
    """, unsafe_allow_html=True)


def result_card(title: str, content: str, bg: str, emoji: str, shadow: str = BLACK):
    st.markdown(f"""
    <div style="
        background:{bg};
        border:3px solid {BLACK};
        border-radius:16px;
        box-shadow:5px 5px 0 {shadow};
        overflow:hidden;
        margin-bottom:18px;
    ">
        <div style="
            background:{BLACK};color:{WHITE};
            font-family:'Space Mono',monospace;
            font-size:11px;font-weight:700;
            letter-spacing:0.12em;text-transform:uppercase;
            padding:9px 18px;
            display:flex;align-items:center;gap:8px;
        ">{emoji} {title}</div>
        <div style="
            padding:20px 22px;
            font-family:'Space Mono',monospace;
            font-size:13px;line-height:1.8;
            color:{BLACK};white-space:pre-wrap;
        ">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def chat_bubble(message: str):
    st.markdown(f"""
    <div style="
        background:{PINK};
        border:3px solid {BLACK};
        border-radius:18px 18px 18px 4px;
        box-shadow:5px 5px 0 {BLACK};
        padding:18px 22px;
        margin-bottom:18px;
        position:relative;
    ">
        <div style="
            font-family:'Space Mono',monospace;
            font-size:9px;font-weight:700;
            letter-spacing:0.2em;color:{PURPLE};
            text-transform:uppercase;margin-bottom:8px;
        ">✨ AI RESPONSE</div>
        <div style="
            font-family:'Nunito',sans-serif;
            font-size:15px;line-height:1.75;
            font-weight:700;color:{BLACK};
            white-space:pre-wrap;
        ">{message}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── SESSION STATE ───────────────────────────────────────────────────────────────
defaults = {
    "pipeline_result": None,
    "status": "🎬 READY — PASTE A URL TO START",
    "status_color": BLACK,
    "status_bg":    WHITE,
    "status_blink": False,
    "chat_history": [],
    "pipeline_ran": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def set_status(label, color=BLACK, bg=WHITE, blink=False):
    st.session_state.status       = label
    st.session_state.status_color = color
    st.session_state.status_bg    = bg
    st.session_state.status_blink = blink


# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="background:{MINT};padding:28px 20px 20px 20px;border-bottom:3px solid {BLACK};">
        <div style="
            font-family:'Space Mono',monospace;
            font-size:22px;font-weight:700;
            color:{BLACK};margin-bottom:6px;
        ">🎬 INSIGHT<br><span style="color:{PURPLE};">FRAME</span></div>
        <div style="
            font-family:'Space Mono',monospace;
            font-size:9px;letter-spacing:0.15em;
            color:#555;text-transform:uppercase;
        ">AI Video Intelligence</div>
    </div>
    <div style="padding:20px 20px 0 20px;background:{MINT};">
    """, unsafe_allow_html=True)

    source_url = st.text_input(
        "📎 Video Source",
        placeholder="https://youtube.com/watch?v=...",
    )
    language = st.selectbox(
        "🌐 Language",
        ["english", "hindi", "spanish", "french", "german", "japanese"],
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    run_btn = st.button("▶  RUN PIPELINE", use_container_width=True)

    st.markdown(f"""
    </div>
    <div style="
        background:{MINT};
        border-top:3px solid {BLACK};
        margin-top:24px;
        padding:20px 20px 28px 20px;
    ">
        <div style="
            font-family:'Space Mono',monospace;
            font-size:10px;font-weight:700;
            letter-spacing:0.1em;color:{PURPLE};
            text-transform:uppercase;margin-bottom:12px;
        ">Pipeline Stages</div>
        <div style="font-family:'Space Mono',monospace;font-size:11px;line-height:2.2;color:{BLACK};">
            <span style="color:{PURPLE};font-weight:700;">01</span> Audio Extract<br>
            <span style="color:{PURPLE};font-weight:700;">02</span> Transcribe<br>
            <span style="color:{PURPLE};font-weight:700;">03</span> Generate Title<br>
            <span style="color:{PURPLE};font-weight:700;">04</span> Summarize<br>
            <span style="color:{PURPLE};font-weight:700;">05</span> Action Items<br>
            <span style="color:{PURPLE};font-weight:700;">06</span> Key Decisions<br>
            <span style="color:{PURPLE};font-weight:700;">07</span> Open Questions<br>
            <span style="color:{PURPLE};font-weight:700;">08</span> Build RAG Chain
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background:{WHITE};
    border:3px solid {BLACK};
    border-radius:20px;
    box-shadow:6px 6px 0 {BLACK};
    padding:28px 36px;
    margin-bottom:24px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    flex-wrap:wrap;
    gap:14px;
">
    <div>
        <div style="
            font-family:'Space Mono',monospace;
            font-size:36px;font-weight:700;
            color:{BLACK};line-height:1.1;
        ">🎬 INSIGHT<span style="color:{PURPLE};">FRAME</span></div>
        <div style="
            font-family:'Nunito',sans-serif;
            font-size:14px;font-weight:800;
            color:#555;letter-spacing:0.08em;
            text-transform:uppercase;margin-top:6px;
        ">AI-Powered Video Intelligence Platform ✨</div>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;">
        {pill_tag("Transcribe 🎙️", MINT, BLACK)}
        {pill_tag("Summarize 📋", PINK, BLACK)}
        {pill_tag("RAG Chat 💬", PURPLE, WHITE)}
    </div>
</div>
""", unsafe_allow_html=True)

# ─── STATUS BAR ─────────────────────────────────────────────────────────────────
status_placeholder = st.empty()
with status_placeholder.container():
    status_pill(
        st.session_state.status,
        bg=st.session_state.status_bg,
        color=st.session_state.status_color,
        blink=st.session_state.status_blink,
    )


# ─── PIPELINE ───────────────────────────────────────────────────────────────────
if run_btn:
    if not source_url.strip():
        st.warning("📎 Paste a YouTube URL in the sidebar first!")
    else:
        st.session_state.chat_history    = []
        st.session_state.pipeline_result = None
        st.session_state.pipeline_ran    = False

        prog = st.progress(0, text="Starting up…")

        def upd(label, color, bg, blink, pct, txt):
            set_status(label, color, bg, blink)
            with status_placeholder.container():
                status_pill(label, bg=bg, color=color, blink=blink)
            prog.progress(pct, text=txt)

        try:
            upd("🎵 Extracting Audio…",    BLACK, LIME,    True, 10, "Stage 01 — Extracting audio…")
            audio_data  = process_youtube_audio(source_url.strip())
            chunks      = audio_data["chunks"]

            upd("📝 Transcribing…",        BLACK, MINT,    True, 25, "Stage 02 — Transcribing chunks…")
            transcript  = transcribe_all(chunks, translate=False)

            upd("🏷️  Generating Title…",   BLACK, PINK,    True, 40, "Stage 03 — Generating title…")
            title       = generate_title(transcript)

            upd("📋 Summarizing…",         BLACK, LIME,    True, 55, "Stage 04 — Summarizing…")
            summary     = summarize(transcript)

            upd("✅ Extracting Actions…",   BLACK, MINT,    True, 65, "Stage 05 — Action items…")
            action_items = extract_action_items(transcript)

            upd("🔑 Key Decisions…",       BLACK, PINK,    True, 75, "Stage 06 — Key decisions…")
            decisions   = extract_key_decisions(transcript)

            upd("❓ Open Questions…",       BLACK, LIME,    True, 85, "Stage 07 — Open questions…")
            questions   = extract_questions(transcript)

            upd("🔗 Building RAG Chain…",  WHITE, PURPLE,  True, 95, "Stage 08 — Building RAG chain…")
            rag_chain   = build_rag_chain(transcript)

            st.session_state.pipeline_result = {
                "title": title, "transcript": transcript,
                "summary": summary, "action_items": action_items,
                "key_decisions": decisions, "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_ran = True
            prog.progress(100, text="Done! 🎉")
            upd("🎉 Complete — Ready to Chat!", BLACK, LIME, False, 100, "Done!")

        except Exception as e:
            upd("❌ Pipeline Error", WHITE, "#E53935", False, 0, "Error")
            st.error(f"**Pipeline failed:** {e}")


# ─── RESULTS ────────────────────────────────────────────────────────────────────
if st.session_state.pipeline_ran and st.session_state.pipeline_result:
    result = st.session_state.pipeline_result

    # Title card
    st.markdown(f"""
    <div style="
        background:{PURPLE};
        border:3px solid {BLACK};
        border-radius:16px;
        box-shadow:6px 6px 0 {BLACK};
        padding:20px 28px;
        margin:8px 0 24px 0;
        display:flex;align-items:center;gap:14px;
    ">
        <span style="font-size:28px;">🎬</span>
        <div>
            <div style="font-family:'Space Mono',monospace;font-size:10px;font-weight:700;
                letter-spacing:0.2em;color:{LPURPLE};text-transform:uppercase;margin-bottom:4px;">
                Video Title
            </div>
            <div style="font-family:'Space Mono',monospace;font-size:18px;font-weight:700;
                color:{WHITE};line-height:1.3;">
                {result['title']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary", "✅ Actions", "🔑 Decisions", "❓ Questions", "📄 Transcript"
    ])

    with tab1:
        section_header("📋", "Summary", PURPLE, WHITE)
        result_card("Generated Summary", result["summary"], MINT, "📋", BLACK)

    with tab2:
        section_header("✅", "Action Items", PINK, BLACK)
        result_card("Action Items", result["action_items"], PINK, "✅", BLACK)

    with tab3:
        section_header("🔑", "Key Decisions", LIME, BLACK)
        result_card("Key Decisions", result["key_decisions"], LIME, "🔑", BLACK)

    with tab4:
        section_header("❓", "Open Questions", MINT, BLACK)
        result_card("Open Questions", result["open_questions"], MINT, "❓", BLACK)

    with tab5:
        section_header("📄", "Full Transcript", BLACK, WHITE)
        st.markdown(f"""
        <div style="
            background:{WHITE};border:3px solid {BLACK};border-radius:14px;
            box-shadow:5px 5px 0 {BLACK};padding:20px;
            font-family:'Space Mono',monospace;font-size:12px;line-height:1.9;
            color:{BLACK};max-height:420px;overflow-y:auto;white-space:pre-wrap;
        ">{result['transcript']}</div>
        """, unsafe_allow_html=True)

    # ── RAG CHAT ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background:{MINT};
        border:3px solid {BLACK};
        border-radius:20px;
        box-shadow:6px 6px 0 {BLACK};
        padding:22px 26px;
        margin-bottom:20px;
    ">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
            <span style="font-size:24px;">💬</span>
            <div style="font-family:'Space Mono',monospace;font-size:15px;font-weight:700;
                color:{BLACK};text-transform:uppercase;letter-spacing:0.06em;">
                Chat with your Video
            </div>
            <span style="
                background:{PURPLE};color:{WHITE};
                border:2px solid {BLACK};border-radius:50px;
                font-family:'Space Mono',monospace;font-size:9px;font-weight:700;
                padding:3px 10px;letter-spacing:0.1em;
            ">RAG ENGINE</span>
        </div>
        <div style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:#444;">
            Ask anything — the AI searches your full transcript to answer. ✨
        </div>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            chat_bubble(msg["content"])

    user_input = st.chat_input("Ask something about this video… 💬")
    if user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        with st.spinner("✨ Thinking…"):
            answer = ask_question(result["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

else:
    # ── Empty state ──────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown(f"""
        <div style="
            background:{WHITE};border:3px solid {BLACK};border-radius:20px;
            box-shadow:6px 6px 0 {BLACK};padding:36px 32px;height:100%;
        ">
            <div style="font-family:'Space Mono',monospace;font-size:32px;font-weight:700;
                color:{BLACK};line-height:1.2;margin-bottom:12px;">
                Hello! 👋
            </div>
            <div style="font-family:'Nunito',sans-serif;font-size:16px;font-weight:800;
                color:#444;margin-bottom:20px;line-height:1.6;">
                I am <span style="color:{PURPLE};">Insight Frame</span> —<br>
                your AI-powered video analyst.
            </div>
            <div style="
                background:{PURPLE};color:{WHITE};
                border:3px solid {BLACK};border-radius:50px;
                font-family:'Space Mono',monospace;font-size:12px;font-weight:700;
                padding:12px 22px;display:inline-block;
                box-shadow:4px 4px 0 {BLACK};
            ">
                Transcribe · Summarize · Chat 🚀
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background:{PINK};border:3px solid {BLACK};border-radius:20px;
            box-shadow:6px 6px 0 {BLACK};padding:30px 28px;
        ">
            <div style="font-family:'Space Mono',monospace;font-size:12px;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:{PURPLE};margin-bottom:16px;">
                ✨ How it works
            </div>
            <div style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;
                color:{BLACK};line-height:2.2;">
                <span style="background:{LIME};border:2px solid {BLACK};border-radius:6px;
                    padding:1px 8px;margin-right:8px;">01</span>Paste a YouTube URL in the sidebar<br>
                <span style="background:{MINT};border:2px solid {BLACK};border-radius:6px;
                    padding:1px 8px;margin-right:8px;">02</span>Pick a language<br>
                <span style="background:{PINK};border:2px solid {BLACK};border-radius:6px;
                    padding:1px 8px;margin-right:8px;">03</span>Hit <strong>▶ RUN PIPELINE</strong><br>
                <span style="background:{LIME};border:2px solid {BLACK};border-radius:6px;
                    padding:1px 8px;margin-right:8px;">04</span>Chat with your video! 💬
            </div>
        </div>

        <div style="
            background:{MINT};border:3px solid {BLACK};border-radius:20px;
            box-shadow:6px 6px 0 {BLACK};padding:22px 28px;margin-top:16px;
            display:flex;align-items:center;gap:16px;
        ">
            <span style="font-size:32px;">🎙️</span>
            <div>
                <div style="font-family:'Space Mono',monospace;font-size:11px;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;color:{PURPLE};">Supports</div>
                <div style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;color:{BLACK};">
                    YouTube URLs · Local Video Files<br>6+ Languages · RAG-powered Chat
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)