"""
TerminationPolicy - Evolution convergence detection

This module implements various termination conditions for the evolutionary loop,
detecting when the agent has converged or reached diminishing returns.
"""

from typing import List, Dict, Any, Optional
import time
from datetime import datetime


class TerminationPolicy:
    """
    Manages termination conditions for the evolutionary loop.

    Supports multiple termination criteria:
    - Success threshold: Score exceeds target
    - Plateau detection: No improvement for N generations
    - Max generations: Hard limit on iterations
    - Time limit: Maximum runtime
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize termination policy with configuration.

        Args:
            config: Configuration dictionary with termination settings
        """
        self.config = config

        # Extract termination parameters
        evolution_config = config.get('evolution', {})

        self.success_threshold = evolution_config.get('success_threshold', 85.0)
        self.plateau_generations = evolution_config.get('plateau_generations', 3)
        self.max_generations = evolution_config.get('max_generations', 10)
        self.time_limit_hours = evolution_config.get('time_limit_hours', 24)
        self.min_improvement = evolution_config.get('min_improvement', 0.5)

        # State tracking
        self.start_time = None
        self.generation_history = []
        self.best_score_so_far = 0.0
        self.generations_without_improvement = 0

    def start(self):
        """Mark the start of evolution process."""
        self.start_time = time.time()
        self.generation_history = []
        self.best_score_so_far = 0.0
        self.generations_without_improvement = 0

    def should_terminate(self, generation_results: Dict[str, Any]) -> tuple[bool, str]:
        """
        Check if evolution should terminate based on current generation results.

        Args:
            generation_results: Results from the current generation including:
                - generation: Generation number
                - best_score: Best score this generation
                - variants: List of variant results

        Returns:
            Tuple of (should_terminate: bool, reason: str)
        """
        generation_num = generation_results.get('generation', 0)
        best_score = generation_results.get('best_score', 0.0)

        # Record generation
        self.generation_history.append({
            'generation': generation_num,
            'best_score': best_score,
            'timestamp': datetime.now().isoformat()
        })

        # Check success threshold
        if best_score >= self.success_threshold:
            return True, f"Success threshold reached: {best_score:.2f} >= {self.success_threshold:.2f}"

        # Check max generations
        if generation_num >= self.max_generations:
            return True, f"Max generations reached: {generation_num} >= {self.max_generations}"

        # Check time limit
        if self.start_time:
            elapsed_hours = (time.time() - self.start_time) / 3600
            if elapsed_hours >= self.time_limit_hours:
                return True, f"Time limit reached: {elapsed_hours:.1f} hours >= {self.time_limit_hours}"

        # Check for plateau (no significant improvement)
        improvement = best_score - self.best_score_so_far
        if improvement < self.min_improvement:
            self.generations_without_improvement += 1
        else:
            self.generations_without_improvement = 0
            self.best_score_so_far = best_score

        if self.generations_without_improvement >= self.plateau_generations:
            return True, f"Performance plateau detected: No improvement for {self.plateau_generations} generations"

        # Continue evolution
        return False, "Continuing evolution"

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of evolution progress and termination status.

        Returns:
            Dictionary with evolution statistics
        """
        if not self.generation_history:
            return {
                'total_generations': 0,
                'best_score_achieved': 0.0,
                'improvement': 0.0,
                'elapsed_time': 0.0
            }

        first_gen = self.generation_history[0]
        last_gen = self.generation_history[-1]

        initial_score = first_gen['best_score']
        final_score = last_gen['best_score']
        improvement = final_score - initial_score

        elapsed_time = 0.0
        if self.start_time:
            elapsed_time = time.time() - self.start_time

        return {
            'total_generations': len(self.generation_history),
            'initial_score': initial_score,
            'best_score_achieved': final_score,
            'improvement': improvement,
            'improvement_percentage': (improvement / initial_score * 100) if initial_score > 0 else 0.0,
            'elapsed_time_seconds': elapsed_time,
            'elapsed_time_hours': elapsed_time / 3600,
            'generations_without_improvement': self.generations_without_improvement,
            'converged': self.generations_without_improvement >= self.plateau_generations
        }

    def get_generation_history(self) -> List[Dict[str, Any]]:
        """
        Get complete history of all generations.

        Returns:
            List of generation records
        """
        return self.generation_history.copy()

    def is_improving(self) -> bool:
        """
        Check if evolution is still showing improvement.

        Returns:
            True if recent generations show improvement
        """
        return self.generations_without_improvement < self.plateau_generations

    def get_best_generation(self) -> Optional[Dict[str, Any]]:
        """
        Get the generation with the best score.

        Returns:
            Generation record with highest score, or None if no history
        """
        if not self.generation_history:
            return None

        return max(self.generation_history, key=lambda g: g['best_score'])

    def predict_convergence(self) -> Dict[str, Any]:
        """
        Predict if/when convergence will occur based on current trends.

        Returns:
            Dictionary with convergence prediction
        """
        if len(self.generation_history) < 3:
            return {
                'prediction': 'insufficient_data',
                'confidence': 'low',
                'message': 'Need at least 3 generations for prediction'
            }

        # Calculate rate of improvement
        recent_gens = self.generation_history[-3:]
        scores = [g['best_score'] for g in recent_gens]

        # Linear regression on recent scores
        avg_improvement = (scores[-1] - scores[0]) / (len(scores) - 1)

        if avg_improvement < self.min_improvement / 2:
            return {
                'prediction': 'plateau_imminent',
                'confidence': 'medium',
                'message': f'Improvement rate ({avg_improvement:.2f}/gen) is slowing',
                'estimated_generations_remaining': self.plateau_generations - self.generations_without_improvement
            }

        # Estimate generations to success
        if avg_improvement > 0:
            score_gap = self.success_threshold - scores[-1]
            gens_to_success = score_gap / avg_improvement
            return {
                'prediction': 'success_likely',
                'confidence': 'medium',
                'message': f'Currently improving at {avg_improvement:.2f} points/gen',
                'estimated_generations_to_success': max(1, int(gens_to_success))
            }

        return {
            'prediction': 'continuing',
            'confidence': 'low',
            'message': 'Evolution continuing with stable improvement'
        }


# Example usage
if __name__ == "__main__":
    print("TerminationPolicy - Evolution Convergence Detection")
    print("=" * 60)

    # Test with sample data
    config = {
        'evolution': {
            'success_threshold': 85.0,
            'plateau_generations': 3,
            'max_generations': 10,
            'min_improvement': 0.5
        }
    }

    policy = TerminationPolicy(config)
    policy.start()

    # Simulate generations
    test_generations = [
        {'generation': 0, 'best_score': 60.0},
        {'generation': 1, 'best_score': 65.0},
        {'generation': 2, 'best_score': 70.0},
        {'generation': 3, 'best_score': 72.0},
        {'generation': 4, 'best_score': 72.5},
        {'generation': 5, 'best_score': 73.0},
    ]

    print("\nSimulating evolution:")
    for gen_result in test_generations:
        should_stop, reason = policy.should_terminate(gen_result)
        print(f"Gen {gen_result['generation']}: Score={gen_result['best_score']:.1f} - {reason}")
        if should_stop:
            print(f"TERMINATING: {reason}")
            break

    print("\nEvolution Summary:")
    summary = policy.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nConvergence Prediction:")
    prediction = policy.predict_convergence()
    for key, value in prediction.items():
        print(f"  {key}: {value}")
