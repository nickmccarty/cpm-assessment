# Personal AI Assistant - Starter Code

## Overview

This starter code provides the foundation for building a professional Personal AI Assistant application. It demonstrates proper software architecture, testing practices, and development workflows that students will expand upon in their Module 1 programming assignment.

## What's Included

### 🏗️ Core Architecture
- **Configuration Management** (`config/settings.py`): Multi-source configuration system
- **AI Client** (`core/ai_client.py`): Professional AI service integration with retries and fallbacks
- **Test Suite** (`tests/test_ai_client.py`): Comprehensive testing framework

### 🧪 Professional Testing
- Unit tests with pytest
- Mock providers for testing without API calls
- Integration test examples
- Performance testing framework
- Test coverage and quality validation

### 📋 Learning Objectives Alignment
This starter code demonstrates:
- **M1-LO1**: Modular code organization with clear separation of concerns
- **M1-LO2**: Object-oriented design with proper class structure
- **M1-LO3**: Professional code quality standards and testing
- **M1-LO4**: Comprehensive error handling and logging
- **M1-LO5**: Foundation for building user interfaces

## Project Structure

```
starter-code/
├── config/
│   ├── __init__.py
│   └── settings.py          # Multi-source configuration management
├── core/
│   ├── __init__.py
│   └── ai_client.py         # AI service integration with error handling
├── tests/
│   ├── __init__.py
│   └── test_ai_client.py    # Comprehensive test suite
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Getting Started

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (for version control)
- Code editor (VS Code recommended)

### Installation

1. **Clone or download the starter code**
   ```bash
   # If using git
   git clone <repository-url>
   cd personal-ai-assistant
   
   # Or download and extract the starter code
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy environment template
   cp .env.template .env
   
   # Edit .env with your API keys
   # At minimum, set:
   AI_ASSISTANT_API_KEY=your_openai_api_key_here
   ```

### Running Tests

The starter code includes a comprehensive test suite to verify functionality:

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -m "not integration" -v    # Unit tests only
pytest tests/ -m integration -v          # Integration tests only
pytest tests/ -m performance -v          # Performance tests only

# Run with coverage
pytest tests/ --cov=core --cov=config --cov-report=html
```

### Testing the AI Client

```python
# Example usage of the AI client
import asyncio
from config.settings import Settings
from core.ai_client import AIClient

async def test_basic_functionality():
    # Load configuration
    settings = Settings.load()
    
    # Create AI client
    client = AIClient(settings)
    
    # Generate response
    response = await client.generate_response("Hello, how are you?")
    
    print(f"Response: {response.content}")
    print(f"Success: {response.success}")
    print(f"Tokens used: {response.tokens_used}")

# Run the test
asyncio.run(test_basic_functionality())
```

## Key Features Demonstrated

### 🔧 Configuration Management
- **Multi-source loading**: Environment variables, config files, defaults
- **Type validation**: Automatic type conversion and validation
- **Error handling**: Graceful handling of configuration issues
- **Flexibility**: Easy to extend for new configuration options

```python
# Example configuration usage
settings = Settings.load("config.ini")
print(f"AI Model: {settings.ai.model}")
print(f"Temperature: {settings.ai.temperature}")

# Validate configuration
issues = settings.validate()
if issues:
    print("Configuration issues:", issues)
```

### 🤖 AI Client Architecture
- **Provider abstraction**: Support for multiple AI services
- **Error handling**: Comprehensive error management with retries
- **Fallback support**: Automatic switching between providers
- **Performance tracking**: Usage statistics and monitoring

```python
# Example AI client features
client = AIClient(settings)

# Basic response generation
response = await client.generate_response("What is AI?")

# With conversation history
history = [{"user": "Hi", "assistant": "Hello!"}]
response = await client.generate_response(
    "How are you?", 
    conversation_history=history
)

# Streaming responses
async for chunk in client.stream_response("Tell me a story"):
    print(chunk, end="")

# Get usage statistics
stats = client.get_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Tokens used: {stats['total_tokens_used']}")
```

### 🧪 Professional Testing
- **Mock providers**: Test without external API dependencies
- **Async testing**: Proper async/await test patterns
- **Error simulation**: Test error handling and recovery
- **Performance testing**: Load and concurrency testing

```python
# Example test structure
class TestAIClient:
    @pytest.fixture
    def mock_client(self):
        # Create client with mock provider
        client = AIClient(test_config)
        client.providers = [MockAIProvider(...)]
        return client
    
    @pytest.mark.asyncio
    async def test_response_generation(self, mock_client):
        response = await mock_client.generate_response("Test")
        assert response.success is True
        assert "Mock" in response.content
```

## Implementation Tasks for Students

The starter code provides the foundation, but students need to implement several key components:

