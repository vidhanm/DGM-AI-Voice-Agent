"""
Termination Policy - Determines when evolution should stop.

This module implements various termination conditions for the evolutionary
loop, including success thresholds, plateau detection, and limits.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class TerminationPolicy:
    """
    Manages termination conditions for the evolutionary loop.

    Supports multiple termination conditions:
    - Success threshold: Performance exceeds target
    - Plateau detection: No improvement for N generations
    - Max generations: Hard limit on evolution
    - Time limit: Maximum runtime
    """

    def __init__(
        self,
        success_threshold: float = 85.0,
        plateau_generations: int = 5,
        max_generations: int = 20,
        time_limit_seconds: Optional[int] = None
    ):
        """
        Initialize termination policy.

        Args:
            success_threshold: Score above which evolution succeeds (0-100)
            plateau_generations: Stop if no improvement for N generations
            max_generations: Maximum number of generations to run
            time_limit_seconds: Optional time limit in seconds
        """
        self.success_threshold = success_threshold
        self.plateau_generations = plateau_generations
        self.max_generations = max_generations
        self.time_limit_seconds = time_limit_seconds

        # Tracking state
        self.start_time = None
        self.generation_scores = []
        self.best_score = 0.0
        self.best_generation = 0
        self.generations_without_improvement = 0

    def start(self):
        """Start the termination policy timer."""
        self.start_time = datetime.utcnow()
        print(f"\n⏱️  Termination policy started")
        print(f"   Success threshold: {self.success_threshold}")
        print(f"   Plateau generations: {self.plateau_generations}")
        print(f"   Max generations: {self.max_generations}")

    def should_terminate(
        self,
        current_generation: int,
        current_score: float
    ) -> Dict[str, Any]:
        """
        Check if evolution should terminate.

        Args:
            current_generation: Current generation number
            current_score: Best score from current generation

        Returns:
            Dict with termination decision and reason

        Example:
            >>> policy = TerminationPolicy()
            >>> result = policy.should_terminate(5, 87.5)
            >>> if result['should_terminate']:
            ...     print(result['reason'])
        """
        # Record score
        self.generation_scores.append({
            'generation': current_generation,
            'score': current_score,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Check if this is a new best
        if current_score > self.best_score:
            improvement = current_score - self.best_score
            self.best_score = current_score
            self.best_generation = current_generation
            self.generations_without_improvement = 0
            print(f"\n📈 New best score: {current_score:.2f} (+{improvement:.2f})")
        else:
            self.generations_without_improvement += 1
            print(f"\n📊 Score: {current_score:.2f} (best: {self.best_score:.2f})")
            print(f"   Generations without improvement: {self.generations_without_improvement}/{self.plateau_generations}")

        # Check termination conditions
        decision = self._evaluate_conditions(current_generation, current_score)

        if decision['should_terminate']:
            print(f"\n🏁 TERMINATION: {decision['reason']}")
            print(f"   Final generation: {current_generation}")
            print(f"   Best score: {self.best_score:.2f} (gen {self.best_generation})")

        return decision

    def _evaluate_conditions(
        self,
        current_generation: int,
        current_score: float
    ) -> Dict[str, Any]:
        """Evaluate all termination conditions."""

        # 1. Success threshold reached
        if current_score >= self.success_threshold:
            return {
                'should_terminate': True,
                'reason': f'success_threshold_reached',
                'message': f'Score {current_score:.2f} exceeded threshold {self.success_threshold}',
                'success': True,
                'final_score': current_score,
                'generations_run': current_generation + 1
            }

        # 2. Plateau detected
        if self.generations_without_improvement >= self.plateau_generations:
            return {
                'should_terminate': True,
                'reason': 'plateau_detected',
                'message': f'No improvement for {self.plateau_generations} generations',
                'success': False,
                'final_score': self.best_score,
                'generations_run': current_generation + 1
            }

        # 3. Max generations reached
        if current_generation >= self.max_generations - 1:  # -1 because 0-indexed
            return {
                'should_terminate': True,
                'reason': 'max_generations_reached',
                'message': f'Reached maximum {self.max_generations} generations',
                'success': current_score >= self.success_threshold * 0.9,  # 90% of threshold
                'final_score': current_score,
                'generations_run': current_generation + 1
            }

        # 4. Time limit exceeded
        if self.time_limit_seconds and self.start_time:
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()
            if elapsed >= self.time_limit_seconds:
                return {
                    'should_terminate': True,
                    'reason': 'time_limit_exceeded',
                    'message': f'Exceeded time limit of {self.time_limit_seconds}s',
                    'success': False,
                    'final_score': current_score,
                    'generations_run': current_generation + 1
                }

        # Continue evolution
        return {
            'should_terminate': False,
            'reason': None,
            'message': 'Evolution continuing',
            'success': None,
            'final_score': current_score,
            'generations_run': current_generation + 1
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get evolution statistics.

        Returns:
            Dict with evolution stats
        """
        if not self.generation_scores:
            return {
                'generations_run': 0,
                'best_score': 0.0,
                'average_score': 0.0,
                'improvement': 0.0
            }

        scores = [g['score'] for g in self.generation_scores]
        initial_score = scores[0] if scores else 0
        final_score = scores[-1] if scores else 0

        stats = {
            'generations_run': len(self.generation_scores),
            'best_score': self.best_score,
            'best_generation': self.best_generation,
            'initial_score': initial_score,
            'final_score': final_score,
            'average_score': sum(scores) / len(scores),
            'improvement': self.best_score - initial_score,
            'improvement_percent': ((self.best_score - initial_score) / initial_score * 100) if initial_score > 0 else 0,
            'score_history': self.generation_scores
        }

        if self.start_time:
            stats['elapsed_seconds'] = (datetime.utcnow() - self.start_time).total_seconds()

        return stats

    def generate_report(self) -> str:
        """
        Generate a human-readable termination report.

        Returns:
            Formatted report string
        """
        stats = self.get_statistics()

        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    EVOLUTION TERMINATION REPORT                      ║
╚══════════════════════════════════════════════════════════════════════╝

📊 PERFORMANCE:
   Initial Score:  {stats['initial_score']:.2f}/100
   Final Score:    {stats['final_score']:.2f}/100
   Best Score:     {stats['best_score']:.2f}/100 (Generation {stats['best_generation']})
   Improvement:    +{stats['improvement']:.2f} ({stats['improvement_percent']:.1f}%)

📈 EVOLUTION PROGRESS:
   Generations:    {stats['generations_run']}
   Average Score:  {stats['average_score']:.2f}/100
"""

        if 'elapsed_seconds' in stats:
            minutes = int(stats['elapsed_seconds'] / 60)
            seconds = int(stats['elapsed_seconds'] % 60)
            report += f"   Time Elapsed:   {minutes}m {seconds}s\n"

        report += f"""
🎯 TERMINATION CONDITIONS:
   Success Threshold:       {self.success_threshold}/100
   Plateau Generations:     {self.plateau_generations}
   Max Generations:         {self.max_generations}

📋 SCORE TRAJECTORY:
"""

        # Add score history
        for gen_data in stats['score_history'][-10:]:  # Last 10 generations
            gen = gen_data['generation']
            score = gen_data['score']
            marker = "🌟" if gen == self.best_generation else "  "
            report += f"   {marker} Gen {gen:2d}: {score:.2f}/100\n"

        return report

    def reset(self):
        """Reset the termination policy for a new evolution run."""
        self.start_time = None
        self.generation_scores = []
        self.best_score = 0.0
        self.best_generation = 0
        self.generations_without_improvement = 0
        print("🔄 Termination policy reset")
