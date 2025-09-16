import os
import sys
import yaml
import argparse
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info


def load_config(path="agent_config.yaml") -> dict:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return dict(config)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print("ERROR: No prompt was provided")
        sys.exit(1)  # or raise, or return, or log


config = load_config()


cli_config = config.get(
    "cli",
    {
        "prog": "agent-template",
        "description": "modular scaffold for building async, tool-using AI agents with memory, I/O, and runtime configuration",
        "epilog": "see README or docs/ for usage examples, architecture notes, and integration tips",
    },
)
load_dotenv()
api_key: str | None = os.getenv("GEMINI_API_KEY") or None
if api_key is None:
    print("ERROR: You need to add your GEMINI_API_KEY to .env")
    sys.exit(1)

model_name = "gemini-2.0-flash-001"

client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)


def get_default_prompt(max_len=140) -> str:
    prompt = os.getenv("DEFAULT_PROMPT")
    if prompt is None:
        raise ValueError("DEFAULT_PROMPT is not defined in .env")
    n = min(max_len, len(prompt))
    return prompt[:n].strip()


def get_response(prompt: str) -> tuple:
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    if response.function_calls is not None:
        fcs = response.function_calls
        text = "\n".join(f"Calling function: {fc.name}({fc.args})" for fc in fcs)
    else:
        text = response.text
    usage_metadata = response.usage_metadata
    prompt_tokens, response_tokens = None, None
    if usage_metadata is not None:
        prompt_tokens = usage_metadata.prompt_token_count
        response_tokens = usage_metadata.candidates_token_count
    return text, prompt_tokens, response_tokens


def main():
    parser = ArgumentParser(**cli_config, exit_on_error=False)
    parser.add_argument("prompt")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    text, p, r = get_response(args.prompt)
    if args.verbose:
        print(f"User prompt: {text}")
        print(f"Prompt tokens: {p}")
        print(f"Response tokens: {r}")
    else:
        print(text)


if __name__ == "__main__":
    main()
