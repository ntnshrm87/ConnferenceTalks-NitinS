"""
Intelligence: The "brain" that processes information and makes decisions using LLMs.
This component uses Perplexity API for web-enhanced AI responses.

Get your Perplexity API key from: https://www.perplexity.ai/settings/api
More info: https://docs.perplexity.ai/
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")

def perplexity_intelligence(prompt: str) -> str:
    """
    Intelligence function using Perplexity API for web-enhanced responses.
    
    Args:
        prompt (str): The question or prompt to send to Perplexity AI
        
    Returns:
        str: The AI response with web-enhanced information
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError(
            "PERPLEXITY_API_KEY not found or not set properly. "
            "Please get your API key from https://www.perplexity.ai/settings/api "
            "and update the .env file"
        )
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )
    
    response = client.chat.completions.create(
        model="sonar-pro",  # Perplexity's web-enhanced model
        messages=[
            {"role": "system", "content": "You are a helpful assistant with access to current web information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("🧠 Perplexity Intelligence Test")
    print("=" * 50)
    
    try:
        # Test with a current events question that benefits from web access
        print("Testing with current information query...")
        result1 = perplexity_intelligence("What are the latest developments in AI technology in 2025?")
        print("\n📊 Current AI Developments:")
        print(result1)
        print("\n" + "=" * 50)
        
        # Test with a technical question
        print("\nTesting with technical query...")
        result2 = perplexity_intelligence("Explain the differences between GPT-4 and Claude AI models")
        print("\n🤖 AI Models Comparison:")
        print(result2)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Go to https://www.perplexity.ai/settings/api")
        print("2. Create an account and get your API key")
        print("3. Update .env file: PERPLEXITY_API_KEY=your-actual-key")
        print("4. Run this script again")
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("- Check if your API key is valid")
        print("- Verify you have credits in your Perplexity account")
        print("- Check your internet connection")