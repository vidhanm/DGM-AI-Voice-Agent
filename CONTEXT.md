# DGM Voice Agent - Development Context

**Last Updated**: 2025-11-17
**Current Phase**: Phase 1 - Core Infrastructure (In Progress)
**Status**: Agent versioning system complete ✅ → Configuration management next

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

### 🔄 Phase 1: Core Infrastructure (IN PROGRESS)
- [x] **Implement agent versioning system (AgentArchive)** ✅
  - Created database models (AgentVersion, Conversation, Evolution)
  - Implemented full CRUD operations
  - Added lineage tracking and performance scoring
  - All tests passing
- [ ] Build configuration management (PromptManager, Config)
- [ ] Create log manager infrastructure (ConversationLogger)

### ⏳ Upcoming Phases
- [ ] Phase 2: Text-based agent & persona simulation
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
- Configuration management for prompt templates
- Log manager for conversation logging

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
