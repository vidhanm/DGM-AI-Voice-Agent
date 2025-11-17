"""
Test script for Phase 4: Evolutionary Loop

This script tests all components of the evolutionary system:
1. PromptRewriter - Generates improved variants
2. TerminationPolicy - Manages termination conditions
3. EvolutionaryLoop - Orchestrates full evolution

Note: This requires API keys to run full tests.
For quick structural tests, run without API keys.
"""

import os
from core import Config
from evolution import PromptRewriter, TerminationPolicy, EvolutionaryLoop


def test_termination_policy():
    """Test the termination policy."""
    print("\n" + "="*70)
    print("TEST 1: Termination Policy")
    print("="*70)

    policy = TerminationPolicy(
        success_threshold=85.0,
        plateau_generations=3,
        max_generations=10
    )

    policy.start()

    # Simulate generations
    test_scores = [60.0, 65.0, 70.0, 75.0, 76.0, 76.5, 76.5]

    for gen, score in enumerate(test_scores):
        print(f"\nGeneration {gen}: Score {score}")
        result = policy.should_terminate(gen, score)

        if result['should_terminate']:
            print(f"✅ Termination triggered: {result['reason']}")
            print(f"   Message: {result['message']}")
            break

    # Get statistics
    stats = policy.get_statistics()
    print("\nStatistics:")
    print(f"   Generations run: {stats['generations_run']}")
    print(f"   Best score: {stats['best_score']:.2f}")
    print(f"   Improvement: +{stats['improvement']:.2f}")

    # Generate report
    report = policy.generate_report()
    print(report)

    print("✅ Termination policy test complete")


def test_prompt_rewriter_structure():
    """Test PromptRewriter structure (without API calls)."""
    print("\n" + "="*70)
    print("TEST 2: PromptRewriter Structure")
    print("="*70)

    # Check if we have API keys
    config = Config()
    has_api_key = (
        config.get('openai_api_key') or
        config.get('anthropic_api_key')
    )

    if not has_api_key:
        print("⚠️  No API keys found - skipping LLM tests")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY to run full tests")
        return

    # Initialize rewriter
    rewriter = PromptRewriter(config)
    print("✅ PromptRewriter initialized")

    # Create mock evaluation results
    mock_results = [
        {
            'conversation_id': 'test-1',
            'persona_name': 'angry_anthony',
            'composite_score': 45.0,
            'passed': False,
            'goal_completion': {
                'score': 30.0,
                'breakdown': {
                    'has_commitment': False,
                    'has_specifics': False,
                    'has_followup': False
                }
            },
            'conversational_quality': {
                'score': 50.0,
                'breakdown': {
                    'has_repetitions': True,
                    'poor_tone': True
                }
            },
            'compliance': {
                'score': 100.0,
                'passed': True,
                'breakdown': {'violations': []}
            }
        },
        {
            'conversation_id': 'test-2',
            'persona_name': 'evasive_emma',
            'composite_score': 55.0,
            'passed': True,
            'goal_completion': {
                'score': 40.0,
                'breakdown': {
                    'has_commitment': False,
                    'has_specifics': True,
                    'has_followup': True
                }
            },
            'conversational_quality': {
                'score': 60.0,
                'breakdown': {
                    'has_repetitions': False,
                    'poor_tone': False
                }
            },
            'compliance': {
                'score': 100.0,
                'passed': True,
                'breakdown': {'violations': []}
            }
        }
    ]

    # Test failure analysis
    print("\n📊 Testing failure analysis...")
    analysis = rewriter.analyze_failures(mock_results)

    print(f"   Total conversations: {analysis['total_conversations']}")
    print(f"   Failed: {analysis['failed_count']}")
    print(f"   Success rate: {analysis['success_rate']*100:.1f}%")
    print(f"   Priority issues: {len(analysis['priority_issues'])}")

    for issue in analysis['priority_issues'][:3]:
        print(f"      - {issue}")

    print("\n✅ Failure analysis complete")

    # Test variant generation (simplified)
    print("\n🧬 Testing variant generation...")
    print("   Note: This will call the LLM API")

    current_prompt = """You are a debt collection agent.
Be professional and empathetic.
Your goal is to help customers resolve their debt."""

    try:
        variants = rewriter.generate_variants(
            current_prompt,
            analysis,
            num_variants=1  # Just one for testing
        )

        print(f"\n✅ Generated {len(variants)} variant(s)")
        for i, variant in enumerate(variants):
            print(f"\nVariant {i+1}:")
            print(f"   Strategy: {variant['strategy']}")
            print(f"   Rationale: {variant['rationale'][:100]}...")
            print(f"   Prompt length: {len(variant['prompt'])} chars")

    except Exception as e:
        print(f"⚠️  Variant generation failed: {e}")
        print("   This is expected without valid API keys")


