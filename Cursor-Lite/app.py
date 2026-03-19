import json
import os
import re
import subprocess
from ddgs import DDGS
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=api_key)
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_files": self.list_files,
            "delete_file": self.delete_file,
            "search_code": self.search_code,
            "run_command": self.run_command,
            "google_search": self.google_search,
        }
        self.system_prompt = """
You are a coding agent like Cursor AI.

Available tools:
- read_file(path) - read a file
- write_file({"path": "...", "content": "..."}) - write/create a file
- list_files(path) - list files in a directory
- delete_file(path) - delete a file
- search_code(keyword) - search for keyword in code files
- run_command(command) - run a terminal command
- google_search(query) - search the web via DuckDuckGo

RULES:
- Always respond with ONLY a single valid JSON object. No extra text.
- You may only use these step values: "plan", "action", "output"
- Do NOT return a step called "observe" - tool results will be provided to you automatically.
- After receiving a tool result, decide: run another action OR give the final output.
- When the task is fully complete, return {"step": "output", ...} with a clear summary.

JSON format:
{"step": "plan"|"action"|"output", "content": "...", "function": "tool_name_or_empty", "input": "input_or_empty"}

Examples:

User: List project files
Agent: {"step": "plan", "content": "I will list all files in the current directory", "function": "", "input": ""}
Agent: {"step": "action", "content": "", "function": "list_files", "input": "."}
[System injects tool result]
Agent: {"step": "output", "content": "The project contains: app.py, ui.py, requirements.txt", "function": "", "input": ""}

User: Create hello.py with print hello
Agent: {"step": "action", "content": "", "function": "write_file", "input": {"path": "hello.py", "content": "print('hello')"}}
[System injects tool result]
Agent: {"step": "output", "content": "Created hello.py with print('hello')", "function": "", "input": ""}

User: Read and summarise app.py
Agent: {"step": "action", "content": "", "function": "read_file", "input": "app.py"}
[System injects file content]
Agent: {"step": "output", "content": "app.py contains ...", "function": "", "input": ""}
"""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def read_file(self, path):
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            return str(e)

    def write_file(self, params):
        try:
            if isinstance(params, dict):
                path = params.get("path")
                content = params.get("content", "")
            else:
                return "Error: write_file needs path and content"
            with open(path, "w") as f:
                f.write(content)
            return "File written successfully"
        except Exception as e:
            return str(e)

    def list_files(self, path="."):
        try:
            return os.listdir(path)
        except Exception as e:
            return str(e)

    def delete_file(self, path):
        try:
            os.remove(path)
            return "File deleted successfully"
        except Exception as e:
            return str(e)

    def search_code(self, keyword):
        results = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".py") or file.endswith(".js"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", errors="ignore") as f:
                            if keyword in f.read():
                                results.append(path)
                    except:
                        pass
        return results

    def run_command(self, command):
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

    def google_search(self, query):
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(
                    query,
                    max_results=5,
                    region="wt-wt",
                    safesearch="off",
                    backend="auto",
                ):
                    results.append({
                        "title": r.get("title"),
                        "link": r.get("href"),
                        "snippet": r.get("body"),
                    })
            if not results:
                return "No results found."
            return results
        except Exception as e:
            return f"Error: {e}"

    def _parse_output(self, text):
        """Parse JSON from model response, stripping markdown fences if present."""
        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        return json.loads(cleaned)

    def process_message(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        max_steps = 50  # prevent infinite loops
        for _ in range(max_steps):
            response = self.client.chat.complete(
                model="codestral-latest",
                messages=self.messages
            )

            output_text = response.choices[0].message.content

            try:
                output = self._parse_output(output_text)
            except Exception as parse_err:
                return {"error": f"Failed to parse response: {parse_err}", "raw": output_text}

            self.messages.append({"role": "assistant", "content": output_text})

            step = output.get("step")

            if step == "action":
                tool_name = output.get("function")
                tool_input = output.get("input")
                if tool_name in self.tools:
                    result = self.tools[tool_name](tool_input)
                    observe_msg = (
                        f"Tool '{tool_name}' returned the following result:\n{result}\n\n"
                        f"Now decide: if more actions are needed continue with the next action, "
                        f"otherwise return the final output JSON."
                    )
                    self.messages.append({"role": "user", "content": observe_msg})
                else:
                    return {"error": f"Unknown tool: {tool_name}"}

            elif step == "output":
                return output

            else:
                # plan step — nudge toward action
                self.messages.append({"role": "user", "content": "Good plan. Now execute the next action JSON."})


        return {"error": "Agent did not produce an output after max steps."}

if __name__ == "__main__":
    agent = Agent()
    print("Cursor-Lite Agent (CLI Mode)")
    print("Type 'exit' to quit\n")
    
    while True:
        user = input("> ")
        if user.lower() == "exit":
            break
        
        result = agent.process_message(user)
        
        if "error" in result:
            print("❌", result["error"])
        elif result.get("step") == "plan":
            print("🧠", result.get("content"))
        elif result.get("step") == "action":
            print("⚙️", f"{result.get('function')} -> {result.get('result')}")
        elif result.get("step") == "output":
            print("🤖", result.get("content"))
