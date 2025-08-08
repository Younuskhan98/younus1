import streamlit as st
import wikipedia
import time
from gtts import gTTS
from io import BytesIO
import base64

# --- Page Setup ---
st.set_page_config(page_title="Wikipedia Chatbot", page_icon="📖")
st.title("Hey I'm V7chatBot")

# --- Sidebar ---
admin_photo_url = "https://i.postimg.cc/pdSJ0TrN/Whats-App-Image-2025-07-30-at-14-39-16-7e12e87a.jpg"

# Circular Admin Photo
st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="{admin_photo_url}" 
             style="width:120px; height:120px; border-radius:50%; object-fit:cover; border: 2px solid #ccc;" />
    </div>
    <p style="text-align:center; font-weight:bold;">Admin</p>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("Options")

# Language Selector
language = st.sidebar.selectbox(
    "Choose Language",
    options=["English", "Kannada", "Tamil", "Telugu", "Urdu", "Malayalam", "Hindi", "Spanish", "French", "German", "Arabic", "Japanese"],
    index=0
)

# Set Wikipedia language
lang_codes = {
    "English": "en", "Kannada": "kn", "Tamil": "ta", "Telugu": "te", "Urdu": "ur",
    "Malayalam": "ml", "Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de",
    "Arabic": "ar", "Japanese": "ja"
}
wikipedia.set_lang(lang_codes[language])

# Theme Selector
theme = st.sidebar.radio("Theme", options=["Light", "Dark"], index=0)
if theme == "Dark":
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #1e1e1e;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# Clear All Button
if st.sidebar.button("🗑 Clear Chat & History"):
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.text_input = ""

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # Each item: {'user': ..., 'bot': ..., 'images': [...], 'audio': ...}
if "history" not in st.session_state:
    st.session_state.history = []

# --- Wikipedia Search Function ---
def get_wikipedia_summary(query):
    try:
        page = wikipedia.page(query, auto_suggest=False, redirect=True)
        summary = page.summary
        image_urls = [img for img in page.images if img.lower().endswith(('.jpg', '.jpeg', '.png'))][:5]

        # Convert summary to speech
        tts = gTTS(summary, lang=lang_codes[language])
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        return summary, image_urls, audio_bytes

    except wikipedia.DisambiguationError as e:
        return f"Your query is ambiguous. Did you mean: {', '.join(e.options[:5])}?", [], None
    except wikipedia.PageError:
        return "Sorry, I couldn't find a page matching your query.", [], None
    except Exception as e:
        return f"Oops, something went wrong. {str(e)}", [], None

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Chat", "📜 History"])

# --- TAB 1: Chat ---
with tab1:
    user_input = st.text_input("Type your question:")

    suggestions = wikipedia.search(user_input) if user_input else []
    selected_query = st.selectbox("Select a suggestion:", options=[""] + suggestions)

    if selected_query.strip() != "":
        summary, image_urls, audio_data = get_wikipedia_summary(selected_query)
        st.session_state.messages.append({
            "user": selected_query,
            "bot": summary,
            "images": image_urls,
            "audio": audio_data
        })
        st.session_state.history.append(selected_query)

    for pair in st.session_state.messages:
        st.markdown(f"🧑‍💻 *You:* {pair['user']}")
        placeholder = st.empty()
        typed_text = ""
        for char in pair['bot']:
            typed_text += char
            placeholder.markdown(f"🤖 *Bot:* {typed_text}")
            time.sleep(0.0001)

        # Auto-playing audio
        if pair.get("audio"):
            audio_bytes = pair["audio"].read()
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio autoplay controls>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

        # Show images
        if pair.get("images"):
            for idx, img_url in enumerate(pair["images"]):
                st.image(img_url, width=350, caption=f"📷 Image {idx + 1}")

# --- TAB 2: History ---
with tab2:
    st.subheader("📜 Your Query History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"{i}. **{item}**")
    else:
        st.info("No history yet.")
