# Voice Agent Setup Guide

Complete guide for setting up and running the Darwin-Gödel Machine Voice Agent with LiveKit.

---

## 📋 Prerequisites

- Python 3.10 or higher
- Microphone access (for testing)
- Internet connection
- API keys (see setup steps below)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Voice Dependencies

```bash
pip install "livekit-agents[deepgram,cartesia,silero]~=1.2"
```

### Step 2: Set Up API Accounts

You'll need accounts for three services (all have free tiers):

1. **LiveKit Cloud** (free tier)
   - Go to: https://cloud.livekit.io
   - Sign up for free account
   - Create a new project
   - Copy API Key, API Secret, and WebSocket URL

2. **Deepgram** ($200 free credit)
   - Go to: https://console.deepgram.com
   - Sign up and verify email
   - Copy API key from dashboard

3. **Cartesia** (check for free tier)
   - Go to: https://cartesia.ai
   - Sign up for account
   - Get API key from dashboard

### Step 3: Configure Environment

Edit your `.env` file:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxx
LIVEKIT_API_SECRET=your_secret_here

# Deepgram STT
DEEPGRAM_API_KEY=your_deepgram_key_here

# Cartesia TTS
CARTESIA_API_KEY=your_cartesia_key_here
```

### Step 4: Run the Voice Agent

```bash
python voice_demo.py dev
```

### Step 5: Join the Room

- Open: https://cloud.livekit.io/projects/<your-project>/rooms
- Click on your room
- Allow microphone access
- Start talking!

---

## 📚 Detailed Setup Guide

### 1. LiveKit Cloud Setup

LiveKit provides the WebRTC infrastructure for real-time voice communication.

#### 1.1 Create Account

1. Visit https://cloud.livekit.io
2. Click "Sign Up"
3. Verify email
4. Log in to dashboard

#### 1.2 Create Project

1. Click "Create Project"
2. Enter project name (e.g., "dgm-voice-agent")
3. Select region closest to you
4. Click "Create"

#### 1.3 Get API Credentials

1. Go to "Settings" → "API Keys"
2. Copy the following:
   - **WebSocket URL** (e.g., `wss://your-project.livekit.cloud`)
   - **API Key** (starts with `API`)
   - **API Secret** (long random string)

3. Add to `.env`:
   ```bash
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=APIxxxxxxxxx
   LIVEKIT_API_SECRET=your_secret_here
   ```

---

### 2. Deepgram STT Setup

Deepgram provides industry-leading speech-to-text with <300ms latency.

#### 2.1 Create Account

1. Visit https://console.deepgram.com
2. Sign up (GitHub, Google, or email)
3. Verify email

#### 2.2 Get API Key

1. You'll receive $200 free credit automatically
2. Go to "API Keys" in dashboard
3. Click "Create New Key"
4. Name it "DGM Voice Agent"
5. Copy the key

#### 2.3 Configure

Add to `.env`:
```bash
DEEPGRAM_API_KEY=your_deepgram_key_here
```

**Pricing Note:** $200 credit covers ~100-150 hours of transcription

---

### 3. Cartesia TTS Setup

Cartesia provides ultra-low latency text-to-speech (95-199ms TTFA).

#### 3.1 Create Account

1. Visit https://cartesia.ai
2. Sign up for account
3. Check for free tier or credits

#### 3.2 Get API Key

1. Go to API settings/dashboard
2. Generate new API key
3. Copy the key

#### 3.3 Configure

Add to `.env`:
```bash
CARTESIA_API_KEY=your_cartesia_key_here
```

---

## 🎯 Testing Your Setup

### Test 1: Check Dependencies

```bash
python voice_demo.py --skip-checks
```

This will show which dependencies are installed.

### Test 2: Run Unit Tests

```bash
python test_voice.py
```

This tests all voice components without requiring API connections.

### Test 3: Start Voice Agent

```bash
python voice_demo.py dev
```

Look for:
```
✅ LiveKit manager initialized
✅ Voice bridge initialized
✅ Voice agent ready and listening...
```

### Test 4: Join and Talk

1. Open LiveKit dashboard: https://cloud.livekit.io
2. Go to "Rooms"
3. You should see your active room
4. Click "Join Room"
5. Allow microphone access
6. Say: "Hello, I need help with my payment"
7. Agent should respond!

---

## 🎛️ Configuration Options

### Voice Configuration (config/settings.yaml)

```yaml
voice:
  enabled: true

  # STT (Speech-to-Text)
  stt:
    provider: deepgram  # or whisper
    model: nova-3       # fastest, most accurate

  # TTS (Text-to-Speech)
  tts:
    provider: cartesia  # or elevenlabs, openai
    model: sonic        # ultra-low latency
    speed: 1.0          # 0.5-2.0

  # Voice Activity Detection
  vad:
    sensitivity: 0.5    # 0-1, higher = more sensitive

  # Conversation settings
  conversation:
    max_duration_seconds: 600  # 10 minutes
    silence_timeout_seconds: 30
```

### Alternative Providers

#### Use OpenAI Whisper (STT):
```yaml
stt:
  provider: whisper
  model: whisper-1
```

Add to `.env`:
```bash
# Already have this for LLM
OPENAI_API_KEY=your_openai_key
```

#### Use ElevenLabs (TTS):
```yaml
tts:
  provider: elevenlabs
  voice_id: your_voice_id
```

Add to `.env`:
```bash
ELEVENLABS_API_KEY=your_elevenlabs_key
```

---

