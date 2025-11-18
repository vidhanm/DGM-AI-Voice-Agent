"""
Persona Engine - Simulates user personas for testing voice agents.

This module provides the PersonaEngine class that loads persona definitions
and generates realistic user responses using an LLM.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI
from anthropic import Anthropic

try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
except ImportError:
    CEREBRAS_AVAILABLE = False

from core import Config


class PersonaEngine:
    """
    Simulates a user persona for testing the voice agent.

    Loads a persona definition from YAML and uses an LLM (OpenAI, Anthropic,
    or Cerebras) to generate responses that match the persona's characteristics,
    background, and emotional state.
    """

    def __init__(
        self,
        persona_name: str,
        personas_dir: str = "simulation/personas",
        config: Optional[Config] = None
    ):
        """
        Initialize the persona engine.

        Args:
            persona_name: Name of the persona (e.g., "angry_anthony")
            personas_dir: Directory containing persona YAML files
            config: Configuration object (creates new if None)

        Example:
            >>> persona = PersonaEngine("angry_anthony")
            >>> response = persona.generate_response(
            ...     "Hello, this is calling about your loan"
            ... )
        """
        self.persona_name = persona_name
        self.personas_dir = Path(personas_dir)
        self.config = config or Config()

        # Load persona definition
        self.persona_data = self._load_persona()

        # LLM configuration
        self.provider = self.config.get('llm.provider', 'openai')
        self.model = self.config.get('llm.model', 'gpt-4-turbo-preview')
        self.temperature = 0.8  # Higher temperature for more varied persona responses
        self.max_tokens = 1000

        # Initialize LLM client
        self._init_llm_client()

        # Create persona system prompt
        self.persona_prompt = self._create_persona_prompt()

        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.turn_count = 0
        self.should_terminate = False
        self.termination_reason = None

        print(f"👤 Initialized persona: {self.persona_data.get('display_name', persona_name)}")
        print(f"   Archetype: {self.persona_data.get('archetype', 'unknown')}")

    def _load_persona(self) -> Dict[str, Any]:
        """Load persona definition from YAML file."""
        persona_file = self.personas_dir / f"{self.persona_name}.yaml"

        if not persona_file.exists():
            raise FileNotFoundError(f"Persona file not found: {persona_file}")

        with open(persona_file, 'r') as f:
            data = yaml.safe_load(f)

        return data

    def _init_llm_client(self):
        """Initialize the LLM client based on provider."""
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=api_key)

        elif self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = Anthropic(api_key=api_key)

        elif self.provider == 'cerebras':
            if not CEREBRAS_AVAILABLE:
                raise ValueError(
                    "Cerebras SDK not installed. Run: pip install cerebras-cloud-sdk"
                )
            api_key = os.getenv('CEREBRAS_API_KEY')
            if not api_key:
                raise ValueError("CEREBRAS_API_KEY environment variable not set")
            self.client = Cerebras(api_key=api_key)

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _create_persona_prompt(self) -> str:
        """Create a detailed system prompt for the persona."""
        pd = self.persona_data

        prompt = f"""You are roleplaying as {pd.get('display_name', self.persona_name)}, a persona in a debt collection conversation simulation.

## Character Profile
{pd.get('description', '')}

## Background
Age: {pd.get('background', {}).get('age', 'unknown')}
Occupation: {pd.get('background', {}).get('occupation', 'unknown')}
Financial Situation: {pd.get('background', {}).get('financial_situation', 'unknown')}
Debt Amount: {pd.get('background', {}).get('debt_amount', 'unknown')}
Payments Missed: {pd.get('background', {}).get('payments_missed', 'unknown')}
Reason for Default: {pd.get('background', {}).get('reason_for_default', 'unknown')}

## Personality Traits
"""
        traits = pd.get('personality_traits', [])
        for trait in traits:
            prompt += f"- {trait}\n"

        prompt += f"""
## Communication Style
Tone: {pd.get('communication_style', {}).get('tone', 'normal')}
Language: {pd.get('communication_style', {}).get('language', 'normal')}

## Emotional State
Primary Emotion: {pd.get('emotional_state', {}).get('primary_emotion', 'neutral')}

## Your Goals
Primary Goal: {pd.get('goals_and_motivations', {}).get('primary_goal', 'unknown')}
Hidden Need: {pd.get('goals_and_motivations', {}).get('hidden_need', 'unknown')}

