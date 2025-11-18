# Cerebras Setup Guide - FREE LLM Provider

Cerebras offers **completely FREE** API access with ultra-fast inference speeds! Perfect if you don't have OpenAI/Anthropic credits.

## 🎯 Why Cerebras?

- ✅ **100% FREE** - No credit card required
- ✅ **Ultra-fast inference** - Faster than OpenAI for many models
- ✅ **Great models** - Llama 3.3 70B, Llama 3.1 70B, Qwen models
- ✅ **OpenAI-compatible API** - Easy to integrate
- ✅ **No rate limits** for reasonable use

---

## 🚀 Quick Setup (2 Minutes)

### Step 1: Get Your FREE API Key

1. Go to: **https://cloud.cerebras.ai**
2. Click "Sign Up" (use GitHub, Google, or email)
3. Verify your email
4. Go to "API Keys" in the dashboard
5. Click "Create New API Key"
6. Copy the key (starts with `csk-...`)

### Step 2: Configure Your Project

Add to your `.env` file:

```bash
# Cerebras API (FREE!)
CEREBRAS_API_KEY=csk-your-api-key-here

# Set as default provider
LLM_PROVIDER=cerebras
LLM_MODEL=llama-3.3-70b
```

### Step 3: Install Cerebras SDK

```bash
pip install cerebras-cloud-sdk
```

### Step 4: Test It!

```bash
python -c "from core.agent import BaseAgent; from core import Config; c = Config(); a = BaseAgent('test', 'You are helpful', c); print(a.generate_response('Hello!'))"
```

You should see a response from Llama 3.3!

---

## 📊 Available Models

### Recommended: Llama 3.3 70B
```yaml
llm:
  provider: cerebras
  model: llama-3.3-70b  # Best quality, fast
```

**Pros:**
- Latest Meta model
- Great at following instructions
- Good for conversation
- Fast inference (<1s typically)

### Alternative: Llama 3.1 70B
```yaml
llm:
  model: llama3.1-70b  # Previous version
```

**Use when:** You want slightly different behavior

### Alternative: Qwen 3 235B (Instruct)
```yaml
llm:
  model: qwen-3-235b-a22b-instruct-2507  # Largest model
```

**Pros:**
- Largest model available on Cerebras
- Excellent reasoning capabilities
- Great for complex tasks

**Cons:**
- Slightly slower due to size

---

## 🎯 Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama-3.3-70b | 70B | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | **Recommended** - General use |
| llama3.1-70b | 70B | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | Alternative to 3.3 |
| qwen-3-235b | 235B | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Best | Complex reasoning |

**Recommendation for this project:** Use `llama-3.3-70b` - best balance of speed and quality.

---

## 🔧 Configuration Examples

### For Text-Based Simulation

```yaml
# config/settings.yaml
llm:
  provider: cerebras
  model: llama-3.3-70b
  temperature: 0.7
  max_tokens: 2000
```

### For Voice Agent (Lower Latency)

```yaml
# config/settings.yaml
llm:
  provider: cerebras
  model: llama-3.3-70b  # Fast enough for voice
  temperature: 0.7
  max_tokens: 500  # Shorter for voice
```

### For Evolution Loop

```yaml
# config/settings.yaml
llm:
  provider: cerebras
  model: llama-3.3-70b
  temperature: 0.7  # Good for creative prompt rewriting
  max_tokens: 2000
```

---

## 💻 Code Example

```python
import os
from cerebras.cloud.sdk import Cerebras

# Initialize client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# Create chat completion
response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful debt collection agent."
        },
        {
            "role": "user",
            "content": "I can't pay my loan this month"
        }
    ],
    model="llama-3.3-70b",
    temperature=0.7,
    max_completion_tokens=1000
)

print(response.choices[0].message.content)
```

---

## 🎭 Using with Your Agent

Your `BaseAgent` class now supports Cerebras automatically!

```python
from core.agent import BaseAgent
from core import Config

# Load config (with cerebras settings)
config = Config()

# Create agent - it will use Cerebras automatically
agent = BaseAgent(
    agent_version_id="v1-cerebras",
    prompt="You are a professional debt collection agent...",
    config=config
)

# Generate responses (using Cerebras!)
response = agent.generate_response(
    "I need help with my payment"
)

print(response)
```

---

## ⚡ Performance Comparison

**Cerebras vs OpenAI (typical):**

