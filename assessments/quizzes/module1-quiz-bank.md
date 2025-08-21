# Module 1 Quiz Bank: LLM Application Foundations

## Quiz 1.1: Code Organization Principles

### Question 1.1.1 - Knowledge Check
**QUESTION TYPE**: Multiple Choice
**LEARNING OBJECTIVE**: M1-LO1 - Analyze differences between script-based and application-based code organization
**DIFFICULTY**: Beginner

**QUESTION**: Which of the following is the primary difference between a script and an application?

**OPTIONS**:
A) Scripts are written in Python, applications are written in other languages
B) Scripts perform single tasks in one file, applications organize functionality across multiple modules
C) Scripts use functions, applications use classes
D) Scripts are for beginners, applications are for experts

**CORRECT ANSWER**: B

**FEEDBACK**:
- **Correct**: Exactly right! Scripts typically contain all functionality in a single file for one-time use, while applications organize code into reusable modules with clear separation of concerns.
- **Option A**: Incorrect. Both scripts and applications can be written in Python or any programming language. The difference is in organization, not language choice.
- **Option C**: Incorrect. Both scripts and applications can use functions and classes. The key difference is modular organization and reusability.
- **Option D**: Incorrect. The complexity level isn't the defining factor. Professional developers write both scripts (for automation) and applications (for users).

---

### Question 1.1.2 - Code Review Scenario
**QUESTION TYPE**: Code Review
**LEARNING OBJECTIVE**: M1-LO1 - Analyze differences between script-based and application-based code organization
**DIFFICULTY**: Intermediate

**QUESTION**: Review this AI assistant code. Identify the THREE main organizational problems that prevent this from being a professional application:

```python
import openai
import json
import os

openai.api_key = "sk-1234567890abcdef"  # API key hardcoded

def main():
    print("AI Assistant v1.0")
    
    conversation_history = []
    
    while True:
        user_input = input("You: ")
        if user_input == "quit":
            break
        
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=conversation_history,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            print(f"AI: {ai_response}")
            
            # Save conversation
            with open("conversations.json", "w") as f:
                json.dump(conversation_history, f)
                
        except Exception as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    main()
```

**OPTIONS** (Select 3):
A) API key is hardcoded instead of using environment variables
B) All functionality is in a single function instead of being modular
C) No proper error handling for specific API failure types
D) Uses Python instead of a compiled language
E) File operations are mixed with API logic instead of being separated
F) The conversation history grows indefinitely without memory management

**CORRECT ANSWERS**: A, B, E

**FEEDBACK**:
- **A - Correct**: Hardcoded API keys are a major security issue and prevent code sharing. Should use environment variables or configuration files.
- **B - Correct**: The main() function handles user interface, API communication, file operations, and conversation management. This should be split into separate modules.
- **C - Partially correct**: While better error handling would improve the code, the basic try-catch is functional for a simple script.
- **D - Incorrect**: Python is perfectly appropriate for AI applications. Language choice isn't the organizational issue here.
- **E - Correct**: File saving logic is embedded within the conversation loop. This should be extracted to a separate conversation management module.
- **F - Partially correct**: Memory management could be improved, but this is an optimization issue rather than a fundamental organizational problem.

---

### Question 1.1.3 - Application Design
**QUESTION TYPE**: Design Challenge
**LEARNING OBJECTIVE**: M1-LO2 - Create modular Python applications with proper function and class structure
**DIFFICULTY**: Intermediate

**QUESTION**: You're tasked with refactoring the code from Question 1.1.2 into a modular application. Design the module structure by matching each responsibility to the appropriate module name:

**RESPONSIBILITIES**:
1. Managing API keys and application settings
2. Handling OpenAI API communication and error recovery
3. Saving and loading conversation history
4. Managing user interface and input/output
5. Orchestrating the overall application flow

**MODULE OPTIONS**:
A) `config.py`
B) `ai_client.py`
C) `conversation_manager.py`
D) `user_interface.py`
E) `main.py`

**CORRECT MAPPING**:
1 → A (config.py)
2 → B (ai_client.py)
3 → C (conversation_manager.py)
4 → D (user_interface.py)
5 → E (main.py)

**FEEDBACK**: 
Excellent modular design! Each module has a single, clear responsibility:
- `config.py` centralizes configuration management
- `ai_client.py` handles all API interactions
- `conversation_manager.py` manages data persistence
- `user_interface.py` handles user interactions
- `main.py` orchestrates the application flow

This separation allows for easy testing, maintenance, and feature additions.

---

## Quiz 1.2: Object-Oriented Programming for AI

### Question 1.2.1 - Concept Understanding
**QUESTION TYPE**: Multiple Choice
**LEARNING OBJECTIVE**: M1-LO2 - Create modular Python applications with proper function and class structure
**DIFFICULTY**: Beginner

