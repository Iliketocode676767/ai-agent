import ast
import json
import os
import re
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """
You are a helpful AI agent.

Rules:
1. If the user asks a simple question, answer directly.
2. If the user asks for a calculation or needs a web fetch, use a valid JSON tool call.
3. When using a tool, respond with ONLY valid JSON in this exact shape:
   {"tool":"calculator","args":{"expr":"2 + 2"}}
   or
   {"tool":"fetch_url","args":{"url":"https://example.com"}}
4. If you do not need a tool, respond with a normal answer.
"""


def safe_calculator(expr: str) -> str:
    expr = expr.strip()
    if not expr:
        return "Error: empty expression."

    allowed_names = {"abs": abs, "round": round, "min": min, "max": max}
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.FloorDiv,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )

    try:
        parsed = ast.parse(expr, mode="eval")
    except SyntaxError:
        return "Error: invalid math expression."

    for node in ast.walk(parsed):
        if not isinstance(node, allowed_nodes):
            return "Error: unsupported expression."

    for node in ast.walk(parsed):
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            return "Error: unsupported symbol."

    try:
        result = eval(compile(parsed, "<expr>", "eval"), {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception:
        return "Error: could not evaluate expression."


def fetch_url_text(url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    text = response.text

    cleaned = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    cleaned = re.sub(r"<style.*?</style>", " ", cleaned, flags=re.S | re.I)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:4000]


def run_tool(tool_name: str, args: Dict[str, Any]) -> str:
    if tool_name == "calculator":
        expr = args.get("expr")
        if not expr:
            return "Error: missing expr argument."
        return safe_calculator(str(expr))

    if tool_name == "fetch_url":
        url = args.get("url")
        if not url:
            return "Error: missing url argument."
        try:
            return fetch_url_text(str(url))
        except Exception as exc:
            return f"Error fetching URL: {exc}"

    return f"Error: unknown tool '{tool_name}'."


class AIAgent:
    def __init__(self, api_key: str | None = None, model: str | None = None, max_steps: int = 5):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or MODEL
        self.max_steps = max_steps

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file or environment.")

    def _chat_completion(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(f"OpenAI API error {response.status_code}: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _is_tool_call(self, text: str) -> bool:
        text = text.strip()
        if not text.startswith("{") or not text.endswith("}"):
            return False
        try:
            parsed = json.loads(text)
            return isinstance(parsed, dict) and "tool" in parsed and "args" in parsed
        except json.JSONDecodeError:
            return False

    def run(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        for _ in range(self.max_steps):
            raw_response = self._chat_completion(messages)
            if self._is_tool_call(raw_response):
                try:
                    tool_call = json.loads(raw_response)
                    tool_name = tool_call["tool"]
                    args = tool_call.get("args", {})
                    tool_result = run_tool(tool_name, args)

                    messages.append({"role": "assistant", "content": raw_response})
                    messages.append({
                        "role": "tool",
                        "content": json.dumps({"tool": tool_name, "result": tool_result}),
                    })
                    messages.append({
                        "role": "user",
                        "content": "Use the tool result to answer the user's question.",
                    })
                    continue
                except Exception:
                    return "The agent tried to use a tool, but the tool call was invalid."

            return raw_response

        return "The agent reached its maximum steps without producing a final answer."
