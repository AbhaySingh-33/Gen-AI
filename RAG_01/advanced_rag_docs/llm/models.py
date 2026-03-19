import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_mistralai import MistralAIEmbeddings

load_dotenv()

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0
)

embeddings = MistralAIEmbeddings(
    model="mistral-embed"
)