**QUESTION**: When should you use a class instead of functions for an AI application component?

**OPTIONS**:
A) Always - classes are more professional than functions
B) When you need to maintain state across multiple interactions
C) When working with AI APIs - they require object-oriented code
D) Never - functions are simpler and always preferred

**CORRECT ANSWER**: B

**FEEDBACK**:
- **Correct**: Classes are ideal when you need to maintain state (like conversation history, user preferences, or API configurations) across multiple method calls.
- **Option A**: Incorrect. Neither approach is inherently more "professional." Choose based on requirements, not perceived sophistication.
- **Option C**: Incorrect. AI APIs work fine with both functional and object-oriented approaches. The choice depends on your application's needs.
- **Option D**: Incorrect. While functions are often simpler, classes provide important benefits for state management and complex functionality.

---

### Question 1.2.2 - Code Implementation
**QUESTION TYPE**: Code Completion
**LEARNING OBJECTIVE**: M1-LO2 - Create modular Python applications with proper function and class structure
**DIFFICULTY**: Intermediate

**QUESTION**: Complete the AIAssistant class to properly maintain conversation history and user preferences:

```python
class AIAssistant:
    def __init__(self, api_key, user_name="User"):
        self.api_client = APIClient(api_key)
        self.user_name = user_name
        # TODO: Add conversation history storage
        # TODO: Add user preferences storage
    
    def chat(self, message):
        # TODO: Add message to conversation history
        # TODO: Get AI response using conversation context
        # TODO: Add AI response to conversation history
        # TODO: Return the response
        pass
    
    def set_preference(self, key, value):
        # TODO: Store user preference
        pass
    
    def get_conversation_length(self):
        # TODO: Return number of conversation exchanges
        pass
```

**SAMPLE SOLUTION**:
```python
class AIAssistant:
    def __init__(self, api_key, user_name="User"):
        self.api_client = APIClient(api_key)
        self.user_name = user_name
        self.conversation_history = []  # Store message exchanges
        self.user_preferences = {}      # Store user settings
    
    def chat(self, message):
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Get AI response with conversation context
        response = self.api_client.send_message(message, self.conversation_history)
        
        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def set_preference(self, key, value):
        self.user_preferences[key] = value
    
    def get_conversation_length(self):
        # Count user messages (conversation exchanges)
        return len([msg for msg in self.conversation_history if msg["role"] == "user"])
```

**ASSESSMENT CRITERIA**:
- **Excellent (4 points)**: Correctly implements all methods with proper state management
- **Good (3 points)**: Implements most methods correctly with minor issues
- **Satisfactory (2 points)**: Basic implementation with some functionality missing
- **Needs Improvement (1 point)**: Minimal implementation or major errors

---

## Quiz 1.3: Error Handling and Robustness

### Question 1.3.1 - Scenario Analysis
**QUESTION TYPE**: Scenario
**LEARNING OBJECTIVE**: M1-LO4 - Apply error handling and logging in AI applications
**DIFFICULTY**: Intermediate

**QUESTION**: Your AI application is deployed and users report it "randomly crashes." You investigate and find these error patterns:

1. "Connection timeout" errors during peak hours
2. "Invalid API key" errors from some users
3. "Rate limit exceeded" errors on weekends
4. "Unexpected response format" errors after AI model updates

Match each error type to the most appropriate handling strategy:

**ERROR TYPES**:
A) Connection timeout errors
B) Invalid API key errors  
C) Rate limit exceeded errors
D) Unexpected response format errors

**HANDLING STRATEGIES**:
1. Retry with exponential backoff (wait 1s, 2s, 4s...)
2. Prompt user to check/update credentials
3. Wait and retry automatically with user notification
4. Log error details and provide graceful fallback response

**CORRECT MAPPING**:
A → 1 (Retry with exponential backoff)
B → 2 (Prompt user to check credentials)
C → 3 (Wait and retry with notification)
D → 4 (Log and fallback)

**FEEDBACK**:
Perfect error handling strategy! Each error type requires a different approach:
- **Connection timeouts**: Often temporary network issues, retry makes sense
- **Invalid credentials**: User action required, can't be fixed automatically
- **Rate limits**: Temporary restriction, automatic retry with user awareness
- **Format changes**: Unexpected issues requiring investigation and graceful degradation

---

### Question 1.3.2 - Code Review
**QUESTION TYPE**: Code Review
**LEARNING OBJECTIVE**: M1-LO4 - Apply error handling and logging in AI applications
**DIFFICULTY**: Advanced

**QUESTION**: Review this error handling code. Identify what's wrong and explain how to improve it:

