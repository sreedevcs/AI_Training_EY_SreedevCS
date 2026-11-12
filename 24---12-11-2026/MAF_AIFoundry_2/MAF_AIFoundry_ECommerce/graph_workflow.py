import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import (
    Agent,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.openai import OpenAIChatClient

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


def read_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith(("PASTE_", "YOUR_")):
        raise ConfigurationError(f"Set {name} correctly in your .env file.")
    return value


class ConfigurationError(ValueError):
    pass


def check_eligibility(request: dict) -> dict:
    issues = []
    if request["amount_inr"] >= 25_000:
        issues.append("The product amount must be below INR 25,000.")
    if not 0 <= request["days_since_delivery"] <= 30:
        issues.append("Return request must be within 30 days of delivery.")
    if not request["invoice_available"]:
        issues.append("Customer invoice is not available.")
    condition = request["item_condition"].upper()
    if condition != "UNOPENED" and not (
        condition == "DAMAGED" and request["photo_evidence_available"]
    ):
        issues.append("The item must be unopened or damaged with photo evidence.")
    if request["previous_returns_90_days"] >= 3:
        issues.append("The customer has three or more previous returns in 90 days.")
    return {"eligible": not issues, "issues": issues}


def check_risk(request: dict) -> tuple[str, str]:
    concerns = []
    if request["amount_inr"] >= 25_000:
        concerns.append("high-value request")
    if request["previous_returns_90_days"] >= 3:
        concerns.append("unusual return frequency")
    if not request["invoice_available"]:
        concerns.append("missing invoice")
    if (
        request["item_condition"].upper() == "DAMAGED"
        and not request["photo_evidence_available"]
    ):
        concerns.append("missing damage photos")
    if concerns:
        level="HIGH"
    else:
        level="LOW"

    if concerns:
        assessment=", ".join(concerns)
    else:
        assessment="No high-risk concerns identified."
    return level, assessment


def build_workflow(chat_client: OpenAIChatClient | None):
    
    eligibility_agent = Agent(
        client=chat_client,
        name="EligibilityAgent",
        instructions=(
            "Explain the provided deterministic eligibility result and exceptions briefly. "
            "Do not change the result or make an approval decision."
        ),
    )
    risk_agent = Agent(
        client=chat_client,
        name="RiskAgent",
        instructions=(
            "Briefly assess return frequency, missing evidence, and request value. "
            "Do not downgrade a supplied HIGH risk level."
        ),
    ) 
    customer_agent = Agent(
        client=chat_client,
        name="CustomerResponseAgent",
        instructions=(
            "Write a short customer message that matches the final decision. "
            "Do not say that a refund was processed or a replacement was initiated. "
            "Never contradict a manager rejection."
        ),
    ) 

#state contains all the information collected so far, including the request, eligibility findings, risk assessment, and manager decision if any.
#ctx is the workflow content, used to send output or continue the workflow.
#async means function can wait for tasks like AI response without blocking the workflow.

#Executor-1 is Eligibility
    @executor(id="eligibility")
    async def eligibility(state: dict, ctx: WorkflowContext[dict]) -> None:
        request = state["request"]
        #Eligibilty was already checked (_eligibility_result and _eligibility_assessment are cached in state.
        if "_eligibility_result" in state:
            findings = state["_eligibility_result"] #returns eligible:True,issues:[] or eligible:False,issues:[some issues]
            explanation = state["_eligibility_assessment"] #explanation of the result which was generated before.
        #Eligiblity was not checked, so we check it.
        else:
            findings = check_eligibility(request)

            #sending request+finding to agent and asking to explaint he result in a short text.
            #await means wait for the AI answer before continuing.
            explanation = (
                await eligibility_agent.run(
                    f"Request: {json.dumps(request)}\nFindings: {json.dumps(findings)}"
                )
            ).text if eligibility_agent else (
                "Eligible." if findings["eligible"] else "; ".join(findings["issues"])
            ) #if no agent present, then generate a custom message by our own.
            #if eligible then explanation is 'eligible' else explanation is a list of issues
        await ctx.send_message({
            **state,
            "eligibility": findings, #result
            "eligibility_assessment": explanation.strip(), #explanation of result
            "_eligibility_result": findings, #cached copy to avoid rechecking
            "_eligibility_assessment": explanation.strip(), #cached copy to avoid rechecking
        })

#Executor-2 is Risk
    @executor(id="risk")
    async def risk(state: dict, ctx: WorkflowContext[dict]) -> None:
        request = state["request"]
        #Risk was already checked (_risk_level and _risk_assessment are cached in state)
        if "_risk_level" in state:
            level = state["_risk_level"]
            assessment = state["_risk_assessment"]
        #Risk calculated using our own function.
        else:
            level, assessment = check_risk(request)
            #The request and corresponding risk level and assessment(concerns) are sent to agent if it is available.
            if risk_agent:
                ai_assessment = await risk_agent.run(
                    f"Request: {json.dumps(request)}\n"
                    f"Deterministic risk level: {level}\nRisk factors: {assessment}"
                )
                #if agent provides a non-empty response, then use it. Otherwise, use our own assessment.
                assessment = ai_assessment.text.strip() or assessment
        await ctx.send_message({
            **state,
            "risk_level": level, #risk level : HIGH or LOW
            "risk_assessment": assessment, #concerns like high return frequency, missing evidence etc.
            "_risk_level": level, #cached copy
            "_risk_assessment": assessment, #cached copy
        })

#Executor-3 is approval
    @executor(id="approval_gateway")
    async def approval_gateway(state: dict, ctx: WorkflowContext[dict]) -> None:
        if state["eligibility"]["eligible"] and state["risk_level"] != "HIGH": #request is eligible and not high risk, then autoapproval
            await ctx.send_message({
                **state,
                "approval_route": "Auto-Approved",
                "final_decision": "AUTO_APPROVED",
            })
            return
        # if not approvable, then:
        #check whether manager already given a decision. If not, pause the workflow and ask for human review.
        if "_manager_decision" not in state:
            await ctx.yield_output({**state, "requires_human_review": True})
            return

        # Got manager decision(which was already provided or got it now)
        decision = state["_manager_decision"].strip().lower()

        #invalid decision, which is neither approve nor reject.
        if decision not in {"approve", "reject"}:
            raise ValueError("Enter approve or reject.")
        #final_decision is MANAGERAPPROVED if approve, else it is MANAGERREJECTED. 
        await ctx.send_message({
            **state,
            "approval_route": "Human Review",
            "final_decision": (
                "MANAGER_APPROVED" if decision == "approve" else "MANAGER_REJECTED"
            ),
        })

#Executor-4 is customer-response
    @executor(id="customer_response")
    async def customer_response(state: dict, ctx: WorkflowContext[dict]) -> None:
        request = state["request"]
        decision = state["final_decision"] #can be AUTO_APPROVED, MANAGER_APPROVED, MANAGER_REJECTED
        approved = decision != "MANAGER_REJECTED" #if decision is not MANAGER_REJECTED(ie, it is MANAGEAPPROVED or AUTOAPPROVED), then approved is true.
        #else approved is false(if decision is MANAGER_REJECTED)
        message = (
            "Your return request has been approved."
            if approved else "Your return request was not approved after manager review."
        )
        # message += " No refund has been processed and no replacement has been initiated."
        if customer_agent:
            #if the agent is present, then gives the model what was the final decision, the message and a guardrail to return the crisp message.
            result = await customer_agent.run(
                f"Final decision: {decision}\nRequired meaning: {message}\n"
                "Return exactly the required message without additions or changes."
            )
            if result.text.strip() == message: #if agent returned the same message, then use it. Otherwise, use the original message itself.
                message = result.text.strip()

        await ctx.yield_output({
            "request_id": request["request_id"],
            "order_id": request["order_id"],
            "product": request["product"],
            "requested_amount_inr": request["amount_inr"],
            "eligibility_findings": state["eligibility"],
            "risk_assessment": state["risk_assessment"],
            "approval_route": state["approval_route"],
            "final_decision": decision,
            "customer_communication_draft": message,
        })

#request->ElgibilityAgent->RiskAGent->ApprovalAgent->CustomerResponseAgent
    return (
        WorkflowBuilder(start_executor=eligibility, name="returns")
        .add_edge(eligibility, risk)
        .add_edge(risk, approval_gateway)
        .add_edge(approval_gateway, customer_response)
        .build()
    )


async def process_request(workflow, request: dict, demo: bool, invalid_demo: bool):
    result = await workflow.run({"request": request}) #start workflow with a state that contains only request
    output = result.get_outputs()[0] #workflow may produce multiple outputs, but take the first one.

    #if the workflow is paused for human review, and manager decision is needed, then:
    if output.get("requires_human_review"):
        paused_request = output
        request = paused_request["request"]
        print(
            f"\nHuman review: {request['request_id']} - "
            f"{request['product']} - INR {request['amount_inr']}"
        )
        print(f"Eligibility issues: {paused_request['eligibility']['issues'] or 'None'}")
        print(f"Risk: {paused_request['risk_assessment']}")

        if demo: #fake dummy data for offline mode.
            decisions = ["later", "reject"] if invalid_demo else [
                "approve" if request["request_id"] == "RET204" else "reject"
            ]
        else:
            decisions = [] #in real mode, we ask user for decision input. We dont predefine any decision

        while True: #run till we get a valid decision from user or demo data.
            #if demo mode, take next fake decision from list. If not, then ask user for the decision input.
            decision = (
                decisions.pop(0)
                if demo else await asyncio.to_thread(input, "Manager decision (approve/reject): ")
            )
            decision = decision.strip().lower()
            if decision in {"approve", "reject"}: #we got a decision, so break loop and continue.
                break
            if demo and not decisions:
                raise ValueError("Offline demo decision must be approve or reject.")
            if not demo:
                print("Please enter approve or reject.")
            else:
                print("Invalid input. Please enter approve or reject.")

        paused_request["_manager_decision"] = decision #the paused request state decision is updated with manager decision.
        paused_request.pop("requires_human_review") #remove the requires_human_review key from paused_request state, as we have got the decision now.
        result = await workflow.run(paused_request) #re-run the workflow with the manager decision added.

    return result.get_outputs()[0] #return final output of workflow after manager decision was processed.


async def main() -> None:
    parser = argparse.ArgumentParser()
    #if we add --offline-demo flag while running the script, then the workflow will run in offline mode with fake data and no real API calls to OpenAI.
    parser.add_argument("--offline-demo", action="store_true")
    args = parser.parse_args()

    with (PROJECT_DIR / "returns.json").open(encoding="utf-8") as file:
        requests = json.load(file)
    print(f"Loaded {len(requests)} return requests.")

    sdk_client = None #openAI SDF client
    chat_client = None #
    if not args.offline_demo:
        sdk_client = AsyncOpenAI(
            api_key=read_setting("AZURE_OPENAI_API_KEY"),
            base_url=read_setting("AZURE_OPENAI_BASE_URL"),
        )
        chat_client = OpenAIChatClient(
            model=read_setting("AZURE_OPENAI_MODEL"),
            async_client=sdk_client,
        )

    try:
        workflow = build_workflow(chat_client)
        results = []
        for index, request in enumerate(requests):
            print(f"\nProcessing {request['request_id']}: {request['product']}")
            # results.append(
            #     await process_request(
            #         workflow, request, args.offline_demo, args.offline_demo and index == 1
            #     )
            # )
            result = await process_request(
                workflow,
                request,
                args.offline_demo,
                args.offline_demo and index == 1,
            )
            results.append(result)

            if result["final_decision"] in {"AUTO_APPROVED", "MANAGER_APPROVED"}:
                print(
                    f"Approved request: {result['request_id']} - "
                    f"{result['product']} - INR {result['requested_amount_inr']} "
                    f"({result['approval_route']})"
                )
            else:
                print(
                    f"Rejected request: {result['request_id']} - "
                    f"{result['product']} - INR {result['requested_amount_inr']} "
                    f"(Manager Review)"
                )
        print("\n" + json.dumps(results, ensure_ascii=False, indent=2))
        print("\nSUMMARY")
        print(f"Total requests: {len(results)}")

        for result in results:
            decision = result["final_decision"]

            if decision == "AUTO_APPROVED":
                status = "Auto-approved"
            elif decision == "MANAGER_APPROVED":
                status = "Manager approved: Yes"
            else:  # MANAGER_REJECTED
                status = "Manager approved: No (rejected)"

            print(
                f"{result['request_id']} | {result['product']} | {status}"
            )

        auto_approved_count = sum(
            result["final_decision"] == "AUTO_APPROVED" for result in results
        )
        manager_approved_count = sum(
            result["final_decision"] == "MANAGER_APPROVED" for result in results
        )
        manager_rejected_count = sum(
            result["final_decision"] == "MANAGER_REJECTED" for result in results
        )

        print(f"\nAuto-approved: {auto_approved_count}")
        print(f"Manager approved: Yes - {manager_approved_count}")
        print(f"Manager approved: No - {manager_rejected_count}")

        print("\nTESTING COMPLETED")
    finally:
        if sdk_client:
            await sdk_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ConfigurationError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
