from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm.models import llm

prompt = PromptTemplate(
    template="""
Generate 3 search queries similar to:

{query}

Return one query per line.
""",
    input_variables=["query"]
)

chain = prompt | llm | StrOutputParser()


def generate_queries(query):

    result = chain.invoke({"query": query})

    queries = [q.strip() for q in result.split("\n") if q.strip()]

    return queries