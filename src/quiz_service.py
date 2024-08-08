# from typing import List, Any, Dict, Optional
# from langchain.chat_models.base import BaseChatModel
# from langchain.schema import HumanMessage, AIMessage
# from langchain.prompts import ChatPromptTemplate
# import json
# import re
# import requests
# from src.question_model import Question
# from src.config import API_CONFIGS
# from pydantic import Field



# class GenericChatModel(BaseChatModel):
#     api_key: str = Field(..., description="API key for the model")
#     model: str = Field(..., description="Model name")
#     provider: str = Field(..., description="Provider name")
#     base_url: str = Field(..., description="Base URL for API requests")
#     temperature: float = Field(default=0.7, description="Temperature for text generation")

#     class Config:
#         arbitrary_types_allowed = True

#     def __init__(self, **data):
#         super().__init__(**data)
#         self.base_url = API_CONFIGS[self.provider]["api_base"]

#     def _generate(self, messages: List[Any], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> Dict[str, Any]:
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }
        
#         formatted_messages = self._format_messages(messages)
        
#         data = {
#             "model": self.model,
#             "messages": formatted_messages,
#             "temperature": self.temperature
#         }
        
#         if self.provider == "Google":
#             data = {
#                 "contents": [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in formatted_messages],
#             }
#             url = f"{self.base_url}{self.model}:generateContent"
#         else:
#             url = self.base_url

#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
        
#         if self.provider == "Google":
#             content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
#         elif self.provider == "Anthropic":
#             content = response.json()["content"][0]["text"]
#         else:
#             content = response.json()["choices"][0]["message"]["content"]

#         return {"generations": [{"text": content}]}

#     def _format_messages(self, messages: List[Any]) -> List[Dict[str, str]]:
#         formatted_messages = []
#         for message in messages:
#             if isinstance(message, HumanMessage):
#                 formatted_messages.append({"role": "user", "content": message.content})
#             elif isinstance(message, AIMessage):
#                 formatted_messages.append({"role": "assistant", "content": message.content})
#             else:
#                 formatted_messages.append({"role": "system", "content": message.content})
#         return formatted_messages

#     def _llm_type(self) -> str:
#         return self.provider.lower()
    

# class QuizService:
#     def __init__(self, api_key: str, model: str, provider: str, temperature: float):
#         self.model = model
#         self.provider = provider
#         self.api_key = api_key
#         self.temperature = temperature
#         self.llm = GenericChatModel(
#             api_key=self.api_key, 
#             model=self.model, 
#             provider=self.provider, 
#             temperature=self.temperature
#         )

#         self.question_template = """
#         Generate {num_questions} multiple-choice questions based on the following text:
#         Text: {text}
#         Your response MUST be in JSON format as follows:
#         [
#             {{
#                 "question": "The question text here",
#                 "options": {{
#                     "A": "Option A text", 
#                     "B": "Option B text",
#                     "C": "Option C text",
#                     "D": "Option D text"  
#                 }},
#                 "correct_answer": "The correct answer letter (A, B, C, or D)",
#                 "explanation": "A brief explanation of the correct answer"
#             }},
#             ...
#         ]
#         Ensure you generate exactly {num_questions} questions.
#         """
#         self.question_prompt = ChatPromptTemplate.from_template(self.question_template)

#     def generate_questions(self, text: str, num_questions: int = 10) -> List[Question]:
#         questions = []
#         try:
#             prompt = self.question_prompt.format_messages(text=text, num_questions=num_questions)[0].content
#             result = self.llm.generate([HumanMessage(content=prompt)])
#             result_content = result.generations[0][0].text

#             result_content = re.sub(r'^```json\s*|\s*```$', '', result_content.strip())
#             parsed_questions = json.loads(result_content)  
#             questions = [Question.from_dict(q) for q in parsed_questions[:num_questions]]
            
#         except json.JSONDecodeError as e:
#             raise ValueError(f"Error parsing JSON: {str(e)}")
#         except Exception as e:
#             raise Exception(f"Error generating questions: {self.provider} - {str(e)}")
        
#         return questions

# from typing import List
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_groq import ChatGroq
# from langchain.schema import HumanMessage
# from langchain.prompts import ChatPromptTemplate
# import json
# import re
# from src.question_model import Question
# from src.config import API_CONFIGS
# import logging
# import logging
# import json
# import re
# from typing import List, Any

# class QuizService:
#     def __init__(self, api_key: str, model: str, provider: str, temperature: float):
#         self.model = model
#         self.provider = provider
#         self.api_key = api_key
#         self.temperature = temperature
#         self.llm = self._initialize_llm()

