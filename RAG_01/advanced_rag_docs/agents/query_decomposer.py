from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm.models import llm

prompt = PromptTemplate(
    template="""
Break the user question into smaller independent questions.

User Question:
{query}

Return each question on a new line.
""",
    input_variables=["query"]
)

chain = prompt | llm | StrOutputParser()


def decompose_query(query):

    result = chain.invoke({"query": query})

    sub_queries = [
        q.strip()
        for q in result.split("\n")
        if q.strip()
    ]

    return sub_queries