```python
def chat_with_ai(message):
    try:
        response = api_client.send_message(message)
        return response
    except:
        return "Error occurred"
```

**ISSUES** (Select all that apply):
A) Catches all exceptions instead of specific ones
B) Doesn't log error details for debugging
C) Provides no useful information to users
D) Doesn't attempt recovery or retry
E) Missing input validation

**CORRECT ANSWERS**: A, B, C, D

**IMPROVED VERSION**:
```python
import logging
import time
from requests.exceptions import ConnectionError, HTTPError, Timeout

def chat_with_ai(message, max_retries=3):
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    for attempt in range(max_retries):
        try:
            response = api_client.send_message(message)
            return response
            
        except ConnectionError as e:
            logging.warning(f"Connection error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return "I'm having trouble connecting. Please check your internet connection and try again."
                
        except HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                logging.info("Rate limited, waiting before retry")
                time.sleep(10)
                continue
            elif e.response.status_code == 401:  # Unauthorized
                logging.error("API authentication failed")
                return "Please check your API credentials in settings."
            else:
                logging.error(f"HTTP error {e.response.status_code}: {e}")
                return f"Service temporarily unavailable. Please try again later."
                
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again or contact support."
```

**FEEDBACK**: The improved version addresses all issues by using specific exception handling, comprehensive logging, helpful user messages, and retry logic with exponential backoff.

---

## Quiz 1.4: User Interface Design

### Question 1.4.1 - CLI Design Principles
**QUESTION TYPE**: Multiple Choice
**LEARNING OBJECTIVE**: M1-LO5 - Design user interfaces for AI tools using Gradio
**DIFFICULTY**: Beginner

**QUESTION**: Which CLI argument pattern follows professional conventions for an AI assistant tool?

**OPTIONS**:
A) `python assistant.py "tell me about quantum computing" --output=file.txt`
B) `python assistant.py --message "tell me about quantum computing" --output file.txt`
C) `python assistant.py -m "tell me about quantum computing" -o file.txt`
D) Both B and C are correct

**CORRECT ANSWER**: D

**FEEDBACK**:
- **Correct**: Professional CLI tools provide both long-form (`--message`, `--output`) and short-form (`-m`, `-o`) options for user convenience.
- **Option A**: While functional, using positional arguments for long text can be problematic with shell escaping and is less explicit.
- **Options B & C individually**: Both are correct patterns, but the best practice is supporting both formats.

---

### Question 1.4.2 - Gradio Interface Design
**QUESTION TYPE**: Design Challenge
**LEARNING OBJECTIVE**: M1-LO5 - Design user interfaces for AI tools using Gradio
**DIFFICULTY**: Intermediate

**QUESTION**: Design a Gradio interface for a document analysis AI tool. Match each UI component to its most appropriate Gradio element:

**REQUIREMENTS**:
1. Upload PDF, Word, or text files
2. Select analysis type (Summary, Key Points, Questions)
3. Adjust response length (Short, Medium, Long)
4. Display analysis results with formatting
5. Download results as a text file

**GRADIO COMPONENTS**:
A) `gr.File(file_types=[".pdf", ".docx", ".txt"])`
B) `gr.Radio(choices=["Summary", "Key Points", "Questions"])`
C) `gr.Slider(minimum=100, maximum=1000, step=100)`
D) `gr.Markdown()`
E) `gr.DownloadButton()`

**CORRECT MAPPING**:
1 → A (File upload with type restrictions)
2 → B (Radio buttons for mutually exclusive options)
3 → C (Slider for numeric range)
4 → D (Markdown for formatted text display)
5 → E (Download button for file export)

**ALTERNATIVE CONSIDERATIONS**:
- **Requirement 3** could also use `gr.Dropdown(choices=["Short", "Medium", "Long"])` for discrete options
- **Requirement 4** could use `gr.Textbox(lines=10)` for plain text display
- **Requirement 2** could use `gr.Dropdown()` if many analysis types exist

**FEEDBACK**: Excellent interface design! Your choices provide intuitive user interactions while maintaining professional functionality. The file type restrictions and formatted output enhance user experience.

---

## Quiz 1.5: Testing and Quality Assurance

### Question 1.5.1 - Testing Strategy
**QUESTION TYPE**: Multiple Choice
**LEARNING OBJECTIVE**: M1-LO3 - Evaluate code quality using professional development standards
**DIFFICULTY**: Intermediate

**QUESTION**: When testing an AI application that calls external APIs, which testing approach is most appropriate for unit tests?

**OPTIONS**:
A) Make real API calls to ensure everything works
B) Use mock objects to simulate API responses
C) Skip testing API-related functions since they're external
D) Only test functions that don't involve APIs

