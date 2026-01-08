from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import asyncio
import threading
import pandas as pd

load_dotenv()

# ------------------------------
# Global caches
# ------------------------------
_agent = None
_client = None
_loop = None
_loop_thread = None


def _start_background_loop():
    """Start a dedicated asyncio event loop in a background thread."""
    global _loop, _loop_thread

    if _loop is None:
        _loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(_loop)
            _loop.run_forever()

        _loop_thread = threading.Thread(target=run_loop, daemon=True)
        _loop_thread.start()


async def _get_agent_async():
    """Async initialization of agent and MCP tools (runs once)."""
    global _agent, _client

    if _agent is not None:
        return _agent

    #MCP client
    _client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["servers/mcp-math-server.py"],
            },
            "mysql": {
                "transport": "stdio",
                "command": "python",
                "args": ["servers/mcp-mysql-server.py"],
            },
        }
    )

    #Gemini LLM
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables")

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=api_key,
        temperature=0.1,
        max_tokens=1000,
        timeout=30,
    )

    #MCP tools
    tools = await _client.get_tools()

    #Agent
    _agent = create_agent(model, tools)

    return _agent

def extract_final_answer(result):
    for msg in reversed(result["messages"]):
        if msg.__class__.__name__ == "ToolMessage":
            content = msg.content

            # Case 1: Table-like (list of dicts)
            if isinstance(content, list) and all(isinstance(row, dict) for row in content):
                return {"type": "table", "data": pd.DataFrame(content)}

            # Case 2: Bullet points (list of strings)
            elif isinstance(content, list):
                bullet_points = [part["text"] for part in content if "text" in part]
                return {"type": "bullet", "data": bullet_points}

            # Case 3: Plain text
            return {"type": "text", "data": str(content)}

    return {"type": "text", "data": "No result returned."}

async def _ask_agent_async(user_prompt: str) -> str:
    agent = await _get_agent_async()

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )

    final_text = extract_final_answer(result)

    print("\n================ FINAL ANSWER ================\n")
    print(final_text)
    print("\n=============================================\n")

    return final_text


def ask_agent_sync(user_prompt: str) -> str:
    """
    Safe synchronous wrapper for Streamlit.
    Uses a background event loop (NO asyncio.run()).
    """
    _start_background_loop()

    future = asyncio.run_coroutine_threadsafe(
        _ask_agent_async(user_prompt), _loop
    )

    return future.result()
