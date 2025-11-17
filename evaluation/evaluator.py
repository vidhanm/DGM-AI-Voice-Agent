"""
Evaluator - Orchestrates all evaluation metrics.

This module provides the main Evaluator class that combines
rule-based metrics and LLM-as-judge evaluation to score conversations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from evaluation.metrics import (
    GoalCompletionMetric,
    ConversationalQualityMetric,
    ComplianceMetric
)
from evaluation.llm_judge import LLMJudge
from core import Config


class Evaluator:
    """
    Main evaluator that orchestrates all metrics.

    Combines:
    - Rule-based metrics (fast, deterministic)
    - LLM-as-judge (sophisticated, nuanced)

    Provides comprehensive scoring for conversations.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        use_llm_judge: bool = True
    ):
        """
        Initialize evaluator.

        Args:
            config: Configuration object
            use_llm_judge: Whether to use LLM-as-judge (requires API key)
        """
        self.config = config or Config()
        self.use_llm_judge = use_llm_judge

        # Initialize metrics
        self.goal_metric = GoalCompletionMetric()
        self.quality_metric = ConversationalQualityMetric()
        self.compliance_metric = ComplianceMetric()

        # Initialize LLM judge if enabled
        if self.use_llm_judge:
            try:
                self.llm_judge = LLMJudge(config)
                print("✅ LLM Judge initialized")
            except Exception as e:
                print(f"⚠️  LLM Judge unavailable: {e}")
                print("   Falling back to rule-based metrics only")
                self.use_llm_judge = False
                self.llm_judge = None
        else:
            self.llm_judge = None

        # Get metric weights from config
        self.weights = self._get_weights()

    def _get_weights(self) -> Dict[str, float]:
        """Get metric weights from configuration."""
        return {
            'goal_completion': self.config.get(
                'evaluation.metrics.goal_completion.weight', 0.4
            ),
            'conversational_quality': self.config.get(
                'evaluation.metrics.conversational_quality.weight', 0.3
            ),
            'compliance': self.config.get(
                'evaluation.metrics.compliance.weight', 0.3
            )
        }

    def evaluate_conversation(
        self,
        transcript: List[Dict[str, str]],
        persona_name: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a complete conversation.

        Args:
            transcript: List of conversation turns
                       [{'speaker': 'agent', 'message': '...'}, ...]
            persona_name: Name of persona in conversation
            conversation_id: Optional conversation ID for logging

        Returns:
            Dict with comprehensive evaluation results

        Example:
            >>> evaluator = Evaluator()
            >>> result = evaluator.evaluate_conversation(
            ...     transcript, "angry_anthony"
            ... )
            >>> print(result['composite_score'])
        """
        print()
        print("=" * 70)
        print(f"📊 Evaluating Conversation: {conversation_id or 'N/A'}")
        print(f"   Persona: {persona_name}")
        print(f"   Turns: {len(transcript)}")
        print("=" * 70)

        # Run rule-based metrics
        goal_result = self.goal_metric.evaluate(transcript)
        quality_result = self.quality_metric.evaluate(transcript)
        compliance_result = self.compliance_metric.evaluate(transcript)

        print()
        print("📈 Rule-Based Metrics:")
        print(f"   Goal Completion: {goal_result['score']:.1f}/100")
        print(f"      {goal_result['explanation']}")
        print(f"   Conversational Quality: {quality_result['score']:.1f}/100")
        print(f"      {quality_result['explanation']}")
        print(f"   Compliance: {compliance_result['score']:.1f}/100")
        print(f"      {compliance_result['explanation']}")

        # Run LLM judge if available
        llm_evaluation = None
        if self.use_llm_judge and self.llm_judge:
            print()
            print("🤖 Running LLM Judge evaluation...")
            try:
                llm_evaluation = self.llm_judge.evaluate_conversation(
                    transcript, persona_name
                )
                print("   ✅ LLM Judge complete")
            except Exception as e:
                print(f"   ⚠️  LLM Judge failed: {e}")
                llm_evaluation = None

        # Calculate composite score
        composite_score = self._calculate_composite_score(
            goal_result['score'],
            quality_result['score'],
            compliance_result['score']
        )

        # Check if passed (compliance is critical)
        passed = compliance_result['passed']

        print()
        print("=" * 70)
        print(f"🎯 COMPOSITE SCORE: {composite_score:.1f}/100")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        print("=" * 70)
        print()

        # Build result
        result = {
            'conversation_id': conversation_id,
            'persona_name': persona_name,
            'evaluated_at': datetime.utcnow().isoformat(),
            'passed': passed,
            'composite_score': composite_score,
            'metrics': {
                'goal_completion': goal_result,
                'conversational_quality': quality_result,
                'compliance': compliance_result
            },
            'weights': self.weights,
            'llm_evaluation': llm_evaluation
        }

        return result

    def _calculate_composite_score(
        self,
        goal_score: float,
        quality_score: float,
        compliance_score: float
    ) -> float:
        """
        Calculate weighted composite score.

        Args:
            goal_score: Goal completion score (0-100)
            quality_score: Quality score (0-100)
            compliance_score: Compliance score (0-100)

        Returns:
            Composite score (0-100)
        """
        composite = (
            goal_score * self.weights['goal_completion'] +
            quality_score * self.weights['conversational_quality'] +
            compliance_score * self.weights['compliance']
        )

        return round(composite, 2)

    def evaluate_batch(
        self,
        conversations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple conversations.

        Args:
            conversations: List of conversation dicts with transcript, persona

        Returns:
            List of evaluation results
        """
        results = []

        print()
        print("=" * 70)
        print(f"📊 Batch Evaluation: {len(conversations)} conversations")
        print("=" * 70)

        for i, conv in enumerate(conversations):
            print(f"\n[{i+1}/{len(conversations)}] Evaluating...")

            result = self.evaluate_conversation(
                transcript=conv['transcript'],
                persona_name=conv['persona_name'],
                conversation_id=conv.get('conversation_id')
            )

            results.append(result)

        # Summary
        avg_score = sum(r['composite_score'] for r in results) / len(results)
        passed_count = sum(1 for r in results if r['passed'])

        print()
        print("=" * 70)
        print(f"📈 Batch Summary:")
        print(f"   Total Conversations: {len(results)}")
        print(f"   Average Score: {avg_score:.1f}/100")
        print(f"   Passed: {passed_count}/{len(results)} ({passed_count/len(results)*100:.1f}%)")
        print("=" * 70)
        print()

        return results

    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics from evaluation results.

        Args:
            results: List of evaluation results

        Returns:
            Dict with statistics
        """
        if not results:
            return {}

        scores = [r['composite_score'] for r in results]
        goal_scores = [r['metrics']['goal_completion']['score'] for r in results]
        quality_scores = [r['metrics']['conversational_quality']['score'] for r in results]
        compliance_scores = [r['metrics']['compliance']['score'] for r in results]

        return {
            'total_evaluated': len(results),
            'composite': {
                'mean': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores)
            },
            'goal_completion': {
                'mean': sum(goal_scores) / len(goal_scores),
                'min': min(goal_scores),
                'max': max(goal_scores)
            },
            'conversational_quality': {
                'mean': sum(quality_scores) / len(quality_scores),
                'min': min(quality_scores),
                'max': max(quality_scores)
            },
            'compliance': {
                'mean': sum(compliance_scores) / len(compliance_scores),
                'pass_rate': sum(1 for r in results if r['passed']) / len(results) * 100
            }
        }

    def __repr__(self):
        llm_status = "enabled" if self.use_llm_judge else "disabled"
        return f"<Evaluator(llm_judge={llm_status})>"
