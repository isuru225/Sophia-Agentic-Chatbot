# Query Flow Explanation: How User Queries Reach the LLM

## 📊 Architecture Overview

```
User (Streamlit UI) 
    ↓
app.py (Streamlit Interface)
    ↓
ask_agent_sync() [Sync wrapper]
    ↓
ask_agent() [Async function]
    ↓
get_agent() [Initializes agent if needed]
    ↓
LangChain Agent (create_agent)
    ↓
┌─────────────────────────────────────┐
│   LLM (Gemini 2.0 Flash)            │
│   + MCP Tools (MySQL, Math)         │
└─────────────────────────────────────┘
    ↓
Response back through the chain
```

## 🔄 Detailed Step-by-Step Flow

### Step 1: User Input (Streamlit UI)
- User types a question in the Streamlit text input field
- Example: "Give me the order numbers of salesman Jagath"
- Location: `app.py` - User interface

### Step 2: Streamlit Captures Input
- When user clicks "Send", Streamlit calls `ask_agent_sync(user_input)`
- Location: `app.py` line 59-64

### Step 3: Sync Wrapper (ask_agent_sync)
- Streamlit doesn't handle async directly, so we use a sync wrapper
- This function runs `asyncio.run(ask_agent(user_prompt))`
- Location: `client.py` - `ask_agent_sync()` function

### Step 4: Async Agent Call (ask_agent)
- The actual async function that processes the query
- Gets the agent instance (initialized once, cached for efficiency)
- Calls `agent.ainvoke()` with the user message
- Location: `client.py` - `ask_agent()` function

### Step 5: Agent Initialization (get_agent)
- **First time only**: Initializes the agent
- Creates `MultiServerMCPClient` to connect to MCP servers (MySQL, Math)
- Initializes the LLM model (Gemini 2.0 Flash)
- Gets tools from MCP servers (execute_sql, add, multiply, etc.)
- Creates the LangChain agent with model + tools
- **Subsequent calls**: Reuses cached agent (faster)
- Location: `client.py` - `get_agent()` function

### Step 6: LLM Processing (Inside LangChain Agent)
The LangChain agent orchestrates this flow:

1. **LLM Receives User Query**
   - The Gemini model receives: "Give me the order numbers of salesman Jagath"

2. **LLM Decides if Tools are Needed**
   - LLM analyzes the query
   - Determines: "This needs database access → use MySQL tool"

3. **LLM Calls Tool (if needed)**
   - LLM generates a tool call: `execute_sql(query="SELECT ord_no FROM Orders JOIN Salesman...")`
   - Agent executes the tool via MCP client
   - MCP client communicates with `mcp-mysql-server.py` via stdio
   - MySQL server executes SQL and returns results

4. **LLM Processes Tool Results**
   - LLM receives SQL results from MySQL tool
   - LLM formats the response in natural language
   - LLM may call multiple tools if needed (e.g., Math + MySQL)

5. **LLM Generates Final Response**
   - LLM creates the final answer: "The order numbers for salesman Jagath are: 70001, 70009, ..."
   - Response is returned to the agent

### Step 7: Response Returns
- Agent returns response dictionary: `{"messages": [...]}`
- `ask_agent()` extracts the text: `response["messages"][-1].content`
- Returns string to `ask_agent_sync()`
- Returns string to Streamlit

### Step 8: Display in UI
- Streamlit receives the response string
- Adds it to chat history
- Displays in the UI as a bot message bubble
- Location: `app.py` - Chat display section

## 🛠️ Key Components

### 1. MultiServerMCPClient
- Manages connections to multiple MCP servers (MySQL, Math)
- Handles stdio communication with server processes
- Provides tools to the LangChain agent

### 2. LangChain Agent (create_agent)
- Orchestrates the conversation flow
- Decides when to use tools
- Manages the conversation state

### 3. LLM (Gemini 2.0 Flash)
- Understands natural language queries
- Generates tool calls when needed
- Formats final responses

### 4. MCP Tools
- **MySQL Tool**: `execute_sql` - Runs SQL queries
- **Math Tools**: `add`, `multiply` - Performs calculations
- Each tool is provided by an MCP server process

## 🔍 Example Flow for "Give me the order numbers of salesman Jagath"

1. User types: "Give me the order numbers of salesman Jagath"
2. Streamlit → `ask_agent_sync()`
3. `ask_agent_sync()` → `ask_agent()` (async)
4. `ask_agent()` → gets agent (initialized if first time)
5. Agent receives query → LLM processes it
6. LLM decides: "Need MySQL tool to query database"
7. LLM generates SQL: `SELECT ord_no FROM Orders JOIN Salesman WHERE Salesman.FirstName = 'Jagath'`
8. Agent calls MySQL tool via MCP client
9. MCP client → MySQL server process → executes SQL
10. MySQL server → returns results: `[70001, 70009, ...]`
11. Results → back to LLM
12. LLM formats response: "The order numbers for salesman Jagath are: 70001, 70009, ..."
13. Response → back through chain → Streamlit UI
14. User sees the answer in the chat interface

## 💡 Important Notes

- **Agent is cached**: Initialized once, reused for all queries (efficient)
- **Tools are discovered dynamically**: MCP servers provide tools at runtime
- **Async handling**: Streamlit uses sync wrapper, but actual logic is async
- **Error handling**: If LLM can't find tools or encounters errors, it will explain to the user
- **Conversation context**: Currently each query is independent (no conversation memory)

## 🚀 Running the Application

```bash
# Terminal 1: Run Streamlit UI
streamlit run app.py

# The MCP servers are automatically started by MultiServerMCPClient
# No need to run them manually!
```

The flow is now fully integrated and ready to use!

