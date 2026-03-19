import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    
    PDF_PATH = "data/document.pdf"

settings = Settings()
