# LangGraph Workflow Project

This project showcases the creation and evolution of AI Agents using Python, the OpenAI API, and the LangGraph library. The file structure guides the user from a basic implementation of a ReAct (Reason and Act) pattern from scratch, to the development of complex workflows using persistence, search tools, and self-evaluation mechanisms.

## Project Contents

* **1.basic_agent_with_sequences.py**: Implements a basic ReAct agent by writing the core loop (Thought, Action, PAUSE, Observation) from scratch, using only the OpenAI API, without any external orchestrators.
* **2.langGraph_components.py**: Serves as an introduction to LangGraph. It creates an agent using `StateGraph`, defines execution nodes (llm, action), manages the state (`AgentState`), and integrates the `TavilySearch` tool.
* **3.agentic_search_tool.py**: A script focused on autonomous web information retrieval. It utilizes the Tavily API, the DuckDuckGo search engine (via the `ddgs` library), and BeautifulSoup for extracting (scraping) text from web pages.
* **3.persistence_and_streaming.py**: Extends the previous LangGraph agent by adding memory (persistence) using SQLite (`SqliteSaver` and `AsyncSqliteSaver`). It demonstrates how the agent can remember conversation history across different threads, as well as how to operate in both synchronous and asynchronous (streaming) modes.
* **lats.py**: Implements an advanced graph using a Generate-Reflect workflow. One agent node generates a text draft, and another node (Evaluator) evaluates it by scoring the text and providing feedback (via structured output with Pydantic). The graph repeats this process until the desired score is achieved or the retry limit is reached.
* **gemini.py**: Contains sample code for creating a similar agent using Google's Gemini models (e.g., `gemini-2.0-flash`) through the `google-genai` SDK.

## System Requirements

* **Python:** Version 3.13 and above.

## Installing Dependencies

All libraries are managed via the `pyproject.toml` file. If you use a package manager like `uv` or `pip`, you can install the dependencies directly from this file. Some of the key dependencies include:
* `langgraph`
* `langchain-openai`
* `langchain-tavily`
* `openai`
* `ddgs` (for DuckDuckGo search)
* `google-genai`
* `beautifulsoup4` (used as `bs4` for web scraping)

## Environment Variables

The scripts load environment variables using the `dotenv` library. To run the files locally, you need to create a `.env` file in the root directory and include the necessary API keys:

* `OPENAI_API_KEY`: For accessing OpenAI models (required in almost all files).
* `TAVILY_API_KEY`: For using the Tavily search agent.