**CORRECT ANSWER**: B

**FEEDBACK**:
- **Correct**: Mock objects allow you to test your application logic without depending on external services, making tests fast, reliable, and free.
- **Option A**: Real API calls make tests slow, expensive, unreliable (network issues), and difficult to test error scenarios.
- **Option C**: API integration logic is critical and must be tested, just not with real external calls.
- **Option D**: This leaves major functionality untested, creating a false sense of security.

---

### Question 1.5.2 - Test Implementation
**QUESTION TYPE**: Code Completion
**LEARNING OBJECTIVE**: M1-LO3 - Evaluate code quality using professional development standards
**DIFFICULTY**: Advanced

**QUESTION**: Complete this unit test for the AIAssistant class to test error handling:

```python
import unittest
from unittest.mock import patch, Mock
from ai_assistant import AIAssistant, APIError

class TestAIAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant = AIAssistant(api_key="test_key")
    
    @patch('ai_assistant.APIClient.send_message')
    def test_api_error_handling(self, mock_send):
        # TODO: Set up mock to raise an APIError
        # TODO: Call the chat method
        # TODO: Assert that error is handled gracefully
        # TODO: Assert that conversation history is not corrupted
        pass
```

**SAMPLE SOLUTION**:
```python
@patch('ai_assistant.APIClient.send_message')
def test_api_error_handling(self, mock_send):
    # Set up mock to raise an APIError
    mock_send.side_effect = APIError("API service unavailable")
    
    # Call the chat method
    response = self.assistant.chat("Hello")
    
    # Assert that error is handled gracefully
    self.assertIn("trouble", response.lower())
    self.assertNotIn("APIError", response)  # User shouldn't see technical errors
    
    # Assert that conversation history is not corrupted
    self.assertEqual(len(self.assistant.conversation_history), 1)  # Only user message
    self.assertEqual(self.assistant.conversation_history[0]["role"], "user")
```

**ASSESSMENT CRITERIA**:
- **Excellent**: Properly mocks exception, tests graceful handling, verifies state consistency
- **Good**: Tests error handling with minor issues in assertion details
- **Satisfactory**: Basic error testing with some missing verification
- **Needs Improvement**: Minimal testing or incorrect mock usage

---

## Module 1 Comprehensive Assessment Quiz

### Question 1.C.1 - Integration Challenge
**QUESTION TYPE**: Scenario
**LEARNING OBJECTIVE**: Multiple (M1-LO1, M1-LO2, M1-LO4, M1-LO5)
**DIFFICULTY**: Advanced

**QUESTION**: You're building an AI-powered customer service application. Based on Module 1 principles, identify the correct implementation approach for each requirement:

**REQUIREMENTS & CHOICES**:

1. **Code Organization**: How should you structure the application?
   - A) Single file with all functionality
   - B) Separate modules for API handling, UI, data storage, and configuration
   - C) One class that handles everything

2. **Error Handling**: A customer reports the app crashes when their internet is slow. What's the best solution?
   - A) Tell customers to use faster internet
   - B) Add timeout handling with retry logic and user feedback
   - C) Remove error handling to make the app faster

3. **User Interface**: The app needs both technical and non-technical users. What should you provide?
   - A) Only a command-line interface for efficiency
   - B) Only a web interface for simplicity
   - C) Both CLI for power users and web interface for general users

4. **Testing**: How should you test the AI integration?
   - A) Only test with real AI APIs to ensure accuracy
   - B) Use mocks for unit tests, real APIs for integration tests
   - C) Don't test AI components since they change frequently

**CORRECT ANSWERS**: 1-B, 2-B, 3-C, 4-B

**FEEDBACK**: 
Perfect application of Module 1 principles! You've demonstrated understanding of:
- **Modular design** for maintainable, scalable applications
- **Robust error handling** that provides excellent user experience
- **Multi-interface design** that serves different user needs
- **Comprehensive testing** that balances reliability with practicality

This approach creates professional-quality applications that can scale and adapt to changing requirements.

---

## Quiz Metadata

**Total Questions**: 12 knowledge checks + 1 comprehensive assessment
**Estimated Completion Time**: 45-60 minutes
**Alignment with Learning Objectives**: 100% coverage of Module 1 LOs
**Difficulty Distribution**: 
- Beginner: 4 questions (33%)
- Intermediate: 7 questions (58%)
- Advanced: 2 questions (17%)

**Assessment Criteria Integration**:
- **Functionality**: Questions test working knowledge of implementation
- **Code Quality**: Questions emphasize professional practices and organization
- **User Experience**: Questions address interface design and error handling
- **Technical Implementation**: Questions cover industry best practices
- **Documentation**: Questions include code clarity and communication