# 📚 AI Study Buddy

AI-powered study assistant — chat with your PDF notes, summarize, generate quizzes & flashcards using Google Gemini.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Features

| | |
|---|---|
| 💬 **Chat with Notes** | Ask questions about your PDF or any topic |
| 📝 **Summarize** | Get a concise bullet-point summary of your notes |
| ❓ **Quiz** | Auto-generate 10 multiple-choice questions |
| 🃏 **Flashcards** | Generate 10 Q&A cards for quick revision |

## Tech Stack

- **Streamlit** — UI & Frontend
- **Google Gemini 2.5 Flash** — AI model
- **PyMuPDF** — PDF parsing

## Getting Started

```bash
git clone https://github.com/Himanshu0730/Study-Buddy-IBM-internship.git
cd Study-Buddy-IBM-internship
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```
> Get your free key from [Google AI Studio](https://aistudio.google.com/)

```bash
streamlit run main.py
```

## Deployment

Deployed on Streamlit Cloud. API key is stored as a secret in the dashboard — never committed to the repo.

---

Built during IBM Internship · MIT License
