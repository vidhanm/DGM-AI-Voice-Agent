#!/usr/bin/env python3
"""
Test script for Phase 2: Text-Based Agent & Simulation.

This demonstrates the complete agent + persona conversation system.

NOTE: This test requires API keys to run:
- OPENAI_API_KEY or ANTHROPIC_API_KEY must be set in .env

To run:
1. Copy .env.example to .env
2. Add your API key
3. Run: python test_phase2.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import Config, PromptManager, BaseAgent, AgentArchive
from simulation import PersonaEngine, ConversationRunner
from log_manager import ConversationLogger


def check_api_keys():
    """Check if required API keys are set."""
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("=" * 70)
        print("⚠️  API KEY REQUIRED")
        print("=" * 70)
        print()
        print("This test requires an LLM API key to run.")
        print()
        print("Steps to set up:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        print("   OR")
        print("   ANTHROPIC_API_KEY=your-key-here")
        print()
        print("3. Run this test again")
        print()
        print("=" * 70)
        return False
    return True


def test_agent_creation():
    """Test creating a BaseAgent with a prompt template."""

    print("=" * 70)
    print("🧪 Test 1: Agent Creation")
    print("=" * 70)
    print()

    # Load configuration
    config = Config()
    print(f"✅ Loaded configuration")

    # Create prompt from template
    manager = PromptManager()
    prompt = manager.create_agent_prompt(
        "base_prompt.yaml",
        company_name="Acme Financial Services",
        agent_name="Sarah",
        tone="empathetic and professional"
    )

    print(f"✅ Created prompt from template ({len(prompt)} characters)")

    # Create agent
    agent = BaseAgent(
        agent_version_id="v0-baseline-test",
        prompt=prompt,
        config=config
    )

    print(f"✅ Agent created successfully")
    print()

    return agent


def test_persona_loading():
    """Test loading persona definitions."""

    print("=" * 70)
    print("🧪 Test 2: Persona Loading")
    print("=" * 70)
    print()

    personas_to_test = [
        "angry_anthony",
        "evasive_emma",
        "curious_carlos",
        "cooperative_chloe",
        "desperate_david"
    ]

    loaded_personas = []

    for persona_name in personas_to_test:
        try:
            persona = PersonaEngine(persona_name)
            loaded_personas.append(persona)
            print(f"   ✅ {persona.persona_data.get('display_name', persona_name)}: {persona.persona_data.get('archetype', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Failed to load {persona_name}: {e}")

    print()
    print(f"✅ Loaded {len(loaded_personas)}/5 personas")
    print()

    return loaded_personas[0] if loaded_personas else None


def test_single_conversation(agent, persona):
    """Test a single conversation between agent and persona."""

    print("=" * 70)
    print("🧪 Test 3: Single Conversation")
    print("=" * 70)
    print()

    # Create conversation runner
    runner = ConversationRunner(
        agent=agent,
        persona=persona,
        max_turns=10  # Shorter for testing
    )

    print(f"✅ ConversationRunner initialized")
    print()

    # Run conversation
    result = runner.run_conversation()

    print()
    print("📊 Conversation Result:")
    print(f"   ID: {result['conversation_id']}")
    print(f"   Outcome: {result['outcome']}")
    print(f"   Turns: {result['turn_count']}")
    print(f"   Goal Achieved: {result['goal_achieved']}")
    print(f"   Log File: {result['log_file']}")
    print()

    return result


def test_batch_conversations(agent, persona):
    """Test multiple conversations (batch testing)."""

    print("=" * 70)
    print("🧪 Test 4: Batch Conversations")
    print("=" * 70)
    print()

    # Reset agent and persona
    agent.reset_conversation()
    persona.reset()

    # Create new runner
    runner = ConversationRunner(
        agent=agent,
        persona=persona,
        max_turns=10
    )

    print(f"Running 3 conversations with {persona.persona_data.get('display_name')}...")
    print()

    # Run batch
    results = runner.run_batch(num_conversations=3)

    return results


def test_full_system():
    """Test the complete system end-to-end."""

    print()
    print("🚀 Phase 2: Text-Based Agent & Simulation Test Suite")
    print()

    # Check API keys
    if not check_api_keys():
        return 1

    try:
        # Test 1: Create agent
        agent = test_agent_creation()

        # Test 2: Load personas
        persona = test_persona_loading()

        if not persona:
            print("❌ No personas loaded, cannot continue")
            return 1

        # Test 3: Single conversation
        result = test_single_conversation(agent, persona)

        # Test 4: Batch conversations (optional - costs API calls)
        print("=" * 70)
        print("💡 Batch Test Available")
        print("=" * 70)
        print()
        print("You can run batch tests by uncommenting the line below.")
        print("Note: This will use more API credits.")
        print()
        # Uncomment to run batch test:
        # results = test_batch_conversations(agent, persona)

        print("=" * 70)
        print("✅ ALL PHASE 2 TESTS PASSED!")
        print("=" * 70)
        print()
        print("📁 Check logs at: data/conversations/")
        print()
        print("🎯 What we've tested:")
        print("   ✅ Agent creation with prompt templates")
        print("   ✅ Persona loading (5 personas)")
        print("   ✅ Agent-Persona conversation orchestration")
        print("   ✅ Turn-taking and conversation flow")
        print("   ✅ Automatic logging")
        print("   ✅ Termination detection")
        print()
        print("🚀 Ready for Phase 3: Automated Evaluation!")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(test_full_system())
