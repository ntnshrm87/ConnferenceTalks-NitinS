"""
Memory: Stores and retrieves relevant information across interactions.
This component maintains conversation history and context to enable coherent multi-turn interactions.
Uses Perplexity API for web-enhanced responses with conversation memory.

More info: https://docs.perplexity.ai/
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")

# Simple in-memory conversation storage
conversation_memory = []

def get_perplexity_client():
    """Initialize and return Perplexity client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError(
            "PERPLEXITY_API_KEY not found or not set properly. "
            "Please get your API key from https://www.perplexity.ai/settings/api "
            "and update the .env file"
        )
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )

def ask_joke_without_memory():
    """Ask for a joke without any conversation memory"""
    client = get_perplexity_client()
    
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "user", "content": "Tell me a joke about programming"}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content

def ask_followup_without_memory():
    """Ask a follow-up question without memory - AI will be confused"""
    client = get_perplexity_client()
    
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "user", "content": "What was my previous question?"}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content

def ask_followup_with_memory(joke_response: str):
    """Ask a follow-up question with conversation memory"""
    client = get_perplexity_client()
    
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "user", "content": "Tell me a joke about programming"},
            {"role": "assistant", "content": joke_response},
            {"role": "user", "content": "What was my previous question?"}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content

def add_to_memory(role: str, content: str):
    """Add a message to conversation memory"""
    conversation_memory.append({"role": role, "content": content})
    
    # Keep only last 10 messages to avoid token limits
    if len(conversation_memory) > 10:
        conversation_memory.pop(0)

def chat_with_memory(user_input: str):
    """Chat with persistent memory across multiple interactions"""
    client = get_perplexity_client()
    
    # Add user input to memory
    add_to_memory("user", user_input)
    
    # Create response using full conversation history
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=conversation_memory,
        max_tokens=200
    )
    
    assistant_response = response.choices[0].message.content
    
    # Add assistant response to memory
    add_to_memory("assistant", assistant_response)
    
    return assistant_response

def clear_memory():
    """Clear conversation memory"""
    global conversation_memory
    conversation_memory = []

if __name__ == "__main__":
    print("🧠 Memory System Test - Perplexity API")
    print("=" * 50)
    
    try:
        # Demo 1: Without Memory
        print("📝 Demo 1: WITHOUT Memory")
        print("-" * 30)
        
        print("Asking for a joke...")
        joke_response = ask_joke_without_memory()
        print(f"🤖 Joke: {joke_response}\n")
        
        print("Asking follow-up without memory...")
        confused_response = ask_followup_without_memory()
        print(f"🤷 Confused AI: {confused_response}\n")
        
        # Demo 2: With Memory
        print("📝 Demo 2: WITH Memory (Single Exchange)")
        print("-" * 40)
        
        print("Asking follow-up WITH memory of previous exchange...")
        memory_response = ask_followup_with_memory(joke_response)
        print(f"🧠 AI with Memory: {memory_response}\n")
        
        # Demo 3: Persistent Memory
        print("📝 Demo 3: PERSISTENT Memory (Multiple Interactions)")
        print("-" * 50)
        
        # Clear any existing memory
        clear_memory()
        
        # Multiple interactions with persistent memory
        questions = [
            "What's the weather like in San Francisco?",
            "What about New York?", 
            "Which city did I ask about first?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"Q{i}: {question}")
            response = chat_with_memory(question)
            print(f"A{i}: {response}\n")
        
        print(f"💭 Memory contains {len(conversation_memory)} messages")
        
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