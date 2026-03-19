from retrieval.retriever import retrieve
from llm.models import llm


def answer_query(query):

    docs = retrieve(query)

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Use the context to answer the question.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    return response.content


while True:

    q = input("\nAsk question: ")

    if q == "exit":
        break

    answer = answer_query(q)

    print("\nAnswer:\n", answer)