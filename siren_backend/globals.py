from dotenv import load_dotenv
import os

load_dotenv()

google_API_key = os.getenv("GOOGLE_API_KEY")

gemini_API_key = os.getenv("GEMINI_API_KEY")