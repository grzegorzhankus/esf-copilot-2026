# Advanced LLM Setup Guide for DGX Spark

This guide explains how to set up and use advanced LLM capabilities on your NVIDIA DGX Spark.

## 🚀 Quick Start

### Option 1: NVIDIA NIM (Recommended for DGX Spark)

NVIDIA NIM provides access to state-of-the-art models optimized for Grace Blackwell architecture.

**1. Get API Key:**
- Visit [NVIDIA Build Platform](https://build.nvidia.com/)
- Sign in with NVIDIA account
- Generate API key (free tier available)

**2. Configure Environment:**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env
```

Add to `.env`:
```bash
NVIDIA_API_KEY=nvapi-your-actual-key-here
LLM_MODEL=llama-4-maverick
```

**3. Install Dependencies:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Verify Setup:**

```python
from core.llm_advanced import get_llm_client

client = get_llm_client()
info = client.get_model_info()
print(f"Using: {info['model']} via {info['backend']}")

# Test generation
response = client.generate("What are the key financial ratios for analyzing company health?")
print(response)
```

---

### Option 2: Ollama (Local Fallback)

For offline usage or testing, use Ollama with local models.

**1. Install Ollama:**

```bash
# Linux/WSL
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Or download from: https://ollama.ai
```

**2. Pull Models:**

```bash
# Recommended for financial analysis
ollama pull llama3.1:8b

# Alternative models
ollama pull mistral:7b
ollama pull deepseek-coder:6.7b
```

**3. Start Ollama Service:**

```bash
ollama serve
```

**4. Configure (Optional):**

```bash
# In .env file
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 📊 Available Models

### NVIDIA NIM Models (Cloud-hosted)

| Model | Parameters | Best For | Speed |
|-------|-----------|----------|-------|
| **Llama 4 Maverick** | 405B | Complex reasoning, multi-hop analysis | Fast |
| **DeepSeek V3** | 685B | Financial reasoning, technical analysis | Medium |
| **Mistral Large 3** | 123B | General analysis, report generation | Fast |
| **Qwen3** | 72B | Multilingual (Polish + English) | Very Fast |

### Ollama Local Models

| Model | Parameters | Best For | RAM Required |
|-------|-----------|----------|--------------|
| **Llama 3.1** | 8B | General chat, Q&A | 8GB |
| **Mistral** | 7B | Fast inference | 6GB |
| **DeepSeek Coder** | 6.7B | Code-related queries | 6GB |

---

## 🎯 Usage Examples

### Basic Text Generation

```python
from core.llm_advanced import get_llm_client, create_financial_analyst_prompt

# Initialize client
client = get_llm_client()

# Create system prompt
system_prompt = create_financial_analyst_prompt(language="en")

# Generate response
response = client.generate(
    prompt="Explain what ROE means and why it's important.",
    system_prompt=system_prompt,
    temperature=0.1
)
print(response)
```

### Multi-turn Chat

```python
messages = [
    {"role": "system", "content": create_financial_analyst_prompt("en")},
    {"role": "user", "content": "What are the main profitability ratios?"},
    {"role": "assistant", "content": "The main profitability ratios are..."},
    {"role": "user", "content": "How do I calculate ROA?"}
]

response = client.chat(messages)
print(response)
```

### Context-Aware Analysis

```python
from core.analysis_file_selector import load_analysis_from_file

# Load analysis data
analysis_data = load_analysis_from_file("outputs/analysis_20260115_123456.json")

# Create context-aware prompt
system_prompt = create_financial_analyst_prompt(
    language="en",
    analysis_data={
        "metrics": {kpi.key: kpi.value for kpi in analysis_data.kpis},
        "red_flags": [rf for rf in analysis_data.red_flags if rf.detected]
    }
)

# Ask contextual question
response = client.generate(
    prompt="Based on this company's financials, what are the main concerns?",
    system_prompt=system_prompt
)
print(response)
```

---

## 🔧 Configuration Options

### Model Selection

To use a specific model, set in `.env`:

```bash
# For NVIDIA NIM
LLM_MODEL=llama-4-maverick    # or deepseek-v3, mistral-large, qwen3

# For Ollama
LLM_MODEL=llama3.1:8b         # or mistral:7b, deepseek-coder:6.7b
```

### Performance Tuning

```bash
# Temperature (0.0 = deterministic, 1.0 = creative)
LLM_TEMPERATURE=0.1

# Max tokens in response
LLM_MAX_TOKENS=4096

# Request timeout (seconds)
LLM_TIMEOUT=60
```

---

## 🚦 Auto-Detection Logic

The system automatically detects the best available LLM:

1. **Check for NVIDIA NIM**: If `NVIDIA_API_KEY` is set and API responds → Use NIM
2. **Check for Ollama**: If Ollama service is running → Use Ollama
3. **Error**: If neither available → Raise error with setup instructions

---

## 🏃 Running the Enhanced App

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not done already)
pip install -r requirements.txt

