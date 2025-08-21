# Common Errors and Debugging Guide

## Import Errors

### Error: `ModuleNotFoundError: No module named 'config'`

**Level 1 Hint**: This is a Python package structure issue. Think about what files Python needs to recognize directories as packages.

**Level 2 Hint**: You need `__init__.py` files in each directory to make them proper Python packages. Check if you have them in all your module directories.

**Level 3 Solution**: Create empty `__init__.py` files in:
```
refactored_app/__init__.py
refactored_app/config/__init__.py
refactored_app/core/__init__.py  
refactored_app/conversation/__init__.py
```

### Error: `ModuleNotFoundError: No module named 'refactored_app'`

**Level 1 Hint**: Python can't find your package. This is about where Python is looking for modules.

**Level 2 Hint**: You might need to run your code from the right directory or adjust your Python path.

**Level 3 Solution**: 
- Run your code from the directory containing `refactored_app/`
- Or add the parent directory to your Python path
- Or use relative imports properly

## Configuration Errors

### Error: `ValueError: OPENAI_API_KEY environment variable is required`

**Level 1 Hint**: Your application needs an API key to work. Where should this come from?

**Level 2 Hint**: Environment variables need to be set before running your Python application. Think about how you set environment variables in your terminal.

**Level 3 Solution**:
```bash
# On Linux/Mac:
export OPENAI_API_KEY='your-key-here'

# On Windows:
set OPENAI_API_KEY=your-key-here

# Or create a .env file with:
OPENAI_API_KEY=your-key-here
```

### Error: `AttributeError: 'Settings' object has no attribute 'openai_api_key'`

**Level 1 Hint**: The Settings class isn't loading configuration properly. Check your `__post_init__` method.

**Level 2 Hint**: Make sure your Settings class is properly initializing and the `__post_init__` method is being called.

**Level 3 Solution**: Verify your Settings dataclass has:
```python
def __post_init__(self):
    self.openai_api_key = os.getenv('OPENAI_API_KEY')
    if not self.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
```

## API Client Errors

### Error: `openai.error.AuthenticationError: Incorrect API key`

**Level 1 Hint**: The API key you're using isn't valid. Double-check your key.

**Level 2 Hint**: Make sure you're using the correct API key format and that it hasn't been revoked.

**Level 3 Solution**: 
- Verify your API key is correct (starts with 'sk-')
- Check that you haven't accidentally included extra spaces or characters
- Ensure the key hasn't been revoked in your OpenAI dashboard

### Error: `AttributeError: 'AIClient' object has no attribute 'model'`

**Level 1 Hint**: Your AIClient isn't initializing properly. Check your `__init__` method.

**Level 2 Hint**: Make sure you're setting all the instance variables in the AIClient constructor.

**Level 3 Solution**: In your AIClient `__init__` method:
```python
def __init__(self):
    openai.api_key = settings.openai_api_key
    self.model = settings.model_name  # Make sure this line exists
    self.max_tokens = settings.max_tokens
    self.temperature = settings.temperature
```

## Conversation Manager Errors

### Error: `TypeError: list indices must be integers or slices, not str`

**Level 1 Hint**: You're trying to access a list item using a string key instead of an integer index.

**Level 2 Hint**: Check how you're accessing message data. Are you treating a list like a dictionary?

**Level 3 Solution**: Make sure you're accessing message dictionaries correctly:
```python
# Correct:
for msg in self.messages:
    role = msg["role"]  # msg is a dictionary
    
# Incorrect:
role = self.messages["role"]  # messages is a list, not a dictionary
```

### Error: `KeyError: 'timestamp'`

**Level 1 Hint**: You're trying to access a key that doesn't exist in your message dictionary.

**Level 2 Hint**: Check that you're adding timestamps when creating messages, or handle the case when they don't exist.

**Level 3 Solution**: Either ensure timestamps are always added:
```python
def add_user_message(self, content: str):
    self.messages.append({
        "role": "user",
        "content": content,
        "timestamp": datetime.now().isoformat()  # Make sure this is here
    })
```

Or handle missing timestamps gracefully:
```python
timestamp = msg.get("timestamp", "unknown")
```

## Application Flow Errors

### Error: `RecursionError: maximum recursion depth exceeded`

**Level 1 Hint**: Something is calling itself repeatedly without stopping. Look for infinite loops or recursive calls.

**Level 2 Hint**: Check your main loop and command handling. Make sure you're not accidentally calling methods that call themselves.

**Level 3 Solution**: Review your control flow:
```python
# Make sure your main loop has proper exit conditions
while self.running:
    # Process input
    # Handle commands (make sure /quit actually sets self.running = False)
    # Don't accidentally call run() from within run()
```

### Error: Application hangs and doesn't respond

**Level 1 Hint**: Your application might be waiting for input that never comes, or stuck in an infinite loop.

**Level 2 Hint**: Check your while loops and input handling. Make sure there are proper exit conditions.

**Level 3 Solution**: Add debug prints to see where your application gets stuck:
```python
print("Starting main loop...")
while self.running:
    print("Waiting for input...")
    user_input = input("You: ")
    print(f"Received: {user_input}")
    # ... rest of processing
```

## File and Path Errors

### Error: `FileNotFoundError: [Errno 2] No such file or directory: 'starter_code/sarahs_chaotic_script.py'`

**Level 1 Hint**: Python can't find the file you're trying to read. Check the file path and your current working directory.

**Level 2 Hint**: File paths are relative to where you run your Python script. Make sure you're running from the right directory.

**Level 3 Solution**: Either:
- Run your script from the lab directory containing `starter_code/`
- Use absolute paths
- Check the file actually exists: `ls starter_code/` or `dir starter_code\`

## JSON and Data Errors

### Error: `json.JSONDecodeError: Expecting ',' delimiter`

**Level 1 Hint**: Your JSON data isn't properly formatted. There's likely a syntax error.

**Level 2 Hint**: Check for missing commas, extra commas, or malformed JSON structure when saving conversation data.

**Level 3 Solution**: Use proper JSON formatting:
```python
# Correct JSON structure
session_data = {
    "session_start": self.session_start.isoformat(),
    "messages": self.messages,  # Note the comma
    "message_count": len(self.messages)  # No comma on last item
}
```

## General Debugging Tips

### 1. Read the Error Message Carefully
- The error type tells you what went wrong
- The line number shows you where
- The message often explains what to fix

### 2. Use Print Debugging
```python
print(f"Variable value: {variable}")
print(f"Type: {type(variable)}")
print(f"Length: {len(variable)}" if hasattr(variable, '__len__') else "No length")
```

### 3. Check Your Assumptions
- Are variables the type you think they are?
- Do files exist where you think they do?
- Are you running from the right directory?

### 4. Isolate the Problem
- Comment out sections of code to narrow down the issue
- Test each module individually
- Use the testing framework to validate components

Remember: Every error is a learning opportunity. Understanding why something broke makes you a better programmer!