import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool
from config.settings import MISTRAL_API_KEY, GITHUB_USERNAME


llm = ChatMistralAI(model="mistral-large-latest", api_key=MISTRAL_API_KEY)

VENV_PYTHON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".venv", "Scripts", "python.exe")


async def call_mcp_tool(script_path: str, tool_name: str, tool_args: dict):
    params = StdioServerParameters(command=VENV_PYTHON, args=[script_path])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result.content[0].text if result.content else ""


async def get_tools_from_server(script_path: str):
    params = StdioServerParameters(command=VENV_PYTHON, args=[script_path])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return result.tools


SERVER_MAP = {
    "list_files": "mcp_servers/filesystem_server.py",
    "read_file": "mcp_servers/filesystem_server.py",
    "write_file": "mcp_servers/filesystem_server.py",
    "get_repo": "mcp_servers/github_server.py",
    "list_repo_files": "mcp_servers/github_server.py",
    "create_issue": "mcp_servers/github_server.py",
}


async def ask_agent(prompt: str):
    fs_tools = await get_tools_from_server("mcp_servers/filesystem_server.py")
    gh_tools = await get_tools_from_server("mcp_servers/github_server.py")

    lc_tools = [
        StructuredTool.from_function(
            func=lambda **kwargs: kwargs,
            name=t.name,
            description=t.description or "",
            args_schema=t.inputSchema
        )
        for t in fs_tools + gh_tools
    ]

    messages = [HumanMessage(content=f"GitHub owner/username is '{GITHUB_USERNAME}'. {prompt}")]
    response = llm.bind_tools(lc_tools).invoke(messages)

    if response.tool_calls:
        for tool_call in response.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            script = SERVER_MAP.get(name)
            print(f"[calling tool: {name} with args: {args}]")
            tool_result = await call_mcp_tool(script, name, args)
            messages.append(response)
            messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

        final = llm.invoke(messages)
        return final.content

    return response.content


if __name__ == "__main__":
    query = input("Ask AI: ")
    res = asyncio.run(ask_agent(query))
    print("\n" + res)