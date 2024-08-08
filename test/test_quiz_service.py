# test_quiz_service.py
import unittest
from src.quiz_service import QuizService
from src.config import PROVIDERS
from dotenv import load_dotenv
import os
from src.question_model import Question

# Load .env file
load_dotenv('E:\\chatbot\\AIQuizz\\.env')

# Set environment variables
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

class TestQuizService(unittest.TestCase):
    def setUp(self):
        self.provider = "OpenAI"
        self.model = "gpt-3.5-turbo"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.temperature = 0.7
        self.quiz_service = QuizService(api_key=self.api_key, model=self.model, provider=self.provider, temperature=self.temperature)

    def test_generate_questions(self):
        text = "Python is a high-level, interpreted programming language."
        num_questions = 3
        questions = self.quiz_service.generate_questions(text, num_questions)

        self.assertEqual(len(questions), num_questions)
        for question in questions:
            self.assertIsInstance(question, Question)
            self.assertIsInstance(question.question, str)
            self.assertIsInstance(question.options, dict)
            self.assertIsInstance(question.correct_answer, str)
            self.assertIsInstance(question.explanation, str)

if __name__ == "__main__":
    unittest.main()