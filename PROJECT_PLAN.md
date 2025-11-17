# Darwin Gödel Machine Voice Agent - Implementation Plan

## 📅 Timeline Overview

**Total Duration**: ~13 days
**Current Phase**: Phase 0 - Setup

---

## Phase 0: Project Setup (Day 1)

### Goals
- Set up project structure
- Install dependencies
- Create documentation

### Tasks
- [x] Create CONTEXT.md for progress tracking
- [x] Create README.md for project overview
- [x] Create PROJECT_PLAN.md
- [ ] Set up folder structure
- [ ] Create requirements.txt
- [ ] Create .env.example
- [ ] Initialize git repository with proper .gitignore

---

## Phase 1: Core Infrastructure (Days 1-2)

### 1.1 Agent Version Management
**Priority**: Critical - Everything depends on this

**Deliverables**:
- `core/agent_archive.py` - AgentArchive class
- Database schema for agent versions
- CRUD operations for agents

**Key Methods**:
- `save_agent(prompt, config, parent_id, metadata)` → version_id
- `get_agent(version_id)` → agent_data
- `get_best_agent(metric)` → agent_data
- `get_lineage(version_id)` → list of ancestors
- `get_generation_stats(generation)` → statistics

**Testing**: Unit tests for CRUD operations

---

### 1.2 Configuration Management
**Priority**: High

**Deliverables**:
- `core/config.py` - Configuration loader
- `core/prompt_manager.py` - Prompt template management
- `config/base_prompt.yaml` - Initial prompt template
- `config/settings.yaml` - System settings

**Features**:
- YAML-based prompt templates with variable substitution
- Validation of required fields
- Environment variable support
- Prompt versioning compatibility

**Testing**: Test template rendering and validation

---

### 1.3 Logging Infrastructure
**Priority**: High

**Deliverables**:
- `logging/conversation_logger.py` - Structured logging
- Log schema definition
- File organization strategy

**Features**:
- JSON-formatted logs
- Conversation transcripts with timestamps
- Turn-level annotations
- Agent reasoning capture
- Performance metrics logging

**Testing**: Verify log format and file creation

---

## Phase 2: Text-Based Agent & Simulation (Days 3-4)

### 2.1 Base Agent (Text Mode)
**Priority**: Critical

**Deliverables**:
- `core/agent.py` - BaseAgent class
- Conversation state management
- Goal tracking

**Key Methods**:
- `generate_response(history, context)` → response
- `reset_conversation()` → None
- `get_conversation_state()` → state_dict

**Testing**: Manual conversation testing

---

### 2.2 Persona Engine
**Priority**: Critical

**Deliverables**:
- `simulation/persona_engine.py` - PersonaEngine class
- `simulation/personas/` - 5 persona definitions
- Persona response generation
- Consistency maintenance

**Personas to Implement**:
1. Angry Anthony (angry.yaml)
2. Evasive Emma (evasive.yaml)
3. Curious Carlos (curious.yaml)
4. Cooperative Chloe (cooperative.yaml)
5. Desperate David (desperate.yaml)

**Each Persona Includes**:
- Background story
- Financial situation
- Communication style
- Goals and motivations
- Trigger words/phrases
- Termination conditions

**Testing**: Generate responses for each persona, verify consistency

---

### 2.3 Conversation Simulator
**Priority**: High

**Deliverables**:
- `simulation/conversation_runner.py` - ConversationRunner class
- Turn-taking logic
- Conversation end detection
- Batch testing capability

**Key Methods**:
- `run_conversation(agent, persona, max_turns)` → transcript
- `run_batch(agent, personas, runs_per_persona)` → results
- `detect_conversation_end(transcript)` → bool, reason

**Testing**: Run multiple simulated conversations

---

## Phase 3: Automated Evaluation (Days 5-6)

### 3.1 Metrics Implementation
**Priority**: Critical

**Deliverables**:
- `evaluation/metrics.py` - Metric calculators
- `evaluation/llm_judge.py` - LLM-as-judge implementation

**Three Core Metrics**:

1. **Goal Completion (0-100)**
   - Payment commitment (50 pts)
   - Amount/date specified (25 pts)
   - Follow-up action (25 pts)
   - Implementation: LLM extraction + rule validation

2. **Conversational Quality (0-100)**
   - No repetitions (25 pts) - n-gram analysis
   - No hallucinations (25 pts) - fact verification
   - Tone match (25 pts) - LLM judge
   - Natural flow (25 pts) - transition analysis

3. **Compliance (0-100 or PASS/FAIL)**
   - No threats (critical)
   - No illegal language (critical)
   - Privacy respected (critical)
   - Professional tone (important)
   - Implementation: Rule-based + LLM verification

**Testing**: Validate metrics on sample conversations

---

### 3.2 Automated Evaluator
**Priority**: Critical

**Deliverables**:
- `evaluation/evaluator.py` - Evaluator class
- Composite scoring
- Failure analysis

**Key Methods**:
- `evaluate_conversation(transcript, persona, agent_id)` → scores
- `evaluate_agent(agent_id, test_suite)` → aggregate_scores
- `analyze_failures(conversations)` → failure_patterns

**Testing**: Run on known good/bad conversations

---

## Phase 4: Evolution System (Days 7-9)

### 4.1 Prompt Rewriter
**Priority**: Critical

