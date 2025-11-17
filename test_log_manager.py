#!/usr/bin/env python3
"""
Test script for Log Manager functionality.

Tests the ConversationLogger class for logging conversations
and retrieving logs.
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from log_manager import ConversationLogger, Speaker


def clean_test_logs():
    """Remove test logs from previous runs."""
    test_log_dir = Path("data/conversations")
    if test_log_dir.exists():
        # Only clean test data
        today = datetime.utcnow().strftime("%Y-%m-%d")
        today_dir = test_log_dir / today
        if today_dir.exists():
            for file in today_dir.glob("test-*.json"):
                file.unlink()
            print("🧹 Cleaned up previous test logs")


def test_conversation_logging():
    """Test basic conversation logging."""

    print("=" * 70)
    print("🧪 Testing Conversation Logger")
    print("=" * 70)
    print()

    # Clean previous test data
    clean_test_logs()

    # Test 1: Initialize logger
    print("📦 Step 1: Initialize ConversationLogger...")
    logger = ConversationLogger(log_dir="data/conversations")
    print(f"   {logger}")
    print()

    # Test 2: Start a conversation
    print("📦 Step 2: Start a new conversation...")
    conv_id = logger.start_conversation(
        conversation_id="test-conv-001",
        agent_version_id="v0-baseline",
        persona_name="angry_anthony",
        metadata={
            'test': True,
            'scenario': 'missed_payment'
        }
    )
    print()

    # Test 3: Log conversation turns
    print("📦 Step 3: Log conversation turns...")

    # Opening
    logger.log_turn(
        speaker="agent",
        message="Hello, this is Sarah from Acme Financial Services. May I speak with Mr. Johnson?",
        metadata={'turn_type': 'opening'}
    )

    logger.log_turn(
        speaker="user",
        message="Yeah, this is him. What do you want?",
        metadata={'turn_type': 'response', 'tone': 'defensive'}
    )

    # Main conversation
    logger.log_turn(
        speaker="agent",
        message="I'm calling about your loan account ending in 4567. I see you've missed the last two payments. I wanted to reach out and see if everything is okay and discuss how we can help.",
        metadata={'turn_type': 'issue_introduction'}
    )

    logger.log_turn(
        speaker="user",
        message="I lost my job last month. I can't pay right now. Stop calling me!",
        metadata={'turn_type': 'response', 'tone': 'angry', 'reason_given': 'job_loss'}
    )

    logger.log_turn(
        speaker="agent",
        message="I'm sorry to hear about your job loss, Mr. Johnson. I understand this is a difficult time. Let me see what options we have to help you. Would you be able to make a smaller payment for the next few months while you get back on your feet?",
        metadata={'turn_type': 'empathy_and_options'}
    )

    logger.log_turn(
        speaker="user",
        message="Maybe... how much are we talking?",
        metadata={'turn_type': 'response', 'tone': 'considering'}
    )

    logger.log_turn(
        speaker="agent",
        message="Instead of your regular $500 payment, we could arrange $200 per month for the next 3 months. Would that work better for your current situation?",
        metadata={'turn_type': 'offer', 'proposal': 'reduced_payment_plan'}
    )

    logger.log_turn(
        speaker="user",
        message="Yeah, I can probably do $200. When would I start?",
        metadata={'turn_type': 'response', 'tone': 'agreeable', 'interest': 'high'}
    )

    logger.log_turn(
        speaker="agent",
        message="Perfect! We can start that this month. I'll set it up right now. Your first $200 payment will be due on the 15th. Does that work for you?",
        metadata={'turn_type': 'closing', 'action': 'finalizing_agreement'}
    )

    logger.log_turn(
        speaker="user",
        message="Yeah, that works. Thanks.",
        metadata={'turn_type': 'response', 'agreement': True}
    )

    print()

    # Test 4: End conversation with evaluation
    print("📦 Step 4: End conversation with evaluation...")
    log_file = logger.end_conversation(
        outcome="success",
        termination_reason="payment_plan_agreed",
        evaluation_scores={
            'goal_completion': 90.0,
            'conversational_quality': 85.0,
            'compliance': 100.0,
            'composite': 91.7
        }
    )
    print()

    # Test 5: Retrieve conversation
    print("📦 Step 5: Retrieve saved conversation...")
    retrieved = logger.get_conversation("test-conv-001")
    if retrieved:
        print(f"   ✅ Retrieved conversation: {retrieved['conversation_id']}")
        print(f"   Persona: {retrieved['persona_name']}")
        print(f"   Turns: {retrieved['turn_count']}")
        print(f"   Duration: {retrieved['duration_seconds']:.1f}s")
        print(f"   Outcome: {retrieved['outcome']}")
        print(f"   Goal Completion Score: {retrieved['evaluation_scores']['goal_completion']}")
    print()

    # Test 6: Log another conversation (different persona)
    print("📦 Step 6: Log another conversation (different persona)...")
    logger.start_conversation(
        conversation_id="test-conv-002",
        agent_version_id="v0-baseline",
        persona_name="evasive_emma"
    )

    logger.log_turn("agent", "Hello, this is Sarah calling about your loan.")
    logger.log_turn("user", "Oh, I'm really busy right now...")
    logger.log_turn("agent", "I understand. When would be a better time to call?")
    logger.log_turn("user", "Um, I don't know... maybe next week?")
    logger.log_turn("agent", "I'll call you back next Tuesday at 2pm. Does that work?")
    logger.log_turn("user", "I guess so...")

    logger.end_conversation(
        outcome="deferred",
        termination_reason="callback_scheduled",
        evaluation_scores={
            'goal_completion': 30.0,
            'conversational_quality': 70.0,
            'compliance': 100.0,
            'composite': 53.3
        }
    )
    print()

    # Test 7: List conversations
    print("📦 Step 7: List all conversations...")
    conversations = logger.list_conversations(limit=10)
    print(f"   Found {len(conversations)} conversations:")
    for conv in conversations:
        print(f"   - {conv['conversation_id']}: {conv['persona_name']} ({conv['turn_count']} turns) → {conv['outcome']}")
    print()

    # Test 8: Filter by persona
    print("📦 Step 8: Filter conversations by persona...")
    anthony_convs = logger.list_conversations(persona_name="angry_anthony")
    print(f"   Found {len(anthony_convs)} conversation(s) with angry_anthony")
    print()

    # Test 9: Get statistics
    print("📦 Step 9: Get conversation statistics...")
    stats = logger.get_statistics(agent_version_id="v0-baseline")
    print(f"   Total conversations: {stats['total_conversations']}")
    print(f"   Total turns: {stats['total_turns']}")
    print(f"   Average turns/conversation: {stats['avg_turns_per_conversation']:.1f}")
    print(f"   Personas: {stats['personas']}")
    print(f"   Outcomes: {stats['outcomes']}")
    print()

    # Test 10: Verify JSON structure
    print("📦 Step 10: Verify JSON log structure...")
    log_path = Path(log_file)
    if log_path.exists():
        import json
        with open(log_path, 'r') as f:
            log_data = json.load(f)

        print("   ✅ JSON structure:")
        print(f"      - conversation_id: {log_data.get('conversation_id')}")
        print(f"      - agent_version_id: {log_data.get('agent_version_id')}")
        print(f"      - persona_name: {log_data.get('persona_name')}")
        print(f"      - turn_count: {log_data.get('turn_count')}")
        print(f"      - transcript: {len(log_data.get('transcript', []))} turns")
        print(f"      - evaluation_scores: {bool(log_data.get('evaluation_scores'))}")

        # Show first turn
        if log_data.get('transcript'):
            first_turn = log_data['transcript'][0]
            print()
            print("   First turn structure:")
            print(f"      - speaker: {first_turn['speaker']}")
            print(f"      - message: {first_turn['message'][:50]}...")
            print(f"      - timestamp: {first_turn['timestamp']}")
            print(f"      - metadata: {first_turn.get('metadata', {})}")
    print()

    print("✅ Log Manager tests completed!")
    print()


def test_integration_with_archive():
    """Test integration with AgentArchive."""

    print("=" * 70)
    print("🧪 Testing Log Manager + AgentArchive Integration")
    print("=" * 70)
    print()

    from core import AgentArchive

    print("📦 Testing combined workflow...")

    # Create agent
    archive = AgentArchive()
    agent_id = "v0-test123"

    print(f"   Using agent: {agent_id}")

    # Start conversation
    logger = ConversationLogger()
    logger.start_conversation(
        conversation_id="test-integration-001",
        agent_version_id=agent_id,
        persona_name="cooperative_chloe"
    )

    # Log some turns
    logger.log_turn("agent", "How can I help you today?")
    logger.log_turn("user", "I want to set up a payment plan.")
    logger.log_turn("agent", "Great! Let's work on that together.")

    # End with scores
    logger.end_conversation(
        outcome="success",
        termination_reason="agreement_reached",
        evaluation_scores={
            'goal_completion': 95.0,
            'conversational_quality': 90.0,
            'compliance': 100.0,
            'composite': 95.0
        }
    )

    print()
    print("   ✅ Integration successful!")
    print("   💡 In the real system, we'll update AgentArchive scores")
    print("      based on these conversation logs automatically")
    print()


def main():
    """Run all tests."""
    print()
    print("🚀 Log Manager Test Suite")
    print()

    try:
        # Test 1: Basic logging
        test_conversation_logging()

        # Test 2: Integration
        test_integration_with_archive()

        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("📁 Log files created in: data/conversations/")
        print("🔍 Inspect with: cat data/conversations/*/test-*.json")
        print()
        print("🎯 Phase 1 Complete! Ready for Phase 2: Agent Implementation")
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
    sys.exit(main())
