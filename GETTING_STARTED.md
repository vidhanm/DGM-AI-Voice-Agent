# Getting Started Guide

## ✅ What We've Completed

### Phase 0: Project Setup ✓
- [x] Created project documentation (CONTEXT.md, README.md, PROJECT_PLAN.md)
- [x] Set up complete folder structure
- [x] Created requirements.txt with all dependencies
- [x] Created .env.example for configuration
- [x] Set up .gitignore for security
- [x] Created main.py entry point
- [x] Initialized Python packages with __init__.py

### Project Structure
```
DGM-AI-Voice-Agent/
├── CONTEXT.md              ← Development progress tracker
├── PROJECT_PLAN.md         ← Detailed implementation plan
├── README.md               ← Project overview
├── GETTING_STARTED.md      ← This file
├── main.py                 ← Entry point
├── requirements.txt        ← Dependencies
├── setup.py               ← Package setup
├── .env.example           ← Configuration template
├── .gitignore             ← Git ignore rules
│
├── core/                  ← Core agent logic (NEXT: implement)
├── voice/                 ← LiveKit integration
├── simulation/            ← Persona simulation
│   └── personas/         ← 5 personas definitions
├── evaluation/            ← Metrics and scoring
├── evolution/             ← Self-evolution system
├── logging/               ← Logging infrastructure
├── data/                  ← Data storage
│   ├── agents/           ← Agent versions
│   ├── conversations/    ← Conversation logs
│   └── evaluations/      ← Evaluation results
└── config/                ← Configuration files
```

---

## 🚀 Next Steps (To Run the Project)

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

**Required API Keys:**
- OpenAI API key (for GPT-4) OR Anthropic API key (for Claude)
- LiveKit credentials (can be set up later for Phase 5)

### 4. Test the Setup

```bash
# This should show help message
python main.py --help
```

---

## 📋 What to Implement Next

### Phase 1: Core Infrastructure (START HERE)

We need to build three foundational systems:

#### 1. Agent Versioning System (`core/agent_archive.py`)
**Why first?** Everything else depends on tracking agent versions.

**What it does:**
- Stores every version of the agent (prompts, configs, scores)
- Tracks parent-child relationships (evolution lineage)
- Retrieves best performing agents
- Maintains change history

**Key methods to implement:**
```python
class AgentArchive:
    def save_agent(prompt, config, parent_id, metadata) -> version_id
    def get_agent(version_id) -> agent_data
    def get_best_agent(metric="composite_score") -> agent_data
    def get_lineage(version_id) -> list[ancestors]
```

#### 2. Configuration Management (`core/config.py`, `core/prompt_manager.py`)
**What it does:**
- Loads YAML configuration files
- Manages prompt templates with variable substitution
- Validates configurations

**Files to create:**
- `config/base_prompt.yaml` - Initial debt collection agent prompt
- `config/settings.yaml` - System settings

#### 3. Logging Infrastructure (`logging/conversation_logger.py`)
**What it does:**
- Logs conversations in structured format (JSON)
- Captures transcripts, scores, metadata
- Enables easy analysis and debugging

---

## 🎯 Recommended Implementation Order

### Session 1: Agent Versioning (2-3 hours)
1. Design database schema
2. Implement AgentArchive class
3. Write basic tests
4. Create first agent version

### Session 2: Configuration (1-2 hours)
1. Create base prompt template
2. Implement PromptManager
3. Add settings file
4. Test template rendering

### Session 3: Logging (1-2 hours)
1. Design log schema
2. Implement ConversationLogger
3. Test logging flow
4. Verify log files created correctly

### Session 4: Base Agent (2-3 hours)
1. Implement BaseAgent class
2. Integrate with LLM (OpenAI/Anthropic)
3. Test with manual conversations
4. Store first conversation logs

---

## 💡 Tips

### Start Simple
- Use SQLite for the database (easier than PostgreSQL)
- Test each component independently
- Don't optimize prematurely

### Good Practices
- Write docstrings for all classes/methods
- Add type hints
- Log liberally (you'll need it for debugging)
- Commit often to git

### Testing Strategy
- Manual testing is fine initially
- Test with simple conversations first
- Gradually increase complexity

---

## 📖 Documentation References

- **CONTEXT.md** - Check current progress and decisions
- **PROJECT_PLAN.md** - See detailed implementation plan
- **README.md** - Project overview and architecture

---

## ❓ Questions?

Refer to:
- Original assignment document
- Demo videos (Cekura, Vogent)
- LiveKit docs: https://docs.livekit.io/

---

## 🎯 Success Checklist for Phase 1

- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] .env file configured with API keys
- [ ] main.py runs without errors
- [ ] AgentArchive class implemented and tested
- [ ] PromptManager can load and render templates
- [ ] ConversationLogger creates log files
- [ ] First test conversation logged successfully

**Once these are done, we move to Phase 2: Persona Simulation!**

---

*Last Updated: 2025-11-17*
*Current Phase: Setup Complete → Ready for Phase 1*