**Deliverables**:
- `evolution/prompt_rewriter.py` - PromptRewriter class
- Meta-prompt templates
- Variant generation strategies

**Key Methods**:
- `propose_improvements(current_prompt, failures, metrics)` → variants
- `generate_variant(strategy, prompt, context)` → new_prompt
- `explain_changes(old_prompt, new_prompt)` → rationale

**Strategies**:
- Tone adjustment
- Structure modification
- Instruction clarification
- Few-shot example addition

**Testing**: Generate variants from baseline prompt

---

### 4.2 Evolutionary Loop
**Priority**: Critical

**Deliverables**:
- `evolution/evolutionary_loop.py` - EvolutionaryLoop class
- Selection strategies
- Generation management

**Key Methods**:
- `run_generation(parent_ids, num_variants)` → generation_results
- `select_parents(generation_results, strategy)` → parent_ids
- `evolve(max_generations, success_threshold)` → best_agent

**Evolution Strategies**:
- Greedy (best performer)
- Exploratory (random selection)
- Ensemble (multiple parents)

**Testing**: Run short evolution cycle (3 generations)

---

### 4.3 Termination Policy
**Priority**: High

**Deliverables**:
- `evolution/termination_policy.py` - TerminationPolicy class
- Convergence detection
- Plateau detection

**Termination Conditions**:
- Success threshold reached (e.g., score > 85)
- Performance plateau (no improvement for N generations)
- Max generations exceeded
- Time limit exceeded

**Testing**: Test each termination condition

---

### 4.4 Explainability
**Priority**: Medium

**Deliverables**:
- Change tracking and rationale storage
- Evolution visualization
- Failure linkage

**Features**:
- Track which changes addressed which failures
- Generate evolution family tree
- Performance progression graphs

**Testing**: Verify all metadata captured

---

## Phase 5: LiveKit Voice Integration (Days 10-11)

### 5.1 LiveKit Setup
**Priority**: High

**Deliverables**:
- `voice/livekit_client.py` - LiveKitClient class
- `voice/audio_handler.py` - Audio processing
- WebRTC connection management

**Key Methods**:
- `connect(room_name)` → connection
- `start_conversation(agent)` → None
- `handle_audio_input(stream)` → text
- `speak(text)` → None

**Testing**: Test voice connection and audio streaming

---

### 5.2 Voice-Specific Adaptations
**Priority**: Medium

**Deliverables**:
- Voice-optimized prompt template
- Latency handling
- Interruption management

**Adaptations**:
- Concise responses (voice fatigue)
- Graceful interruption handling
- Prosody markers for TTS
- Filler word management

**Testing**: Live voice conversations

---

### 5.3 Voice Testing & Recording
**Priority**: High

**Deliverables**:
- Test conversations with evolved agent
- Audio recording for submission
- Voice-specific bug fixes

**Testing**: Record 2-3 minute conversation demonstrating success

---

## Phase 6: Final Integration & Deliverables (Days 12-13)

### 6.1 End-to-End Testing
**Priority**: Critical

**Tasks**:
- Run full evolution cycle
- Generate final evolved prompt
- Validate improvements
- Test edge cases

---

### 6.2 Documentation
**Priority**: High

**Deliverables**:
- Complete README with setup instructions
- Architecture documentation
- API documentation (docstrings)
- Usage examples

---

### 6.3 Submission Artifacts
**Priority**: Critical

**Required Deliverables**:
1. **GitHub Repository** (public)
   - Clean, documented code
   - Comprehensive README
   - All source code

2. **Audio Recording**
   - 2-3 minute conversation with final agent
   - Demonstrates successful debt collection

3. **Logs & Data**
   - Agent version archive
   - Evolution history
   - Conversation transcripts
   - Evaluation scores
   - Failure analysis

4. **Demo Video** (2-3 minutes)
   - Show evolution process
   - Display metrics over time
   - Demonstrate voice agent
   - Explain key improvements

---

### 6.4 Demo Video Creation
**Priority**: High

**Script**:
1. Introduction (15s)
2. Show baseline agent performance (30s)
3. Demonstrate evolution process (60s)
4. Show final agent improvements (30s)
5. Live voice demo (30s)
6. Conclusion (15s)

---

## 🎯 Success Criteria

### Technical
- [ ] Voice agent functional with LiveKit
- [ ] 5 distinct personas implemented
- [ ] 3 automated metrics working
- [ ] Evolution loop completes successfully
- [ ] Performance improvement demonstrated

### Submission
- [ ] Public GitHub repo with README
- [ ] Audio recording of conversation
- [ ] Complete logs and artifacts
- [ ] 2-3 minute demo video
- [ ] Submission form completed

---

## 🚀 Quick Wins (MVP Path)

If time-constrained, prioritize:
1. Text-based agent + 3 personas (not 5)
2. Simple metrics (focus on goal completion)
3. Basic evolution (greedy selection, 5 generations)
4. Minimal LiveKit integration
5. Core documentation

---

## 📊 Progress Tracking

Update CONTEXT.md after each phase completion.

**Current Status**: Phase 0 - Project Setup
**Next Milestone**: Complete Phase 1 - Core Infrastructure
**Blockers**: None

---

*This plan is a living document and may be adjusted based on discoveries during implementation.*
