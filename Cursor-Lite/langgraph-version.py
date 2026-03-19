import os
import json
import subprocess
import re
import time
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langsmith import traceable
from mistralai import Mistral
from ddgs import DDGS

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# =========================
# TOOLS
# =========================

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return str(e)


def write_file(params):
    try:
        path = params["path"]
        content = params.get("content", "")
        with open(path, "w") as f:
            f.write(content)
        return "File written successfully"
    except Exception as e:
        return str(e)


def list_files(path="."):
    try:
        return os.listdir(path)
    except Exception as e:
        return str(e)


def delete_file(path):
    try:
        os.remove(path)
        return "File deleted"
    except Exception as e:
        return str(e)


def search_code(keyword):
    results = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") or file.endswith(".js"):
                p = os.path.join(root, file)
                try:
                    with open(p, "r", errors="ignore") as f:
                        if keyword in f.read():
                            results.append(p)
                except:
                    pass
    return results


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return str(e)


def google_search(query):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append({
                    "title": r["title"],
                    "link": r["href"],
                    "snippet": r["body"]
                })
        return results
    except Exception as e:
        return str(e)


TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "delete_file": delete_file,
    "search_code": search_code,
    "run_command": run_command,
    "google_search": google_search
}

# =========================
# STATE
# =========================

class AgentState(TypedDict):
    messages: list
    step: str
    function: str
    input: str
    result: str
    output: str


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """You are a helpful AI assistant.

When you need to use a tool, respond with JSON:
{"step": "action", "function": "tool_name", "input": "tool_input", "content": "explanation"}

When providing final answer, respond with JSON:
{"step": "output", "content": "your answer"}

Available tools: read_file, write_file, list_files, delete_file, search_code, run_command, google_search
"""


# =========================
# PARSE OUTPUT
# =========================

def parse_json(text):
    try:
        cleaned = re.sub(r"```(?:json)?", "", text).strip()
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        return json.loads(cleaned)
    except:
        return {"step": "output", "content": text, "function": None, "input": None}


# =========================
# LLM NODE
# =========================

@traceable(name="agent_reasoning")
def agent_node(state: AgentState):

    messages = state["messages"]

    for attempt in range(3):
        try:
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=messages
            )
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(2 ** attempt)
            else:
                state["step"] = "output"
                state["output"] = f"Error: {str(e)}"
                return state

    text = response.choices[0].message.content

    data = parse_json(text)

    state["step"] = data.get("step", "output")
    state["function"] = data.get("function")
    state["input"] = data.get("input")
    state["output"] = data.get("content", text)

    return state


# =========================
# TOOL NODE
# =========================

@traceable(name="tool_execution")
def tool_node(state: AgentState):

    tool_name = state["function"]
    tool_input = state["input"]

    if tool_name not in TOOLS:
        result = "Unknown tool"
    else:
        result = TOOLS[tool_name](tool_input)

    state["result"] = result

    state["messages"].append({
        "role": "user",
        "content": f"Tool {tool_name} returned: {result}"
    })

    return state


# =========================
# ROUTER
# =========================

def router(state: AgentState):

    if state["step"] == "action" and state["function"]:
        return "tool"

    if state["step"] == "output":
        return "end"

    return "end"


# =========================
# GRAPH
# =========================

builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tool", tool_node)

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    router,
    {
        "tool": "tool",
        "agent": "agent",
        "end": END
    }
)

builder.add_edge("tool", "agent")

graph = builder.compile()


# =========================
# CLI
# =========================

def run_agent():

    state = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT}
        ],
        "step": "",
        "function": "",
        "input": "",
        "result": "",
        "output": ""
    }

    print("Cursor-Lite Agent (LangGraph Version)\n")

    while True:

        user = input("> ")

        if user == "exit":
            break

        state["messages"].append({
            "role": "user",
            "content": user
        })

        result = graph.invoke(state)

        print("\n🤖", result["output"], "\n")


if __name__ == "__main__":
    run_agent()