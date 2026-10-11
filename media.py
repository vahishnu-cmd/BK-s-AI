import subprocess
import os
import streamlit as st

def generate_teacher_audio(text, language="English", output_file="lesson.mp3"):
    """
    Generates high-quality natural voice audio using edge-tts.
    Supports the multilingual requirement seamlessly.
    """
    voice_map = {
        "English": "en-US-ChristopherNeural", # Professional male voice
        "Hindi": "hi-IN-MadhurNeural",       # Natural Hindi voice
        "Hinglish": "hi-IN-SwaraNeural"      # Good for mixed language
    }
    voice = voice_map.get(language, "en-US-ChristopherNeural")
    
    # Run edge-tts via command line to avoid complex async loops in Streamlit
    command = f'edge-tts --voice "{voice}" --text "{text}" --write-media "{output_file}"'
    subprocess.run(command, shell=True)
    return output_file

def render_avatar_video(audio_file_path, on_screen_text):
    """
    Renders a dynamic visual component mimicking an AI video presentation.
    """
    st.markdown(f"### 📺 Lesson Visuals")
    st.info(on_screen_text) # Subject-aware on-screen text 
    if os.path.exists(audio_file_path):
        st.audio(audio_file_path, format="audio/mp3", autoplay=True)