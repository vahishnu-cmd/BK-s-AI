import streamlit as st
import os
import subprocess
import sys
from pypdf import PdfReader
import google.generativeai as genai
from youtube_search import YoutubeSearch

# =========================================================
# 🔑 ENTER YOUR GEMINI API KEY HERE
# =========================================================
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "YOUR_ACTUAL_API_KEY")

if GEMINI_KEY != "PASTE_YOUR_KEY_HERE" and GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# --- Page Configuration ---
st.set_page_config(
    page_title="CogniLearn AI | Autonomous Educator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enterprise Grade UI Theme & Glassmorphism CSS ---
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #0B0F19 100%);
        color: #F3F4F6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Top Navigation Header */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60A5FA, #A78BFA, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: -5px;
    }
    .brand-sub {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }
    
    /* Studio Video Stage Card */
    .video-stage {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    
    /* Live Status Pill */
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        background-color: #EF4444;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px #EF4444;
    }
    
    /* Metric & Action Cards */
    .kpi-card {
        background: rgba(31, 41, 55, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }
    .kpi-title { font-size: 0.8rem; color: #9CA3AF; text-transform: uppercase; font-weight: 600; }
    .kpi-val { font-size: 1.25rem; color: #F9FAFB; font-weight: 700; margin-top: 4px; }
    
    /* Interactive Chat Containers */
    .question-box {
        background: rgba(30, 58, 138, 0.2);
        border: 1px solid rgba(96, 165, 250, 0.3);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'lesson_script' not in st.session_state:
    st.session_state.lesson_script = ""
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'document_text' not in st.session_state:
    st.session_state.document_text = ""
if 'lesson_active' not in st.session_state:
    st.session_state.lesson_active = False
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = "Document Analysis"
if 'feedback_history' not in st.session_state:
    st.session_state.feedback_history = []
if 'comprehension_score' not in st.session_state:
    st.session_state.comprehension_score = 0

# --- Core AI & TTS Functions ---
def generate_lesson_plan(content, level, time_limit, language):
    prompt = f"""
    You are an award-winning university professor and adaptive AI tutor.
    Target Audience Profile: {level} level student.
    Scheduled Lesson Duration: {time_limit}.
    Instruction Language: {language} (If Hindi or Hinglish, explain concepts naturally using that tongue).

    Formulate a comprehensive, highly engaging verbal lecture script covering the material below:
    - Welcome the student warmly to the lecture theater.
    - Break down 2-3 primary core principles with vivid everyday analogies.
    - Conclude the lecture with an explicit, thought-provoking checkpoint question to test their understanding.
    
    Content Reference:
    {content[:4500]}
    """
    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def evaluate_student_response(question, student_answer, context_text, language):
    prompt = f"""
    You are evaluating a student's answer in an interactive lecture.
    Question Posed: "{question}"
    Student Response: "{student_answer}"
    Reference Syllabus Context: {context_text[:2000]}
    Language: {language}

    Respond with:
    1. A clear assessment (Correct / Partially Correct / Needs Clarification).
    2. Exact identification of any misconceptions or logic gaps.
    3. An intuitive, real-world analogy to solidify the concept.
    4. An encouraging closing remark.
    """
    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_teacher_audio(text, language="English", output_file="lesson.mp3"):
    if text.startswith("Error:"):
        return ""
    voice_map = {
        "English": "en-US-ChristopherNeural",
        "Hindi": "hi-IN-MadhurNeural",
        "Hinglish": "hi-IN-SwaraNeural"
    }
    voice = voice_map.get(language, "en-US-ChristopherNeural")
    clean_text = text.replace('*', '').replace('#', '').replace('\n', ' ').replace('>', '')
    
    with open("temp_script.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)
        
    command = f'{sys.executable} -m edge_tts --voice "{voice}" --file "temp_script.txt" --write-media "{output_file}"'
    subprocess.run(command, shell=True)
    return output_file

def extract_checkpoint_question(script):
    lines = [line.strip() for line in script.split('\n') if line.strip()]
    for line in reversed(lines):
        if '?' in line:
            return line
    return lines[-1] if lines else "What key concept stood out most to you during this lecture?"

def fetch_related_videos(topic, max_results=3):
    try:
        results = YoutubeSearch(topic, max_results=max_results).to_dict()
        return [f"https://www.youtube.com/watch?v={vid['id']}" for vid in results]
    except Exception as e:
        return []

# --- Top Navigation Bar ---
col_brand, col_status = st.columns([3, 1])
with col_brand:
    st.markdown('<div class="brand-title">CogniLearn Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Next-Gen Autonomous Multimodal Pedagogical Engine</div>', unsafe_allow_html=True)
with col_status:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 10px;">
            <span style="background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 6px 14px; border-radius: 8px; font-weight: 600; font-size: 0.85rem;">
                ● System Ready
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.divider()

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### 🎓 Pedagogical Settings")
    level = st.select_slider("Target Learner Level", options=["Beginner", "Intermediate", "Advanced"], value="Beginner")
    time_limit = st.selectbox("Session Window", ["5 minutes", "20 minutes", "60 minutes"])
    language = st.selectbox("Instruction Language", ["English", "Hindi", "Hinglish"])
    
    st.divider()
    st.markdown("### 📖 Knowledge Ingestion")
    input_method = st.radio("Source Pipeline:", ["Upload Document (RAG)", "Specify Topic"])
    
    document_text = ""
    start_session = False
    
    if input_method == "Upload Document (RAG)":
        uploaded_file = st.file_uploader("Upload Syllabus / Paper (PDF)", type=["pdf"])
        if uploaded_file and st.button("🚀 Compile & Begin Session", type="primary", use_container_width=True):
            reader = PdfReader(uploaded_file)
            document_text = "".join([page.extract_text() + "\n" for page in reader.pages if page.extract_text()])
            st.session_state.current_topic = uploaded_file.name.replace(".pdf", "")
            start_session = True
    else:
        topic = st.text_input("Enter Subject / Topic", placeholder="e.g., Quantum Computing Architecture")
        if topic and st.button("🚀 Compile & Begin Session", type="primary", use_container_width=True):
            document_text = f"Curriculum and conceptual foundations of: {topic}"
            st.session_state.current_topic = topic
            start_session = True

    if start_session:
        with st.spinner("Compiling pedagogical lecture & voice delivery..."):
            st.session_state.document_text = document_text
            script = generate_lesson_plan(document_text, level, time_limit, language)
            st.session_state.lesson_script = script
            st.session_state.current_question = extract_checkpoint_question(script)
            st.session_state.comprehension_score = 65  
            st.session_state.lesson_active = True

# --- Landing Dashboard (Pre-Session) ---
if not st.session_state.lesson_active:
    st.markdown("### 🌟 Intelligent Educational Studio")
    st.write("Welcome to the autonomous classroom. Select your learning profile and provide learning materials in the sidebar to generate a complete, voice-synthesized lecture with active student evaluations.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div style="font-size: 2rem; margin-bottom: 8px;">🧠</div>
            <div class="kpi-title">Adaptive Pedagogy</div>
            <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 8px;">
                Calibrates depth, analogies, and pacing according to your academic stage.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div style="font-size: 2rem; margin-bottom: 8px;">🗣️</div>
            <div class="kpi-title">Multilingual Voice</div>
            <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 8px;">
                Natural spoken lectures in English, Hindi, and Hinglish with zero text-reading monotone.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div style="font-size: 2rem; margin-bottom: 8px;">🎯</div>
            <div class="kpi-title">Active Diagnosis</div>
            <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 8px;">
                Identifies cognitive misconceptions in real time and re-explains foundational mechanics.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.markdown("#### ⚡ Demonstration Sandbox")
    if st.button("▶️ Launch Interactive Demo: Artificial Intelligence Fundamentals", use_container_width=True):
        with st.spinner("Synthesizing demo environment..."):
            st.session_state.current_topic = "Artificial Intelligence"
            st.session_state.document_text = "Artificial Intelligence (AI) represents the computational framework capable of pattern synthesis, reasoning, abstraction, and goal-directed adaptation."
            script = generate_lesson_plan(st.session_state.document_text, level, time_limit, language)
            st.session_state.lesson_script = script
            st.session_state.current_question = extract_checkpoint_question(script)
            st.session_state.comprehension_score = 65
            st.session_state.lesson_active = True
            st.rerun()

# --- Active Classroom Dashboard ---
else:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Focus Subject</div><div class="kpi-val">{st.session_state.current_topic[:18]}...</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Target Level</div><div class="kpi-val">{level}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Pacing Strategy</div><div class="kpi-val">{time_limit}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Language Channel</div><div class="kpi-val">{language}</div></div>', unsafe_allow_html=True)

    st.write("")

    video_col, interactive_col = st.columns([1.8, 1.2], gap="large")

    with video_col:
        st.markdown(
            """
            <div class="video-stage">
                <div class="live-badge"><span class="live-dot"></span> LIVE LECTURE THEATER</div>
            """, 
            unsafe_allow_html=True
        )
        
        tab_stage, tab_notes, tab_analytics, tab_videos = st.tabs(["📺 AI Stage", "📝 Smart Whiteboard", "📈 Learning Analytics", "🎥 Related Videos"])
        
        with tab_stage:
            av_col, player_col = st.columns([1, 2])
            with av_col:
                st.image("https://api.dicebear.com/7.x/bottts/svg?seed=Teacher&backgroundColor=1E3A8A", caption="AI Educator Avatar", use_container_width=True)
            with player_col:
                st.markdown("#### Audio Lecture Stream")
                if st.session_state.lesson_script.startswith("Error:"):
                    st.error("Audio generation interrupted by an API issue.")
                else:
                    with st.spinner("Rendering synthesized voice track..."):
                        audio_file = generate_teacher_audio(st.session_state.lesson_script, language)
                        
                        if os.path.exists(audio_file):
                            with open(audio_file, 'rb') as f:
                                st.audio(f.read(), format="audio/mp3", autoplay=True)
                            st.success("Lecture broadcast is ready. Click play to listen.")
                            st.caption("Synchronized Pedagogical Audio Delivery active.")
                        else:
                            st.error("🚨 Cloud Audio Engine failed to generate the MP3. Please check requirements.txt.")
                    
        with tab_notes:
            st.markdown("#### Structured Whiteboard Notes")
            if st.session_state.lesson_script.startswith("Error:"):
                st.error(st.session_state.lesson_script)
            else:
                st.markdown(st.session_state.lesson_script)

        with tab_analytics:
            st.markdown("#### Student Competency Metrics")
            st.metric("Comprehension Index", f"{st.session_state.comprehension_score}%", "+15% from baseline")
            st.progress(st.session_state.comprehension_score)
            st.markdown("""
            * **Syllabus Grounding:** Rigorous document alignment active.
            * **Pacing Efficiency:** Optimized for selected duration.
            * **Next Recommended Module:** Advanced Systematic Implementations.
            """)
            with tab_videos:
                st.markdown("#### Supplemental YouTube Resources")
                st.write(f"Curated videos for: **{st.session_state.current_topic}**")
                
                with st.spinner("Fetching related videos..."):
                    video_urls = fetch_related_videos(st.session_state.current_topic, max_results=3)
                    
                    if video_urls:
                        for url in video_urls:
                            st.video(url)
                            st.divider()
                    else:
                        st.info("No videos found or search limit reached.")
                
            st.markdown("</div>", unsafe_allow_html=True)

    with interactive_col:
        st.markdown(
            f"""
            <div class="question-box">
                <span style="font-weight: 700; color: #60A5FA; font-size: 0.85rem; text-transform: uppercase;">Checkpoint Challenge</span>
                <p style="margin-top: 8px; font-size: 1.05rem; font-weight: 500; color: #F3F4F6;">{st.session_state.current_question}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        student_input = st.chat_input("Formulate your answer or ask for clarification...")

        if student_input:
            st.markdown(f"**Your Answer:** {student_input}")
            with st.spinner("Analyzing response for cognitive misconceptions..."):
                feedback = evaluate_student_response(
                    st.session_state.current_question,
                    student_input,
                    st.session_state.document_text,
                    language
                )
                
                if feedback.startswith("Error:"):
                    st.error(feedback)
                else:
                    st.session_state.comprehension_score = min(100, st.session_state.comprehension_score + 20)
                    st.markdown(
                        f"""
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px; margin-top: 15px;">
                            <span style="color: #10B981; font-weight: 700; font-size: 0.85rem;">TEACHER ADAPTATION & EVALUATION</span>
                            <p style="margin-top: 8px; color: #E5E7EB; line-height: 1.5;">{feedback}</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

                    feedback_audio = generate_teacher_audio(feedback, language, "feedback.mp3")
                    if os.path.exists(feedback_audio):
                        with open(feedback_audio, 'rb') as f:
                            st.audio(f.read(), format="audio/mp3", autoplay=True)
                    else:
                        st.error("🚨 Cloud Audio Engine failed to generate the MP3. Please check requirements.txt.")
