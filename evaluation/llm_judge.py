"""
LLM-as-Judge Evaluator

Uses an LLM to provide sophisticated evaluation of conversation quality,
going beyond simple rule-based metrics.
"""

import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from anthropic import Anthropic

try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
except ImportError:
    CEREBRAS_AVAILABLE = False

from core import Config


class LLMJudge:
    """
    Uses an LLM to evaluate conversation quality.

    Provides nuanced assessment that goes beyond keyword matching,
    understanding context, tone, and effectiveness.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize LLM judge.

        Args:
            config: Configuration object
        """
        self.config = config or Config()

        # LLM configuration (use simpler/cheaper model for evaluation)
        self.provider = self.config.get('llm.provider', 'openai')
        # Use faster model for judging (or configured model for Cerebras)
        if self.provider == 'openai':
            self.model = 'gpt-3.5-turbo'
        elif self.provider == 'cerebras':
            self.model = self.config.get('llm.model', 'llama-3.3-70b')  # Use configured model
        else:
            self.model = 'claude-3-haiku-20240307'
        self.temperature = 0.3  # Lower temperature for consistent evaluation
        self.max_tokens = 1500

        # Initialize LLM client
        self._init_llm_client()

    def _init_llm_client(self):
        """Initialize the LLM client."""
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=api_key)

        elif self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
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

    def evaluate_conversation(
        self,
        transcript: List[Dict[str, str]],
        persona_name: str
    ) -> Dict[str, Any]:
        """
        Evaluate a conversation using LLM judgment.

        Args:
            transcript: List of conversation turns
            persona_name: Name of the persona

        Returns:
            Dict with LLM evaluation results
        """
        # Format transcript for LLM
        formatted_transcript = self._format_transcript(transcript)

        # Create evaluation prompt
        eval_prompt = self._create_evaluation_prompt(
            formatted_transcript,
            persona_name
        )

        # Get LLM evaluation
        evaluation = self._get_llm_evaluation(eval_prompt)

        return evaluation

    def _format_transcript(self, transcript: List[Dict[str, str]]) -> str:
        """Format transcript for LLM."""
        lines = []
        for turn in transcript:
            speaker = "AGENT" if turn['speaker'] == 'agent' else "USER"
            lines.append(f"{speaker}: {turn['message']}")

        return "\n".join(lines)

    def _create_evaluation_prompt(
        self,
        transcript: str,
        persona_name: str
    ) -> str:
        """Create the evaluation prompt for the LLM."""
        return f"""You are an expert evaluator of debt collection conversations. Analyze the following conversation and provide scores.

CONVERSATION TRANSCRIPT:
{transcript}

PERSONA: {persona_name}

Evaluate the conversation on these dimensions:

1. GOAL ACHIEVEMENT (0-100):
   - Did the user commit to a payment or payment plan?
   - Were specific details (amount, date) discussed?
   - Was there a clear next step?

2. CONVERSATIONAL QUALITY (0-100):
   - Was the agent empathetic and professional?
   - Did the conversation flow naturally?
   - Were there any repetitions or awkward moments?
   - Did the agent respond appropriately to the user's concerns?

3. COMPLIANCE (0-100):
   - Did the agent avoid threats or pressure tactics?
   - Was the language professional and respectful?
   - Were privacy and legal guidelines followed?
   - Any use of inappropriate language?

4. OVERALL ASSESSMENT:
   - What did the agent do well?
   - What could be improved?
   - Was the approach appropriate for this persona?

Provide your evaluation in this exact JSON format:
{{
    "goal_achievement": {{
        "score": <0-100>,
        "reasoning": "<brief explanation>"
    }},
    "conversational_quality": {{
        "score": <0-100>,
        "reasoning": "<brief explanation>"
    }},
    "compliance": {{
        "score": <0-100>,
        "reasoning": "<brief explanation>",
        "violations": ["<list any violations or empty array>"]
    }},
    "overall": {{
        "strengths": ["<strength 1>", "<strength 2>"],
        "weaknesses": ["<weakness 1>", "<weakness 2>"],
        "recommendation": "<brief recommendation>"
    }}
}}

Respond ONLY with valid JSON, no other text."""

    def _get_llm_evaluation(self, prompt: str) -> Dict[str, Any]:
        """Get evaluation from LLM."""
        try:
            if self.provider == 'openai':
                return self._get_openai_evaluation(prompt)
            elif self.provider == 'anthropic':
                return self._get_anthropic_evaluation(prompt)
            elif self.provider == 'cerebras':
                return self._get_cerebras_evaluation(prompt)
        except Exception as e:
            print(f"❌ LLM Judge error: {e}")
            return self._get_fallback_evaluation()

    def _get_openai_evaluation(self, prompt: str) -> Dict[str, Any]:
        """Get evaluation from OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert conversation evaluator. Respond only with valid JSON.'
                },
                {'role': 'user', 'content': prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        content = response.choices[0].message.content

        # Parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_fallback_evaluation()

    def _get_anthropic_evaluation(self, prompt: str) -> Dict[str, Any]:
        """Get evaluation from Anthropic."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system='You are an expert conversation evaluator. Respond only with valid JSON.',
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )

        content = response.content[0].text

        # Parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_fallback_evaluation()

    def _get_cerebras_evaluation(self, prompt: str) -> Dict[str, Any]:
        """Get evaluation from Cerebras (OpenAI-compatible API)."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert conversation evaluator. Respond only with valid JSON.'
                },
                {'role': 'user', 'content': prompt}
            ],
            temperature=self.temperature,
            max_completion_tokens=self.max_tokens,
            stream=False
        )

        content = response.choices[0].message.content

        # Parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_fallback_evaluation()

    def _get_fallback_evaluation(self) -> Dict[str, Any]:
        """Fallback evaluation if LLM fails."""
        return {
            'goal_achievement': {
                'score': 50,
                'reasoning': 'LLM evaluation failed, using default'
            },
            'conversational_quality': {
                'score': 50,
                'reasoning': 'LLM evaluation failed, using default'
            },
            'compliance': {
                'score': 100,
                'reasoning': 'No critical issues detected (fallback)',
                'violations': []
            },
            'overall': {
                'strengths': ['Unable to evaluate'],
                'weaknesses': ['LLM evaluation unavailable'],
                'recommendation': 'Re-evaluate with working LLM'
            }
        }

    def __repr__(self):
        return f"<LLMJudge(provider={self.provider}, model={self.model})>"
