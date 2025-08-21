# Module 1.2: Object-Oriented Programming for AI - Script

**TITLE**: Building an AI Assistant Class
**MODULE**: 1.2 | **DURATION**: 4:50 | **TYPE**: Concept + Live Coding
**SETUP**: VS Code with previous module's code, new file ready for class creation

---

## SCRIPT

**[VISUAL: VS Code showing the modular code from previous lesson]**
**[00:00 - 00:25]**

**SCRIPT**: "Our code is much better organized now, but let's take it to the next level. Sometimes you need more than just functions - you need to keep track of state, manage complex interactions, and create reusable components. This is where classes come in. Today we'll build an AI Assistant class that demonstrates when and why object-oriented programming makes your AI applications more powerful."

**[VISUAL: Comparison between functions and classes for AI applications]**
**[00:25 - 00:55]**

**SCRIPT**: "Think about the difference between a calculator and a personal assistant. A calculator performs one operation at a time - you give it numbers, it gives you an answer. That's like a function. But a personal assistant remembers your preferences, learns from your interactions, and maintains context across conversations. That's more like a class - it has both behavior and memory."

**[VISUAL: Live coding - creating the AIAssistant class structure]**
**[00:55 - 01:35]**

**SCRIPT**: "Let's build this together. I'm creating a class called AIAssistant. Notice how I start with the __init__ method - this is where we set up the assistant's initial state. We're storing the API client, user preferences, and conversation history. This is the 'memory' that makes our assistant more than just a collection of functions."

```python
class AIAssistant:
    def __init__(self, api_key, user_name="User"):
        self.api_client = APIClient(api_key)
        self.user_name = user_name
        self.conversation_history = []
        self.user_preferences = {}
```

**[VISUAL: Adding methods that use and modify the instance state]**
**[01:35 - 02:15]**

**SCRIPT**: "Now let's add methods that make use of this state. The chat method doesn't just send a message to the API - it remembers the conversation, personalizes responses using the user's name, and can reference previous interactions. This is something you can't easily do with standalone functions."

**[VISUAL: Demonstrating state management with conversation history]**
**[02:15 - 02:45]**

**SCRIPT**: "Watch what happens when I call the chat method multiple times. The assistant remembers our previous conversation. When I ask 'What did I just ask you about?', it can reference the conversation history stored in the instance. This persistent state is what makes classes powerful for AI applications."

**[VISUAL: Adding personalization features using stored preferences]**
**[02:45 - 03:15]**

**SCRIPT**: "Let's add personalization. The assistant can learn and store user preferences - maybe you prefer technical explanations, or you're working on a specific project. These preferences are remembered across sessions and influence how the AI responds. Try doing this with standalone functions - it gets messy quickly."

**[VISUAL: Creating specialized AI assistant classes through inheritance]**
**[03:15 - 03:50]**

**SCRIPT**: "Here's where it gets really powerful. We can create specialized assistants using inheritance. A WritingAssistant inherits all the basic functionality but adds methods for grammar checking and style analysis. A CodeAssistant adds methods for code review and debugging. Each specialized class builds on the foundation without duplicating code."

**[VISUAL: Side-by-side comparison of function-based vs class-based approach]**
**[03:50 - 04:20]**

**SCRIPT**: "Compare our class-based approach to the function-based version. With functions, we'd have to pass conversation history and preferences to every function call. With classes, this state is managed automatically. The code is cleaner, the functionality is more sophisticated, and extending it is straightforward."

**[VISUAL: Demonstrating when NOT to use classes]**
**[04:20 - 04:40]**

**SCRIPT**: "Important note - not everything needs to be a class. Simple utility functions for text processing or file operations work fine as functions. Use classes when you need to maintain state, when you have complex interactions between data and behavior, or when you want to create multiple instances with different configurations."

**[VISUAL: Preview of next lesson on error handling]**
**[04:40 - 04:50]**

**SCRIPT**: "Next, we'll make our AI Assistant bulletproof by adding comprehensive error handling. You'll learn how professionals handle the inevitable API failures and unexpected user inputs."

---

## ACCESSIBILITY NOTES
- Class concepts explained with real-world analogies
- Code structure clearly described during live coding
- State management concepts explained verbally
- Inheritance relationships described with clear examples

## TECHNICAL REQUIREMENTS
- VS Code with Python syntax highlighting
- Previous lesson's modular code available
- Live coding environment ready
- Multiple terminal windows for testing different assistant instances