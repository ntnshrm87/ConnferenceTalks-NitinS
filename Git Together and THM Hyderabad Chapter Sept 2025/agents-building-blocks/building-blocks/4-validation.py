"""
Validation: Ensures LLM outputs match predefined data schemas.
This component provides schema validation and structured data parsing to guarantee consistent data formats for downstream code.

More info: https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses
"""

import os
import json
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")


class TaskResult(BaseModel):
    """
    More info: https://docs.pydantic.dev
    """

    task: str
    completed: bool
    priority: int


def get_perplexity_client():
    """Initialize and return Perplexity client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError("PERPLEXITY_API_KEY not found or not set properly")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

def structured_intelligence(prompt: str) -> TaskResult:
    client = get_perplexity_client()
    
    system_prompt = """Extract task information from the user input and return as JSON.
    Format: {"task": "description", "completed": true/false, "priority": 1-10}
    Priority: 1=low, 5=medium, 10=high"""
    
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    
    try:
        # Extract JSON from response
        response_text = response.choices[0].message.content
        # Find JSON in the response (in case there's extra text)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in response")
        
        # Create and validate TaskResult
        return TaskResult(**json_data)
    except (json.JSONDecodeError, ValueError) as e:
        # Fallback with default values if parsing fails
        print(f"Warning: Could not parse structured output: {e}")
        return TaskResult(
            task=prompt[:50] + "..." if len(prompt) > 50 else prompt,
            completed=False,
            priority=5
        )


if __name__ == "__main__":
    result = structured_intelligence(
        "I need to complete the project presentation by Friday, it's high priority"
    )
    print("Structured Output:")
    print(result.model_dump_json(indent=2))
    print(f"Extracted task: {result.task}")
