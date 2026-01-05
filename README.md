# 🤖 Sophia – Agentic Chatbot

Sophia is an **agentic chatbot** built using **LangChain**, **Google Gemini**, and **Model Context Protocol (MCP)**.  
It can intelligently respond to user queries by accessing a **MySQL database**, performing **mathematical computations**, and maintaining **stateful conversations**.

---

## 🚀 Features

- 🧠 LLM-powered agent using **Google Gemini**
- 🗄️ Tool-based access to **MySQL database**
- ➗ Built-in **math tool** for calculations
- 💬 Context-aware, stateful conversations
- 🌐 Interactive **Streamlit UI**
- 🔄 Persistent MCP sessions
- ❌ Clean conversation termination (`/end`, `/quit`, `/bye`)

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangChain**
- **LangChain MCP Adapters**
- **Google Gemini (Generative AI)**
- **Streamlit**
- **MySQL**
- **Asyncio**

---

## 📁 Project Structure

Sophia-Agentic-Chatbot/
│
├── app.py                  # Streamlit frontend
├── client.py               # Agent, MCP, and async logic
├── .env                    # Environment variables
├── servers/
│   ├── mcp-math-server.py  # Math MCP server
│   └── mcp-mysql-server.py # MySQL MCP server
└── README.md

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_api_key_here

---

## 📦 Installation
1️⃣ Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux / macOS

2️⃣ Install dependencies
pip install \
  streamlit \
  python-dotenv \
  langchain \
  langchain-google-genai \
  langchain-mcp-adapters

▶️ Running the Application
streamlit run app.py

---

## Open your browser at:

http://localhost:8501

---

## 💬 Usage

Ask natural language questions

Query data from the MySQL database

Perform math calculations

Maintain conversational context automatically

End the conversation using:

/end
/quit
/bye