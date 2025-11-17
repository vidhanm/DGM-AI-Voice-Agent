#!/usr/bin/env python3
"""
Test script for Phase 3: Automated Evaluation System.

Tests the three core metrics and LLM-as-judge evaluation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from evaluation import (
    GoalCompletionMetric,
    ConversationalQualityMetric,
    ComplianceMetric,
    LLMJudge,
    Evaluator
)


def create_sample_transcripts():
    """Create sample conversation transcripts for testing."""

    # Successful conversation
    success_transcript = [
        {'speaker': 'agent', 'message': 'Hello, this is Sarah from Acme Financial. Is this a good time to talk?'},
        {'speaker': 'user', 'message': 'Um, I guess so. What is this about?'},
        {'speaker': 'agent', 'message': 'I\'m calling about your loan account. I see you\'ve missed a payment. Can we discuss how to get this resolved?'},
        {'speaker': 'user', 'message': 'Yeah, I lost my job last month. I can\'t pay the full amount right now.'},
        {'speaker': 'agent', 'message': 'I\'m sorry to hear about your job loss. That must be really stressful. Let\'s see if we can work out a payment plan that fits your current situation. Would that help?'},
        {'speaker': 'user', 'message': 'Yeah, that would help a lot. What kind of options do I have?'},
        {'speaker': 'agent', 'message': 'We could arrange a reduced payment plan. Instead of the full $500, what if we did $200 per month for the next few months?'},
        {'speaker': 'user', 'message': '$200 I can do. When would that start?'},
        {'speaker': 'agent', 'message': 'We can start that this month. First payment would be due on the 15th. Does that work for you?'},
        {'speaker': 'user', 'message': 'Yes, the 15th works. Thank you for being understanding.'},
        {'speaker': 'agent', 'message': 'You\'re welcome! I\'ll set that up right now. You\'ll get a confirmation email today.'},
        {'speaker': 'user', 'message': 'Great, thank you so much.'}
    ]

    # Failed conversation (compliance issues)
    failed_transcript = [
        {'speaker': 'agent', 'message': 'This is about your overdue payment. You need to pay immediately.'},
        {'speaker': 'user', 'message': 'I can\'t pay right now, I lost my job.'},
        {'speaker': 'agent', 'message': 'That\'s not my problem. If you don\'t pay, we will sue you and garnish your wages.'},
        {'speaker': 'user', 'message': 'What? You can\'t do that!'},
        {'speaker': 'agent', 'message': 'Yes we can. You have no choice. Pay now or face legal action.'},
        {'speaker': 'user', 'message': 'I\'m hanging up now.'}
    ]

    # Incomplete conversation
    incomplete_transcript = [
        {'speaker': 'agent', 'message': 'Hello, calling about your account.'},
        {'speaker': 'user', 'message': 'I\'m really busy right now.'},
        {'speaker': 'agent', 'message': 'This will only take a moment.'},
        {'speaker': 'user', 'message': 'Can you call back later?'},
        {'speaker': 'agent', 'message': 'When would be a good time?'},
        {'speaker': 'user', 'message': 'Maybe next week?'},
    ]

    return {
        'success': success_transcript,
        'failed': failed_transcript,
        'incomplete': incomplete_transcript
    }


def test_individual_metrics():
    """Test each metric individually."""

    print("=" * 70)
    print("🧪 Test 1: Individual Metrics")
    print("=" * 70)
    print()

    transcripts = create_sample_transcripts()

    # Test Goal Completion Metric
    print("📊 Testing Goal Completion Metric...")
    goal_metric = GoalCompletionMetric()

    for name, transcript in transcripts.items():
        result = goal_metric.evaluate(transcript)
        print(f"\n   {name.upper()}:")
        print(f"   Score: {result['score']}/100")
        print(f"   {result['explanation']}")
        print(f"   Breakdown: {result['breakdown']}")

    # Test Conversational Quality Metric
    print("\n" + "=" * 70)
    print("📊 Testing Conversational Quality Metric...")

    quality_metric = ConversationalQualityMetric()

    for name, transcript in transcripts.items():
        result = quality_metric.evaluate(transcript)
        print(f"\n   {name.upper()}:")
        print(f"   Score: {result['score']}/100")
        print(f"   {result['explanation']}")

    # Test Compliance Metric
    print("\n" + "=" * 70)
    print("📊 Testing Compliance Metric...")

    compliance_metric = ComplianceMetric()

    for name, transcript in transcripts.items():
        result = compliance_metric.evaluate(transcript)
        print(f"\n   {name.upper()}:")
        print(f"   Score: {result['score']}/100")
        print(f"   Passed: {result['passed']}")
        print(f"   {result['explanation']}")
        if result['violations']:
            print(f"   Violations: {result['violations']}")

    print()
    print("✅ Individual metrics test complete!")
    print()


def test_evaluator():
    """Test the full Evaluator."""

    print("=" * 70)
    print("🧪 Test 2: Full Evaluator")
    print("=" * 70)
    print()

    transcripts = create_sample_transcripts()

    # Create evaluator (LLM judge will be disabled if no API key)
    print("Creating evaluator...")
    evaluator = Evaluator(use_llm_judge=False)  # Disable LLM judge for basic testing
    print()

    # Evaluate successful conversation
    print("🎯 Evaluating SUCCESSFUL conversation...")
    result = evaluator.evaluate_conversation(
        transcript=transcripts['success'],
        persona_name='cooperative_chloe',
        conversation_id='test-success-001'
    )

    print("\n📊 Detailed Results:")
    print(f"   Composite Score: {result['composite_score']}/100")
    print(f"   Passed: {result['passed']}")
    print(f"   Goal: {result['metrics']['goal_completion']['score']}")
    print(f"   Quality: {result['metrics']['conversational_quality']['score']}")
    print(f"   Compliance: {result['metrics']['compliance']['score']}")

    # Evaluate failed conversation
    print("\n" + "=" * 70)
    print("🎯 Evaluating FAILED conversation (compliance issues)...")
    result = evaluator.evaluate_conversation(
        transcript=transcripts['failed'],
        persona_name='angry_anthony',
        conversation_id='test-failed-001'
    )

    print()
    print("✅ Full evaluator test complete!")
    print()


def test_batch_evaluation():
    """Test batch evaluation."""

    print("=" * 70)
    print("🧪 Test 3: Batch Evaluation")
    print("=" * 70)
    print()

    transcripts = create_sample_transcripts()

    # Create batch of conversations
    conversations = [
        {
            'conversation_id': 'batch-001',
            'transcript': transcripts['success'],
            'persona_name': 'cooperative_chloe'
        },
        {
            'conversation_id': 'batch-002',
            'transcript': transcripts['incomplete'],
            'persona_name': 'evasive_emma'
        },
        {
            'conversation_id': 'batch-003',
            'transcript': transcripts['failed'],
            'persona_name': 'angry_anthony'
        }
    ]

    # Evaluate batch
    evaluator = Evaluator(use_llm_judge=False)
    results = evaluator.evaluate_batch(conversations)

    # Get statistics
    stats = evaluator.get_statistics(results)
    print()
    print("📈 Statistics:")
    print(f"   Total Evaluated: {stats['total_evaluated']}")
    print(f"   Average Composite Score: {stats['composite']['mean']:.1f}")
    print(f"   Compliance Pass Rate: {stats['compliance']['pass_rate']:.1f}%")
    print()

    print("✅ Batch evaluation test complete!")
    print()


def test_with_real_logs():
    """Test evaluation on real conversation logs from Phase 2."""

    print("=" * 70)
    print("🧪 Test 4: Evaluate Real Conversation Logs")
    print("=" * 70)
    print()

    # Try to load real logs from Phase 1
    import json
    from pathlib import Path

    log_dir = Path("data/conversations")

    if not log_dir.exists():
        print("⚠️  No conversation logs found. Run Phase 2 tests first.")
        print()
        return

    # Find log files
    log_files = list(log_dir.glob("*/*.json"))

    if not log_files:
        print("⚠️  No conversation log files found.")
        print()
        return

    print(f"Found {len(log_files)} conversation logs")
    print()

    # Evaluate first log file
    log_file = log_files[0]
    print(f"Evaluating: {log_file.name}")

    with open(log_file, 'r') as f:
        log_data = json.load(f)

    # Create evaluator
    evaluator = Evaluator(use_llm_judge=False)

    # Evaluate
    result = evaluator.evaluate_conversation(
        transcript=log_data['transcript'],
        persona_name=log_data['persona_name'],
        conversation_id=log_data['conversation_id']
    )

    print()
    print("✅ Real log evaluation complete!")
    print()


def main():
    """Run all Phase 3 tests."""

    print()
    print("🚀 Phase 3: Automated Evaluation System Test Suite")
    print()

    try:
        # Test 1: Individual metrics
        test_individual_metrics()

        # Test 2: Full evaluator
        test_evaluator()

        # Test 3: Batch evaluation
        test_batch_evaluation()

        # Test 4: Real logs (if available)
        test_with_real_logs()

        print("=" * 70)
        print("✅ ALL PHASE 3 TESTS PASSED!")
        print("=" * 70)
        print()
        print("🎯 What we've tested:")
        print("   ✅ Goal Completion Metric")
        print("   ✅ Conversational Quality Metric")
        print("   ✅ Compliance Metric")
        print("   ✅ Full Evaluator orchestration")
        print("   ✅ Batch evaluation")
        print("   ✅ Statistics generation")
        print()
        print("💡 Next Steps:")
        print("   - Integrate with ConversationRunner")
        print("   - Use evaluations to guide evolution (Phase 4)")
        print("   - Test with LLM-as-judge (requires API key)")
        print()
        print("🚀 Ready for Phase 4: Evolutionary Loop!")
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
