import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="AI College Syllabus Assistant",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI College Syllabus Assistant")
st.write(
    "Your AI-powered learning companion for explanations, "
    "exam preparation, summaries and MCQs."
)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "API key not found. Add GEMINI_API_KEY to your .env file "
        "and restart the application."
    )
    st.stop()

client = genai.Client(api_key=api_key)

# Sidebar settings
st.sidebar.header("Study Settings")

subject = st.sidebar.selectbox(
    "Select subject",
    [
        "Artificial Intelligence",
        "Data Structures",
        "Database Management Systems",
        "Operating Systems",
        "Computer Networks",
        "Other",
    ],
)

answer_level = st.sidebar.selectbox(
    "Explanation level",
    ["Beginner", "Intermediate", "Exam-oriented"],
)

answer_length = st.sidebar.selectbox(
    "Answer format",
    ["Short", "Detailed", "5-mark answer", "10-mark answer"],
)

mode = st.sidebar.selectbox(
    "Choose a feature",
    [
        "Ask a Question",
        "Summarize Notes",
        "Generate MCQs",
        "Compare Prompts",
    ],
)

st.sidebar.caption("Powered by a Large Language Model (LLM)")

# Main inputs
notes = st.text_area(
    "Paste your syllabus or class notes (optional)",
    height=150,
    placeholder="Paste your syllabus or notes here...",
)

if mode == "Ask a Question":
    task = st.text_area(
        "Enter your question",
        placeholder="Example: Explain A* search with an example.",
        height=100,
    )

elif mode == "Summarize Notes":
    task = st.text_area(
        "What topic should be summarized?",
        placeholder="Example: Summarize the A* search algorithm.",
        height=100,
    )

elif mode == "Generate MCQs":
    task = st.text_area(
        "Enter the topic for MCQs",
        placeholder="Example: Generate questions on intelligent agents.",
        height=100,
    )

else:
    task = st.text_area(
        "Enter the topic to compare prompts on",
        placeholder="Example: Explain the A* search algorithm.",
        height=100,
    )


def build_prompt(style):
    context = notes.strip() or "No reference notes were provided."

    if style == "Detailed":
        format_instruction = "Give a detailed explanation with examples."
    elif style == "5-mark answer":
        format_instruction = (
            "Write an exam-ready 5-mark answer with a definition, "
            "key points and an example."
        )
    elif style == "10-mark answer":
        format_instruction = (
            "Write a structured 10-mark answer with an introduction, "
            "detailed explanation, example and conclusion."
        )
    else:
        format_instruction = "Give a concise answer with key points."

    if mode == "Summarize Notes":
        action = (
            "Summarize the requested topic from the reference notes. "
            "Highlight definitions, key concepts and important points."
        )
    elif mode == "Generate MCQs":
        action = (
            "Generate five multiple-choice questions on the requested "
            "topic. Give four options per question, the correct answer "
            "and a short explanation."
        )
    else:
        action = "Answer the student's question accurately."

    return f"""
You are an educational AI assistant for college students.

SUBJECT: {subject}
STUDENT LEVEL: {answer_level}
REQUESTED FORMAT: {style}

REFERENCE NOTES:
{context}

STUDENT REQUEST:
{task}

INSTRUCTIONS:
1. {action}
2. {format_instruction}
3. Explain technical terms clearly.
4. Use headings and numbered points where helpful.
5. Do not invent facts or claim that information appears in
   the notes when it does not.
6. If reference notes are supplied, prioritize them.
   If the answer is not supported by the notes, say so clearly.
7. If no notes are supplied, answer using general subject knowledge
   and indicate when a detail should be verified.
8. Keep the answer relevant to the student's request.
"""


def generate_answer(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text or "The model returned an empty response."


if st.button("Generate Answer", type="primary"):
    if not task.strip():
        st.warning("Please enter a question or topic first.")
    else:
        try:
            with st.spinner("Generating your answer..."):
                if mode == "Compare Prompts":
                    basic_prompt = (
                        f"Explain {task} in the subject {subject} "
                        "in a few simple sentences."
                    )
                    engineered_prompt = build_prompt(answer_length)

                    left, right = st.columns(2)

                    with left:
                        st.subheader("Prompt A: Basic")
                        st.code(basic_prompt, language="text")
                        st.markdown(generate_answer(basic_prompt))

                    with right:
                        st.subheader("Prompt B: Engineered")
                        st.code(engineered_prompt, language="text")
                        st.markdown(generate_answer(engineered_prompt))

                    st.info(
                        "Compare accuracy, relevance, structure and "
                        "clarity. The engineered prompt gives the model "
                        "more specific instructions."
                    )

                else:
                    prompt = build_prompt(answer_length)
                    answer = generate_answer(prompt)

                    st.subheader("AI Response")
                    st.markdown(answer)

                    st.download_button(
                        "Download Answer",
                        data=answer,
                        file_name="study_answer.txt",
                        mime="text/plain",
                    )

        except Exception as error:
            st.error(
                "The AI request failed. Check your internet connection, "
                "API key, API quota and model availability."
            )
            st.caption(f"Technical details: {error}")

st.divider()
st.caption(
    "AI-generated answers can contain mistakes. "
    "Verify important facts with your official course materials."
)