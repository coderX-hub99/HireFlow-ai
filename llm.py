from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


if not OPENAI_API_KEY:
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)


def ask_structured(system_prompt: str, user_prompt: str, response_model):
    """
    Send a prompt to OpenAI and return a validated Pydantic object.
    """

    if client is None:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to your .env file."
        )

    response = client.responses.parse(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        text_format=response_model,
    )

    if response.output_parsed is None:
        raise RuntimeError("The model returned no structured result.")

    return response.output_parsed