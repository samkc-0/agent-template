import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key: str | None = os.getenv("GEMINI_API_KEY") or None
if api_key is None:
    print("ERROR: You need to add your GEMINI_API_KEY to .env")
    sys.exit(1)

model_name = "gemini-2.0-flash-001"

client = genai.Client(api_key=api_key)


def get_default_prompt(max_len=140) -> str:
    prompt = os.getenv("DEFAULT_PROMPT")
    if prompt is None:
        raise ValueError("DEFAULT_PROMPT is not defined in .env")
    n = min(max_len, len(prompt))
    return prompt[:n].strip()


def get_response(prompt: str) -> tuple[str | None, int | None, int | None]:
    response = client.models.generate_content(model=model_name, contents=prompt)
    text = response.text
    usage_metadata = response.usage_metadata
    prompt_tokens, response_tokens = None, None
    if usage_metadata is not None:
        prompt_tokens = usage_metadata.prompt_token_count
        response_tokens = usage_metadata.candidates_token_count
    return text, prompt_tokens, response_tokens


def main():
    if len(sys.argv) < 2:
        print("ERROR: No prompt was provided")
        sys.exit(1)
    else:
        prompt = sys.argv[1]
    text, p, r = get_response(prompt)
    print(text)
    print(f"Prompt tokens: {p}")
    print(f"Response tokens: {r}")


if __name__ == "__main__":
    main()
