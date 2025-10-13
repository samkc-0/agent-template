import os
import sys
import argparse
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from dotenv import load_dotenv
from functions.get_file_content import get_file_content
from functions.call_function import call_function, available_schema
from config import SYSTEM_PROMPT, DEFAULT_PROMPT


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_model():
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def parse_args():
    parser = argparse.ArgumentParser(prog="AGENT")

    parser.add_argument(
        "prompt", default=DEFAULT_PROMPT, help="intial prompt for the agent"
    )

    parser.add_argument(
        "-v", "--verbose", default=False, action="store_true", help="verbose mode"
    )

    args = parser.parse_args()
    user_prompt = args.prompt
    verbose = args.verbose
    return user_prompt, verbose


def color_text(text: str, color: str) -> str:
    return f"\033[{color}m{text}\033[0m"


def generate_content(client, messages, verbose=False):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_schema], system_instruction=SYSTEM_PROMPT
            ),
        )

    except ServerError as e:
        if verbose:
            print(e)
        return None

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    print(color_text(response.text, "33"))

    for function_call_part in response.function_calls:
        print(function_call_part)


def main():
    user_prompt, verbose = parse_args()
    client = get_model()
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    generate_content(client, messages, verbose)


if __name__ == "__main__":
    main()
