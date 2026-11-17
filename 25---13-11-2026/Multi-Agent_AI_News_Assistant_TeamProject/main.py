
from typing import TypedDict, Optional, Any

from langgraph.graph import StateGraph, START, END

from agents.research_agent import research_node
from agents.summarizer_agent import summarizer_node
from agents.notifier_agent import notifier_node


# --------------------------------------------------
# 1. Define the shared state used by all three agents
# --------------------------------------------------

class NewsState(TypedDict, total=False):
    topic: str

    research_results: Optional[dict]
    summary: Optional[dict]

    notification: Optional[str]
    notification_path: Optional[str]

    status: str
    error: Optional[str]

    notification_status: Optional[str]
    notification_error: Optional[str]


# --------------------------------------------------
# 2. Conditional routing functions
# --------------------------------------------------

def route_after_research(state: NewsState):
    """Continue only if the Research Agent succeeds."""

    if state.get("status") == "success":
        return "continue"

    return "stop"


def route_after_summarizer(state: NewsState):
    """Continue only if the Summarizer Agent succeeds."""

    if state.get("status") == "success":
        return "continue"

    return "stop"


# --------------------------------------------------
# 3. Build the LangGraph workflow
# --------------------------------------------------

def build_workflow():

    workflow = StateGraph(NewsState)

    # Register all three agents as nodes
    workflow.add_node("research", research_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("notifier", notifier_node)

    # Starting point
    workflow.add_edge(START, "research")

    # Research -> Summarizer (conditional)
    workflow.add_conditional_edges(
        "research",
        route_after_research,
        {
            "continue": "summarizer",
            "stop": END
        }
    )

    # Summarizer -> Notifier (conditional)
    workflow.add_conditional_edges(
        "summarizer",
        route_after_summarizer,
        {
            "continue": "notifier",
            "stop": END
        }
    )

    # Notifier -> End
    workflow.add_edge("notifier", END)

    return workflow.compile()


# --------------------------------------------------
# 4. Execute the complete AI News Assistant
# --------------------------------------------------

def run_news_assistant(topic: str):

    print("\n" + "=" * 60)
    print("          MULTI-AGENT AI NEWS ASSISTANT")
    print("=" * 60)

    print(f"\nTechnology Topic: {topic}")

    # Initialize graph
    app = build_workflow()

    # Initial shared state
    initial_state: NewsState = {
        "topic": topic,
        "status": "pending"
    }

    # Execute all agents through LangGraph
    final_state = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("                  EXECUTION RESULT")
    print("=" * 60)

    # Research result
    research_output = final_state.get("research_results")

    if research_output:
        print("\n[AGENT 1: RESEARCH AGENT]")

        if research_output.get("status") == "success":
            findings = research_output.get("findings", [])
            print(f"Research completed successfully.")
            print(f"Articles collected: {len(findings)}")
        else:
            print("Research failed.")
            print("Error:", research_output.get("error"))

    # Summary result
    summary_output = final_state.get("summary")

    if summary_output:
        print("\n[AGENT 2: SUMMARIZER AGENT]")

        if final_state.get("status") == "success":
            print("Summary generated successfully.")

            for index, point in enumerate(
                summary_output.get("summary", []), start=1
            ):
                print(f"\n{index}. {point}")

            print("\nSources:")
            for source in summary_output.get("sources", []):
                print(source)

        else:
            print("Summarization failed.")
            print("Error:", final_state.get("error"))

    # Notification result
    print("\n[AGENT 3: NOTIFIER AGENT]")

    if final_state.get("notification_status") == "success":

        print("Employee notification generated successfully.")

        print("\nSaved File:")
        print(final_state.get("notification_path"))

        print("\nGenerated Email:")
        print("-" * 60)
        print(final_state.get("notification", ""))

    else:
        print("Notification generation failed.")
        print(final_state.get("notification_error", "No error details available."))

    print("\n" + "=" * 60)
    print("                 WORKFLOW COMPLETED")
    print("=" * 60)

    return final_state


# --------------------------------------------------
# 5. Main entry point
# --------------------------------------------------

if __name__ == "__main__":

    print("\nWelcome to Multi-Agent AI News Assistant!")

    topic = input(
        "\nEnter a technology topic to research: "
    ).strip()

    if not topic:
        print("\nError: Please enter a valid technology topic.")

    else:
        try:
            run_news_assistant(topic)

        except Exception as e:
            print("\nWorkflow execution failed.")
            print("Error:", str(e))
