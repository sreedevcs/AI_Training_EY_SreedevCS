
import os
import re

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

MAX_RESULTS = 8


def get_tavily_client():

    api_key = os.getenv("TAVILY_API_KEY")

    if api_key:
        print("[Agent 1] Using Tavily API key.")
        return TavilyClient(api_key=api_key)

    print("[Agent 1] Using Tavily keyless mode.")
    return TavilyClient()


def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def search_articles(query):

    print("[Agent 1] Connecting to Tavily Search...")

    client = get_tavily_client()

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=MAX_RESULTS,
        topic="news"
    )

    results = response.get("results", [])

    if not results:
        raise ValueError("Tavily returned no search results.")

    return results


def research_topic(topic):

    print("\n[Agent 1] Research Agent Started")

    try:

        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Technology topic cannot be empty.")

        topic = topic.strip()

        print(f"[Agent 1] Researching: {topic}")

        search_query = f"Latest developments and news about {topic}"

        results = search_articles(search_query)

        findings = []
        seen_urls = set()

        for result in results:

            title = clean_text(result.get("title", ""))

            description = clean_text(
                result.get("content", "")
            )

            source_url = result.get("url", "")

            published_date = result.get(
                "published_date",
                "Not provided"
            )

            if not title or not description or not source_url:
                continue

            if not source_url.startswith(("https://", "http://")):
                continue

            if source_url in seen_urls:
                continue

            seen_urls.add(source_url)

            findings.append({
                "title": title,
                "description": description,
                "source_url": source_url,
                "published_date": published_date
            })

        if not findings:
            raise ValueError("No usable research findings collected.")

        output = {
            "topic": topic,
            "findings": findings,
            "status": "success",
            "error": None
        }

        print(
            f"[Agent 1] Collected {len(findings)} research findings."
        )

        print("[Agent 1] Research Completed Successfully")

        return output

    except Exception as e:

        print(f"[Agent 1] Error: {str(e)}")

        return {
            "topic": topic if isinstance(topic, str) else "",
            "findings": [],
            "status": "error",
            "error": str(e)
        }


def research_node(state):

    topic = state.get("topic", "")

    result = research_topic(topic)

    return {
        "research_results": result,
        "status": result["status"],
        "error": result["error"]
    }


if __name__ == "__main__":

    topic = input("Enter technology topic to research: ")

    research_output = research_topic(topic)

    print("\n========== RESEARCH OUTPUT ==========")

    print("Topic:", research_output["topic"])
    print("Status:", research_output["status"])

    if research_output["status"] == "success":

        for index, finding in enumerate(
            research_output["findings"], start=1
        ):

            print(f"\nArticle {index}")
            print("Title:", finding["title"])
            print("Description:", finding["description"])
            print("Source:", finding["source_url"])
            print("Published Date:", finding["published_date"])

    else:

        print("Error:", research_output["error"])
