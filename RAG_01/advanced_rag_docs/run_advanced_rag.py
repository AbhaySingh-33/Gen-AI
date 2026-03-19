from retrieval.advanced_retriever import retrieve_advanced
from llm.models import llm


def answer_query(query):
    docs = retrieve_advanced(query)

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""Answer the question using the context.

Context:
{context}

Question:
{query}

Answer clearly.
"""

    response = llm.invoke(prompt)

    return response.content


while True:
    query = input("\nAsk question: ")

    if query == "exit":
        break

    answer = answer_query(query)

    print("\nAnswer:\n", answer)
