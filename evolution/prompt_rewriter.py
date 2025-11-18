"""
PromptRewriter - LLM-based prompt evolution engine

This module implements the core Darwin-Gödel mutation mechanism that rewrites
agent prompts based on performance feedback and evaluation metrics.
"""

import os
from typing import Dict, Any, List, Optional
import json
from openai import OpenAI
from anthropic import Anthropic

try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
except ImportError:
    CEREBRAS_AVAILABLE = False


class PromptRewriter:
    """
    LLM-based prompt mutation engine that generates improved prompt variants
    based on performance feedback and evaluation metrics.

    Implements multiple mutation strategies:
    - Tone adjustment (empathy, assertiveness)
    - Structure modification (reordering, clarity)
    - Instruction clarification (specificity)
    - Few-shot example addition
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the PromptRewriter with configuration.

        Args:
            config: Configuration dictionary containing LLM settings
        """
        self.config = config
        self.provider = config.get('llm', {}).get('provider', 'openai')
        self.model = config.get('llm', {}).get('model', 'gpt-4-turbo-preview')

        # Initialize LLM client
        self._init_llm_client()

    def _init_llm_client(self):
        """Initialize the appropriate LLM client based on provider."""
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
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

    def propose_improvements(
        self,
        current_prompt: str,
        evaluation_results: List[Dict[str, Any]],
        strategy: str = "adaptive"
    ) -> Dict[str, Any]:
        """
        Analyze performance and propose prompt improvements.

        Args:
            current_prompt: The current agent prompt
            evaluation_results: List of evaluation results from test conversations
            strategy: Mutation strategy to use

        Returns:
            Dictionary containing:
                - new_prompt: The improved prompt
                - rationale: Explanation of changes
                - strategy_used: Strategy that was applied
                - addressed_issues: List of issues addressed
        """
        # Analyze evaluation results to identify failure patterns
        failure_analysis = self._analyze_failures(evaluation_results)

        # Generate meta-prompt based on strategy
        meta_prompt = self._create_meta_prompt(
            current_prompt,
            failure_analysis,
            strategy
        )

        # Get LLM to rewrite prompt
        response = self._generate_llm_response(meta_prompt)

        # Parse response
        result = self._parse_rewrite_response(response)
        result['strategy_used'] = strategy
        result['failure_analysis'] = failure_analysis

        return result

    def _analyze_failures(self, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze evaluation results to identify common failure patterns.

        Args:
            evaluation_results: List of evaluation dictionaries

        Returns:
            Dictionary with failure analysis including:
                - avg_scores: Average scores across metrics
                - common_issues: List of recurring problems
                - persona_specific: Issues grouped by persona type
        """
        if not evaluation_results:
            return {
                'avg_scores': {},
                'common_issues': [],
                'persona_specific': {}
            }

        # Calculate average scores
        total_goal = 0.0
        total_quality = 0.0
        total_compliance = 0.0
        total_composite = 0.0
        count = len(evaluation_results)

        common_issues = []
        persona_issues = {}

        for result in evaluation_results:
            metrics = result.get('metrics', {})

            # Aggregate scores
            total_goal += metrics.get('goal_completion', {}).get('score', 0.0)
            total_quality += metrics.get('conversational_quality', {}).get('score', 0.0)
            total_compliance += metrics.get('compliance', {}).get('score', 0.0)
            total_composite += result.get('composite_score', 0.0)

            # Collect issues
            goal_issues = metrics.get('goal_completion', {}).get('explanation', '')
            quality_issues = metrics.get('conversational_quality', {}).get('breakdown', {})
            compliance_issues = metrics.get('compliance', {}).get('violations', [])

            if goal_issues:
                common_issues.append(f"Goal: {goal_issues}")

            for metric, details in quality_issues.items():
                if isinstance(details, dict) and details.get('score', 100) < 50:
                    common_issues.append(f"Quality-{metric}: {details.get('issues', [])}")

            if compliance_issues:
                common_issues.append(f"Compliance: {', '.join(compliance_issues)}")

            # Group by persona
            persona = result.get('persona_name', 'unknown')
            if persona not in persona_issues:
                persona_issues[persona] = []
            persona_issues[persona].append({
                'score': result.get('composite_score', 0.0),
                'issues': [goal_issues] + [str(v) for v in compliance_issues]
            })

        avg_scores = {
            'goal_completion': total_goal / count,
            'conversational_quality': total_quality / count,
            'compliance': total_compliance / count,
            'composite': total_composite / count
        }

        return {
            'avg_scores': avg_scores,
            'common_issues': common_issues[:10],  # Top 10 issues
            'persona_specific': persona_issues
        }

    def _create_meta_prompt(
        self,
        current_prompt: str,
        failure_analysis: Dict[str, Any],
        strategy: str
    ) -> str:
        """
        Create the meta-prompt that instructs the LLM how to rewrite the agent prompt.

        Args:
            current_prompt: Current agent prompt
            failure_analysis: Analysis of performance issues
            strategy: Mutation strategy to apply

        Returns:
            Meta-prompt string
        """
        avg_scores = failure_analysis.get('avg_scores', {})
        common_issues = failure_analysis.get('common_issues', [])

        meta_prompt = f"""You are an expert AI prompt engineer specializing in debt collection agent optimization.

Your task is to improve the following debt collection agent prompt based on performance evaluation data.

CURRENT PROMPT:
{current_prompt}

PERFORMANCE ANALYSIS:
- Goal Completion Score: {avg_scores.get('goal_completion', 0):.1f}/100
- Conversational Quality Score: {avg_scores.get('conversational_quality', 0):.1f}/100
- Compliance Score: {avg_scores.get('compliance', 0):.1f}/100
- Composite Score: {avg_scores.get('composite', 0):.1f}/100

IDENTIFIED ISSUES:
{chr(10).join(f'- {issue}' for issue in common_issues) if common_issues else '- No specific issues identified'}

MUTATION STRATEGY: {strategy}

INSTRUCTIONS:
Based on the {strategy} strategy, rewrite the prompt to address the identified weaknesses while maintaining compliance and professionalism.

"""

        # Add strategy-specific guidance
        if strategy == "tone_adjustment":
            meta_prompt += """
Focus on adjusting the tone and empathy level:
- Increase empathy if quality scores are low
- Balance assertiveness with compassion
- Improve rapport-building language
"""
        elif strategy == "structure_modification":
            meta_prompt += """
Focus on reorganizing the prompt structure:
- Improve clarity and readability
- Reorder instructions for better flow
- Add section headers if helpful
- Remove redundant instructions
"""
        elif strategy == "instruction_clarification":
            meta_prompt += """
Focus on making instructions more specific:
- Add concrete examples where vague
- Specify exact behaviors expected
- Clarify edge case handling
- Define success criteria clearly
"""
        elif strategy == "few_shot_examples":
            meta_prompt += """
Focus on adding concrete examples:
- Add example dialogues for difficult scenarios
- Show good vs. bad responses
- Include persona-specific examples
- Demonstrate compliance best practices
"""
        else:  # adaptive
            meta_prompt += """
Focus on the most impactful improvements:
- Address the lowest-scoring metrics first
- Balance multiple improvement areas
- Make changes that will have broad impact
- Maintain overall prompt coherence
"""

        meta_prompt += """

RESPONSE FORMAT:
Provide your response as a JSON object with the following structure:
{
    "new_prompt": "The complete rewritten prompt",
    "rationale": "Detailed explanation of what you changed and why",
    "addressed_issues": ["issue1", "issue2", "issue3"],
    "expected_improvements": "What metrics should improve and by how much"
}

Ensure the new_prompt is complete and ready to use. Do not use placeholders.
"""

        return meta_prompt

    def _generate_llm_response(self, prompt: str) -> str:
        """
        Generate response from LLM.

        Args:
            prompt: The meta-prompt

        Returns:
            LLM response string
        """
        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI prompt engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content

        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        elif self.provider == 'cerebras':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI prompt engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=4000,
                stream=False
            )
            return response.choices[0].message.content

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _parse_rewrite_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM's rewrite response.

        Args:
            response: Raw LLM response

        Returns:
            Parsed dictionary with new_prompt, rationale, etc.
        """
        try:
            # Try to parse as JSON
            if '```json' in response:
                # Extract JSON from code block
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            elif '{' in response and '}' in response:
                # Find JSON object
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            else:
                json_str = response

            parsed = json.loads(json_str)

            # Validate required fields
            if 'new_prompt' not in parsed:
                raise ValueError("Missing 'new_prompt' in response")

            return {
                'new_prompt': parsed.get('new_prompt', ''),
                'rationale': parsed.get('rationale', 'No rationale provided'),
                'addressed_issues': parsed.get('addressed_issues', []),
                'expected_improvements': parsed.get('expected_improvements', '')
            }

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: treat entire response as new prompt
            return {
                'new_prompt': response,
                'rationale': 'Unable to parse structured response',
                'addressed_issues': [],
                'expected_improvements': '',
                'parse_error': str(e)
            }

    def explain_changes(self, old_prompt: str, new_prompt: str) -> str:
        """
        Generate a detailed explanation of changes between two prompts.

        Args:
            old_prompt: Original prompt
            new_prompt: New prompt

        Returns:
            Detailed explanation of differences
        """
        explanation_prompt = f"""Compare these two AI agent prompts and explain what changed:

OLD PROMPT:
{old_prompt[:1000]}...

NEW PROMPT:
{new_prompt[:1000]}...

Provide a concise summary of:
1. Major structural changes
2. Tone/style modifications
3. New instructions added
4. Instructions removed or modified
5. Overall impact on agent behavior

Keep the explanation under 200 words."""

        return self._generate_llm_response(explanation_prompt)

    def generate_variant(
        self,
        base_prompt: str,
        strategy: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a single prompt variant using specified strategy.

        Args:
            base_prompt: The base prompt to mutate
            strategy: Mutation strategy to use
            context: Optional context for mutation (failures, scores, etc.)

        Returns:
            Dictionary with variant and metadata
        """
        if context is None:
            context = {'avg_scores': {}, 'common_issues': []}

        # Create fake evaluation results from context
        evaluation_results = [{
            'composite_score': context.get('avg_scores', {}).get('composite', 50.0),
            'metrics': {
                'goal_completion': {'score': context.get('avg_scores', {}).get('goal_completion', 50.0)},
                'conversational_quality': {'score': context.get('avg_scores', {}).get('conversational_quality', 50.0)},
                'compliance': {'score': context.get('avg_scores', {}).get('compliance', 100.0)}
            }
        }]

        return self.propose_improvements(base_prompt, evaluation_results, strategy)


# Example usage
if __name__ == "__main__":
    print("PromptRewriter - Darwin-Gödel Prompt Evolution Engine")
    print("=" * 60)
    print("\nThis module provides LLM-based prompt mutation capabilities.")
    print("Use it through the EvolutionaryLoop for automatic prompt improvement.")
