from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm.models import llm
from config.settings import TOPICS
import time

prompt = PromptTemplate(
    template="""
Classify the following text into one of these topics:

{topics}

Text:
{text}

Return only the topic name.
""",
    input_variables=["text", "topics"]
)

chain = prompt | llm | StrOutputParser()


def classify_chunk(chunk):

    text = chunk.page_content[:1000]

    time.sleep(1)  # Rate limiting: 1 second delay between API calls
    
    topic = chain.invoke({
        "text": text,
        "topics": ",".join(TOPICS)
    })

    topic = topic.strip().lower()

    if topic not in TOPICS:
        topic = "general"

    return topic