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

    if response.function_calls is None:
        return response.text

    function_call_results = []
    for f in response.function_calls:
        result = call_function(f, verbose)
        
        if not result.parts:
            raise Exception("no result from function call")
        
        response = result.parts[0].function_response.response

        if not response:
            raise Exception("no result from function call")
        
        if verbose:
            message = "\n".join(f"{key}: {value}" for key, value in response.items())
            return message

        function_call_results.append(result.parts[0])

    return ""


def main():
    user_prompt, verbose = parse_args()
    client = get_model()
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    # while True:
    #     message = generate_content(client, messages, verbose)
        
    #     messages.append(message)
    #     print(color_text(message, "33"))
        
    #     prompt = input("> ")
    #     if prompt == "exit":
    #         sys.exit(0)
        
    #     messages.append(types.Content(role="user", parts=[types.Part(text=prompt)]))
    message = generate_content(client, messages, verbose)
    print(message)


if __name__ == "__main__":
    main()
