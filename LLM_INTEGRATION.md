# LM Studio Integration Documentation

This document explains how to set up and use the LM Studio integration in the Audience Dropper application.

## Overview

The LLM integration uses LM Studio with any compatible model to:
1. **Analyze conversation history** from the audience creation chatbot
2. **Generate summaries** of user responses
3. **Extract 10 relevant keywords** for audience targeting
4. **Provide intelligent responses** based on the conversation context

## Features

### 🤖 Smart Conversation Analysis
- Processes the complete conversation history after all 6 questions are answered
- Generates contextual summaries of what the user is looking for
- Extracts relevant keywords automatically

### 🔑 Intelligent Keyword Extraction
- Uses LLM to analyze conversation context
- Extracts exactly 10 relevant keywords
- Focuses on terms useful for audience targeting
- Falls back to default keywords if LLM is unavailable

### 🛡️ Robust Error Handling
- Graceful fallback when LLM server is unavailable
- Continues working with simulated responses
- Detailed error logging for debugging

## Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **LM Studio** installed (see installation guide below)
3. **Internet connection** for downloading models

### Step 1: Install LM Studio

#### All Platforms
1. Download from: https://lmstudio.ai
2. Install the downloaded executable
3. Launch LM Studio application

### Step 2: Run Setup Script

```bash
python setup_llm.py
```

This script will:
- Check if LM Studio is installed
- Guide you through model setup
- Help you start the Local Server
- Test the integration

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test the Integration

```bash
python test_llm.py
```

## Usage

### In the Application

1. **Start the Flask app**: `python app.py`
2. **Navigate to audience creation**: Go to `/audiences/create/step1`
3. **Answer the 6 questions** in the chatbot
4. **After the 6th question**, the LLM will:
   - Analyze your conversation
   - Generate a summary
   - Extract 10 relevant keywords
   - Display the results

### Conversation Flow

```
Question 1: "Who are you looking for?"
User: "I want to find people interested in starting an online business"

Question 2: "What type of conversations are you looking for?"
User: "People discussing entrepreneurship and side hustles"

... (4 more questions)

After Question 6: LLM processes the entire conversation and generates:
- Summary: "User is looking for aspiring entrepreneurs aged 25-45 who want to start online businesses"
- Keywords: ["entrepreneurship", "online business", "side hustle", "dropshipping", ...]
```

## Technical Details

### LM Studio Configuration

The LM Studio server is configured in `utils/llm_server.py`:

```python
class LLMServer:
    def __init__(self, base_url="http://localhost:1234", 
                 model_name="your-model-name"):
        # Configuration for LM Studio API
```

### API Endpoints

- **Base URL**: `http://localhost:1234`
- **Generate Endpoint**: `/v1/chat/completions`
- **Model**: Any model loaded in LM Studio

### Request Format

```json
{
    "model": "your-model-name",
    "messages": [
        {"role": "system", "content": "System prompt here"},
        {"role": "user", "content": "User prompt here"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": false
}
```

## File Structure

```
utils/
├── llm_server.py          # Main LLM server implementation
├── audience_helpers.py    # Updated with LLM integration
└── database.py           # Database utilities

routes/
└── audiences.py          # Updated route handlers

test_llm.py               # Test script for LLM functionality
setup_llm.py              # Setup script for Ollama and model
```

## Troubleshooting

### Common Issues

#### 1. "LM Studio server not accessible"
**Solution**: 
- Make sure LM Studio is running
- Go to 'Local Server' tab and click 'Start Server'
- Check if the server is running on http://localhost:1234
- Make sure a model is loaded

#### 2. "Model not found"
**Solution**:
- In LM Studio, go to 'Search' tab
- Download and load your preferred model
- Make sure the model is selected in 'Local Server' tab

#### 3. "Connection timeout"
**Solution**:
- Check if LM Studio server is running on port 1234
- Restart the Local Server in LM Studio
- Check firewall settings

#### 4. "Memory issues"
**Solution**:
- The model requires ~8GB RAM
- Close other applications
- Consider using a smaller model

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export DEBUG_LLM=true
```

### Manual Testing

Test the LM Studio server manually:
```bash
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "stream": false
  }'
```

## Performance Considerations

### Model Size
- **Model**: 8B parameters
- **Memory**: ~8GB RAM required
- **Download**: ~4GB initial download

### Response Times
- **First request**: 10-30 seconds (model loading)
- **Subsequent requests**: 2-5 seconds
- **Keyword extraction**: 3-8 seconds

### Optimization Tips
1. Keep Ollama server running
2. Use SSD storage for faster model loading
3. Ensure adequate RAM (16GB+ recommended)
4. Close unnecessary applications

## Fallback Behavior

If the LLM server is unavailable, the application will:
1. **Continue working** with simulated responses
2. **Use default keywords** for audience targeting
3. **Log errors** for debugging
4. **Maintain full functionality** without LLM features

## Future Enhancements

### Planned Features
- [ ] Support for multiple LLM models
- [ ] Caching of LLM responses
- [ ] Batch processing of conversations
- [ ] Custom prompt templates
- [ ] A/B testing of different prompts

### Model Alternatives
- **Hermes 3 Llama 3.1 8B** - Good balance of performance and speed
- **Llama 2 7B** - Smaller, faster
- **Mistral 7B** - Good performance/size ratio
- **CodeLlama 7B** - Code-focused responses
- **Any GGUF model** - LM Studio supports most GGUF format models

## Support

For issues with:
- **LM Studio Integration**: Check this documentation
- **LM Studio Setup**: Visit https://lmstudio.ai/docs
- **Model Issues**: Check model compatibility
- **Application Issues**: Check the main README.md

## License

The LM Studio integration supports various models, each subject to their own license terms. Please review the license of any model you use.
