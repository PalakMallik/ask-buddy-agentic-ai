
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_core.messages import AIMessageChunk
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from datetime import date

# ==========================================
# ENVIRONMENT VARIABLES
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# ==========================================
# LLM
# ==========================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    streaming=True
)


# ==========================================
# GOOGLE SEARCH TOOL
# ==========================================

search = GoogleSerperAPIWrapper()

search_tool = Tool(
    name="google_search",
    func=search.run,
    description=(
        "Google Search tool for retrieving current and verified "
        "information. You MUST call this tool whenever the user "
        "asks about the current age of a living person, current "
        "office holders, recent events, latest news, current "
        "statistics, prices or time-sensitive information. "
        "This requirement also applies to follow-up questions, "
        "even when relevant information exists in conversation "
        "memory. Never rely solely on old conversation context "
        "for time-sensitive facts. Include relevant source URLs."
    )
)


# ==========================================
# MEMORY
# ==========================================

memory = InMemorySaver()

# Tracks conversations initialized in the current process.
initialized_threads = set()


TODAY = date.today().strftime("%B %d, %Y")

# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = f"""
You are Ask Buddy, an intelligent, friendly and helpful AI assistant.

CURRENT DATE: {TODAY}

IMPORTANT INSTRUCTIONS:

1. Always be aware of the current date.
2. Never use outdated dates or years in your answers.
3. Use Google Search whenever current information is required.
4. ALWAYS search Google when users ask about:
   - Current age of a living person.
   - Current political office holders.
   - Latest news and developments.
   - Current prices and statistics.
   - Recent events and achievements.
5. Even if the answer appears in previous conversation
   history, search again when the information is time-sensitive.
6. When a user asks a follow-up question, use previous
   conversation context to understand the reference.
7. Calculate someone's age using their verified date
   of birth and the CURRENT DATE.
8. Never blindly copy an age mentioned in an old article.
9. Include relevant source URLs in your answers.
10. Never invent facts, dates or sources.
11. If information cannot be verified, say so clearly.

Be conversational, accurate, informative and concise.
"""


# ==========================================
# CREATE AI AGENT
# ==========================================

agent = create_agent(
    model=llm,
    tools=[search_tool],
    checkpointer=memory,
    system_prompt=SYSTEM_PROMPT
)


# ==========================================
# HELPER FUNCTION
# ==========================================

def extract_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )

    return ""


# ==========================================
# STREAM AI RESPONSE
# ==========================================

def stream_response(history: list[dict], conversation_id: int):

    thread_id = str(conversation_id)

    # Restore full database history when a thread
    # has not yet been initialized in this process.
    if thread_id in initialized_threads:

        input_messages = [
            {
                "role": history[-1]["role"],
                "content": history[-1]["content"]
            }
        ]

    else:

        input_messages = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in history
        ]

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Stream agent output
    for chunk, metadata in agent.stream(
        {"messages": input_messages},
        config=config,
        stream_mode="messages"
    ):

        # Only display AI-generated text, not tool output.
        if metadata.get("langgraph_node") != "model":
            continue

        if isinstance(chunk, AIMessageChunk):

            text = extract_text(chunk.content)

            if text:
                yield text

    initialized_threads.add(thread_id)


# ==========================================
# NON-STREAMING COMPATIBILITY
# ==========================================

def generate_response(
    history: list[dict],
    conversation_id: int = 0
) -> str:

    return "".join(
        stream_response(history, conversation_id)
    )
