"""
EvolutionaryLoop - Darwin-Gödel Machine Orchestrator

This module implements the main evolutionary loop that orchestrates:
- Agent generation and mutation
- Evaluation across persona test suite
- Selection of best performers
- Termination detection
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from core.config import Config
from core.agent_archive import AgentArchive
from core.prompt_manager import PromptManager
from core.agent import BaseAgent
from simulation.persona_engine import PersonaEngine
from simulation.conversation_runner import ConversationRunner
from evaluation.evaluator import Evaluator
from evolution.prompt_rewriter import PromptRewriter
from evolution.termination_policy import TerminationPolicy
from log_manager.conversation_logger import ConversationLogger


class EvolutionaryLoop:
    """
    Main orchestrator for the Darwin-Gödel evolutionary system.

    Implements the complete evolution cycle:
    1. Select parent agent(s)
    2. Generate prompt variants via mutation
    3. Evaluate variants across persona test suite
    4. Select best performer for next generation
    5. Check termination conditions
    6. Repeat until convergence or limits reached
    """

    def __init__(
        self,
        config: Config,
        agent_archive: AgentArchive,
        prompt_manager: PromptManager,
        evaluator: Evaluator
    ):
        """
        Initialize the evolutionary loop.

        Args:
            config: Configuration object
            agent_archive: Agent version storage
            prompt_manager: Prompt template manager
            evaluator: Evaluation system
        """
        self.config = config
        self.agent_archive = agent_archive
        self.prompt_manager = prompt_manager
        self.evaluator = evaluator

        # Initialize components
        self.prompt_rewriter = PromptRewriter(config.to_dict())
        self.termination_policy = TerminationPolicy(config.to_dict())
        self.conversation_logger = ConversationLogger()

        # Evolution parameters
        evolution_config = config.get('evolution', {})
        self.variants_per_generation = evolution_config.get('variants_per_generation', 3)
        self.selection_strategy = evolution_config.get('selection_strategy', 'greedy')
        self.mutation_strategies = evolution_config.get(
            'mutation_strategies',
            ['adaptive', 'tone_adjustment', 'structure_modification']
        )

        # Test suite configuration
        self.test_personas = config.get('simulation.test_personas', [
            'angry_anthony',
            'evasive_emma',
            'curious_carlos',
            'cooperative_chloe',
            'desperate_david'
        ])
        self.conversations_per_persona = evolution_config.get('conversations_per_persona', 1)

        # Evolution state
        self.current_generation = 0
        self.evolution_log = []

    def evolve(
        self,
        initial_agent_id: Optional[str] = None,
        max_generations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run the complete evolutionary loop until termination.

        Args:
            initial_agent_id: Starting agent version ID (creates baseline if None)
            max_generations: Override max generations from config

        Returns:
            Dictionary with evolution results:
                - best_agent_id: Final best agent version
                - best_score: Final best score
                - generations: Number of generations run
                - termination_reason: Why evolution stopped
                - evolution_history: Complete lineage
        """
        print("=" * 70)
        print("DARWIN-GÖDEL MACHINE - EVOLUTIONARY LOOP STARTING")
        print("=" * 70)

        # Initialize
        self.termination_policy.start()
        self.current_generation = 0

        # Get or create initial agent
        if initial_agent_id:
            current_agent_id = initial_agent_id
            print(f"\nStarting from existing agent: {current_agent_id}")
        else:
            current_agent_id = self._create_baseline_agent()
            print(f"\nCreated baseline agent: {current_agent_id}")

        # Evaluate baseline
        print("\n" + "=" * 70)
        print(f"EVALUATING BASELINE AGENT: {current_agent_id}")
        print("=" * 70)
        baseline_results = self._evaluate_agent(current_agent_id)
        baseline_score = baseline_results['avg_composite_score']
        print(f"\nBaseline Score: {baseline_score:.2f}/100")

        # Update baseline agent with scores
        self._update_agent_scores(current_agent_id, baseline_results)

        # Main evolution loop
        while True:
            self.current_generation += 1

            print("\n" + "=" * 70)
            print(f"GENERATION {self.current_generation}")
            print("=" * 70)

            # Run one generation
            generation_results = self.run_generation(
                parent_id=current_agent_id,
                generation=self.current_generation
            )

            # Log generation
            self.evolution_log.append(generation_results)

            # Check termination
            should_stop, reason = self.termination_policy.should_terminate(generation_results)

            print(f"\n{reason}")

            if should_stop:
                print("\n" + "=" * 70)
                print("EVOLUTION TERMINATED")
                print("=" * 70)
                break

            # Select best agent for next generation
            current_agent_id = generation_results['best_agent_id']

            # Check max generations override
            if max_generations and self.current_generation >= max_generations:
                reason = f"Max generations override reached: {max_generations}"
                print(f"\n{reason}")
                break

        # Final summary
        final_summary = self._generate_final_summary(current_agent_id, reason)

        print("\n" + "=" * 70)
        print("EVOLUTION COMPLETE")
        print("=" * 70)
        print(f"\nBest Agent: {final_summary['best_agent_id']}")
        print(f"Final Score: {final_summary['best_score']:.2f}/100")
        print(f"Improvement: +{final_summary['improvement']:.2f} points")
        print(f"Generations: {final_summary['generations']}")
        print(f"Reason: {final_summary['termination_reason']}")

        return final_summary

    def run_generation(
        self,
        parent_id: str,
        generation: int
    ) -> Dict[str, Any]:
        """
        Run one generation of evolution.

        Args:
            parent_id: Parent agent version ID
            generation: Generation number

        Returns:
            Dictionary with generation results
        """
        print(f"\nParent Agent: {parent_id}")

        # Get parent agent
        parent = self.agent_archive.get_agent(parent_id)
        parent_prompt = parent.prompt
        parent_score = parent.composite_score

        print(f"Parent Score: {parent_score:.2f}/100")

        # Get parent's evaluation results for mutation context
        parent_eval_results = self._get_agent_evaluation_results(parent_id)

        # Generate variants
        print(f"\nGenerating {self.variants_per_generation} variants...")
        variants = []

        for i in range(self.variants_per_generation):
            strategy = self.mutation_strategies[i % len(self.mutation_strategies)]
            print(f"  Variant {i+1}: {strategy} strategy")

            variant_info = self.prompt_rewriter.propose_improvements(
                current_prompt=parent_prompt,
                evaluation_results=parent_eval_results,
                strategy=strategy
            )

            # Save variant to archive
            variant_id = self.agent_archive.save_agent(
                prompt=variant_info['new_prompt'],
                config=parent.config,
                parent_id=parent_id,
                generation=generation,
                mutation_strategy=strategy,
                change_rationale=variant_info['rationale']
            )

            variants.append({
                'version_id': variant_id,
                'strategy': strategy,
                'rationale': variant_info['rationale']
            })

        # Evaluate all variants
        print(f"\nEvaluating {len(variants)} variants...")
        variant_scores = []

        for i, variant in enumerate(variants):
            print(f"\n  Evaluating Variant {i+1} ({variant['version_id']})...")
            eval_results = self._evaluate_agent(variant['version_id'])
            score = eval_results['avg_composite_score']

            # Update agent with scores
            self._update_agent_scores(variant['version_id'], eval_results)

            variant_scores.append({
                'version_id': variant['version_id'],
                'score': score,
                'strategy': variant['strategy']
            })

            print(f"    Score: {score:.2f}/100")

        # Select best variant
        best_variant = max(variant_scores, key=lambda v: v['score'])
        best_score = best_variant['score']
        best_agent_id = best_variant['version_id']

        print(f"\n  Best Variant: {best_agent_id}")
        print(f"  Best Score: {best_score:.2f}/100")
        print(f"  Improvement: {best_score - parent_score:+.2f} points")

        return {
            'generation': generation,
            'parent_id': parent_id,
            'parent_score': parent_score,
            'variants': variant_scores,
            'best_agent_id': best_agent_id,
            'best_score': best_score,
            'improvement': best_score - parent_score
        }

    def _create_baseline_agent(self) -> str:
        """
        Create the baseline agent from template.

        Returns:
            Agent version ID
        """
        # Load base prompt template
        template = self.prompt_manager.load_template('base_prompt.yaml')
        base_prompt = template.template

        # Save as generation 0
        version_id = self.agent_archive.save_agent(
            prompt=base_prompt,
            config=self.config.to_dict(),
            parent_id=None,
            generation=0,
            mutation_strategy='baseline',
            change_rationale='Initial baseline agent from template'
        )

        return version_id

    def _evaluate_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Evaluate an agent across all test personas.

        Args:
            agent_id: Agent version ID to evaluate

        Returns:
            Aggregated evaluation results
        """
        agent = self.agent_archive.get_agent(agent_id)

        all_eval_results = []

        for persona_name in self.test_personas:
            for conv_num in range(self.conversations_per_persona):
                # Create agent instance
                agent_instance = BaseAgent(
                    agent_version_id=agent_id,
                    prompt=agent.prompt,
                    config=self.config
                )

                # Create persona
                persona = PersonaEngine(
                    persona_name=persona_name,
                    personas_dir='simulation/personas',
                    config=self.config
                )

                # Run conversation
                runner = ConversationRunner(
                    agent=agent_instance,
                    persona=persona,
                    logger=self.conversation_logger,
                    max_turns=self.config.get('simulation.max_turns', 20)
                )

                result = runner.run_conversation()

                # Evaluate conversation
                eval_result = self.evaluator.evaluate_conversation(
                    transcript=result['transcript'],
                    persona_name=persona_name,
                    conversation_id=result['conversation_id']
                )

                eval_result['persona_name'] = persona_name
                eval_result['conversation_id'] = result['conversation_id']
                all_eval_results.append(eval_result)

        # Aggregate results
        avg_composite = sum(r['composite_score'] for r in all_eval_results) / len(all_eval_results)
        avg_goal = sum(r['metrics']['goal_completion']['score'] for r in all_eval_results) / len(all_eval_results)
        avg_quality = sum(r['metrics']['conversational_quality']['score'] for r in all_eval_results) / len(all_eval_results)
        avg_compliance = sum(r['metrics']['compliance']['score'] for r in all_eval_results) / len(all_eval_results)

        return {
            'agent_id': agent_id,
            'avg_composite_score': avg_composite,
            'avg_goal_score': avg_goal,
            'avg_quality_score': avg_quality,
            'avg_compliance_score': avg_compliance,
            'conversation_results': all_eval_results
        }

    def _update_agent_scores(self, agent_id: str, eval_results: Dict[str, Any]):
        """
        Update agent's scores in the archive.

        Args:
            agent_id: Agent version ID
            eval_results: Evaluation results dictionary
        """
        self.agent_archive.update_scores(
            version_id=agent_id,
            goal_completion=eval_results['avg_goal_score'],
            conversational_quality=eval_results['avg_quality_score'],
            compliance=eval_results['avg_compliance_score']
        )

    def _get_agent_evaluation_results(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve evaluation results for an agent from conversation logs.

        Args:
            agent_id: Agent version ID

        Returns:
            List of evaluation results
        """
        # In a full implementation, this would load from logs
        # For now, create minimal evaluation context
        agent = self.agent_archive.get_agent(agent_id)

        return [{
            'composite_score': agent.composite_score,
            'metrics': {
                'goal_completion': {'score': agent.goal_completion_score},
                'conversational_quality': {'score': agent.conversational_quality_score},
                'compliance': {'score': agent.compliance_score}
            }
        }]

    def _generate_final_summary(self, best_agent_id: str, termination_reason: str) -> Dict[str, Any]:
        """
        Generate final evolution summary.

        Args:
            best_agent_id: Final best agent ID
            termination_reason: Why evolution terminated

        Returns:
            Summary dictionary
        """
        best_agent = self.agent_archive.get_agent(best_agent_id)
        lineage = self.agent_archive.get_lineage(best_agent_id)

        # Get baseline (generation 0)
        baseline = next((a for a in lineage if a.generation == 0), None)
        baseline_score = baseline.composite_score if baseline else 0.0

        improvement = best_agent.composite_score - baseline_score

        return {
            'best_agent_id': best_agent_id,
            'best_score': best_agent.composite_score,
            'baseline_score': baseline_score,
            'improvement': improvement,
            'improvement_percentage': (improvement / baseline_score * 100) if baseline_score > 0 else 0.0,
            'generations': self.current_generation,
            'termination_reason': termination_reason,
            'lineage': [agent.to_dict() for agent in lineage],
            'evolution_log': self.evolution_log,
            'policy_summary': self.termination_policy.get_summary()
        }

    def get_best_agent(self) -> Optional[Dict[str, Any]]:
        """
        Get the current best agent across all generations.

        Returns:
            Best agent info or None
        """
        best = self.agent_archive.get_best_agent(metric='composite_score')
        if not best:
            return None

        return {
            'version_id': best.version_id,
            'generation': best.generation,
            'composite_score': best.composite_score,
            'prompt': best.prompt
        }


# Example usage
if __name__ == "__main__":
    print("EvolutionaryLoop - Darwin-Gödel Machine Orchestrator")
    print("=" * 60)
    print("\nThis module orchestrates the complete evolution cycle:")
    print("  1. Generate prompt variants")
    print("  2. Evaluate across persona test suite")
    print("  3. Select best performers")
    print("  4. Check termination conditions")
    print("  5. Repeat until convergence")