# Run Streamlit app
streamlit run app/app.py
```

The app will automatically use the best available LLM backend.

---

## 🧪 Testing Your Setup

Run these tests to verify everything works:

```python
# Test 1: Check backend availability
from core.llm_advanced import AdvancedLLMClient

try:
    client = AdvancedLLMClient()
    print(f"✓ LLM backend configured: {client.config.backend.value}")
    print(f"✓ Model: {client.config.model.value}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Simple generation
try:
    response = client.generate("Say hello!")
    print(f"✓ Generation works: {response[:50]}...")
except Exception as e:
    print(f"✗ Generation failed: {e}")

# Test 3: Financial analysis
try:
    system_prompt = create_financial_analyst_prompt("en")
    response = client.generate(
        "What is a good debt-to-equity ratio?",
        system_prompt=system_prompt
    )
    print(f"✓ Financial analysis: {response[:100]}...")
except Exception as e:
    print(f"✗ Analysis failed: {e}")
```

---

## 📈 Performance Comparison

### Response Times (DGX Spark)

| Model | Backend | Tokens/sec | Latency (first token) |
|-------|---------|------------|----------------------|
| Llama 4 Maverick | NIM | ~100 | ~200ms |
| DeepSeek V3 | NIM | ~80 | ~250ms |
| Llama 3.1 8B | Ollama (local) | ~50 | ~100ms |

### Quality Comparison

| Task | Llama 4 | DeepSeek V3 | Mistral Large | Qwen3 |
|------|---------|-------------|---------------|-------|
| Financial Reasoning | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Polish Language | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Code Generation | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Report Writing | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🛠️ Troubleshooting

### "NVIDIA NIM not available"

**Solution:**
```bash
# Check if API key is set
echo $NVIDIA_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $NVIDIA_API_KEY" \
     https://integrate.api.nvidia.com/v1/models
```

### "Ollama not available"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull a model if needed
ollama pull llama3.1:8b
```

### "No LLM backend available"

**Solution:** Install at least one backend:
- For cloud: Set `NVIDIA_API_KEY` in `.env`
- For local: Install Ollama and pull a model

### Slow responses with Ollama

**Solution:** Use smaller models or switch to NVIDIA NIM:
```bash
# Smaller, faster models
ollama pull phi3:3.8b
ollama pull gemma2:9b
```

---

## 🎓 Best Practices

### 1. Use Appropriate Temperature

```python
# Factual Q&A (deterministic)
client.generate(prompt, temperature=0.0)

# Analysis with some reasoning
client.generate(prompt, temperature=0.1)

# Creative content
client.generate(prompt, temperature=0.7)
```

### 2. Provide Context

```python
# Bad
response = client.generate("What's the ROE?")

# Good
response = client.generate(
    "What's the ROE?",
    system_prompt=create_financial_analyst_prompt(
        "en",
        analysis_data={"metrics": current_analysis}
    )
)
```

### 3. Handle Errors Gracefully

```python
try:
    response = client.generate(prompt)
except requests.Timeout:
    response = "Analysis timed out. Please try again."
except Exception as e:
    response = f"Error: {str(e)}"
```

---

## 📚 Further Reading

- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [LLM Best Practices for Financial Analysis](https://arxiv.org/abs/2401.00001)

---

## 🆘 Support

If you encounter issues:

1. Check logs: `tail -f app.log`
2. Verify environment: `env | grep LLM`
3. Test manually: Run examples above
4. Open issue: [GitHub Issues](https://github.com/your-repo/issues)
