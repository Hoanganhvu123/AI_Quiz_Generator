import streamlit as st
from src.quiz_service import QuizService
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import PyPDF2
import io
from src.config import PROVIDERS
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_llm(provider: str, model: str, api_key: str, temperature: float):
    """Khởi tạo LLM dựa trên nhà cung cấp và mô hình đã chọn"""
    if provider == "OpenAI":
        return ChatOpenAI(temperature=temperature, model_name=model, api_key=api_key)
    elif provider == "Google":
        return ChatGoogleGenerativeAI(temperature=temperature, model=model, google_api_key=api_key)
    elif provider == "Anthropic":
        return ChatAnthropic(temperature=temperature, model=model, anthropic_api_key=api_key)
    elif provider == "Groq":
        return ChatGroq(temperature=temperature, model_name=model, groq_api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def main():
    st.set_page_config(page_title="AI-Generated English Quiz", page_icon="🎓")
    st.title("AI-Generated English Quiz")

    # Sidebar for model selection and API key input
    with st.sidebar:
        st.header("Configuration")
        provider = st.selectbox("Select Provider", list(PROVIDERS.keys()))
        selected_model = st.selectbox("Select Model", PROVIDERS[provider])
        api_key = st.text_input(f"Enter {provider} API Key", type="password")
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    if not api_key:
        st.warning("Please enter an API key to continue.")
        return

    # Initialize LLM and QuizService with user-provided configuration
    llm = initialize_llm(provider, selected_model, api_key, temperature)
    quiz_service = QuizService(llm=llm)

    num_questions = st.slider("Number of questions", min_value=1, max_value=20, value=10)

    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf'])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            text_input = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text_input = ""
            for page in pdf_reader.pages:
                text_input += page.extract_text()
        st.text_area("File content", text_input, height=200)
    else:
        text_input = st.text_area("Or enter text for quiz generation", height=200)

    if st.button("Generate Questions"):
        if not text_input:
            st.error("Please enter some text or upload a file.")
        else:
            with st.spinner("Generating questions..."):
                try:
                    logging.info(f"Attempting to generate questions with text: {text_input[:100]}...")  # Log first 100 chars
                    questions = quiz_service.generate_questions(text_input, num_questions)
                    st.session_state.questions = questions
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.success("Questions generated successfully!")
                except Exception as e:
                    logging.error(f"Error occurred while generating questions: {str(e)}")
                    st.error(f"An error occurred while generating questions: {str(e)}")
                    logging.exception("Full traceback:")  # This will log the full traceback

    if 'questions' in st.session_state and st.session_state.questions:
        st.markdown("---")  # Add a separator line for clarity

        question = st.session_state.questions[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")
        st.progress((st.session_state.current_question + 1) / len(st.session_state.questions))
        st.write(question.question)

        answer = st.radio("Choose your answer:", list(question.options.items()), format_func=lambda x: f"{x[0]}. {x[1]}")

        st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)  # Add spacing between options and buttons

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("Previous Question"):
                if st.session_state.current_question > 0:
                    st.session_state.current_question -= 1

        with col2:
            if st.button("Submit"):
                if answer[0] == question.correct_answer:
                    st.success("Correct! 🎉")
                    st.session_state.score += 1
                else:
                    st.error(f"Incorrect. The correct answer is {question.correct_answer}.")
                st.info(f"Explanation: {question.explanation}")

        with col3:
            if st.button("Next Question"):
                if st.session_state.current_question < len(st.session_state.questions) - 1:
                    st.session_state.current_question += 1
                else:
                    st.success(f"Quiz completed! Your score: {st.session_state.score}/{len(st.session_state.questions)}")
                    if st.button("Restart Quiz"):
                        del st.session_state.questions
                        del st.session_state.current_question
                        del st.session_state.score

