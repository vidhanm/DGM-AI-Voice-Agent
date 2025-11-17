"""
Evolution Package - Darwin-Gödel Machine Components

This package implements the self-evolving agent system inspired by
Darwin-Gödel machines. It provides:

- PromptRewriter: LLM-based prompt mutation engine
- EvolutionaryLoop: Main evolution orchestrator
- TerminationPolicy: Convergence detection
"""

from evolution.prompt_rewriter import PromptRewriter
from evolution.evolutionary_loop import EvolutionaryLoop
from evolution.termination_policy import TerminationPolicy

__all__ = [
    'PromptRewriter',
    'EvolutionaryLoop',
    'TerminationPolicy'
]
