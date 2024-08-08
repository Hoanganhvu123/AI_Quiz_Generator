import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('E:\\chatbot\\AIQuizz\\.env')

# Set environment variables
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Retrieve and check environment variables
api_key = os.getenv('GROQ_API_KEY')

# Ensure they are all strings
if not all([api_key]):
    raise ValueError("One or more environment variables are not set or are empty")

# Print out the values to debug
print(f"API Key: {api_key}")