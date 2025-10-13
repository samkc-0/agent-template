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
from functions.utils import color_printer


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

    if response.candidates is not None:
        text = ""
        for candidate in response.candidates:
            if candidate.content is None:
                continue
            messages.append(candidate.content)

    if response.function_calls is None:
        return response
    
    for f in response.function_calls:
        result = call_function(f, verbose)
        
        if not result.parts:
            raise Exception("no result from function call")
        
        if not result.parts[0].function_response.response:
            raise Exception("no result from function call")

        message = ""
        for part in result.parts:
            message = "\n".join(f"{key}: {value}" for key, value in part.function_response.response.items())
            messages.append(types.Content(role="user", parts=[types.Part(text=message)]))
        
        if verbose:
            color_printer(33)(message)

    return None


def main():

    yellow_text = color_printer(33)
    red_text = color_printer(31)

    user_prompt, verbose = parse_args()
    client = get_model()

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    for _ in range(20):
        try:
            response = generate_content(client, messages, verbose)
            if response is not None:
                yellow_text(response.text)
                break
        except Exception as e:
            red_text(f"oops, something went wrong:\n{e}")
            break

if __name__ == "__main__":
    main()
