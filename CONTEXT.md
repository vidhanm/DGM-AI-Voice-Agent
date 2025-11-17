# DGM Voice Agent - Development Context

**Last Updated**: 2025-11-17
**Current Phase**: Project Setup
**Status**: Starting implementation

---

## 🎯 Project Overview

Building a Darwin Gödel Machine-inspired self-evolving voice agent for debt collection that:
- Continuously improves through simulated conversations
- Uses automated evaluation to score performance
- Rewrites its own prompts based on empirical results
- Works with LiveKit for voice interactions

---

## 📋 Current Progress

### ✅ Completed
- [x] Created comprehensive implementation plan
- [x] Designed system architecture
- [x] Set up project tracking

### 🔄 In Progress
- [ ] Project structure setup
- [ ] Core infrastructure

### ⏳ Upcoming
- [ ] Text-based agent implementation
- [ ] Persona simulation engine
- [ ] Automated evaluation system
- [ ] Evolutionary loop
- [ ] Voice integration

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

*This section will be updated as we learn and discover things during implementation*

-

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
