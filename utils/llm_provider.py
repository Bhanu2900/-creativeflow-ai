import os

from openai import OpenAI
from groq import Groq


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


github_client = None
groq_client = None


if GITHUB_TOKEN:
    github_client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN
    )


if GROQ_API_KEY:
    groq_client = Groq(
        api_key=GROQ_API_KEY
    )


def generate_completion(
    messages,
    temperature=0.7,
    max_tokens=1000
):
    """
    Primary:
        GitHub Models

    Fallback:
        Groq
    """

    # ---------- GitHub Models ----------
    if github_client:
        try:

            print("🚀 Using GitHub Models")

            response = github_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "provider": "github_models",
                "content": response.choices[0].message.content
            }

        except Exception as e:

            print(
                f"⚠️ GitHub Models failed: {e}"
            )

    # ---------- Groq Fallback ----------
    if groq_client:

        print("🔄 Falling back to Groq")

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "provider": "groq",
            "content": response.choices[0].message.content
        }

    raise Exception(
        "No AI provider configured."
    )