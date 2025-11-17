"""
Base Agent - The core conversational agent for debt collection.

This module implements the BaseAgent class that uses an LLM to conduct
debt collection conversations based on configurable prompts.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI
from anthropic import Anthropic

from core import Config, PromptManager


class BaseAgent:
    """
    The core conversational agent for debt collection.

    Uses an LLM (OpenAI or Anthropic) to generate responses based on
    a system prompt, maintaining conversation context and tracking goals.
    """

    def __init__(
        self,
        agent_version_id: str,
        prompt: str,
        config: Optional[Config] = None,
        model: Optional[str] = None
    ):
        """
        Initialize the agent.

        Args:
            agent_version_id: Unique identifier for this agent version
            prompt: System prompt for the agent
            config: Configuration object (creates new if None)
            model: Override LLM model (uses config default if None)

        Example:
            >>> config = Config()
            >>> manager = PromptManager()
            >>> prompt = manager.create_agent_prompt(
            ...     "base_prompt.yaml",
            ...     company_name="Acme Financial",
            ...     agent_name="Sarah",
            ...     tone="empathetic"
            ... )
            >>> agent = BaseAgent("v0-abc123", prompt, config)
        """
        self.agent_version_id = agent_version_id
        self.system_prompt = prompt
        self.config = config or Config()

        # LLM configuration
        self.provider = self.config.get('llm.provider', 'openai')
        self.model = model or self.config.get('llm.model', 'gpt-4-turbo-preview')
        self.temperature = self.config.get('llm.temperature', 0.7)
        self.max_tokens = self.config.get('llm.max_tokens', 2000)

        # Initialize LLM client
        self._init_llm_client()

        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.conversation_context: Dict[str, Any] = {}
        self.goal_achieved = False

        print(f"🤖 Initialized {self.provider.upper()} agent: {agent_version_id}")
        print(f"   Model: {self.model}")
        print(f"   Prompt length: {len(self.system_prompt)} chars")

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

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_response(
        self,
        user_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response to the user's message.

        Args:
            user_message: The user's message
            metadata: Optional metadata for this turn

        Returns:
            Agent's response

        Example:
            >>> agent = BaseAgent("v0-abc123", prompt)
            >>> response = agent.generate_response(
            ...     "I can't pay my loan this month"
            ... )
            >>> print(response)
        """
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })

        # Generate response based on provider
        if self.provider == 'openai':
            response = self._generate_openai_response()
        elif self.provider == 'anthropic':
            response = self._generate_anthropic_response()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # Add assistant response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })

        # Check if goal achieved (simple keyword detection for now)
        if self._check_goal_achievement(response, user_message):
            self.goal_achieved = True

        return response

    def _generate_openai_response(self) -> str:
        """Generate response using OpenAI API."""
        messages = [
            {'role': 'system', 'content': self.system_prompt}
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
            return f"I apologize, I'm having technical difficulties. Could you please repeat that?"

    def _generate_anthropic_response(self) -> str:
        """Generate response using Anthropic API."""
        # Anthropic uses a different format
        # System prompt is separate, history doesn't include system messages
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=self.conversation_history
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ Anthropic API error: {e}")
            return f"I apologize, I'm having technical difficulties. Could you please repeat that?"

    def _check_goal_achievement(self, agent_response: str, user_message: str) -> bool:
        """
        Check if the conversation goal has been achieved.

        This is a simple heuristic for now. In Phase 3, we'll use
        proper LLM-based evaluation.

        Args:
            agent_response: Agent's latest response
            user_message: User's latest message

        Returns:
            True if goal likely achieved
        """
        # Keywords indicating agreement
        agreement_keywords = [
            'i agree', 'yes', 'okay', 'ok', 'sure', 'i will',
            "i'll pay", "i'll make", 'sounds good', 'that works',
            'i can do that', 'agreed', 'deal'
        ]

        user_lower = user_message.lower()

        # Check if user agreed to something
        for keyword in agreement_keywords:
            if keyword in user_lower:
                # Make sure it's in context of payment
                payment_context = ['payment', 'pay', 'plan', 'amount', 'date', 'schedule']
                agent_lower = agent_response.lower()

                if any(word in agent_lower for word in payment_context):
                    return True

        return False

    def reset_conversation(self):
        """Reset conversation state for a new conversation."""
        self.conversation_history = []
        self.conversation_context = {}
        self.goal_achieved = False
        print("🔄 Conversation state reset")

    def get_conversation_state(self) -> Dict[str, Any]:
        """
        Get the current conversation state.

        Returns:
            Dictionary with conversation state
        """
        return {
            'agent_version_id': self.agent_version_id,
            'turn_count': len(self.conversation_history) // 2,
            'goal_achieved': self.goal_achieved,
            'history_length': len(self.conversation_history),
            'context': self.conversation_context
        }

    def set_context(self, key: str, value: Any):
        """Set a context variable for this conversation."""
        self.conversation_context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self.conversation_context.get(key, default)

    def __repr__(self):
        """String representation."""
        return f"<BaseAgent(id={self.agent_version_id}, model={self.model}, turns={len(self.conversation_history)//2})>"
