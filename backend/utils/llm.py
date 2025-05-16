import dotenv

dotenv.load_dotenv()
import os

from openai import AzureOpenAI

api_key = os.getenv("OPENAI_API_KEY")

openai_client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-06-01",
    azure_endpoint="https://hkust.azure-api.net",
    azure_deployment="gpt-4o-mini",
)

def get_LLM_output(system_prompt: str, user_prompt: str) -> str:
    """
    Gets generation output from LLM
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    return response.choices[0].message.content