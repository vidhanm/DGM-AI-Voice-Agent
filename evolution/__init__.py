"""
Evolution Package - Darwin-Gödel Machine Components

This package implements the self-evolving agent system inspired by
Darwin-Gödel machines. It provides:

- AgentArchive: Version control and storage for agents
- PromptRewriter: LLM-based prompt mutation engine
- EvolutionaryLoop: Main evolution orchestrator
- TerminationPolicy: Convergence detection
"""

from core.agent_archive import AgentArchive  # AgentArchive is in core, not evolution
from evolution.prompt_rewriter import PromptRewriter
from evolution.evolutionary_loop import EvolutionaryLoop
from evolution.termination_policy import TerminationPolicy

__all__ = [
    'AgentArchive',
    'PromptRewriter',
    'EvolutionaryLoop',
    'TerminationPolicy'
]