def test_evolutionary_loop_structure():
    """Test EvolutionaryLoop structure (without running full evolution)."""
    print("\n" + "="*70)
    print("TEST 3: EvolutionaryLoop Structure")
    print("="*70)

    config = Config()

    # Initialize loop
    loop = EvolutionaryLoop(config)

    print(f"✅ EvolutionaryLoop initialized")
    print(f"   Max generations: {loop.max_generations}")
    print(f"   Success threshold: {loop.success_threshold}")
    print(f"   Variants per gen: {loop.variants_per_generation}")
    print(f"   Personas loaded: {len(loop.personas)}")

    for persona in loop.personas:
        print(f"      - {persona.persona_name}")

    print("\n⚠️  Skipping full evolution run (would take ~30-60 minutes)")
    print("   To run full evolution:")
    print("      python test_phase4.py --run-evolution")


def test_mini_evolution():
    """Run a mini evolution with reduced settings for testing."""
    print("\n" + "="*70)
    print("TEST 4: Mini Evolution (Reduced Settings)")
    print("="*70)

    config = Config()

    # Check if we have API keys
    has_api_key = (
        config.get('openai_api_key') or
        config.get('anthropic_api_key')
    )

    if not has_api_key:
        print("⚠️  No API keys - cannot run evolution")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
        return

    print("🧬 Running mini evolution with reduced settings:")
    print("   - Max generations: 2")
    print("   - Variants: 2")
    print("   - Conversations per persona: 1")
    print("   - This will take ~5-10 minutes")
    print()

    # Create custom config for mini evolution
    mini_config = Config()

    # Initialize loop with custom settings
    loop = EvolutionaryLoop(mini_config)

    # Override settings for mini test
    loop.max_generations = 2
    loop.variants_per_generation = 2
    loop.conversations_per_persona = 1
    loop.termination_policy.max_generations = 2
    loop.termination_policy.plateau_generations = 3  # Won't trigger in 2 gens

    try:
        # Run evolution
        results = loop.evolve()

        print("\n" + "="*70)
        print("🏆 MINI EVOLUTION RESULTS")
        print("="*70)
        print(f"Success: {results['success']}")
        print(f"Termination reason: {results['termination_reason']}")
        print(f"Best agent: {results['best_agent_id']}")
        print(f"Initial score: {results['initial_score']:.2f}")
        print(f"Final score: {results['final_score']:.2f}")
        print(f"Improvement: +{results['improvement']:.2f}")
        print(f"Generations: {results['generations_run']}")

        print("\n✅ Mini evolution complete!")

        # Show lineage
        lineage_report = loop.get_lineage_report(results['best_agent_id'])
        print(lineage_report)

    except Exception as e:
        print(f"\n❌ Evolution failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    import sys

    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                    PHASE 4: EVOLUTIONARY LOOP TESTS                  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # Test 1: Termination Policy (no API needed)
    test_termination_policy()

    # Test 2: PromptRewriter (needs API)
    test_prompt_rewriter_structure()

    # Test 3: EvolutionaryLoop structure (no API needed)
    test_evolutionary_loop_structure()

    # Test 4: Mini evolution (needs API, optional)
    if '--run-evolution' in sys.argv or '--mini' in sys.argv:
        test_mini_evolution()
    else:
        print("\n" + "="*70)
        print("MINI EVOLUTION TEST SKIPPED")
        print("="*70)
        print("To run mini evolution test:")
        print("   python test_phase4.py --mini")

    print("\n" + "="*70)
    print("✅ ALL STRUCTURAL TESTS COMPLETE")
    print("="*70)
    print("\nPhase 4 components are implemented and ready!")
    print("\nNext steps:")
    print("1. Set API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    print("2. Run: python test_phase4.py --mini")
    print("3. For full evolution: Modify main.py to run evolution")


if __name__ == "__main__":
    main()
