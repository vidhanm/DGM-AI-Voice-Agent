"""
Log Manager module for Darwin Godel Machine Voice Agent.

This module provides structured logging for conversations, evaluations,
and evolution history.
"""

from .conversation_logger import ConversationLogger, ConversationTurn, Speaker

__all__ = [
    'ConversationLogger',
    'ConversationTurn',
    'Speaker'
]
