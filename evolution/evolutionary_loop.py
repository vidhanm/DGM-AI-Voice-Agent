"""
Evolutionary Loop - Main orchestrator for agent evolution.

This module implements the Darwin-Gödel Machine inspired evolutionary loop
that automatically improves agent prompts through iterative testing and selection.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

from core import Config, BaseAgent, PromptManager, AgentArchive
from simulation import PersonaEngine, ConversationRunner
from evaluation import Evaluator
from evolution.prompt_rewriter import PromptRewriter
from evolution.termination_policy import TerminationPolicy


class EvolutionaryLoop:
    """
    Orchestrates the entire evolution process.

    The loop follows these steps:
    1. Start with baseline or parent agent
    2. Run conversations with all personas
    3. Evaluate performance
    4. Analyze failures
    5. Generate improved variants
    6. Test all variants
    7. Select best performer
    8. Check termination conditions
    9. Repeat from step 2 with best agent
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the evolutionary loop.

        Args:
            config: Configuration object
        """
        self.config = config or Config()

        # Initialize components
        self.archive = AgentArchive()
        self.prompt_manager = PromptManager()
        self.evaluator = Evaluator(config)
        self.rewriter = PromptRewriter(config)

        # Get evolution settings
        self.max_generations = self.config.get('evolution.max_generations', 20)
        self.success_threshold = self.config.get('evolution.success_threshold', 85.0)
        self.plateau_generations = self.config.get('evolution.plateau_generations', 5)
        self.variants_per_generation = self.config.get('evolution.variants_per_generation', 3)
        self.conversations_per_persona = self.config.get('simulation.conversations_per_persona', 3)

        # Initialize termination policy
        self.termination_policy = TerminationPolicy(
            success_threshold=self.success_threshold,
            plateau_generations=self.plateau_generations,
            max_generations=self.max_generations
        )

        # Load personas
        self.personas = self._load_personas()

        # Evolution tracking
        self.evolution_history = []

        print("🧬 Evolutionary Loop initialized")
        print(f"   Max generations: {self.max_generations}")
        print(f"   Success threshold: {self.success_threshold}")
        print(f"   Variants per generation: {self.variants_per_generation}")
        print(f"   Personas: {len(self.personas)}")

    def _load_personas(self) -> List[PersonaEngine]:
        """Load all enabled personas."""
        personas = []
        persona_configs = self.config.get('personas', [])

        for persona_config in persona_configs:
            if persona_config.get('enabled', True):
                persona_name = persona_config['name']
                try:
                    persona = PersonaEngine(persona_name)
                    personas.append(persona)
                except Exception as e:
                    print(f"⚠️  Failed to load persona {persona_name}: {e}")

        return personas

    def evolve(
        self,
        baseline_prompt: Optional[str] = None,
        parent_version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete evolution process.

        Args:
            baseline_prompt: Starting prompt (if None, loads from base_prompt.yaml)
            parent_version_id: Optional parent agent to start from

        Returns:
            Dict with evolution results

        Example:
            >>> loop = EvolutionaryLoop()
            >>> results = loop.evolve()
            >>> print(f"Best agent: {results['best_agent_id']}")
            >>> print(f"Final score: {results['final_score']}")
        """
        print("\n" + "="*70)
        print("🧬 STARTING EVOLUTIONARY LOOP")
        print("="*70)

        self.termination_policy.start()

        # Get or create baseline agent
        if parent_version_id:
            current_agent = self.archive.get_agent(parent_version_id)
            current_prompt = current_agent.prompt
            current_generation = current_agent.generation + 1
        elif baseline_prompt:
            current_prompt = baseline_prompt
            current_generation = 0
        else:
            # Load from base_prompt.yaml
            template_data = self.prompt_manager.load_template('base_prompt')
            current_prompt = template_data['template']
            current_generation = 0

        # Save baseline if generation 0
        if current_generation == 0:
            baseline_id = self.archive.save_agent(
                prompt=current_prompt,
                parent_id=None,
                generation=0,
                mutation_strategy='baseline',
                change_rationale='Initial baseline agent'
            )
            current_agent_id = baseline_id
        else:
            current_agent_id = parent_version_id

        # Evolution loop
        while True:
            print(f"\n{'='*70}")
            print(f"📊 GENERATION {current_generation}")
            print(f"{'='*70}")

            # Evaluate current agent
            print(f"\n🧪 Testing current agent: {current_agent_id}")
            current_results = self._test_agent(current_agent_id, current_prompt)

            # Calculate average composite score
            avg_score = sum(r['composite_score'] for r in current_results) / len(current_results)
            print(f"\n📊 Current agent average score: {avg_score:.2f}/100")

            # Update scores in archive
            self._update_agent_scores(current_agent_id, current_results)

            # Check termination
            termination = self.termination_policy.should_terminate(
                current_generation,
                avg_score
            )

            if termination['should_terminate']:
                break

            # Analyze failures
            failure_analysis = self.rewriter.analyze_failures(current_results)

            # Generate variants
            variants = self.rewriter.generate_variants(
                current_prompt,
                failure_analysis,
                self.variants_per_generation
            )

            # Test all variants
            variant_results = []
            for i, variant in enumerate(variants):
                print(f"\n{'='*70}")
                print(f"🧬 VARIANT {i+1}/{len(variants)} (Generation {current_generation + 1})")
                print(f"   Strategy: {variant['strategy']}")
                print(f"   Rationale: {variant['rationale'][:100]}...")
                print(f"{'='*70}")

                # Save variant to archive
                variant_id = self.archive.save_agent(
                    prompt=variant['prompt'],
                    parent_id=current_agent_id,
                    generation=current_generation + 1,
                    mutation_strategy=variant['strategy'],
                    change_rationale=variant['rationale']
                )

                # Test variant
                variant_test_results = self._test_agent(variant_id, variant['prompt'])

                # Calculate variant score
                variant_score = sum(r['composite_score'] for r in variant_test_results) / len(variant_test_results)

                # Update variant scores
                self._update_agent_scores(variant_id, variant_test_results)

                variant_results.append({
                    'variant_id': variant_id,
                    'score': variant_score,
                    'strategy': variant['strategy'],
                    'results': variant_test_results
                })

                print(f"   Variant score: {variant_score:.2f}/100")

            # Select best variant (greedy selection)
            best_variant = max(variant_results, key=lambda v: v['score'])
            print(f"\n🏆 Best variant: {best_variant['variant_id']} (score: {best_variant['score']:.2f})")

            # Record evolution step
            self.evolution_history.append({
                'generation': current_generation,
                'parent_id': current_agent_id,
                'parent_score': avg_score,
                'variants': variant_results,
                'best_variant_id': best_variant['variant_id'],
                'best_variant_score': best_variant['score'],
                'improvement': best_variant['score'] - avg_score,
                'timestamp': datetime.utcnow().isoformat()
            })

            # Move to next generation with best variant
            current_agent_id = best_variant['variant_id']
            current_prompt = self.archive.get_agent(current_agent_id).prompt
            current_generation += 1

        # Evolution complete
        print("\n" + "="*70)
        print("🏁 EVOLUTION COMPLETE")
        print("="*70)

        # Get final best agent
        best_agent = self.archive.get_best_agent()

        # Mark as best
        self.archive.mark_as_best(best_agent.version_id)

        # Generate reports
        stats = self.termination_policy.get_statistics()
        report = self.termination_policy.generate_report()

        print(report)

        # Save evolution history
        self._save_evolution_history()

        return {
            'success': termination.get('success', False),
            'termination_reason': termination['reason'],
            'best_agent_id': best_agent.version_id,
            'final_score': best_agent.composite_score,
            'initial_score': stats['initial_score'],
            'improvement': stats['improvement'],
            'generations_run': stats['generations_run'],
            'evolution_history': self.evolution_history,
            'statistics': stats
        }

    def _test_agent(
        self,
        agent_id: str,
        prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Test an agent across all personas.

        Args:
            agent_id: Agent version ID
            prompt: Agent prompt text

        Returns:
            List of evaluation results
        """
        results = []

        for persona in self.personas:
            for run in range(self.conversations_per_persona):
                print(f"\n   Testing with {persona.persona_name} (run {run+1}/{self.conversations_per_persona})")

                # Create agent
                agent = BaseAgent(agent_id, prompt, self.config)

                # Run conversation
                runner = ConversationRunner(agent, persona)
                conv_result = runner.run_conversation()

                # Evaluate conversation
                evaluation = self.evaluator.evaluate_conversation(
                    conv_result['transcript'],
                    persona.persona_name,
                    conv_result['conversation_id']
                )

                # Add metadata
                evaluation['agent_version_id'] = agent_id
                evaluation['persona_name'] = persona.persona_name
                evaluation['run_number'] = run + 1

                results.append(evaluation)

        return results

    def _update_agent_scores(
        self,
        agent_id: str,
        results: List[Dict[str, Any]]
    ):
        """Update agent scores in archive based on evaluation results."""

        # Calculate averages
        avg_goal = sum(r['goal_completion']['score'] for r in results) / len(results)
        avg_quality = sum(r['conversational_quality']['score'] for r in results) / len(results)
        avg_compliance = sum(r['compliance']['score'] for r in results) / len(results)

        # Count outcomes
        total = len(results)
        passed = sum(1 for r in results if r['passed'])
        failed = total - passed

        # Update in archive
        self.archive.update_scores(
            agent_id,
            goal_completion=avg_goal,
            conversational_quality=avg_quality,
            compliance=avg_compliance,
            total_conversations=total,
            successful_conversations=passed,
            failed_conversations=failed
        )

    def _save_evolution_history(self):
        """Save evolution history to file."""
        os.makedirs('data/evolution', exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'data/evolution/evolution_history_{timestamp}.json'

        history_data = {
            'config': {
                'max_generations': self.max_generations,
                'success_threshold': self.success_threshold,
                'variants_per_generation': self.variants_per_generation,
                'conversations_per_persona': self.conversations_per_persona
            },
            'history': self.evolution_history,
            'statistics': self.termination_policy.get_statistics(),
            'timestamp': datetime.utcnow().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(history_data, f, indent=2)

        print(f"\n💾 Evolution history saved: {filename}")

    def get_lineage_report(self, agent_id: str) -> str:
        """
        Generate a lineage report showing evolution path.

        Args:
            agent_id: Agent version ID

        Returns:
            Formatted lineage report
        """
        lineage = self.archive.get_lineage(agent_id)

        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                        EVOLUTION LINEAGE                             ║
╚══════════════════════════════════════════════════════════════════════╝

Agent: {agent_id}
Generations: {len(lineage)}

"""

        for i, agent in enumerate(lineage):
            marker = "🌟" if agent.is_best else "  "
            arrow = "   " if i == 0 else " ↓ "

            report += f"{arrow}{marker} Gen {agent.generation}: {agent.version_id}\n"
            report += f"      Score: {agent.composite_score:.2f}/100"

            if agent.mutation_strategy:
                report += f" | Strategy: {agent.mutation_strategy}\n"
            else:
                report += "\n"

            if agent.change_rationale and i > 0:
                rationale = agent.change_rationale[:80]
                report += f"      Rationale: {rationale}...\n"

            report += "\n"

        return report
