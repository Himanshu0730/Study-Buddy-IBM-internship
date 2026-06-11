import streamlit as st
import google.generativeai as genai
import fitz
import time
import os
from dotenv import load_dotenv

# -------------------------------
# Configuration
# -------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Check your .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

PDF_CHAR_LIMIT = 30_000

SYSTEM_PROMPT = (
    "You are a helpful AI Study Buddy. "
    "You help students understand, summarize, and quiz themselves on study material. "
    "Be clear, concise, and educational."
)

FEATURE_PLACEHOLDERS = {
    "Chat": "Ask a question about your notes or any topic...",
    "Summarize Notes": "Type anything to summarize your uploaded PDF...",
    "Generate Quiz": "Type anything to generate a quiz from your PDF...",
    "Generate Flashcards": "Type anything to generate flashcards from your PDF...",
}

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Buddy")
st.caption("Ask questions, summarize notes, generate quizzes and flashcards.")

# -------------------------------
# Helper Functions
# -------------------------------
def extract_pdf_text(file) -> str:
    """Extract text from an uploaded PDF file object."""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in pdf)
    return text[:PDF_CHAR_LIMIT]


def build_prompt(feature: str, user_input: str, pdf_text: str) -> str:
    """Build the appropriate prompt based on selected feature."""
    notes_block = f"\n\n---\nNotes:\n{pdf_text}\n---" if pdf_text else ""

    if feature == "Chat":
        if pdf_text:
            return (
                f"{SYSTEM_PROMPT}\n\n"
                f"Answer the following question using the uploaded notes where relevant.{notes_block}\n\n"
                f"Question: {user_input}"
            )
        return f"{SYSTEM_PROMPT}\n\nQuestion: {user_input}"

    if feature == "Summarize Notes":
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Summarize the following notes clearly and concisely using simple language. "
            f"Use bullet points for key ideas.{notes_block}"
        )

    if feature == "Generate Quiz":
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Create exactly 10 multiple-choice questions based on the notes below.\n"
            f"Use ONLY this format, separated by '---':\n\n"
            f"---\n"
            f"Question: <question text>\n\n"
            f"A) <option>\nB) <option>\nC) <option>\nD) <option>\n\n"
            f"Answer: <letter>\n"
            f"---\n"
            f"{notes_block}"
        )

    if feature == "Generate Flashcards":
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Create exactly 10 flashcards based on the notes below.\n"
            f"Use ONLY this format, separated by '---':\n\n"
            f"---\n"
            f"Question: <question>\n"
            f"Answer: <answer>\n"
            f"---\n"
            f"{notes_block}"
        )

    return user_input


def stream_response(prompt: str, placeholder) -> str:
    """Stream Gemini response and display it with a cursor. Returns full text."""
    full_response = ""
    for chunk in model.generate_content(prompt, stream=True):
        if chunk.text:
            full_response += chunk.text
            placeholder.markdown(full_response + "▌")
    placeholder.empty()
    return full_response


def parse_blocks(text: str) -> list:
    """Split on '---' and return non-empty stripped blocks."""
    return [b.strip() for b in text.split("---") if b.strip()]


def display_flashcards(text: str):
    for i, card in enumerate(parse_blocks(text), 1):
        with st.expander(f"🃏 Flashcard {i}"):
            st.markdown(card)


def display_quiz(text: str):
    for i, block in enumerate(parse_blocks(text), 1):
        if "Answer:" not in block:
            continue
        parts = block.split("Answer:", 1)
        question_part = parts[0].strip()
        answer_part = parts[1].strip() if len(parts) > 1 else "Not available"

        st.markdown(f"### ❓ Question {i}")
        st.markdown(question_part)
        with st.expander("✅ Show Answer"):
            st.success(answer_part)
        st.divider()


# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("📂 Study Tools")

    uploaded_file = st.file_uploader("Upload PDF Notes", type=["pdf"])

    feature = st.selectbox(
        "Choose Feature",
        ["Chat", "Summarize Notes", "Generate Quiz", "Generate Flashcards"]
    )

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your AI Study Buddy 📚. Upload notes or ask me anything."
        }]
        st.session_state.pop("pdf_text", None)
        st.session_state.pop("pdf_name", None)
        st.rerun()

# -------------------------------
# PDF Loading (cached by filename)
# -------------------------------
pdf_text = ""

if uploaded_file:
    if st.session_state.get("pdf_name") != uploaded_file.name:
        try:
            with st.spinner("Reading PDF..."):
                st.session_state.pdf_text = extract_pdf_text(uploaded_file)
                st.session_state.pdf_name = uploaded_file.name
            st.sidebar.success("PDF Loaded ✅")
        except Exception as e:
            st.sidebar.error(f"Error reading PDF: {e}")
    else:
        st.sidebar.success(f"PDF Ready: {uploaded_file.name} ✅")

    pdf_text = st.session_state.get("pdf_text", "")

needs_pdf = feature in ("Summarize Notes", "Generate Quiz", "Generate Flashcards")
if needs_pdf and not pdf_text:
    st.sidebar.warning("⚠️ Upload a PDF to use this feature.")

# -------------------------------
# Chat History Init
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your AI Study Buddy 📚. Upload notes or ask me anything."
    }]

# -------------------------------
# Display Chat History
# -------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------
# Chat Input
# -------------------------------
placeholder_text = FEATURE_PLACEHOLDERS.get(feature, "Type here...")
disabled = needs_pdf and not pdf_text

prompt = st.chat_input(placeholder_text, disabled=disabled)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            built_prompt = build_prompt(feature, prompt, pdf_text)

            with st.spinner("Thinking..."):
                full_response = stream_response(built_prompt, message_placeholder)

            if feature == "Generate Flashcards":
                display_flashcards(full_response)
            elif feature == "Generate Quiz":
                display_quiz(full_response)
            else:
                st.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ Error: {e}"
            st.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})