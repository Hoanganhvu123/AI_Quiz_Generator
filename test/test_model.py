# quiz_service.py
from typing import List
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from src.question_model import Question
import json
import re
import logging
from dotenv import load_dotenv
import os
import logging
from langchain_groq import ChatGroq

class QuizService:
    def __init__(self, llm):
        self.llm = llm

        self.question_template = """
        Generate {num_questions} multiple-choice questions based on the following text:
        Text: {text}
        Your response MUST be in JSON format as follows:
        [
            {{
                "question": "The question text here",
                "options": {{
                    "A": "Option A text", 
                    "B": "Option B text",
                    "C": "Option C text",
                    "D": "Option D text"  
                }},
                "correct_answer": "The correct answer letter (A, B, C, or D)",
                "explanation": "A brief explanation of the correct answer"
            }},
            ...
        ]
        Ensure you generate exactly {num_questions} questions.
        """
        self.question_prompt = PromptTemplate(
            input_variables=["text", "num_questions"],
            template=self.question_template,
        )

 
    def generate_questions(self, text: str, num_questions: int = 10) -> List[Question]:
        """
        Generate a list of multiple-choice questions based on the given text.

        This method uses an LLM (Large Language Model) to generate a specified number
        of multiple-choice questions from the provided text. The result from the LLM is expected
        to be in JSON format. The method processes the output to extract and parse the JSON,
        and then converts the parsed JSON into a list of `Question` objects.

        Args:
            text (str): The input text from which to generate questions.
            num_questions (int, optional): The number of questions to generate. Defaults to 10.

        Returns:
            List[Question]: A list of `Question` objects generated from the input text.

        Raises:
            ValueError: If the JSON output from the LLM is invalid or cannot be parsed.
            Exception: For any other general errors during the question generation process.

        Process:
            1. Invoke the LLM with the provided text and number of questions using a prompt template.
            2. Capture the raw output from the LLM, which is expected to include JSON-formatted questions.
            3. Locate the start and end of the JSON content within the raw output.
            4. Extract the JSON content, ignoring any additional text before or after the JSON.
            5. Parse the JSON string into a list of dictionaries.
            6. Convert the parsed JSON into a list of `Question` objects.
            7. Handle any potential errors, such as invalid JSON or other exceptions, and log them for debugging.

        Example:
            >>> text = "Python is a high-level, interpreted programming language."
            >>> num_questions = 5
            >>> questions = generate_questions(text, num_questions)
            >>> for question in questions:
            >>>     print(question.question)
            >>>     for option, answer in question.options.items():
            >>>         print(f"{option}: {answer}")
            >>>     print(f"Correct Answer: {question.correct_answer}")
            >>>     print(f"Explanation: {question.explanation}")
        """
        questions = []
        try:
            chain = LLMChain(llm=self.llm, prompt=self.question_prompt)
            result = chain.run(text=text, num_questions=num_questions)
            logging.info(f"Raw result from LLMChain: {result}")

            # Loại bỏ các đoạn văn bản không mong muốn trước khi JSON thực sự bắt đầu
            json_start_index = result.find("[")
            json_end_index = result.rfind("]") + 1
            if json_start_index == -1 or json_end_index == -1:
                raise ValueError("No valid JSON found in the output.")

            result = result[json_start_index:json_end_index]

            parsed_questions = json.loads(result)
            questions = [Question.from_dict(q) for q in parsed_questions[:num_questions]]

        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error. Content: {result}")
            raise ValueError(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            logging.error(f"General Exception. Error details: {str(e)}")
            raise Exception(f"Error generating questions: {str(e)}")

        return questions




# Load .env file
load_dotenv('E:\\chatbot\\AIQuizz\\.env')

# Set environment variables
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")

# Logging configuration
logging.basicConfig(level=logging.INFO)

def main():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or not isinstance(api_key, str):
        raise ValueError("GROQ_API_KEY is not set or is not a string")

    temperature = 0.7
    model = "llama3-70b-8192"

    # Initialize the LLM (Groq in this case)
    llm = ChatGroq(temperature=temperature, groq_api_key=api_key, model_name=model)

    # Initialize QuizService with the chosen LLM
    quiz_service = QuizService(llm=llm)

    text = "Python is a high-level, interpreted programming language. It is known for its simple and readable syntax, making it a popular choice for beginners and experienced programmers alike. Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. With its extensive standard library and vast ecosystem of third-party packages, Python is widely used for web development, data analysis, artificial intelligence, and more."
    num_questions = 5

    print(f"Generating {num_questions} questions based on the following text:")
    print(text)
    print()

    questions = quiz_service.generate_questions(text, num_questions)

    for i, question in enumerate(questions, start=1):
        print(f"Question {i}: {question.question}")
        for option, text in question.options.items():
            print(f"{option}. {text}")
        print(f"Correct Answer: {question.correct_answer}")
        print(f"Explanation: {question.explanation}")
        print()

if __name__ == "__main__":
    main()