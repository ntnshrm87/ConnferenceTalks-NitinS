"""
Feedback: Provides strategic points where human judgement is required.
This component implements approval workflows and human-in-the-loop processes for high-risk decisions or complex judgments.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")


def get_human_approval(content: str) -> bool:
    print(f"Generated content:\n{content}\n")
    response = input("Approve this? (y/n): ")
    return response.lower().startswith("y")


def get_perplexity_client():
    """Initialize and return Perplexity client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError("PERPLEXITY_API_KEY not found or not set properly")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

def intelligence_with_human_feedback(prompt: str) -> None:
    client = get_perplexity_client()

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Generate creative and thoughtful content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    
    draft_response = response.choices[0].message.content

    if get_human_approval(draft_response):
        print("✅ Final answer approved")
    else:
        print("❌ Answer not approved")


if __name__ == "__main__":
    intelligence_with_human_feedback("Write a short poem about technology")