#         self.question_template = """
#         Generate {num_questions} multiple-choice questions based on the following text:
#         Text: {text}
#         Your response MUST be in JSON format as follows:
#         [
#             {{
#                 "question": "The question text here",
#                 "options": {{
#                     "A": "Option A text", 
#                     "B": "Option B text",
#                     "C": "Option C text",
#                     "D": "Option D text"  
#                 }},
#                 "correct_answer": "The correct answer letter (A, B, C, or D)",
#                 "explanation": "A brief explanation of the correct answer"
#             }},
#             ...
#         ]
#         Ensure you generate exactly {num_questions} questions.
#         """
#         self.question_prompt = ChatPromptTemplate.from_template(self.question_template)

#     def _initialize_llm(self):
#         if self.provider == "OpenAI":
#             return ChatOpenAI(temperature=self.temperature, model_name=self.model, api_key=self.api_key)
#         elif self.provider == "Google":
#             return ChatGoogleGenerativeAI(temperature=self.temperature, model=self.model, google_api_key=self.api_key)
#         elif self.provider == "Anthropic":
#             return ChatAnthropic(temperature=self.temperature, model=self.model, anthropic_api_key=self.api_key)
#         elif self.provider == "Groq":
#             return ChatGroq(temperature=self.temperature, model_name=self.model, groq_api_key=self.api_key)
#         else:
#             raise ValueError(f"Unsupported provider: {self.provider}")
        
#     def _extract_content(self, result: Any) -> str:
#         if isinstance(result, str):
#             return result
#         elif isinstance(result, tuple):
#             return str(result[1]) if len(result) > 1 else str(result[0])
#         elif hasattr(result, 'generations'):
#             return result.generations[0][0].text
#         elif hasattr(result, 'content'):
#             return result.content
#         else:
#             return str(result)


   
    # def generate_questions(self, text: str, num_questions: int = 10) -> List[Question]:
    #     questions = []
    #     result = None
    #     result_content = None
    #     try:
    #         prompt = self.question_prompt.format_messages(text=text, num_questions=num_questions)[0].content
    #         logging.info(f"Generated prompt: {prompt}")
            
    #         result = self.llm.generate([HumanMessage(content=prompt)])
    #         logging.info(f"Raw result from LLM: {result}")
    #         logging.info(f"Type of result: {type(result)}")
            
    #         result_content = self._extract_content(result)
    #         logging.info(f"Extracted result_content: {result_content}")
            
    #         # Tìm và trích xuất phần JSON từ kết quả
    #         json_match = re.search(r'\[.*\]', result_content, re.DOTALL)
    #         if json_match:
    #             json_str = json_match.group()
    #             parsed_questions = json.loads(json_str)
    #             questions = [Question.from_dict(q) for q in parsed_questions[:num_questions]]
    #         else:
    #             raise ValueError("No JSON data found in the response")
            
    #     except json.JSONDecodeError as e:
    #         logging.error(f"JSON Decode Error. Content: {result_content}")
    #         raise ValueError(f"Error parsing JSON: {str(e)}")
    #     except Exception as e:
    #         logging.error(f"General Exception. Result: {result}")
    #         logging.error(f"Result content: {result_content}")
    #         logging.error(f"Error details: {str(e)}")
    #         raise Exception(f"Error generating questions: {self.provider} - {str(e)}")
        
    #     return questions
    

# quiz_service.py
from typing import List, Dict, Any
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from src.question_model import Question
import json
import re
import logging



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
        """
        questions = []
        try:
            chain = self.question_prompt | self.llm
            result = chain.invoke({"text": text, "num_questions": num_questions})

            # Trích xuất nội dung từ AIMessage
            result_content = result.content  # Lấy chuỗi văn bản từ đối tượng AIMessage
            logging.info(f"Raw result content: {result_content}")

            # Loại bỏ các đoạn văn bản không mong muốn trước khi JSON thực sự bắt đầu
            json_start_index = result_content.find("[")
            json_end_index = result_content.rfind("]") + 1
            if json_start_index == -1 or json_end_index == -1:
                raise ValueError("No valid JSON found in the output.")

            # Thực hiện phép toán cắt trên result_content thay vì trên result
            result_content = result_content[json_start_index:json_end_index]

            parsed_questions = json.loads(result_content)
            questions = [Question.from_dict(q) for q in parsed_questions[:num_questions]]

        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error. Content: {result_content}")
            raise ValueError(f"Error parsing JSON: {str(e)}")
        except Exception as e:
            logging.error(f"General Exception. Error details: {str(e)}")
            raise Exception(f"Error generating questions: {str(e)}")

        return questions
