from duckduckgo_search import DDGS

def generate_lesson_plan(document_text, level, time_limit, language):
    """Generates the structured lesson script using free cloud AI (No API Key)."""
    prompt = f"""
    You are an expert AI Teacher. 
    Act as a human educator. I have uploaded learning material.
    Student Profile: {level} level. 
    Available Time: {time_limit}.
    Language: {language}.
    
    Based ONLY on the material provided below, generate a lesson script. 
    Do not output a list. Output a natural conversational script that a teacher would speak out loud to explain the core concepts.
    At the very end of the script, ask ONE interactive checkpoint question to test understanding.
    
    Material: {document_text[:3000]} # Keeping it slightly shorter for free endpoints
    """
    
    # This calls a free AI endpoint silently!
    response = DDGS().chat(prompt, model="gpt-4o-mini")
    return response

def evaluate_student_response(question, student_answer, context_text):
    """Evaluates the answer and detects misconceptions using free AI."""
    prompt = f"""
    You are an AI Teacher. You asked your student this question: "{question}"
    The student answered: "{student_answer}"
    
    1. Determine if the answer is correct based on this context: {context_text[:1500]}
    2. If incorrect, IDENTIFY THE MISCONCEPTION. Do not just say "wrong". 
    3. Re-explain the concept using a simple analogy.
    4. Speak directly to the student in a supportive tone.
    """
    
    # Call the free endpoint again for evaluation
    response = DDGS().chat(prompt, model="gpt-4o-mini")
    return response