"""
Conversation Runner - Orchestrates conversations between agent and persona.

This module provides the ConversationRunner class that manages the dialogue
between a BaseAgent and a PersonaEngine, including logging and evaluation.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from core import BaseAgent
from simulation.persona_engine import PersonaEngine
from log_manager import ConversationLogger


class ConversationRunner:
    """
    Orchestrates conversations between an agent and a persona.

    Manages turn-taking, logging, termination detection, and provides
    a complete conversation result for evaluation.
    """

    def __init__(
        self,
        agent: BaseAgent,
        persona: PersonaEngine,
        logger: Optional[ConversationLogger] = None,
        max_turns: int = 20
    ):
        """
        Initialize the conversation runner.

        Args:
            agent: The BaseAgent instance
            persona: The PersonaEngine instance
            logger: Optional ConversationLogger (creates new if None)
            max_turns: Maximum number of conversation turns

        Example:
            >>> agent = BaseAgent("v0-abc123", prompt)
            >>> persona = PersonaEngine("angry_anthony")
            >>> runner = ConversationRunner(agent, persona)
            >>> result = runner.run_conversation()
        """
        self.agent = agent
        self.persona = persona
        self.logger = logger or ConversationLogger()
        self.max_turns = max_turns

        self.conversation_id = None
        self.turn_count = 0

    def run_conversation(
        self,
        opening_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a complete conversation between agent and persona.

        Args:
            opening_message: Optional custom opening from agent
                           (uses default if None)

        Returns:
            Dictionary with conversation result

        Example:
            >>> runner = ConversationRunner(agent, persona)
            >>> result = runner.run_conversation()
            >>> print(f"Goal achieved: {result['goal_achieved']}")
            >>> print(f"Turns: {result['turn_count']}")
        """
        # Generate conversation ID
        self.conversation_id = f"conv-{str(uuid.uuid4())[:8]}"

        # Start logging
        self.logger.start_conversation(
            conversation_id=self.conversation_id,
            agent_version_id=self.agent.agent_version_id,
            persona_name=self.persona.persona_name,
            metadata={
                'max_turns': self.max_turns,
                'persona_archetype': self.persona.persona_data.get('archetype', 'unknown')
            }
        )

        print()
        print("="* 70)
        print(f"🎬 Starting Conversation: {self.conversation_id}")
        print(f"   Agent: {self.agent.agent_version_id}")
        print(f"   Persona: {self.persona.persona_data.get('display_name', self.persona.persona_name)}")
        print("=" * 70)
        print()

        # Agent opens the conversation
        if opening_message is None:
            # Default opening
            company_name = "our company"
            opening_message = f"Hello, this is calling from {company_name}. Is this a good time to talk about your account?"

        # Log agent's opening
        self.logger.log_turn("agent", opening_message)
        print(f"🤖 AGENT: {opening_message}")

        self.turn_count = 0
        termination_reason = None

        # Conversation loop
        while self.turn_count < self.max_turns:
            # Persona responds to agent
            persona_response = self.persona.generate_response(opening_message if self.turn_count == 0 else agent_response)

            # Log persona response
            self.logger.log_turn("user", persona_response)
            print(f"👤 PERSONA: {persona_response}")

            self.turn_count += 1

            # Check if persona wants to terminate
            if self.persona.should_terminate:
                termination_reason = self.persona.termination_reason
                print(f"\n   ⏹️  Persona terminated: {termination_reason}")
                break

            # Agent responds to persona
            agent_response = self.agent.generate_response(persona_response)

            # Log agent response
            self.logger.log_turn("agent", agent_response)
            print(f"🤖 AGENT: {agent_response}")

            # Check if agent achieved goal
            if self.agent.goal_achieved:
                termination_reason = "goal_achieved"
                print(f"\n   ✅ Goal achieved!")
                break

            # Check max turns
            if self.turn_count >= self.max_turns:
                termination_reason = "max_turns_reached"
                print(f"\n   ⏱️  Max turns reached")
                break

        # Determine outcome
        outcome = self._determine_outcome(termination_reason)

        # Capture transcript before logger clears it
        transcript = [turn.to_dict() for turn in self.logger.current_turns]

        # End logging (we'll add evaluation in Phase 3)
        log_file = self.logger.end_conversation(
            outcome=outcome,
            termination_reason=termination_reason,
            evaluation_scores={}  # Will be filled in Phase 3
        )

        print()
        print("=" * 70)
        print(f"🏁 Conversation Ended")
        print(f"   Outcome: {outcome}")
        print(f"   Turns: {self.turn_count}")
        print(f"   Reason: {termination_reason}")
        print("=" * 70)
        print()

        # Return result
        return {
            'conversation_id': self.conversation_id,
            'agent_version_id': self.agent.agent_version_id,
            'persona_name': self.persona.persona_name,
            'transcript': transcript,
            'turn_count': self.turn_count,
            'outcome': outcome,
            'termination_reason': termination_reason,
            'goal_achieved': self.agent.goal_achieved,
            'log_file': log_file
        }

    def _determine_outcome(self, termination_reason: Optional[str]) -> str:
        """
        Determine the conversation outcome.

        Args:
            termination_reason: Why the conversation ended

        Returns:
            Outcome string
        """
        if termination_reason == "goal_achieved":
            return "success"
        elif termination_reason == "agreement_reached":
            return "success"
        elif termination_reason == "explicit_termination":
            return "failure"
        elif termination_reason == "max_turns_reached":
            return "incomplete"
        else:
            return "unknown"

    def run_batch(
        self,
        num_conversations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Run multiple conversations with the same agent and persona.

        Args:
            num_conversations: Number of conversations to run

        Returns:
            List of conversation results

        Example:
            >>> runner = ConversationRunner(agent, persona)
            >>> results = runner.run_batch(num_conversations=5)
            >>> success_rate = sum(1 for r in results if r['outcome'] == 'success') / len(results)
        """
        results = []

        for i in range(num_conversations):
            print(f"\n📊 Running conversation {i+1}/{num_conversations}...")

            # Reset agent and persona state
            self.agent.reset_conversation()
            self.persona.reset()

            # Run conversation
            result = self.run_conversation()
            results.append(result)

        # Summary
        print("\n" + "=" * 70)
        print(f"📈 Batch Results ({num_conversations} conversations)")
        print("=" * 70)

        successes = sum(1 for r in results if r['outcome'] == 'success')
        failures = sum(1 for r in results if r['outcome'] == 'failure')
        incomplete = sum(1 for r in results if r['outcome'] == 'incomplete')

        print(f"   Successes: {successes}/{num_conversations} ({successes/num_conversations*100:.1f}%)")
        print(f"   Failures: {failures}/{num_conversations}")
        print(f"   Incomplete: {incomplete}/{num_conversations}")
        print(f"   Avg Turns: {sum(r['turn_count'] for r in results) / num_conversations:.1f}")
        print("=" * 70)
        print()

        return results

    def __repr__(self):
        """String representation."""
        return f"<ConversationRunner(agent={self.agent.agent_version_id}, persona={self.persona.persona_name})>"
