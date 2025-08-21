# Module 1.4: Command Line Interfaces - Script

**TITLE**: Building Professional CLI Tools for AI Applications
**MODULE**: 1.4 | **DURATION**: 4:40 | **TYPE**: Live Coding + Demo
**SETUP**: VS Code with argparse examples, terminal ready, sample CLI tools for reference

---

## SCRIPT

**[VISUAL: Comparing amateur vs professional command-line tools]**
**[00:00 - 00:30]**

**SCRIPT**: "Every developer loves a good command-line tool. But there's a huge difference between amateur scripts that ask for input step by step, and professional CLI tools that accept arguments, provide help, and integrate seamlessly with other tools. Today we're transforming our AI Assistant into a professional command-line interface that power users will love."

**[VISUAL: Examples of popular CLI tools and their argument patterns]**
**[00:30 - 01:00]**

**SCRIPT**: "Think about the CLI tools you use - git, pip, docker. They all follow similar patterns. They accept commands and options, provide helpful error messages, and include comprehensive help systems. These patterns exist because they work. We're going to implement these same patterns for our AI applications."

**[VISUAL: Live coding - setting up argparse for the AI Assistant]**
**[01:00 - 01:45]**

**SCRIPT**: "Python's argparse module makes building professional CLIs straightforward. Watch as I create a command-line interface for our AI Assistant. I'm defining positional arguments for the user's message, optional arguments for different modes, and flags for various features. Notice how I'm providing descriptions for each argument - this becomes the help text."

```python
import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        description="Personal AI Assistant - Your intelligent command-line companion",
        epilog="Examples:\n  %(prog)s 'What is machine learning?'\n  %(prog)s --file input.txt --output response.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('message', nargs='?', help='Your message to the AI assistant')
    parser.add_argument('--file', '-f', help='Read input from file')
    parser.add_argument('--output', '-o', help='Write response to file')
    parser.add_argument('--model', choices=['gpt-4', 'claude', 'gemini'], default='gpt-4')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    return parser
```

**[VISUAL: Demonstrating the automatic help generation]**
**[01:45 - 02:15]**

**SCRIPT**: "Here's the magic - argparse automatically generates beautiful help text from our argument definitions. Users can run 'ai-assistant --help' and get comprehensive documentation. This is what separates professional tools from amateur scripts. No more asking users to remember complex syntax."

**[VISUAL: Implementing different command modes and subcommands]**
**[02:15 - 02:50]**

**SCRIPT**: "Professional CLI tools often have multiple modes. I'm adding subcommands for different assistant functions - chat for conversation, analyze for text analysis, and configure for settings management. Each subcommand has its own arguments and help text. This creates a clean, organized interface that scales as your application grows."

**[VISUAL: Adding configuration file management]**
**[02:50 - 03:20]**

**SCRIPT**: "Power users love configuration files. I'm implementing a system that reads default settings from a config file, but allows command-line arguments to override them. This gives users flexibility - quick one-off commands with arguments, or saved configurations for regular workflows."

**[VISUAL: Implementing proper exit codes and error handling]**
**[03:20 - 03:50]**

**SCRIPT**: "Professional CLI tools communicate success and failure through exit codes. Zero means success, non-zero means different types of errors. This allows our tool to integrate with shell scripts and automation workflows. I'm also ensuring error messages go to stderr, not stdout, so they don't interfere with data processing pipelines."

**[VISUAL: Adding interactive mode with rich features]**
**[03:50 - 04:15]**

**SCRIPT**: "Sometimes users want an interactive session. I'm adding an interactive mode that provides a rich experience - command history, auto-completion, and colorized output. This gives users the best of both worlds - quick command-line usage for automation, and rich interaction for exploration."

**[VISUAL: Testing the CLI with various usage patterns]**
**[04:15 - 04:35]**

**SCRIPT**: "Let's test our CLI with different usage patterns. Single commands, file input and output, configuration changes, and interactive mode. Notice how each pattern feels natural and follows Unix conventions. This is what makes CLI tools feel professional and integrated."

**[VISUAL: Preview of next lesson on web interfaces]**
**[04:35 - 04:40]**

**SCRIPT**: "Next, we'll create web interfaces using Gradio, making our AI tools accessible to non-technical users while maintaining all the power of our CLI version."

---

## ACCESSIBILITY NOTES
- CLI patterns explained with reference to familiar tools
- Argument syntax clearly described and demonstrated
- Help text examples read aloud to show clarity
- Interactive features described for screen reader users

## TECHNICAL REQUIREMENTS
- Terminal with proper color support
- VS Code with argparse documentation available
- Sample configuration files prepared
- Multiple terminal windows for testing different usage patterns
- Example CLI tools for comparison (git, pip, etc.)