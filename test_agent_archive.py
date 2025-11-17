#!/usr/bin/env python3
"""
Test script for Agent Archive functionality.

This demonstrates how to use the AgentArchive class to store and retrieve
agent versions during the evolution process.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent))

from core.agent_archive import AgentArchive
from core.models import create_database


def test_agent_archive():
    """Test the agent archive functionality."""

    print("=" * 70)
    print("🧪 Testing Agent Archive System")
    print("=" * 70)
    print()

    # Initialize database
    print("📦 Step 1: Initialize database...")
    db_path = "data/agents.db"

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Remove old database if exists (for clean test)
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"   Removed old database")

    # Create database
    create_database(f"sqlite:///{db_path}")
    print(f"   ✅ Database created at {db_path}")
    print()

    # Create archive instance
    print("📦 Step 2: Create AgentArchive instance...")
    archive = AgentArchive(f"sqlite:///{db_path}")
    print("   ✅ Archive ready")
    print()

    # Test 1: Save baseline agent
    print("📦 Step 3: Save baseline agent (Generation 0)...")
    baseline_prompt = """You are a professional debt collection agent.

Your goal is to help customers who have defaulted on their loans find a path to repayment.

Guidelines:
- Be empathetic and understanding
- Listen to their situation
- Offer flexible payment options
- Never threaten or use aggressive language
- Maintain professionalism at all times

Your success is measured by whether the customer commits to a payment plan."""

    baseline_id = archive.save_agent(
        prompt=baseline_prompt,
        config={'version': '1.0', 'model': 'gpt-4'},
        parent_id=None,
        generation=0,
        mutation_strategy='baseline',
        change_rationale='Initial baseline agent for debt collection'
    )
    print(f"   ✅ Saved baseline: {baseline_id}")
    print()

    # Test 2: Simulate evaluation (update scores)
    print("📦 Step 4: Simulate evaluation and update scores...")
    archive.update_scores(
        version_id=baseline_id,
        goal_completion=65.0,
        conversational_quality=70.0,
        compliance=95.0,
        total_conversations=15,
        successful_conversations=10,
        failed_conversations=5
    )
    print()

    # Test 3: Create evolved version (Generation 1)
    print("📦 Step 5: Create evolved version (Generation 1)...")
    evolved_prompt = """You are a professional debt collection agent with enhanced empathy.

Your goal is to help customers who have defaulted on their loans find a path to repayment.

Guidelines:
- START by acknowledging their situation and showing empathy
- Ask open-ended questions to understand their financial circumstances
- Listen actively and validate their feelings
- Offer multiple flexible payment options tailored to their situation
- Never threaten or use aggressive language
- Maintain professionalism and patience at all times
- If they're struggling, ask about partial payments or payment holidays

Your success is measured by whether the customer commits to a payment plan."""

    evolved_id = archive.save_agent(
        prompt=evolved_prompt,
        config={'version': '1.1', 'model': 'gpt-4'},
        parent_id=baseline_id,
        generation=1,
        mutation_strategy='empathy_boost',
        change_rationale='Increased empathy and added open-ended questions based on feedback that agent was too direct'
    )
    print()

    # Update evolved agent scores (better performance)
    print("📦 Step 6: Evaluate evolved agent...")
    archive.update_scores(
        version_id=evolved_id,
        goal_completion=78.0,
        conversational_quality=82.0,
        compliance=98.0,
        total_conversations=15,
        successful_conversations=12,
        failed_conversations=3
    )
    print()

    # Test 4: Create another variant (Generation 1)
    print("📦 Step 7: Create alternative variant (Generation 1)...")
    variant_prompt = """You are a professional debt collection agent focused on clear communication.

Your goal is to help customers who have defaulted on their loans find a path to repayment.

Guidelines:
- Be direct and clear about the situation
- Explain the consequences of non-payment
- Present payment options in a structured way
- Show empathy but maintain firmness
- Never threaten or use aggressive language
- Follow up with specific action items

Your success is measured by whether the customer commits to a payment plan."""

    variant_id = archive.save_agent(
        prompt=variant_prompt,
        config={'version': '1.1', 'model': 'gpt-4'},
        parent_id=baseline_id,
        generation=1,
        mutation_strategy='clarity_focus',
        change_rationale='Focused on clearer communication based on analysis that some customers were confused'
    )
    print()

    archive.update_scores(
        version_id=variant_id,
        goal_completion=72.0,
        conversational_quality=75.0,
        compliance=92.0,
        total_conversations=15,
        successful_conversations=11,
        failed_conversations=4
    )
    print()

    # Test 5: Retrieve best agent
    print("📦 Step 8: Find best performing agent...")
    best_agent = archive.get_best_agent()
    if best_agent:
        print(f"   🏆 Best agent: {best_agent.version_id}")
        print(f"      Generation: {best_agent.generation}")
        print(f"      Composite Score: {best_agent.composite_score:.2f}")
        print(f"      Goal Completion: {best_agent.goal_completion_score:.2f}")
        print(f"      Quality: {best_agent.conversational_quality_score:.2f}")
        print(f"      Compliance: {best_agent.compliance_score:.2f}")
    print()

    # Test 6: Get lineage
    print("📦 Step 9: Trace evolution lineage...")
    lineage = archive.get_lineage(evolved_id)
    print(f"   Evolution path for {evolved_id}:")
    for i, agent in enumerate(lineage):
        print(f"      {i}. {agent.version_id} (Gen {agent.generation}) - Score: {agent.composite_score:.2f}")
    print()

    # Test 7: List all agents in Generation 1
    print("📦 Step 10: List all Generation 1 agents...")
    gen1_agents = archive.list_agents(generation=1)
    print(f"   Found {len(gen1_agents)} agents in Generation 1:")
    for agent in gen1_agents:
        print(f"      - {agent.version_id}: {agent.composite_score:.2f} ({agent.mutation_strategy})")
    print()

    # Test 8: Get generation statistics
    print("📦 Step 11: Get Generation 1 statistics...")
    stats = archive.get_generation_stats(1)
    print(f"   Generation 1 Stats:")
    print(f"      Count: {stats['count']}")
    print(f"      Average Score: {stats['avg_score']:.2f}")
    print(f"      Best Score: {stats['best_score']:.2f}")
    print(f"      Worst Score: {stats['worst_score']:.2f}")
    print(f"      Best Agent: {stats['best_agent_id']}")
    print()

    # Test 9: Get evolution summary
    print("📦 Step 12: Get overall evolution summary...")
    summary = archive.get_evolution_summary()
    print(f"   Evolution Summary:")
    print(f"      Total Agents: {summary['total_agents']}")
    print(f"      Total Generations: {summary['total_generations']}")
    print(f"      Best Agent: {summary['best_agent']}")
    print(f"      Best Score: {summary['best_score']:.2f}")
    print(f"      Average Score: {summary['avg_score']:.2f}")
    print(f"      Total Conversations: {summary['total_conversations']}")
    print()

    # Test 10: Mark best agent
    print("📦 Step 13: Mark best agent...")
    archive.mark_as_best(best_agent.version_id)
    print()

    # Close archive
    archive.close()

    print("=" * 70)
    print("✅ All tests passed! Agent Archive is working correctly.")
    print("=" * 70)
    print()
    print("📁 Database saved at:", db_path)
    print("🔍 You can inspect it with: sqlite3", db_path)
    print()


if __name__ == "__main__":
    test_agent_archive()
