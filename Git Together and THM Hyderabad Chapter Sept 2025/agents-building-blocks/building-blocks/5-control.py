"""
Control: Provides deterministic decision-making and process flow control.
This component handles if/then logic, routing based on conditions, and process orchestration for predictable behavior.
"""

import os
import json
import re
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")


class IntentClassification(BaseModel):
    intent: Literal["question", "request", "complaint"]
    confidence: float
    reasoning: str


def get_perplexity_client():
    """Initialize and return Perplexity client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError("PERPLEXITY_API_KEY not found or not set properly")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

def route_based_on_intent(user_input: str) -> tuple[str, IntentClassification]:
    client = get_perplexity_client()
    
    system_prompt = """Classify user input into one of three categories: question, request, or complaint.
    Return JSON format: {"intent": "question/request/complaint", "confidence": 0.0-1.0, "reasoning": "explanation"}"""
    
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150
    )

    try:
        response_text = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in response")
        
        classification = IntentClassification(**json_data)
    except (json.JSONDecodeError, ValueError):
        # Fallback classification based on keywords
        if any(word in user_input.lower() for word in ["what", "how", "why", "when", "where", "?"]):
            intent = "question"
        elif any(word in user_input.lower() for word in ["please", "can you", "schedule", "book"]):
            intent = "request"
        else:
            intent = "complaint"
        
        classification = IntentClassification(
            intent=intent,
            confidence=0.5,
            reasoning="Fallback classification based on keywords"
        )

    intent = classification.intent

    if intent == "question":
        result = answer_question(user_input)
    elif intent == "request":
        result = process_request(user_input)
    elif intent == "complaint":
        result = handle_complaint(user_input)
    else:
        result = "I'm not sure how to help with that."

    return result, classification


def answer_question(question: str) -> str:
    client = get_perplexity_client()
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": "Answer the user's question clearly and concisely."},
            {"role": "user", "content": question}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content


def process_request(request: str) -> str:
    return f"Processing your request: {request}"


def handle_complaint(complaint: str) -> str:
    return f"I understand your concern about: {complaint}. Let me escalate this."


if __name__ == "__main__":
    # Test different types of inputs
    test_inputs = [
        "What is machine learning?",
        "Please schedule a meeting for tomorrow",
        "I'm unhappy with the service quality",
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result, classification = route_based_on_intent(user_input)
        print(
            f"Intent: {classification.intent} (confidence: {classification.confidence})"
        )
        print(f"Reasoning: {classification.reasoning}")
        print(f"Response: {result}")
