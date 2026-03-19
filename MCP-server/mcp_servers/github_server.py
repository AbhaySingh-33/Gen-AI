import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp.server.fastmcp import FastMCP
import requests
from config.settings import GITHUB_TOKEN

server = FastMCP("github-server")

BASE_URL = "https://api.github.com"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


@server.tool()
def get_repo(owner: str, repo: str):
    """Get repository details"""

    url = f"{BASE_URL}/repos/{owner}/{repo}"

    res = requests.get(url, headers=headers)

    return res.json()


@server.tool()
def list_repo_files(owner: str, repo: str):
    """List files in repository"""

    url = f"{BASE_URL}/repos/{owner}/{repo}/contents"

    res = requests.get(url, headers=headers)

    files = [f["name"] for f in res.json()]

    return files


@server.tool()
def create_issue(owner: str, repo: str, title: str, body: str):
    """Create GitHub issue"""

    url = f"{BASE_URL}/repos/{owner}/{repo}/issues"

    data = {
        "title": title,
        "body": body
    }

    res = requests.post(url, headers=headers, json=data)

    return res.json()


if __name__ == "__main__":
    server.run(transport="stdio")