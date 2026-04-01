"""
Recovery: Manages failures and exceptions gracefully in agent workflows.
This component implements retry logic, fallback processes, and error handling to ensure system resilience.
"""

import os
import json
import re
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")


class UserInfo(BaseModel):
    name: str
    email: str
    age: Optional[int] = None  # Optional field


def get_perplexity_client():
    """Initialize and return Perplexity client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError("PERPLEXITY_API_KEY not found or not set properly")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

def resilient_intelligence(prompt: str) -> str:
    client = get_perplexity_client()

    system_prompt = """Extract user information from the text and return as JSON.
    Format: {"name": "full name", "email": "email@domain.com", "age": number_or_null}
    If age is not mentioned, use null."""

    try:
        # Get structured output
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )

        response_text = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_data = json.loads(json_match.group())
            user_data = UserInfo(**json_data).model_dump()
        else:
            raise ValueError("No JSON found in response")

        try:
            # Try to access age field and check if it's valid
            age = user_data["age"]
            if age is None:
                raise ValueError("Age is None")
            age_info = f"User is {age} years old"
            return age_info

        except (KeyError, TypeError, ValueError):
            print("❌ Age not available, using fallback info...")
            # Fallback to available information
            return f"User {user_data['name']} has email {user_data['email']}"

    except Exception as e:
        print(f"❌ API or parsing error: {e}, using emergency fallback...")
        # Emergency fallback - extract basic info with simple parsing
        words = prompt.split()
        name = "Unknown"
        email = "unknown@example.com"
        
        # Simple name extraction (look for capitalized words)
        for i, word in enumerate(words):
            if word.istitle() and i < len(words) - 1 and words[i+1].istitle():
                name = f"{word} {words[i+1]}"
                break
        
        # Simple email extraction
        for word in words:
            if "@" in word and "." in word:
                email = word.strip(".,!?")
                break
        
        return f"User {name} has email {email} (extracted with fallback method)"


if __name__ == "__main__":
    result = resilient_intelligence(
        "My name is John Smith and my email is john@example.com"
    )
    print("Recovery Output:")
    print(result)
