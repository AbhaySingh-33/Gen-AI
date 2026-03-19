from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser




load_dotenv()

print("🚀 Starting RAG PDF Chatbot...")

# 2. PDF Load + Chunking
print("📄 Loading PDF...")

pdf_path = Path(__file__).parent / "Backend Basics.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()  # pure pages

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)
chunks = text_splitter.split_documents(docs)
print(f"✅ {len(chunks)} chunks created")

# 3. Embeddings + Vector Store
print("🔍 Creating embeddings & vector store...")
embeddings = MistralAIEmbeddings(model="mistral-embed")
vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 4. Mistral LLM + RAG Chain
print("🤖 Setting up Mistral LLM & RAG chain...")
llm = ChatMistralAI(model="mistral-large-latest")

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Use ONLY the context below to answer.

Context: {context}

Question: {question}

Answer precisely based on the context. If you don't know, say you don't know.
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("✅ RAG Pipeline ready! Ask your questions...")

# 5. Interactive Chat Loop (YAHAN EXECUTE HOGA)
while True:
    query = input("\n❓ your question  (type 'quit' to exit) ")
    if query.lower() == 'quit':
        break
    
    result = rag_chain.invoke(query)
    print(f"\n💬 Answer: {result}\n")

print("👋 Chatbot closed. Goodbye!")