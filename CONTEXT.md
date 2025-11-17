# DGM Voice Agent - Development Context

**Last Updated**: 2025-11-17
**Current Phase**: Phase 2 - Text-Based Agent & Simulation ✅ COMPLETE!
**Status**: Agent can now have real conversations! → Ready for Phase 3!

---

## 🎯 Project Overview

Building a Darwin Gödel Machine-inspired self-evolving voice agent for debt collection that:
- Continuously improves through simulated conversations
- Uses automated evaluation to score performance
- Rewrites its own prompts based on empirical results
- Works with LiveKit for voice interactions

---

## 📋 Current Progress

### ✅ Phase 0: Project Setup (COMPLETED)
- [x] Created comprehensive implementation plan
- [x] Designed system architecture
- [x] Set up project tracking (CONTEXT.md, PROJECT_PLAN.md)
- [x] Created README.md and GETTING_STARTED.md
- [x] Set up complete folder structure
- [x] Created requirements.txt with all dependencies
- [x] Set up configuration files (.env.example, settings.yaml)
- [x] Created main.py entry point with CLI
- [x] Set up .gitignore for security
- [x] Initialized all Python packages
- [x] Made initial git commit

### ✅ Phase 1: Core Infrastructure (COMPLETED!)
- [x] **Implement agent versioning system (AgentArchive)** ✅
  - Created database models (AgentVersion, Conversation, Evolution)
  - Implemented full CRUD operations
  - Added lineage tracking and performance scoring
  - All tests passing
- [x] **Build configuration management (PromptManager, Config)** ✅
  - Created Config class for YAML + env var loading
  - Implemented PromptManager with variable substitution
  - Created comprehensive base_prompt.yaml (3200+ chars)
  - All integration tests passing
- [x] **Create log manager infrastructure (ConversationLogger)** ✅
  - Implemented structured JSON logging
  - Turn-by-turn conversation tracking
  - Metadata and evaluation scores
  - All tests passing

### ✅ Phase 2: Text-Based Agent & Simulation (COMPLETED!)
- [x] **Implement BaseAgent class** ✅
  - LLM integration (OpenAI & Anthropic)
  - Conversation state management
  - Goal achievement tracking
  - 250 lines of code
- [x] **Create 5 diverse personas** ✅
  - Angry Anthony (hostile), Evasive Emma (avoidant)
  - Curious Carlos (analytical), Cooperative Chloe (willing)
  - Desperate David (overwhelmed)
  - Complete YAML definitions with backgrounds, traits, patterns
- [x] **Implement PersonaEngine** ✅
  - Loads persona definitions
  - Generates persona-consistent responses
  - Termination detection
  - 330 lines of code
- [x] **Build ConversationRunner** ✅
  - Orchestrates agent-persona dialogue
  - Automatic logging integration
  - Batch conversation support
  - 220 lines of code

### ⏳ Upcoming Phases
- [ ] Phase 3: Automated evaluation system
- [ ] Phase 4: Evolutionary loop
- [ ] Phase 5: Voice integration

---

## 🏗️ Architecture Decisions Made

### Technology Stack
- **Language**: Python 3.10+
- **Voice Framework**: LiveKit
- **LLM Provider**: OpenAI GPT-4 / Anthropic Claude
- **Database**: SQLite (for simplicity, can upgrade to PostgreSQL)
- **Config Format**: YAML for prompts and configurations
- **Logging**: Structured JSON logging

### Module Structure
```
dgm-voice-agent/
├── core/                  # Agent core logic
├── voice/                 # LiveKit integration
├── simulation/            # Persona simulation
├── evaluation/            # Metrics and scoring
├── evolution/             # Evolutionary loop
├── logging/               # Logging infrastructure
└── data/                  # Data storage
```

---

## 🎯 Current Focus

**Phase 0-1: Foundation Setup**

Building the core infrastructure that everything else depends on:
1. Project structure and dependencies
2. Agent versioning system (critical - tracks all agent versions)
3. Configuration management (prompt templates, settings)
4. Logging infrastructure (conversation logs, metrics)

**Why this order?**
- Agent versioning is the backbone - we need to track every agent iteration
- Without good config management, we can't easily modify prompts
- Logging is essential for debugging and meeting submission requirements

