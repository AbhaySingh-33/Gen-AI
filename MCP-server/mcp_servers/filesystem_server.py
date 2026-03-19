from mcp.server.fastmcp import FastMCP
import os

server = FastMCP("filesystem-server")

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@server.tool()
def list_files():
    """List files and folders in the project directory"""
    return "\n".join(os.listdir(BASE_PATH))

@server.tool()
def read_file(filename: str):
    """Read file content"""
    path = os.path.join(BASE_PATH, filename)

    with open(path, "r") as f:
        return f.read()

@server.tool()
def write_file(filename: str, content: str):
    """Write content to file"""
    path = os.path.join(BASE_PATH, filename)

    with open(path, "w") as f:
        f.write(content)

    return "file written successfully"


if __name__ == "__main__":
    server.run(transport="stdio")