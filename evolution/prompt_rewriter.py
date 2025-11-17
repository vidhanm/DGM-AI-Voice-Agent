"""
Prompt Rewriter - Generates improved prompt variants based on failure analysis.

This module uses LLM-based meta-prompting to analyze conversation failures
and propose targeted improvements to the agent's system prompt.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime

from core import Config


class PromptRewriter:
    """
    Analyzes conversation failures and generates improved prompt variants.

    Uses different mutation strategies to create diverse prompt variants:
    - Tone adjustment: Modify empathy, professionalism, assertiveness
    - Structure modification: Reorganize sections, add/remove guidelines
    - Instruction clarification: Make specific instructions clearer
    - Example addition: Add concrete examples to guidelines
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the prompt rewriter.

        Args:
            config: Configuration object
        """
        self.config = config or Config()

        # Initialize LLM client based on provider
        provider = self.config.get('llm.provider', 'openai')
        if provider == 'openai':
            import openai
            self.client = openai.OpenAI(
                api_key=self.config.get('openai_api_key')
            )
            self.model = self.config.get('llm.model', 'gpt-4-turbo-preview')
            self.use_openai = True
        elif provider == 'anthropic':
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=self.config.get('anthropic_api_key')
            )
            self.model = self.config.get('llm.model', 'claude-3-opus-20240229')
            self.use_openai = False
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def analyze_failures(
        self,
        evaluation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a set of conversation evaluations to identify failure patterns.

        Args:
            evaluation_results: List of evaluation results from Evaluator

        Returns:
            Dict with failure analysis

        Example:
            >>> rewriter = PromptRewriter()
            >>> analysis = rewriter.analyze_failures(results)
            >>> print(analysis['main_issues'])
        """
        print("\n🔍 Analyzing conversation failures...")

        # Separate successful and failed conversations
        failed = [r for r in evaluation_results if not r.get('passed', True) or r.get('composite_score', 0) < 70]
        successful = [r for r in evaluation_results if r.get('passed', True) and r.get('composite_score', 0) >= 70]

        print(f"   Failed: {len(failed)}, Successful: {len(successful)}")

        # Extract failure patterns by metric
        goal_failures = []
        quality_failures = []
        compliance_failures = []

        for result in failed:
            if result.get('goal_completion', {}).get('score', 0) < 60:
                goal_failures.append(result)
            if result.get('conversational_quality', {}).get('score', 0) < 60:
                quality_failures.append(result)
            if not result.get('compliance', {}).get('passed', True):
                compliance_failures.append(result)

        # Identify common patterns
        patterns = {
            'goal_completion_issues': self._extract_goal_issues(goal_failures),
            'quality_issues': self._extract_quality_issues(quality_failures),
            'compliance_issues': self._extract_compliance_issues(compliance_failures),
            'persona_specific_issues': self._extract_persona_issues(failed)
        }

        # Generate summary
        analysis = {
            'total_conversations': len(evaluation_results),
            'failed_count': len(failed),
            'success_rate': len(successful) / len(evaluation_results) if evaluation_results else 0,
            'failure_patterns': patterns,
            'priority_issues': self._prioritize_issues(patterns),
            'timestamp': datetime.utcnow().isoformat()
        }

        print(f"   Success rate: {analysis['success_rate']*100:.1f}%")
        print(f"   Priority issues: {len(analysis['priority_issues'])}")

        return analysis

    def _extract_goal_issues(self, failures: List[Dict]) -> List[str]:
        """Extract common goal completion issues."""
        issues = []

        for result in failures:
            breakdown = result.get('goal_completion', {}).get('breakdown', {})

            if not breakdown.get('has_commitment', False):
                issues.append("Agent failed to secure payment commitment")
            if not breakdown.get('has_specifics', False):
                issues.append("Agent didn't get specific payment details (amount/date)")
            if not breakdown.get('has_followup', False):
                issues.append("Agent didn't establish follow-up actions")

        # Count and deduplicate
        issue_counts = {}
        for issue in issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return [f"{issue} ({count}x)" for issue, count in sorted(
            issue_counts.items(), key=lambda x: x[1], reverse=True
        )]

    def _extract_quality_issues(self, failures: List[Dict]) -> List[str]:
        """Extract common conversational quality issues."""
        issues = []

        for result in failures:
            breakdown = result.get('conversational_quality', {}).get('breakdown', {})

            if breakdown.get('has_repetitions', False):
                issues.append("Agent repeated itself or got stuck in loops")
            if breakdown.get('poor_tone', False):
                issues.append("Agent's tone was inappropriate")
            if breakdown.get('unnatural_flow', False):
                issues.append("Conversation flow was unnatural")

        issue_counts = {}
        for issue in issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return [f"{issue} ({count}x)" for issue, count in sorted(
            issue_counts.items(), key=lambda x: x[1], reverse=True
        )]

    def _extract_compliance_issues(self, failures: List[Dict]) -> List[str]:
        """Extract compliance violations."""
        issues = []

        for result in failures:
            violations = result.get('compliance', {}).get('breakdown', {}).get('violations', [])
            issues.extend(violations)

        issue_counts = {}
        for issue in issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return [f"{issue} ({count}x)" for issue, count in sorted(
            issue_counts.items(), key=lambda x: x[1], reverse=True
        )]

    def _extract_persona_issues(self, failures: List[Dict]) -> Dict[str, List[str]]:
        """Identify issues specific to certain personas."""
        persona_issues = {}

        for result in failures:
            persona = result.get('persona_name', 'unknown')
            if persona not in persona_issues:
                persona_issues[persona] = []

            # Add specific failure reason
            reason = f"Score: {result.get('composite_score', 0):.1f}"
            persona_issues[persona].append(reason)

        return persona_issues

    def _prioritize_issues(self, patterns: Dict[str, Any]) -> List[str]:
        """Prioritize issues by severity and frequency."""
        priority = []

        # Compliance is highest priority
        if patterns['compliance_issues']:
            priority.extend(patterns['compliance_issues'][:3])

        # Then goal completion
        if patterns['goal_completion_issues']:
            priority.extend(patterns['goal_completion_issues'][:3])

        # Then quality
        if patterns['quality_issues']:
            priority.extend(patterns['quality_issues'][:2])

        return priority

    def generate_variants(
        self,
        current_prompt: str,
        failure_analysis: Dict[str, Any],
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate improved prompt variants based on failure analysis.

        Args:
            current_prompt: The current agent prompt
            failure_analysis: Analysis from analyze_failures()
            num_variants: Number of variants to generate

        Returns:
            List of variant dictionaries with prompt, strategy, and rationale

        Example:
            >>> variants = rewriter.generate_variants(prompt, analysis, 3)
            >>> for v in variants:
            ...     print(f"{v['strategy']}: {v['rationale']}")
        """
        print(f"\n🧬 Generating {num_variants} prompt variants...")

        strategies = [
            'tone_adjustment',
            'structure_modification',
            'instruction_clarification',
            'example_addition'
        ]

        variants = []

        for i in range(num_variants):
            strategy = strategies[i % len(strategies)]

            print(f"   Generating variant {i+1}/{num_variants} ({strategy})...")

            variant = self._generate_single_variant(
                current_prompt,
                failure_analysis,
                strategy
            )

            variants.append(variant)

        print(f"✅ Generated {len(variants)} variants")
        return variants

    def _generate_single_variant(
        self,
        current_prompt: str,
        failure_analysis: Dict[str, Any],
        strategy: str
    ) -> Dict[str, Any]:
        """Generate a single prompt variant using specified strategy."""

        # Build the meta-prompt for LLM
        meta_prompt = self._build_meta_prompt(
            current_prompt,
            failure_analysis,
            strategy
        )

        # Generate improved prompt using LLM
        if self.use_openai:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at improving AI agent prompts."},
                    {"role": "user", "content": meta_prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            content = response.choices[0].message.content
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": meta_prompt}
                ]
            )
            content = response.content[0].text

        # Parse the response
        improved_prompt, rationale = self._parse_llm_response(content)

        return {
            'prompt': improved_prompt,
            'strategy': strategy,
            'rationale': rationale,
            'failure_analysis': failure_analysis,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _build_meta_prompt(
        self,
        current_prompt: str,
        failure_analysis: Dict[str, Any],
        strategy: str
    ) -> str:
        """Build the meta-prompt for generating improved variants."""

        priority_issues = failure_analysis.get('priority_issues', [])
        success_rate = failure_analysis.get('success_rate', 0) * 100

        strategy_instructions = {
            'tone_adjustment': """
Adjust the TONE and EMOTIONAL APPROACH of the prompt:
- Make it more empathetic and understanding
- Balance professionalism with warmth
- Emphasize listening and patience
- Reduce any language that might feel pushy or aggressive
""",
            'structure_modification': """
REORGANIZE and RESTRUCTURE the prompt:
- Move critical information earlier
- Create clearer sections
- Add emphasis to important guidelines
- Remove redundant or conflicting instructions
""",
            'instruction_clarification': """
Make INSTRUCTIONS MORE SPECIFIC and ACTIONABLE:
- Turn vague guidelines into concrete steps
- Add explicit do's and don'ts
- Clarify success criteria
- Provide decision-making guidance
""",
            'example_addition': """
Add CONCRETE EXAMPLES to illustrate guidelines:
- Show good vs bad conversation patterns
- Provide sample responses for difficult situations
- Illustrate how to handle specific persona types
- Demonstrate compliance in action
"""
        }

        meta_prompt = f"""You are improving a debt collection agent's system prompt based on performance data.

CURRENT PERFORMANCE:
- Success rate: {success_rate:.1f}%
- Conversations evaluated: {failure_analysis.get('total_conversations', 0)}

KEY ISSUES TO ADDRESS:
{chr(10).join(f"- {issue}" for issue in priority_issues[:5])}

IMPROVEMENT STRATEGY: {strategy}
{strategy_instructions.get(strategy, '')}

CURRENT PROMPT:
{current_prompt}

TASK:
Generate an improved version of this prompt that addresses the key issues using the {strategy} strategy.

REQUIREMENTS:
1. Keep the same overall structure and YAML format
2. Maintain all compliance requirements (FDCPA, privacy, etc.)
3. Focus on addressing the specific issues identified
4. Make concrete, targeted improvements
5. Don't make the prompt excessively long

OUTPUT FORMAT:
First, provide your RATIONALE (2-3 sentences explaining what you changed and why).
Then provide the IMPROVED PROMPT on a new line after "---PROMPT---"

Example format:
RATIONALE: I adjusted the tone to be more empathetic by adding active listening cues and removing pushy language. This addresses the issue of poor tone in quality scores.

---PROMPT---
[Your improved prompt here]
"""

        return meta_prompt

    def _parse_llm_response(self, content: str) -> Tuple[str, str]:
        """Parse LLM response to extract rationale and improved prompt."""

        # Split on the delimiter
        if '---PROMPT---' in content:
            parts = content.split('---PROMPT---')
            rationale = parts[0].strip()
            improved_prompt = parts[1].strip()

            # Extract just the rationale text
            if 'RATIONALE:' in rationale:
                rationale = rationale.split('RATIONALE:')[1].strip()
        else:
            # Fallback: treat entire response as the prompt
            rationale = "LLM generated improved prompt"
            improved_prompt = content.strip()

        return improved_prompt, rationale

    def explain_changes(
        self,
        old_prompt: str,
        new_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate a detailed explanation of changes between two prompts.

        Args:
            old_prompt: Previous prompt version
            new_prompt: New prompt version

        Returns:
            Dict with change analysis
        """
        # Simple diff analysis
        old_lines = set(old_prompt.split('\n'))
        new_lines = set(new_prompt.split('\n'))

        added = new_lines - old_lines
        removed = old_lines - new_lines

        return {
            'lines_added': len(added),
            'lines_removed': len(removed),
            'added_content': list(added)[:10],  # First 10 additions
            'removed_content': list(removed)[:10],  # First 10 removals
            'length_change': len(new_prompt) - len(old_prompt),
            'significant_change': len(added) + len(removed) > 5
        }