## 🔧 Troubleshooting

### Issue: "LiveKit credentials not configured"

**Solution:**
1. Check `.env` file exists
2. Verify all three LiveKit variables are set:
   - `LIVEKIT_URL`
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
3. Ensure URL starts with `wss://`
4. No quotes around values in `.env`

### Issue: "ImportError: livekit not found"

**Solution:**
```bash
pip install "livekit-agents[deepgram,cartesia,silero]~=1.2"
```

### Issue: "Cannot connect to room"

**Checklist:**
- [ ] LiveKit API keys are correct
- [ ] Firewall allows WebSocket connections
- [ ] Internet connection is active
- [ ] LiveKit Cloud project is active

### Issue: "No audio output / Agent not speaking"

**Checklist:**
- [ ] Cartesia API key is set
- [ ] TTS provider is configured correctly
- [ ] Check browser console for errors
- [ ] Try with OpenAI TTS instead

### Issue: "Agent not hearing me"

**Checklist:**
- [ ] Deepgram API key is set
- [ ] Microphone permissions granted
- [ ] Microphone is working (test in browser)
- [ ] VAD sensitivity not too low
- [ ] Try with Whisper STT instead

### Issue: "High latency / Delays"

**Solutions:**
1. Use recommended providers (Deepgram + Cartesia)
2. Check internet connection speed
3. Reduce `max_response_length` in settings
4. Use faster LLM model (GPT-3.5 instead of GPT-4)

---

## 📊 Monitoring and Logs

### Conversation Logs

All voice conversations are logged to:
```
data/conversations/YYYY-MM-DD/voice-*.json
```

View logs:
```bash
cat data/conversations/$(date +%Y-%m-%d)/voice-*.json | python -m json.tool
```

### Latency Metrics

Check latency in conversation logs:
```json
{
  "voice_stats": {
    "latency_metrics": {
      "avg_stt_ms": 280,
      "avg_llm_ms": 850,
      "avg_tts_ms": 180,
      "avg_total_ms": 1310
    }
  }
}
```

**Target latencies:**
- STT: <300ms (Deepgram)
- LLM: <1000ms (GPT-4 Turbo)
- TTS: <200ms (Cartesia)
- **Total: <1500ms** ✅

---

## 🎬 Usage Examples

### Example 1: Basic Voice Conversation

```bash
python voice_demo.py dev
```

### Example 2: Use Specific Evolved Agent

```bash
python main.py --mode voice --agent-id v5-abc123
```

### Example 3: Test Different TTS Providers

Edit `config/settings.yaml`:
```yaml
voice:
  tts:
    provider: openai  # Try OpenAI TTS
    model: tts-1
    voice: nova
```

Then run:
```bash
python voice_demo.py dev
```

### Example 4: Run with Verbose Logging

```bash
python voice_demo.py dev --verbose
```

---

## 🌟 Best Practices

### For Development

1. **Start with voice_demo.py** for easy testing
2. **Use dev mode** (`voice_demo.py dev`) for auto-reload
3. **Monitor logs** in `data/conversations/`
4. **Test with different scenarios** (angry, cooperative, evasive users)

### For Production

1. **Use evolved agents** (not baseline)
2. **Monitor latency metrics** regularly
3. **Set appropriate timeouts**
4. **Enable conversation logging**
5. **Use production-grade providers**

### For Best Voice Quality

1. **Keep responses short** (under 3 sentences)
2. **Use voice-optimized prompt** (`voice_prompt.yaml`)
3. **Enable SSML** for natural prosody
4. **Fine-tune VAD sensitivity**
5. **Use Cartesia TTS** for lowest latency

---

## 📈 Cost Estimates

### Free Tier Usage (Estimated)

- **LiveKit Cloud:** Free tier = 1000 participant minutes/month = ~16 hours of calls
- **Deepgram:** $200 credit = ~100-150 hours of transcription
- **Cartesia:** Check current pricing/free tier
- **OpenAI (LLM):** Pay per token, ~$0.01-0.02 per conversation

**Total for testing:** $0-5/month with free tiers

### Production Usage (Estimated)

For 100 calls/day, 5 min average:
- LiveKit: ~$10-20/month
- Deepgram: ~$30-50/month
- Cartesia: Variable (check pricing)
- OpenAI: ~$50-100/month

**Total:** ~$100-200/month for moderate usage

---

## 🆘 Getting Help

### Documentation
- LiveKit Docs: https://docs.livekit.io/agents/
- Deepgram Docs: https://developers.deepgram.com/
- Cartesia Docs: https://docs.cartesia.ai/

### Community
- LiveKit Discord: https://livekit.io/discord
- Deepgram Community: https://discord.gg/deepgram

### Project Issues
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

---

## ✅ Checklist

Before deploying:

- [ ] All API keys configured in `.env`
- [ ] Voice dependencies installed
- [ ] Unit tests passing (`python test_voice.py`)
- [ ] Voice agent starts without errors
- [ ] Can join room and hear greeting
- [ ] Agent hears and responds to speech
- [ ] Latency is acceptable (<2s total)
- [ ] Conversation logs are being created
- [ ] Interruption handling works
- [ ] Can run with evolved agent

---

## 🎓 Next Steps

1. **Test with all 5 personas** (simulate different user types)
2. **Run evolution** to optimize prompts for voice
3. **Record demo conversations** for submission
4. **Monitor and optimize latency**
5. **Deploy to production** if needed

---

*Last Updated: Phase 5 - LiveKit Voice Integration Complete*
