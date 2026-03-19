from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from langsmith import traceable
from pydantic import BaseModel
from mistralai import Mistral
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


# Schema
class DetectCallResponse(BaseModel):
    is_question_ai: bool

class CodingAIResponse(BaseModel):
    answer: str

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    
# ---------------- DETECT QUERY ----------------

@traceable(name="detect_query")
def detect_query(state: State):

    user_message = state.get("user_message")

    SYSTEM_PROMPT = """
You are an AI assistant.
Detect if the user query is related to coding.

Return JSON with this exact field name:
{
"is_question_ai": true
}
"""

    response = client.chat.complete(
        model="mistral-large-latest",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    parsed = DetectCallResponse(**data)

    state["is_coding_question"] = parsed.is_question_ai

    return state


# ---------------- ROUTER ----------------

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:

    if state.get("is_coding_question"):
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# ---------------- SOLVE CODING ----------------
@traceable(name="solve_coding_question")
def solve_coding_question(state: State):
    user_message = state.get("user_message")
    
    SYSTEM_PROMPT = """
You are a coding assistant.
Solve the programming problem.

Return JSON:
{
"answer": "your answer"
}
"""

    response = client.chat.complete(
        model="mistral-large-latest",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    content = response.choices[0].message.content
    data = json.loads(content)

    parsed = CodingAIResponse(**data)

    state["ai_message"] = parsed.answer

    return state

# ---------------- SIMPLE CHAT ----------------

@traceable(name="solve_simple_question")
def solve_simple_question(state: State):

    user_message = state.get("user_message")

    SYSTEM_PROMPT = """
You are a friendly assistant.

Return JSON:
{
"answer": "response"
}
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    parsed = CodingAIResponse(**data)

    state["ai_message"] = parsed.answer

    return state


# ---------------- GRAPH ----------------
graph_builder = StateGraph(State)

graph_builder.add_node("detect_query",detect_query)
graph_builder.add_node("solve_coding_question",solve_coding_question)
graph_builder.add_node("solve_simple_question",solve_simple_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query",route_edge)

graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

def call_graph():

    state = {
        "user_message": "How are you buddy?",
        "ai_message": "",
        "is_coding_question": False
    }

    result = graph.invoke(state)

    print("Final Result:", result)


call_graph()