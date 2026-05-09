from __future__ import annotations

import ast
import os
from datetime import datetime
from typing import cast

import chainlit as cl
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    OpenAIProvider,
    RunContextWrapper,
    Runner,
    function_tool,
    handoff,
)
from agents.run import RunConfig
from dotenv import load_dotenv


load_dotenv(override=True)

deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
deepseek_model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

class UserProfile:
    def __init__(self, name: str, uid: int, favorite_topic: str = "artificial intelligence") -> None:
        self.name = name
        self.uid = uid
        self.favorite_topic = favorite_topic


def safe_math(expression: str) -> float:
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.UAdd,
        ast.USub,
        ast.Constant,
    )

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return +evaluate(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow):
                return left**right
            if isinstance(node.op, ast.Mod):
                return left % right
        raise ValueError("Only simple arithmetic expressions are allowed.")

    parsed = ast.parse(expression, mode="eval")
    if not all(isinstance(node, allowed_nodes) for node in ast.walk(parsed)):
        raise ValueError("Unsupported expression.")
    return evaluate(parsed)


@function_tool
async def get_current_time(wrapper: RunContextWrapper[UserProfile]) -> str:
    return (
        f"Current local time for {wrapper.context.name} is "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


@function_tool
async def get_user_profile(wrapper: RunContextWrapper[UserProfile]) -> str:
    profile = wrapper.context
    return (
        f"User profile: name={profile.name}, uid={profile.uid}, "
        f"favorite_topic={profile.favorite_topic}"
    )


@function_tool
async def calculate_expression(expression: str) -> str:
    try:
        value = safe_math(expression)
        return f"{expression} = {value:g}"
    except Exception as exc:
        return f"Could not calculate '{expression}': {exc}"


def get_deepseek_api_key() -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is not set. Add it to your .env file.")
    return api_key


def build_run_config() -> RunConfig:
    client = AsyncOpenAI(api_key=get_deepseek_api_key(), base_url=deepseek_base_url)
    model = OpenAIChatCompletionsModel(
        model=deepseek_model_name,
        openai_client=client,
    )
    provider = OpenAIProvider(openai_client=client)
    return RunConfig(model=model, model_provider=provider, tracing_disabled=True)


def build_agent() -> Agent:
    billing_agent = Agent(
        name="Billing Agent",
        instructions="You only answer questions related to billing, invoices, payments, and receipts.",
    )

    refund_agent = Agent(
        name="Refund Agent",
        instructions=(
            "You only handle refund-related requests and guide users through the refund process."
        ),
    )

    billing_handoff = handoff(
        agent=billing_agent,
        tool_name_override="billing_support",
        tool_description_override="Handle billing, invoices, receipts, and payment questions.",
    )

    refund_handoff = handoff(
        agent=refund_agent,
        tool_name_override="refund_support",
        tool_description_override="Handle damaged-item, late-delivery, or general refund requests.",
    )

    return Agent(
        name="Light Speed",
        instructions=(
            "You are a helpful AI chatbot. Answer clearly and concisely. "
            "Use the provided tools when appropriate and hand off billing or refund questions to specialist agents."
        ),
        tools=[get_current_time, get_user_profile, calculate_expression],
        handoffs=[billing_handoff, refund_handoff],
    )


@cl.on_chat_start
async def start() -> None:
    try:
        config = build_run_config()
    except ValueError as exc:
        await cl.Message(
            content=(
                f"Startup failed: {exc}\n\n"
                "Create a `.env` file with `DEEPSEEK_API_KEY` or export it in your shell, then restart with `chainlit run main.py -w`."
            )
        ).send()
        return

    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    cl.user_session.set("agent", build_agent())
    cl.user_session.set(
        "context",
        UserProfile(
            name=os.getenv("USER_NAME", "Student"),
            uid=int(os.getenv("USER_ID", "101")),
            favorite_topic=os.getenv("FAVORITE_TOPIC", "artificial intelligence"),
        ),
    )

    await cl.Message(
        content=(
            "# Light Speed Chat Bot\n\n"
            "Ask me anything, or try a billing/refund question to see handoffs.\n\n"
            "You can also ask for the current time, a simple calculation, or your saved profile data to exercise tool calling."
        )
    ).send()


@cl.on_message
async def main(message: cl.Message) -> None:
    status = cl.Message(content="Thinking...")
    await status.send()

    agent = cast(Agent, cl.user_session.get("agent"))
    config = cast(RunConfig, cl.user_session.get("config"))
    context = cast(UserProfile, cl.user_session.get("context"))
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=history,
            context=context,
            run_config=config,
        )
        status.content = result.final_output
        await status.update()
        cl.user_session.set("chat_history", result.to_input_list())
    except Exception as exc:
        error_text = str(exc)
        if "401" in error_text or "Authentication Fails" in error_text or "invalid_request_error" in error_text:
            status.content = (
                "DeepSeek rejected the API key. Replace `DEEPSEEK_API_KEY` in your `.env` file with a valid DeepSeek key, "
                "then restart Chainlit."
            )
        else:
            status.content = f"Error: {exc}"
        await status.update()


if __name__ == "__main__":
    print("Run this chatbot with: chainlit run main.py -w")
