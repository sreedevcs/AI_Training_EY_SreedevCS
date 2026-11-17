
import os
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


# ==================================================
# 1. ENVIRONMENT CONFIGURATION
# ==================================================

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
MODEL = os.getenv("OPENROUTER_MODEL", MODEL)
if not API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in .env file"
    )


# ==================================================
# 2. EMAIL OUTPUT STRUCTURE
# ==================================================

class EmailDraft(BaseModel):

    subject: str = Field(
        description="Professional email subject line"
    )

    introduction: str = Field(
        description="Short professional email introduction"
    )

    closing: str = Field(
        description="Professional email closing"
    )


parser = PydanticOutputParser(
    pydantic_object=EmailDraft
)


# ==================================================
# 3. NOTIFIER AGENT
# ==================================================

class NotifierAgent:

    def __init__(self, output_dir="notifier/output"):

        # Initialize OpenRouter LLM

        self.llm = ChatOpenAI(
            model=MODEL,
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
            max_retries=2,
            timeout=60
        )

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Email generation prompt

        self.prompt = ChatPromptTemplate.from_messages([

            (
                "system",
                """
                You are a professional corporate email assistant.

                Your task is to prepare an employee notification
                about the latest technology developments.

                Follow these rules:

                1. Write in a professional business tone.
                2. Generate a relevant email subject.
                3. Write a concise introduction.
                4. Write a professional closing.
                5. Do not invent facts or source links.
                6. Do not modify the five research points.
                7. The five research points will be inserted separately.
                8. Do not generate the complete email.
                9. Return only the requested structured fields.

                {format_instructions}
                """
            ),

            (
                "human",
                """
                Technology Topic:

                {topic}

                Research Summary:

                {summary}

                Generate the email subject, introduction
                and closing.
                """
            )

        ])


    # ==================================================
    # 4. VALIDATE INPUT
    # ==================================================

    def validate_input(self, topic, summary_points):

        if not isinstance(topic, str) or not topic.strip():

            raise ValueError(
                "Technology topic cannot be empty."
            )

        if not isinstance(summary_points, list):

            raise ValueError(
                "Summary points must be a list."
            )

        if len(summary_points) != 5:

            raise ValueError(
                "Exactly five summary points are required."
            )

        for point in summary_points:

            if not isinstance(point, str) or not point.strip():

                raise ValueError(
                    "Summary points cannot be empty."
                )


    # ==================================================
    # 5. NORMALIZE AND VALIDATE SOURCE LINKS
    # ==================================================

    def validate_sources(self, sources):

        if not isinstance(sources, list):

            raise ValueError(
                "Sources must be provided as a list."
            )

        valid_sources = []
        seen_urls = set()

        for source in sources:

            # Agent 2 currently returns URLs as strings.
            # Also support dictionaries for flexibility.

            if isinstance(source, str):

                url = source.strip()

                parsed = urlparse(url)

                title = (
                    parsed.netloc
                    if parsed.netloc
                    else "Research Source"
                )

            elif isinstance(source, dict):

                url = source.get("url", "").strip()

                title = source.get(
                    "title",
                    "Research Source"
                ).strip()

                parsed = urlparse(url)

            else:
                continue

            if (
                parsed.scheme not in ("http", "https")
                or not parsed.netloc
            ):
                continue

            if url not in seen_urls:

                valid_sources.append({

                    "title": title or "Research Source",

                    "url": url

                })

                seen_urls.add(url)

        return valid_sources


    # ==================================================
    # 6. GENERATE EMAIL
    # ==================================================

    def generate_email(
        self,
        topic,
        summary_points,
        sources
    ):

        self.validate_input(
            topic,
            summary_points
        )

        valid_sources = self.validate_sources(
            sources
        )

        # Format five key points

        summary_text = "\n".join(

            f"{i + 1}. {point}"

            for i, point in enumerate(summary_points)

        )

        # Generate email subject, introduction and closing

        chain = self.prompt | self.llm | parser

        email_draft = chain.invoke({

            "topic": topic,

            "summary": summary_text,

            "format_instructions":
                parser.get_format_instructions()

        })

        # Build complete email

        email_content = f"""
==================================================
EMPLOYEE TECHNOLOGY NEWS NOTIFICATION
==================================================

Subject: {email_draft.subject}

Hello Team,

{email_draft.introduction}


LATEST TECHNOLOGY DEVELOPMENTS
--------------------------------------------------

{summary_text}


SOURCES
--------------------------------------------------
"""

        if valid_sources:

            for index, source in enumerate(
                valid_sources,
                start=1
            ):

                email_content += (

                    f"\n{index}. {source['title']}\n"

                    f"   {source['url']}\n"

                )

        else:

            email_content += (
                "\nNo valid source links were provided.\n"
            )

        email_content += f"""

{email_draft.closing}

Best Regards,
Technology News Assistant

==================================================
"""

        return email_content.strip()


    # ==================================================
    # 7. SAVE EMAIL TO TEXT FILE
    # ==================================================

    def save_notification(self, email_content):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            f"technology_news_{timestamp}.txt"
        )

        file_path = self.output_dir / filename

        try:

            file_path.write_text(
                email_content,
                encoding="utf-8"
            )

            return str(file_path.resolve())

        except OSError as error:

            raise RuntimeError(
                f"Unable to save notification: {error}"
            ) from error


    # ==================================================
    # 8. COMPLETE NOTIFIER WORKFLOW
    # ==================================================

    def run(
        self,
        topic,
        summary_points,
        sources
    ):

        print("\n[Agent 3] Notifier Agent Started")

        email_content = self.generate_email(
            topic,
            summary_points,
            sources
        )

        file_path = self.save_notification(
            email_content
        )

        print(
            "[Agent 3] Email notification generated."
        )

        print(
            "[Agent 3] Notification saved successfully."
        )

        return {

            "notification": email_content,

            "notification_path": file_path,

            "notification_status": "success"

        }


