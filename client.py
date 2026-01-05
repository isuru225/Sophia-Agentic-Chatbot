from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# Global agent cache (initialized once, reused for efficiency)
_agent = None
_client = None

async def get_agent():
    """
    Initialize and return the agent with MCP tools.
    Uses caching to avoid re-initializing on every call.
    """
    global _agent, _client
    
    if _agent is None:
        # Step 1: Initialize MCP Client (connects to math and mysql servers)
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
                    "args": ["servers/mcp-mysql-server.py"]
                }
            }
        )
        
        # Step 2: Initialize LLM (Gemini model)
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",  # Using supported model
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
            max_tokens=1000,
            timeout=30
        )
        
        # Step 3: Get tools from MCP servers
        tools = await _client.get_tools()
        
        # Step 4: Create agent with LLM and tools
        _agent = create_agent(model, tools)
    
    return _agent

async def ask_agent(user_prompt: str) -> str:
    """
    Process a user query through the LLM agent.
    
    Flow:
    1. User prompt comes in
    2. Agent (LLM) analyzes the prompt
    3. Agent decides if tools are needed (MySQL, Math, etc.)
    4. If tools needed, agent calls them via MCP
    5. Agent processes tool results and generates final answer
    6. Returns the response text
    
    Args:
        user_prompt: The user's question/request
        
    Returns:
        The agent's response as a string
    """
    agent = await get_agent()
    
    # Invoke agent with user message
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_prompt}]}
    )
    
    # Extract the final response text from the agent's messages
    return response["messages"][-1].content

# Sync wrapper for Streamlit (which doesn't handle async directly)
def ask_agent_sync(user_prompt: str) -> str:
    """Synchronous wrapper for ask_agent - use this from Streamlit"""
    return asyncio.run(ask_agent(user_prompt))

async def main():
    """Original main function for testing"""
    mysql_response = await ask_agent("Give me the order numbers of salesman Jagath")
    print("MySQL response: ", mysql_response)

if __name__ == "__main__":
    asyncio.run(main())