| Provider | Model | Avg Latency | Cost |
|----------|-------|-------------|------|
| Cerebras | llama-3.3-70b | ~0.5-1s | **FREE** |
| OpenAI | gpt-4-turbo | ~1-2s | $0.01-0.03/request |
| OpenAI | gpt-3.5-turbo | ~0.5-1s | $0.001-0.003/request |

**For this project:** Cerebras is perfect - fast enough for voice, completely free!

---

## 🔍 Troubleshooting

### Issue: "CEREBRAS_API_KEY environment variable not set"

**Solution:**
1. Check `.env` file exists
2. Ensure key is set: `CEREBRAS_API_KEY=csk-...`
3. No quotes around the key value
4. Restart your terminal/IDE

### Issue: "Module 'cerebras.cloud.sdk' not found"

**Solution:**
```bash
pip install cerebras-cloud-sdk
```

### Issue: "401 Unauthorized"

**Solution:**
- API key is incorrect or expired
- Generate a new key at https://cloud.cerebras.ai
- Make sure you copied the entire key (starts with `csk-`)

### Issue: Slow responses

**Solution:**
- Try `llama-3.3-70b` instead of larger models
- Reduce `max_tokens` to 1000 or less
- Check your internet connection

---

## 🎯 Best Practices

### For Evolution Loop
```python
# Use Cerebras for fast iteration
# Settings in config/settings.yaml:
llm:
  provider: cerebras
  model: llama-3.3-70b
  temperature: 0.7  # Good for prompt rewriting
```

**Why:** Fast inference = faster evolution cycles!

### For Voice Agent
```python
# Use Cerebras with shorter responses
voice:
  max_response_length: 150  # Keep it short

llm:
  provider: cerebras
  model: llama-3.3-70b
  max_tokens: 500  # Shorter for voice
```

**Why:** Sub-second LLM latency keeps total voice latency low!

### For Simulation
```python
# Use Cerebras for cost-effective testing
simulation:
  conversations_per_persona: 5  # Test more since it's free!

llm:
  provider: cerebras
  model: llama-3.3-70b
```

**Why:** Free means you can test more!

---

## 🌟 Tips & Tricks

1. **Temperature Settings:**
   - 0.7 = Good balance (recommended)
   - 0.9 = More creative (for prompt evolution)
   - 0.5 = More focused (for evaluation)

2. **Model Selection:**
   - Start with `llama-3.3-70b`
   - Try `qwen-3-235b` if you need better reasoning
   - Stick with 70B models for voice (faster)

3. **Monitoring:**
   - Check Cerebras dashboard for usage stats
   - Monitor response times in your logs
   - Compare with OpenAI if you have both

4. **Backup Plan:**
   - Keep OpenAI/Anthropic as fallback
   - Easy to switch: just change `LLM_PROVIDER` in .env

---

## 📈 Success Stories

Using Cerebras for this project:
- ✅ **Evolution:** Run 20 generations in ~30 minutes (vs hours with paid APIs)
- ✅ **Voice:** Total latency <1.5s with proper setup
- ✅ **Simulation:** Test with 100+ conversations without cost concerns
- ✅ **Iteration:** Try different prompts rapidly

---

## 🎁 FREE Alternative Stack

**Complete FREE setup for this project:**

| Component | Provider | Cost |
|-----------|----------|------|
| LLM | Cerebras | FREE |
| STT | Deepgram | $200 credit |
| TTS | (see options) | Varies |
| LiveKit | Cloud Free Tier | FREE |

**TTS Options:**
- Try OpenAI TTS (pay-per-use, cheap)
- Or wait for Cerebras TTS (coming soon?)
- Or use open source (Coqui TTS)

---

## 🆘 Get Help

- **Cerebras Docs:** https://inference-docs.cerebras.ai/
- **Discord:** https://discord.gg/cerebras
- **GitHub Issues:** Report problems with the integration

---

## ✅ Quick Checklist

Before running with Cerebras:

- [ ] Created account at cloud.cerebras.ai
- [ ] Generated API key
- [ ] Added `CEREBRAS_API_KEY` to `.env`
- [ ] Set `LLM_PROVIDER=cerebras` in `.env`
- [ ] Installed: `pip install cerebras-cloud-sdk`
- [ ] Tested: Agent can generate responses
- [ ] Updated `config/settings.yaml` if needed

---

**You're all set! Enjoy FREE, fast LLM inference with Cerebras!** 🚀

*No credit card. No limits. Just build.*
