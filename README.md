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

```bash
# Run text-based simulation with personas
python main.py --mode simulate --generations 5

# Run single conversation with voice
python main.py --mode voice

# Run full evolution cycle
python main.py --mode evolve --generations 10 --threshold 85
```

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
