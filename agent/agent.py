"""
AI Agent for Mobile Analytics using LangGraph.

Usage:
    uv run python agent/agent.py --interactive
    uv run python agent/agent.py --query "What's total revenue?"
"""

import argparse
import sys
from pathlib import Path
from typing import Literal

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from agent.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from agent.prompts import SYSTEM_PROMPT
from agent.tools.snowflake_tools import query_snowflake
from agent.tools.kafka_tools import query_realtime_alerts


# Initialize LLM with tools
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL,
    temperature=OPENAI_TEMPERATURE,
)

# Bind tools to LLM
tools = [query_snowflake, query_realtime_alerts]
llm_with_tools = llm.bind_tools(tools)


# Define agent state
class AgentState(MessagesState):
    """State for the agent, includes message history."""
    pass


# Define nodes
def call_model(state: AgentState):
    """Call the LLM to decide next action."""
    messages = state["messages"]

    # Add system prompt if not present
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Determine if we should continue to tools or end."""
    messages = state["messages"]
    last_message = messages[-1]

    # If LLM made a tool call, continue to tools
    if last_message.tool_calls:
        return "tools"

    # Otherwise, end
    return "__end__"


# Build the graph
def create_agent():
    """Create the agent graph."""

    # Create tool node
    tool_node = ToolNode(tools)

    # Build graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    # Compile with memory
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# Create global agent instance
agent = create_agent()


def chat(message: str, thread_id: str = "default") -> str:
    """
    Send a message to the agent and get a response.

    Args:
        message: User's question
        thread_id: Conversation thread ID for memory

    Returns:
        Agent's response text
    """
    config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    # Get the last message (agent's response)
    return result["messages"][-1].content


def interactive_mode():
    """Run agent in interactive CLI mode."""
    print("\n" + "=" * 60)
    print("Ameno Technologies - Mobile Analytics AI Agent")
    print("=" * 60)
    print(f"Model: {OPENAI_MODEL}")
    print("Type 'quit' to exit, 'new' for new conversation")
    print("=" * 60 + "\n")

    thread_id = "interactive_1"
    thread_count = 1

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            if user_input.lower() == "new":
                thread_count += 1
                thread_id = f"interactive_{thread_count}"
                print(f"\n--- New conversation (thread: {thread_id}) ---")
                continue

            print("\nAgent: ", end="", flush=True)
            response = chat(user_input, thread_id)
            print(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def single_query(query: str):
    """Run a single query and print result."""
    print(f"\nQuery: {query}\n")
    print("-" * 40)
    response = chat(query, "single_query")
    print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mobile Analytics AI Agent")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--query", "-q", type=str, help="Single query mode")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.query:
        single_query(args.query)
    else:
        # Default to interactive
        interactive_mode()