# ==================================================
# 9. LANGGRAPH-COMPATIBLE NODE
# ==================================================

def notifier_node(state):

    try:

        # Agent 2 returns:
        # {
        #     "summary": {
        #         "topic": "...",
        #         "summary": [...],
        #         "sources": [...]
        #     }
        # }

        summary_data = state.get("summary")

        if not isinstance(summary_data, dict):

            raise ValueError(
                "Summarizer Agent output is missing or invalid."
            )

        if state.get("status") == "error":

            raise ValueError(
                state.get(
                    "error",
                    "Summarizer Agent failed."
                )
            )

        topic = summary_data.get("topic", "")

        summary_points = summary_data.get(
            "summary", []
        )

        sources = summary_data.get(
            "sources", []
        )

        # Initialize Notifier Agent

        notifier = NotifierAgent()

        # Generate and save notification

        result = notifier.run(

            topic=topic,

            summary_points=summary_points,

            sources=sources

        )

        return result

    except Exception as error:

        print(
            f"[Agent 3] Error: {str(error)}"
        )

        return {

            "notification_status": "failed",

            "notification_error": str(error)

        }


# ==================================================
# 10. STANDALONE TEST
# ==================================================

if __name__ == "__main__":

    # Sample output from Agent 2

    sample_summary_output = {

        "topic": "Latest Developments in Generative AI",

        "summary": [

            "Generative AI models are improving reasoning capabilities.",

            "Multimodal AI is combining text, images and audio.",

            "AI agents are increasingly automating business workflows.",

            "Organizations are adopting AI for productivity improvements.",

            "AI safety and responsible AI governance remain important."

        ],

        "sources": [

            "https://openai.com/research/",

            "https://ai.google/"

        ]

    }

    try:

        agent = NotifierAgent()

        result = agent.run(

            topic=sample_summary_output["topic"],

            summary_points=sample_summary_output["summary"],

            sources=sample_summary_output["sources"]

        )

        print(
            "\nNOTIFIER AGENT EXECUTED SUCCESSFULLY"
        )

        print("\nGENERATED EMAIL:\n")

        print(result["notification"])

        print("\nSAVED FILE:")

        print(result["notification_path"])

    except Exception as error:

        print(
            "\nNotifier Agent Error:",
            error
        )
