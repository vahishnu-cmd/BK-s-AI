# 🎓 CogniLearn Studio
**Next-Gen Autonomous Multimodal Pedagogical Engine**

CogniLearn Studio is an enterprise-grade AI educational platform that transforms static documents into adaptive, voice-guided interactive lectures. Built for the AI Innovation Hackathon, this application bridges the gap between static text and active learning through real-time RAG processing, natural voice synthesis, and dynamic student evaluation.

## ✨ Key Features
* **🧠 Adaptive Pedagogical Engine:** Dynamically structures lesson depth, vocabulary, and pacing based on the selected academic profile (Beginner, Intermediate, Advanced).
* **🗣️ Multilingual Voice Synthesis:** Leverages neural text-to-speech pipelines (`edge-tts`) to deliver natural spoken lectures in **English**, **Hindi**, and **Hinglish**.
* **📚 Document Ingestion (RAG):** Automated PDF parsing for custom syllabus and textbook analysis alongside direct topic prompts.
* **🎯 Active Misconception Diagnosis:** Pauses the learning flow with interactive Q&A checkpoints, evaluating submissions, identifying logic gaps, and offering intuitive real-world analogies.
* **📊 Learning Analytics:** Real-time competency tracking and progress metrics displayed on a custom glassmorphic Streamlit dashboard.

## 🛠️ Tech Stack
* **Frontend & UI:** Streamlit (Python)
* **AI Core:** Google Gemini API (`gemini-3.6-flash`)
* **Audio Pipeline:** `edge-tts` (Configured for cloud-safe Linux execution)
* **Document Parsing:** `pypdf`

## 🚀 Live Demo
You can try the fully deployed application here:
**[Launch CogniLearn Studio](https://cognilearn-ai-teacher-jfnatcl5szmat3zwvrzf9u.streamlit.app/)**

## 💻 Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/tspratham09-hue/CogniLearn-AI-Teacher.git](https://github.com/tspratham09-hue/CogniLearn-AI-Teacher.git)
   cd CogniLearn-AI-Teacher