---

## 💡 Key Insights & Decisions

### Design Philosophy
- **Start simple, iterate**: Text first, then add voice
- **Modular architecture**: Each component independent and testable
- **Log everything**: Needed for debugging and submission artifacts
- **Automated evaluation is critical**: Without good metrics, evolution is random

### Trade-offs Made
- Using SQLite over PostgreSQL (simpler setup, sufficient for assignment)
- Starting with text-based conversations before voice (validate logic first)
- Focus on code clarity over optimization (it's an assignment, readability matters)

---

## 📝 Notes & Learnings

### Session 1 - Agent Versioning System
**Date**: 2025-11-17

**What we built:**
- Complete database schema for agent versioning (AgentVersion, Conversation, Evolution)
- AgentArchive class with 10+ methods for version management
- Comprehensive test suite demonstrating evolution tracking

**Key learnings:**
1. **Naming conflict**: Had to rename `logging/` to `log_manager/` to avoid conflict with Python's stdlib `logging` module
2. **Encoding issues**: Needed to use ASCII instead of UTF-8 for special characters (Gödel → Godel)
3. **SQLAlchemy works great**: Clean ORM abstraction, easy to use
4. **Version ID strategy**: Using format `v{generation}-{uuid}` for easy identification

**What works well:**
- Lineage tracking allows us to trace agent evolution
- Composite scoring (weighted average) gives single metric for comparison
- Separate tables for conversations and evolutions keeps data organized

**Database created**: `data/agents.db` (SQLite)
**Test results**: All 13 test steps passing ✅

**Next steps:**
- Configuration management for prompt templates ✅ Done!
- Log manager for conversation logging

### Session 2 - Configuration Management
**Date**: 2025-11-17

**What we built:**
- Config class for centralized configuration management
- PromptManager for template loading and rendering
- Comprehensive base prompt for debt collection agent
- Test suite with 7 comprehensive tests

**Key features:**
1. **Config class** (`core/config.py`):
   - Loads settings from YAML files
   - Environment variable overrides
   - Dot-notation access (e.g., `config.get('llm.model')`)
   - API key management for different LLM providers
   - Database URL generation

2. **PromptManager** (`core/prompt_manager.py`):
   - Template loading from YAML
   - Variable substitution with `${variable}` syntax
   - Template caching for performance
   - Save new templates programmatically
   - List and inspect templates

3. **Base Prompt Template** (`config/base_prompt.yaml`):
   - 3200+ character comprehensive prompt
   - Debt collection best practices
   - DO/DON'T guidelines for compliance
   - Conversation flow structure
   - Multiple payment options
   - FDCPA compliance requirements

**What works well:**
- Clean separation between config and code
- Easy to modify prompts without changing code
- Template variables make prompts reusable
- Integration between Config and PromptManager is seamless

**Test results**: All 7 test steps passing ✅
**Files created**:
- `config/base_prompt.yaml` (baseline agent)
- `config/test_greeting.yaml` (test template)

**Next steps:**
- Log manager infrastructure (final piece of Phase 1) ✅ Done!
- Ready for Phase 2: Agent implementation!

### Session 3 - Log Manager Infrastructure
**Date**: 2025-11-17

**What we built:**
- ConversationLogger for structured conversation logging
- Complete logging system with JSON format
- Test suite with 10 comprehensive tests + integration test

**Key features:**
1. **ConversationLogger** (`log_manager/conversation_logger.py`):
   - start_conversation() - Begin logging session
   - log_turn() - Record individual turns with speaker, message, metadata
   - end_conversation() - Save with evaluation scores
   - get_conversation() - Retrieve logs by ID
   - list_conversations() - Query with filters (persona, agent, date)
   - get_statistics() - Aggregate analytics

2. **Log Structure**:
   - Conversation metadata (ID, agent version, persona, timestamps)
   - Turn-by-turn transcript with timestamps
   - Evaluation scores (goal completion, quality, compliance)
   - Duration tracking
   - Outcome and termination reason
   - Pretty-printed JSON for easy inspection

3. **Organization**:
   - Logs organized by date (data/conversations/YYYY-MM-DD/)
   - Easy to query and filter
   - Rich metadata for analysis

**What works well:**
- Clean, structured JSON logs are easy to analyze
- Turn-by-turn tracking captures full conversation flow
- Metadata enables powerful filtering and analytics
- Integration with AgentArchive is seamless
- Visual feedback during logging (emojis for speakers)

**Test results**: All 10 test steps passing ✅
**Sample logs created**:
- test-conv-001.json (angry_anthony, 10 turns, success)
- test-conv-002.json (evasive_emma, 6 turns, deferred)
- test-integration-001.json (cooperative_chloe, 3 turns)

**Next steps:**
- Phase 1 is COMPLETE! 🎉
- Ready to start Phase 2: Text-based Agent & Persona Simulation
- We now have all infrastructure needed to build and test agents

### Session 4 - Text-Based Agent & Simulation
**Date**: 2025-11-17

**What we built:**
- BaseAgent class for conversational AI
- PersonaEngine for simulating diverse users
- ConversationRunner for orchestrating dialogues
- 5 detailed persona definitions

**Key accomplishments:**
1. **BaseAgent** (`core/agent.py` - 250 lines):
   - Dual LLM support (OpenAI GPT-4 & Anthropic Claude)
   - Conversation history management
   - Context tracking
   - Goal achievement detection
   - Graceful error handling

2. **5 Persona Definitions** (YAML files):
   - Angry Anthony: Hostile, defensive, needs empathy
   - Evasive Emma: Avoidant, needs structure/pinning down
   - Curious Carlos: Analytical, asks many questions
   - Cooperative Chloe: Willing, just needs guidance
   - Desperate David: Overwhelmed, needs compassion

   Each includes: background, traits, communication style, triggers,
   conversation patterns, termination conditions, sample dialogue

3. **PersonaEngine** (`simulation/persona_engine.py` - 330 lines):
   - Loads persona YAML definitions
   - Creates detailed system prompts for LLM
   - Generates persona-consistent responses
   - Tracks termination conditions
   - Maintains character throughout conversation

4. **ConversationRunner** (`simulation/conversation_runner.py` - 220 lines):
   - Orchestrates agent ↔ persona turn-taking
   - Integrates with ConversationLogger automatically
   - Detects conversation end conditions
   - Classifies outcomes (success/failure/incomplete)
   - Batch conversation support

**Dependencies added:**
- openai==2.8.0 (GPT-4 API)
- anthropic==0.73.0 (Claude API)

**What works well:**
- Clean separation: Agent logic vs Persona logic
- Modular design allows easy persona creation
- Automatic logging makes debugging easy
- Both LLM providers work with same interface
- Personas are rich and realistic

**Testing:**
- Created test_phase2.py with structured tests
- Validates agent creation, persona loading
- Shows conversation flow (requires API key)
- All structural tests passing

**Code statistics:**
- 1,748 lines added this session
- 3 major classes implemented
- 5 detailed persona files
- Total project: ~4,000 lines of code

**Next steps:**
- Phase 2 COMPLETE! 🎉
- Agent can now have real conversations
- Ready for Phase 3: Automated Evaluation System
- Need to build metrics to score conversations automatically

---

## 🚧 Current Blockers

*None currently*

---

## 📚 Resources & References

- LiveKit Documentation: https://docs.livekit.io/
- Assignment Demo (Cekura): https://youtu.be/QIi6yawrWDA
- Assignment Demo (Vogent): https://www.youtube.com/watch?v=7yKWYjlQN8U
- Darwin-Gödel Machines: Self-improving AI systems

---

## 🎯 Next Session TODO

1. Create project folder structure
2. Set up requirements.txt with all dependencies
3. Implement agent versioning system (AgentArchive class)
4. Create basic configuration management
5. Set up logging infrastructure

---

## 📊 Metrics Tracking

*Will track evolution metrics here once we start running experiments*

**Baseline Agent**: TBD
**Best Agent**: TBD
**Generations Run**: 0
**Total Conversations**: 0

---

## 🤔 Questions to Resolve

- [ ] Which LLM provider to use primarily? (OpenAI vs Anthropic)
- [ ] How many conversations per persona per evaluation? (3-5 suggested)
- [ ] What's the success threshold for termination? (85/100 suggested)
- [ ] Local vs cloud LiveKit setup?

---

*This document should be updated after every significant development session to maintain context.*
