# Module 1.1: Code Organization Principles - Script

**TITLE**: From Script Chaos to Application Structure
**MODULE**: 1.1 | **DURATION**: 4:45 | **TYPE**: Concept + Demo
**SETUP**: VS Code with example script open, terminal ready, file explorer visible

---

## SCRIPT

**[VISUAL: VS Code showing a 200-line monolithic AI script]**
**[00:00 - 00:20]**

**SCRIPT**: "Take a look at this script. It's actually functional - it connects to an AI API, processes user input, handles some file operations, and generates output. But there's a problem. Can you spot it? This is what we call 'script chaos' - everything mixed together in one giant file."

**[VISUAL: Highlighting different sections of the script that serve different purposes]**
**[00:20 - 00:50]**

**SCRIPT**: "Let's analyze what's happening here. We have API connection logic mixed with user input handling, file processing scattered throughout, and configuration values hardcoded everywhere. This works for a quick proof of concept, but what happens when you want to add features? Or when someone else needs to understand your code?"

**[VISUAL: Diagram showing the problems with monolithic code]**
**[00:50 - 01:20]**

**SCRIPT**: "Monolithic scripts create four major problems. First, debugging becomes a nightmare - when something breaks, you have to hunt through the entire file. Second, reusing code is impossible - everything is tangled together. Third, collaboration is difficult - multiple people can't work on the same script. And finally, testing is nearly impossible - you can't easily test individual pieces."

**[VISUAL: Split screen showing the same functionality organized into logical modules]**
**[01:20 - 01:50]**

**SCRIPT**: "Here's the same functionality, but organized using professional principles. Notice how we have separate modules for API handling, user interface, file operations, and configuration. Each module has a single, clear responsibility. This is called 'separation of concerns' - one of the most important concepts in professional development."

**[VISUAL: Live demonstration of creating the api_client.py module]**
**[01:50 - 02:30]**

**SCRIPT**: "Let's practice this together. I'll extract the API handling code into its own module. Watch how I identify all the code related to API communication, create a new file called 'api_client.py', and move the related functions. Notice how I'm also creating a clear interface - other parts of the application don't need to know how the API works, they just need to call our functions."

**[VISUAL: Creating the config.py module with proper configuration management]**
**[02:30 - 03:00]**

**SCRIPT**: "Next, let's handle configuration. Instead of hardcoded values scattered throughout, we create a dedicated config module. This makes it easy to change settings without hunting through code, and it provides a single place to manage API keys, file paths, and user preferences."

**[VISUAL: Demonstrating the user_interface.py module extraction]**
**[03:00 - 03:30]**

**SCRIPT**: "The user interface logic gets its own module too. This separation is crucial because you might want multiple interfaces - command line, web, maybe even a mobile app someday. By keeping the interface separate from the business logic, you make all of these possibilities easier."

**[VISUAL: File structure view showing the organized application]**
**[03:30 - 04:00]**

**SCRIPT**: "Look at our final structure. We have main.py as the entry point, api_client.py for AI interactions, config.py for settings, user_interface.py for user interactions, and file_operations.py for data handling. Each file has a clear purpose, and the relationships between them are obvious."

**[VISUAL: Running the refactored application to show it works the same]**
**[04:00 - 04:30]**

**SCRIPT**: "The beautiful thing is that our application works exactly the same from the user's perspective, but now it's maintainable, testable, and ready for enhancement. When you want to add a new feature, you know exactly where it belongs. When something breaks, you know where to look."

**[VISUAL: Preview of the next lesson on object-oriented programming]**
**[04:30 - 04:45]**

**SCRIPT**: "In our next lesson, we'll take this further by exploring when and how to use classes to organize your code even better. You'll learn to think like a professional developer about application architecture."

---

## ACCESSIBILITY NOTES
- Code structure diagrams include detailed descriptions
- File organization is explained verbally alongside visual demonstration
- Color-coded sections have corresponding text labels
- Screen reader users receive detailed descriptions of file structures

## TECHNICAL REQUIREMENTS
- VS Code with file explorer visible
- Example monolithic script prepared
- Multiple Python files ready for demonstration
- Terminal for testing refactored code