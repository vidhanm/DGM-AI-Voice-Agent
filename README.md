# Darwin Gödel Machine Voice Agent

A self-evolving voice agent platform for debt collection that continuously improves through automated testing and prompt rewriting.

## 🎯 Overview

This project implements a Darwin-Gödel Machine-inspired system that:
- Simulates conversations with diverse user personas
- Automatically evaluates agent performance across multiple metrics
- Evolves agent prompts based on empirical results
- Integrates with LiveKit for voice interactions

**Assignment**: Riverline AI Engineer Hiring Challenge

---

## 🏗️ Architecture

```
dgm-voice-agent/
├── core/                  # Core agent logic and management
│   ├── agent.py          # Base agent class
│   ├── prompt_manager.py # Prompt versioning & templates
│   └── config.py         # Configuration management
├── voice/                # Voice integration
│   ├── livekit_client.py
│   └── audio_handler.py
├── simulation/           # Conversation simulation
│   ├── persona_engine.py
│   ├── personas/         # 5 user personas
│   └── conversation_runner.py
├── evaluation/           # Automated evaluation
│   ├── metrics.py
│   ├── evaluator.py
│   └── llm_judge.py
├── evolution/            # Self-evolution system
│   ├── agent_archive.py
│   ├── prompt_rewriter.py
│   ├── evolutionary_loop.py
│   └── termination_policy.py
├── logging/              # Logging infrastructure
│   └── conversation_logger.py
├── data/                 # Data storage
│   ├── agents/          # Agent versions
│   ├── conversations/   # Conversation logs
│   └── evaluations/     # Evaluation results
├── config/              # Configuration files
│   ├── base_prompt.yaml
│   └── settings.yaml
└── main.py              # Main entry point
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key or Anthropic API key
- LiveKit account (for voice features)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd DGM-AI-Voice-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

#### Web Interface (Recommended)

The easiest way to use this system is through the web interface:

```bash
# Install web dependencies
pip install fastapi uvicorn websockets

# Start the web server
python app.py

# Open browser to http://localhost:8000
```

The web UI provides:
- 🏠 **Dashboard** - System status and quick actions
- 🤖 **Simulate** - Run conversations with personas
- 🧬 **Evolve** - Real-time evolution with progress tracking
- 📊 **Evaluate** - Comprehensive agent evaluation
- 📚 **Results** - Browse all agents and compare performance

#### Command Line Interface

```bash
# Run text-based simulation with personas
python main.py --mode simulate --generations 5

# Run voice agent (LiveKit)
python main.py --mode voice

# Or use the interactive demo
python voice_demo.py dev

# Run full evolution cycle
python main.py --mode evolve --generations 10 --threshold 85

# Use specific evolved agent for voice
python main.py --mode voice --agent-id v5-abc123

# Evaluate a specific agent
python main.py --mode evaluate --agent-id v5-abc123
```

### Voice Agent Setup

1. **Install voice dependencies:**
   ```bash
   pip install "livekit-agents[deepgram,cartesia,silero]~=1.2"
   ```

2. **Set up API keys** (see `VOICE_SETUP.md` for details):
   - LiveKit Cloud: https://cloud.livekit.io (free tier)
   - Deepgram STT: https://console.deepgram.com ($200 free credit)
   - Cartesia TTS: https://cartesia.ai

3. **Update `.env` file:**
   ```bash
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   DEEPGRAM_API_KEY=your_deepgram_key
   CARTESIA_API_KEY=your_cartesia_key
   ```

4. **Run the voice agent:**
   ```bash
   python voice_demo.py dev
   ```

5. **Join the room:**
   - Open https://cloud.livekit.io/projects/<your-project>/rooms
   - Or use LiveKit Playground: https://meet.livekit.io/
   - Allow microphone access and start talking!

See [VOICE_SETUP.md](VOICE_SETUP.md) for detailed setup instructions.

---

## 📊 Features

### Part 1: Base Voice Agent
- ✅ LiveKit integration for voice conversations
- ✅ Configurable prompt templates
- ✅ Modular architecture (prompt, logic, voice layers)
- ✅ 5 diverse personas for testing
- ✅ Automated evaluation across 3 metrics:
  - Goal completion
  - Conversational quality
  - Compliance

### Part 2: Self-Evolution
- ✅ Agent version archive with change history
- ✅ LLM-based prompt rewriting loop
- ✅ Automated testing and selection
- ✅ Termination policy (threshold + plateau detection)
- ✅ Explainability (rationale + failure linkage)

---

## 📈 Evaluation Metrics

### 1. Goal Completion (0-100)
- Payment commitment achieved
- Amount and date specified
- Follow-up action agreed

### 2. Conversational Quality (0-100)
- No repetitions or loops
- No hallucinations
- Appropriate tone
- Natural conversation flow

### 3. Compliance (0-100)
- No threats or illegal language
- Privacy respected
- Professional communication

---

## 🧬 Evolution Process

1. **Initialize**: Start with baseline prompt
2. **Simulate**: Run conversations with all personas
3. **Evaluate**: Score performance automatically
4. **Analyze**: Identify failure patterns
5. **Rewrite**: Generate improved prompt variants
6. **Test**: Evaluate new variants
7. **Select**: Promote best performer
8. **Repeat**: Until success threshold or plateau

---

## 🎭 User Personas

1. **Angry Anthony**: Hostile, defensive
2. **Evasive Emma**: Avoidant, excuse-making
3. **Curious Carlos**: Question-asking, detail-oriented
4. **Cooperative Chloe**: Willing, needs guidance
5. **Desperate David**: Emotional, financial hardship

---

## 📝 Development Log

See `CONTEXT.md` for detailed development progress and decisions.
See `PROJECT_PLAN.md` for complete implementation plan.

---

## 🎥 Demo

*(Will be added after implementation)*

- Video demo: [Link TBD]
- Audio recording: [Link TBD]
- Evolution logs: `data/evolution_logs/`

---

## 📄 License

This project is created for the Riverline AI Engineer hiring assignment.

---

## 👤 Author

*Your Name*
*Your Contact*

---

## 🙏 Acknowledgments

- Riverline AI for the challenging assignment
- LiveKit for voice infrastructure
- OpenAI/Anthropic for LLM capabilities