### 🏗️ Core Implementation Tasks

#### 1. Complete Configuration System
- [ ] Implement `Settings.from_environment()` method
- [ ] Add `_merge_settings()` function for configuration precedence
- [ ] Add validation for all configuration sections
- [ ] Implement configuration file format support (YAML, TOML)

#### 2. Expand AI Provider Support
- [ ] Complete `AnthropicProvider` implementation
- [ ] Add Google AI (Gemini) provider
- [ ] Implement provider-specific optimizations
- [ ] Add cost tracking per provider

#### 3. Enhanced Error Handling
- [ ] Implement retry strategies with exponential backoff
- [ ] Add circuit breaker pattern for failing providers
- [ ] Create user-friendly error message mappings
- [ ] Add error analytics and monitoring

#### 4. Advanced Features
- [ ] Response caching to avoid duplicate API calls
- [ ] Batch processing for multiple requests
- [ ] Prompt templates and chaining
- [ ] Usage analytics and reporting

### 🎯 Interface Implementation Tasks

#### 5. Command-Line Interface
- [ ] Build CLI using the foundation from Lab 1.5
- [ ] Integrate with configuration system
- [ ] Add all required commands (chat, config, history, etc.)
- [ ] Implement proper argument validation

#### 6. Web Interface
- [ ] Build Gradio interface using Lab 1.6 concepts
- [ ] Integrate with AI client and configuration
- [ ] Add file upload and processing
- [ ] Implement user authentication and profiles

#### 7. Conversation Management
- [ ] Build conversation persistence system
- [ ] Add search and retrieval capabilities
- [ ] Implement conversation export features
- [ ] Add conversation analytics

### 🚀 Advanced Implementation Tasks

#### 8. User Profile System
- [ ] Multi-user support with separate histories
- [ ] Role-based access controls
- [ ] User preference management
- [ ] Usage analytics per user

#### 9. File Processing
- [ ] Support multiple file formats (.txt, .pdf, .docx, .csv)
- [ ] Intelligent content extraction
- [ ] Batch file processing
- [ ] File content summarization

#### 10. Production Features
- [ ] Logging and monitoring
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Deployment configuration

## Development Workflow

### 🔄 Recommended Development Process

1. **Start with Tests**: Understand the expected behavior by reading and running tests
2. **Implement Core Features**: Focus on one module at a time
3. **Test Continuously**: Run tests after each implementation
4. **Document Progress**: Keep README and code comments updated
5. **Iterate and Improve**: Refactor based on test feedback

### 📊 Quality Standards

- **Code Coverage**: Aim for >80% test coverage
- **Documentation**: All public methods should have docstrings
- **Type Hints**: Use type hints for better code clarity
- **Error Handling**: No unhandled exceptions in production code
- **Performance**: Response times <2 seconds for basic operations

### 🎯 Assessment Alignment

This starter code specifically supports assessment criteria:

- **Technical Implementation (40%)**
  - Code organization: Clear module structure demonstrated
  - OOP design: BaseAIProvider and inheritance patterns
  - Error handling: Comprehensive error management system

- **Professional Practices (20%)**
  - Testing: Complete test suite with multiple test types
  - Documentation: Professional README and code documentation
  - Code quality: Type hints, proper naming, clean structure

## Common Issues and Solutions

### 🔧 Troubleshooting

#### API Key Issues
```python
# Check if API key is properly loaded
settings = Settings.load()
if not settings.ai.api_key:
    print("Set AI_ASSISTANT_API_KEY environment variable")

# Validate configuration
issues = settings.validate()
if issues:
    print("Configuration issues:", issues)
```

#### Import Errors
```bash
# Make sure you're in the virtual environment
which python  # Should show venv path

# Install missing packages
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Test Failures
```bash
# Run specific failing test with verbose output
pytest tests/test_ai_client.py::TestAIClient::test_specific_method -v -s

# Check test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests without external dependencies
pytest tests/ -m "not integration"
```

## Next Steps

After setting up and understanding the starter code:

1. **Implement missing methods** marked with `# TODO`
2. **Add your own tests** for new functionality
3. **Build the CLI interface** using patterns from Lab 1.5
4. **Create the web interface** using concepts from Lab 1.6
5. **Integrate all components** into a complete application

## Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Async/Await in Python](https://docs.python.org/3/library/asyncio.html)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Gradio Documentation](https://gradio.app/docs)

## Support

This starter code is designed to provide a solid foundation while leaving room for creativity and learning. The TODO comments and test structure guide you toward implementing a professional-quality application.

Remember: This isn't just about completing the assignment – you're building a tool that could genuinely help people be more productive. Focus on creating something you'd be proud to use and show to others!

---

**Good luck with your implementation!** 🚀