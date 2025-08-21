# Lab 1.1: Script to Application Transformation
**Module 1 | Duration: 2-3 hours | Bridge: Scripts → Applications**

## Overview
Transform Sarah's chaotic 200+ line monolithic AI script into a professional, modular application using separation of concerns and object-oriented design principles.

## Learning Objectives
- ✅ Analyze problems in monolithic script organization
- ✅ Apply separation of concerns principles
- ✅ Implement object-oriented design for AI applications
- ✅ Create professional code organization structure

## Prerequisites
- Basic Python syntax and functions
- Simple API interaction experience
- Jupyter notebook environment setup
- VS Code or similar IDE access

## Estimated Time
- **Analysis Phase**: 30 minutes
- **Refactoring Implementation**: 90-120 minutes  
- **Testing and Validation**: 30 minutes
- **Reflection and Documentation**: 30 minutes

## Lab Structure

### Part 1: Problem Analysis (30 minutes)
Examine Sarah's monolithic script and identify organizational problems that prevent scaling and maintenance.

### Part 2: Architecture Planning (30 minutes)
Design a modular architecture using professional separation of concerns principles.

### Part 3: Implementation (90 minutes)
- Configuration module with environment variables
- AI client with robust error handling
- Conversation manager for data persistence
- Main application class for orchestration
- Clean entry point design

### Part 4: Testing and Validation (30 minutes)
Verify the refactored application maintains functionality while improving organization.

### Part 5: Reflection and Portfolio (30 minutes)
Document the transformation and prepare portfolio-quality presentation.

## Success Criteria
- [ ] Monolithic script successfully decomposed into logical modules
- [ ] Each module demonstrates single responsibility principle
- [ ] Application maintains identical functionality to original
- [ ] Code organization meets professional standards
- [ ] Error handling implemented throughout
- [ ] Configuration managed securely via environment variables
- [ ] Documentation enables others to understand and use the code

## Files Included
- `notebook.ipynb` - Main interactive lab content
- `starter_code/` - Sarah's original problematic script
- `solution_examples/` - Reference implementations for guidance
- `tests/` - Validation tests for refactored code
- `hints/` - Progressive disclosure support system

## Environment Setup
```bash
# Create virtual environment
python -m venv lab1_env
source lab1_env/bin/activate  # On Windows: lab1_env\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Set environment variable for testing
export OPENAI_API_KEY='your-key-here'  # On Windows: set OPENAI_API_KEY=your-key-here
```

## Getting Started
1. Open `notebook.ipynb` in Jupyter
2. Follow the step-by-step guided transformation
3. Use hints if you get stuck
4. Test your implementation against provided validation criteria
5. Complete the reflection and portfolio documentation

## Support Resources
- **Hints System**: Progressive disclosure for stuck points
- **Solution Examples**: Reference implementations (use only after attempting)
- **Testing Framework**: Automated validation of your refactoring
- **Office Hours**: Instructor support sessions (check course schedule)

## Portfolio Integration
This lab produces:
- **Professional Code Repository**: Well-organized Python application
- **Before/After Analysis**: Documentation of transformation process
- **Technical Writing Sample**: Reflection on software architecture decisions
- **Problem-Solving Demonstration**: Evidence of systematic refactoring approach

## Next Steps
Successful completion prepares you for:
- Lab 1.5: Command-Line Interfaces
- Lab 1.6: Web Interfaces with Gradio
- Module 1 Programming Assignment: Personal AI Assistant
- Advanced Module 2 topics in robust AI systems

---

**Lab Version**: v1.0.0  
**Last Updated**: 2025-08-21  
**Estimated Success Rate**: 90%+ with proper engagement