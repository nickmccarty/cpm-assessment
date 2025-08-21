#!/usr/bin/env python3
"""
Sarah's Original AI Assistant Script - BEFORE REFACTORING
This script demonstrates common organizational problems in growing AI projects.

WARNING: This script is intentionally poorly organized to demonstrate problems.
Do not use this as a template for your own projects!

Problems demonstrated:
- Mixed responsibilities in a single file
- Hardcoded configuration values
- Minimal error handling
- Global state management
- Difficult testing and maintenance
"""

import openai
import os
import json
import datetime
from typing import List, Dict

# Problem #1: Hardcoded configuration - Security and flexibility issues
API_KEY = "your-api-key-here"  # Should be environment variable!
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1000
TEMPERATURE = 0.7
CONVERSATION_FILE = "conversations.json"

# Problem #2: Global variables - State management nightmare
conversation_history = []
user_preferences = {}
api_call_count = 0

def main():
    """
    Main function doing too many things - Problem #3: Mixed responsibilities
    This function handles:
    - User interface
    - File operations  
    - API configuration
    - Command processing
    - Data persistence
    - Error handling (minimal)
    
    In a professional application, each of these would be separate modules.
    """
    global conversation_history, user_preferences, api_call_count
    
    print("Welcome to Sarah's AI Assistant!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Commands: /save filename, /clear, /stats, /help")
    
    # Problem #4: File operations mixed with main logic
    if os.path.exists(CONVERSATION_FILE):
        try:
            with open(CONVERSATION_FILE, 'r') as f:
                conversation_history = json.load(f)
            print(f"Loaded {len(conversation_history)} previous conversations.")
        except Exception as e:
            print(f"Could not load conversation history: {e}")
            conversation_history = []
    
    # Problem #5: API setup mixed with business logic
    if API_KEY == "your-api-key-here":
        print("ERROR: Please set your OpenAI API key in the script!")
        return
    
    openai.api_key = API_KEY
    
    # Problem #6: Main interaction loop doing everything
    while True:
        try:
            user_input = input("\\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            
            # Problem #7: Command handling mixed with main loop
            if user_input.lower().startswith('/save '):
                filename = user_input[6:].strip()
                if not filename:
                    print("Please specify a filename: /save filename.json")
                    continue
                try:
                    with open(filename, 'w') as f:
                        json.dump(conversation_history, f, indent=2)
                    print(f"Conversation saved to {filename}")
                except Exception as e:
                    print(f"Error saving file: {e}")
                continue
            
            if user_input.lower() == '/clear':
                conversation_history = []
                print("Conversation cleared")
                continue
            
            if user_input.lower() == '/stats':
                print(f"API calls made: {api_call_count}")
                print(f"Conversation length: {len(conversation_history)}")
                print(f"Model: {MODEL}")
                continue
                
            if user_input.lower() == '/help':
                print("Available commands:")
                print("  /save filename - Save conversation to file")
                print("  /clear - Clear conversation history")  
                print("  /stats - Show usage statistics")
                print("  /help - Show this help message")
                print("  quit/exit/bye - End conversation")
                continue
            
            # Problem #8: AI interaction logic mixed with everything else
            # Build context from conversation history
            messages = [{"role": "system", "content": "You are a helpful AI assistant for a marketing consultant."}]
            
            # Add recent conversation history (last 20 exchanges to manage token limits)
            recent_history = conversation_history[-20:] if len(conversation_history) > 20 else conversation_history
            
            for exchange in recent_history:
                messages.append({"role": "user", "content": exchange["user"]})
                messages.append({"role": "assistant", "content": exchange["assistant"]})
            
            messages.append({"role": "user", "content": user_input})
            
            # Problem #9: Minimal error handling - Production systems need robust error management
            try:
                response = openai.ChatCompletion.create(
                    model=MODEL,
                    messages=messages,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
                
                assistant_response = response.choices[0].message.content
                api_call_count += 1
                
                print(f"\\nAI: {assistant_response}")
                
                # Problem #10: Data persistence logic scattered throughout
                conversation_history.append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "user": user_input,
                    "assistant": assistant_response
                })
                
                # Auto-save conversation (no error handling for file operations)
                try:
                    with open(CONVERSATION_FILE, 'w') as f:
                        json.dump(conversation_history, f, indent=2)
                except:
                    print("Warning: Could not save conversation")
                    
            except openai.error.RateLimitError:
                print("Rate limit exceeded. Please wait a moment and try again.")
            except openai.error.APIError as e:
                print(f"OpenAI API error: {e}")
            except openai.error.InvalidRequestError as e:
                print(f"Invalid request: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                print("Please try again.")
        
        except KeyboardInterrupt:
            print("\\n\\nGoodbye!")
            break
        except Exception as e:
            print(f"\\nUnexpected error in main loop: {e}")
            print("Continuing...")
    
    print("\\nGoodbye! Your conversation has been saved.")

# Problem #11: No clear module structure or reusability
if __name__ == "__main__":
    main()

"""
PROBLEMS SUMMARY FOR STUDENTS TO IDENTIFY:

1. Security Issues:
   - Hardcoded API key in source code
   - No environment variable usage

2. Code Organization:
   - All functionality in single file and function
   - Mixed responsibilities (UI, API, file operations, configuration)
   - No separation of concerns

3. Error Handling:
   - Minimal error handling
   - No graceful degradation
   - Poor user feedback for errors

4. State Management:
   - Global variables for application state
   - No encapsulation or data protection

5. Testing Challenges:
   - Cannot test individual components
   - Dependencies are tightly coupled
   - No mocking capabilities

6. Maintenance Issues:
   - Hard to add new features
   - Difficult to debug problems
   - Cannot reuse components

7. Collaboration Problems:
   - Single file conflicts in version control
   - No clear ownership of functionality
   - Cannot divide work among team members

8. Scalability Limitations:
   - File becomes unwieldy as features grow
   - Performance optimization difficult
   - Cannot easily add new interfaces (web, API, etc.)

This script works for basic functionality but demonstrates why professional
applications require proper architectural planning and modular design.
"""