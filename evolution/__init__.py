"""
Evolution - Self-improving agent system.

This package implements the Darwin-Gödel Machine inspired evolutionary loop
that continuously improves agent prompts through automated testing and selection.
"""

from evolution.prompt_rewriter import PromptRewriter
from evolution.termination_policy import TerminationPolicy
from evolution.evolutionary_loop import EvolutionaryLoop

__all__ = [
    'PromptRewriter',
    'TerminationPolicy',
    'EvolutionaryLoop'
]