## Important Instructions
1. Stay in character at all times
2. Respond as {pd.get('display_name', self.persona_name)} would, not as an AI
3. Use natural, conversational language
4. Show the emotions and behaviors described in your profile
5. Be realistic - people don't always say the perfect thing
6. Keep responses concise (1-3 sentences typically)
7. React naturally to how the agent treats you
8. Your responses should evolve based on the conversation

## Notes
{pd.get('notes', '')}

Remember: You are {pd.get('display_name', self.persona_name)}. Respond naturally as this person would in this situation.
"""

        return prompt

    def generate_response(
        self,
        agent_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a persona response to the agent's message.

        Args:
            agent_message: The agent's latest message
            metadata: Optional metadata

        Returns:
            Persona's response

        Example:
            >>> persona = PersonaEngine("angry_anthony")
            >>> response = persona.generate_response(
            ...     "I'm calling about your missed payment"
            ... )
        """
        # Add agent message to history
        self.conversation_history.append({
            'role': 'user',
            'content': f"[AGENT]: {agent_message}"
        })

        self.turn_count += 1

        # Generate response based on provider
        if self.provider == 'openai':
            response = self._generate_openai_response()
        elif self.provider == 'anthropic':
            response = self._generate_anthropic_response()
        elif self.provider == 'cerebras':
            response = self._generate_cerebras_response()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # Add persona response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })

        # Check termination conditions
        self._check_termination(response)

        return response

    def _generate_openai_response(self) -> str:
        """Generate response using OpenAI API."""
        messages = [
            {'role': 'system', 'content': self.persona_prompt}
        ] + self.conversation_history

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            # Fallback response based on persona
            return self._get_fallback_response()

    def _generate_anthropic_response(self) -> str:
        """Generate response using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.persona_prompt,
                messages=self.conversation_history
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ Anthropic API error: {e}")
            return self._get_fallback_response()

    def _generate_cerebras_response(self) -> str:
        """Generate response using Cerebras API (OpenAI-compatible)."""
        # Cerebras uses OpenAI-compatible API format
        messages = [
            {'role': 'system', 'content': self.persona_prompt}
        ] + self.conversation_history

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                stream=False  # Non-streaming for now
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Cerebras API error: {e}")
            return self._get_fallback_response()

    def _get_fallback_response(self) -> str:
        """Get a fallback response if LLM fails."""
        archetype = self.persona_data.get('archetype', 'neutral')

        fallbacks = {
            'hostile': "Look, I don't have time for this right now.",
            'avoidant': "Um, can I call you back later?",
            'analytical': "Can you explain that more clearly?",
            'cooperative': "Okay, what do you need from me?",
            'desperate': "I'm trying my best here..."
        }

        return fallbacks.get(archetype, "Could you repeat that?")

    def _check_termination(self, response: str):
        """
        Check if the conversation should terminate.

        Based on turn count, keywords, and persona termination conditions.
        """
        # Check turn count limits
        max_turns = 20  # Default maximum

        if self.turn_count >= max_turns:
            self.should_terminate = True
            self.termination_reason = "max_turns_reached"
            return

        # Check for explicit termination keywords
        termination_keywords = [
            "goodbye", "hang up", "hanging up", "i'm done",
            "stop calling", "end this call", "talk later", "bye"
        ]

        response_lower = response.lower()
        for keyword in termination_keywords:
            if keyword in response_lower:
                self.should_terminate = True
                self.termination_reason = "explicit_termination"
                return

        # Check for agreement keywords (successful termination)
        agreement_keywords = [
            "i agree", "sounds good", "that works", "i'll do that",
            "okay, deal", "yes, i will", "thank you"
        ]

        for keyword in agreement_keywords:
            if keyword in response_lower:
                # Only terminate on agreement after several turns
                if self.turn_count >= 5:
                    self.should_terminate = True
                    self.termination_reason = "agreement_reached"
                    return

    def reset(self):
        """Reset the persona for a new conversation."""
        self.conversation_history = []
        self.turn_count = 0
        self.should_terminate = False
        self.termination_reason = None
        print("🔄 Persona state reset")

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current persona state.

        Returns:
            Dictionary with persona state
        """
        return {
            'persona_name': self.persona_name,
            'display_name': self.persona_data.get('display_name', self.persona_name),
            'archetype': self.persona_data.get('archetype', 'unknown'),
            'turn_count': self.turn_count,
            'should_terminate': self.should_terminate,
            'termination_reason': self.termination_reason
        }

    def __repr__(self):
        """String representation."""
        return f"<PersonaEngine(name={self.persona_name}, turns={self.turn_count})>"
