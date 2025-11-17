"""
Conversation Logger for Darwin Godel Machine Voice Agent.

This module provides structured logging for conversations between
the agent and personas, storing transcripts, metadata, and evaluation
results in JSON format for easy analysis.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Speaker(Enum):
    """Enumeration of conversation speakers."""
    AGENT = "agent"
    USER = "user"
    SYSTEM = "system"


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""
    speaker: str  # "agent" or "user" or "system"
    message: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'speaker': self.speaker,
            'message': self.message,
            'timestamp': self.timestamp,
            'metadata': self.metadata or {}
        }


class ConversationLogger:
    """
    Manages logging of conversations to structured JSON files.

    Provides easy-to-use methods for logging conversations with metadata,
    organizing logs by date and agent version, and retrieving logs for analysis.
    """

    def __init__(self, log_dir: str = "data/conversations"):
        """
        Initialize the conversation logger.

        Args:
            log_dir: Directory where conversation logs will be saved
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current conversation state
        self.current_conversation: Optional[Dict[str, Any]] = None
        self.current_turns: List[ConversationTurn] = []

    def start_conversation(
        self,
        conversation_id: str,
        agent_version_id: str,
        persona_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new conversation session.

        Args:
            conversation_id: Unique identifier for this conversation
            agent_version_id: ID of the agent version being used
            persona_name: Name of the persona (e.g., "angry_anthony")
            metadata: Additional metadata

        Returns:
            conversation_id

        Example:
            >>> logger = ConversationLogger()
            >>> conv_id = logger.start_conversation(
            ...     "conv-001",
            ...     "v0-abc123",
            ...     "angry_anthony"
            ... )
        """
        self.current_conversation = {
            'conversation_id': conversation_id,
            'agent_version_id': agent_version_id,
            'persona_name': persona_name,
            'started_at': datetime.utcnow().isoformat(),
            'ended_at': None,
            'metadata': metadata or {},
            'turn_count': 0,
            'status': 'in_progress'
        }

        self.current_turns = []

        print(f"📝 Started conversation: {conversation_id}")
        print(f"   Agent: {agent_version_id}")
        print(f"   Persona: {persona_name}")

        return conversation_id

    def log_turn(
        self,
        speaker: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a single turn in the conversation.

        Args:
            speaker: Who is speaking ("agent", "user", or "system")
            message: The message content
            metadata: Optional metadata for this turn

        Example:
            >>> logger.log_turn("agent", "Hello, how can I help you?")
            >>> logger.log_turn("user", "I can't pay my loan this month")
        """
        if not self.current_conversation:
            raise ValueError("No conversation in progress. Call start_conversation() first.")

        turn = ConversationTurn(
            speaker=speaker,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata
        )

        self.current_turns.append(turn)
        self.current_conversation['turn_count'] += 1

        # Print turn for visibility
        speaker_emoji = "🤖" if speaker == "agent" else "👤" if speaker == "user" else "🔔"
        print(f"{speaker_emoji} [{speaker}]: {message[:100]}{'...' if len(message) > 100 else ''}")

    def end_conversation(
        self,
        outcome: Optional[str] = None,
        termination_reason: Optional[str] = None,
        evaluation_scores: Optional[Dict[str, float]] = None
    ) -> str:
        """
        End the current conversation and save to file.

        Args:
            outcome: Conversation outcome (e.g., "success", "failure")
            termination_reason: Why the conversation ended
            evaluation_scores: Evaluation metrics

        Returns:
            Path to saved log file

        Example:
            >>> logger.end_conversation(
            ...     outcome="success",
            ...     termination_reason="payment_agreed",
            ...     evaluation_scores={"goal_completion": 85.0}
            ... )
        """
        if not self.current_conversation:
            raise ValueError("No conversation in progress.")

        # Update conversation metadata
        self.current_conversation['ended_at'] = datetime.utcnow().isoformat()
        self.current_conversation['status'] = 'completed'
        self.current_conversation['outcome'] = outcome
        self.current_conversation['termination_reason'] = termination_reason
        self.current_conversation['evaluation_scores'] = evaluation_scores or {}

        # Calculate duration
        started = datetime.fromisoformat(self.current_conversation['started_at'])
        ended = datetime.fromisoformat(self.current_conversation['ended_at'])
        duration = (ended - started).total_seconds()
        self.current_conversation['duration_seconds'] = duration

        # Build complete log
        log_data = {
            **self.current_conversation,
            'transcript': [turn.to_dict() for turn in self.current_turns]
        }

        # Save to file
        log_file = self._save_log(log_data)

        print(f"✅ Conversation ended: {self.current_conversation['conversation_id']}")
        print(f"   Turns: {self.current_conversation['turn_count']}")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Saved to: {log_file}")

        # Reset state
        self.current_conversation = None
        self.current_turns = []

        return str(log_file)

    def _save_log(self, log_data: Dict[str, Any]) -> Path:
        """
        Save log data to a JSON file.

        Organizes logs by date and agent version for easy retrieval.

        Args:
            log_data: Complete conversation log

        Returns:
            Path to saved file
        """
        # Organize by date (YYYY-MM-DD)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        date_dir = self.log_dir / date_str

        date_dir.mkdir(parents=True, exist_ok=True)

        # Filename: {conversation_id}.json
        filename = f"{log_data['conversation_id']}.json"
        log_file = date_dir / filename

        # Save with pretty printing for readability
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, sort_keys=False)

        return log_file

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a conversation log by ID.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation log data or None if not found

        Example:
            >>> logger = ConversationLogger()
            >>> conv = logger.get_conversation("conv-001")
        """
        # Search through date directories
        for date_dir in self.log_dir.iterdir():
            if not date_dir.is_dir():
                continue

            log_file = date_dir / f"{conversation_id}.json"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    return json.load(f)

        return None

    def list_conversations(
        self,
        agent_version_id: Optional[str] = None,
        persona_name: Optional[str] = None,
        date: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List conversations with optional filtering.

        Args:
            agent_version_id: Filter by agent version
            persona_name: Filter by persona
            date: Filter by date (YYYY-MM-DD)
            limit: Maximum number to return

        Returns:
            List of conversation summaries

        Example:
            >>> logger = ConversationLogger()
            >>> conversations = logger.list_conversations(
            ...     agent_version_id="v0-abc123",
            ...     limit=5
            ... )
        """
        conversations = []

        # Determine which directories to search
        if date:
            search_dirs = [self.log_dir / date] if (self.log_dir / date).exists() else []
        else:
            search_dirs = [d for d in self.log_dir.iterdir() if d.is_dir()]

        # Search through directories
        for date_dir in sorted(search_dirs, reverse=True):
            for log_file in date_dir.glob("*.json"):
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)

                    # Apply filters
                    if agent_version_id and log_data.get('agent_version_id') != agent_version_id:
                        continue
                    if persona_name and log_data.get('persona_name') != persona_name:
                        continue

                    # Add summary
                    conversations.append({
                        'conversation_id': log_data['conversation_id'],
                        'agent_version_id': log_data['agent_version_id'],
                        'persona_name': log_data['persona_name'],
                        'started_at': log_data['started_at'],
                        'turn_count': log_data['turn_count'],
                        'outcome': log_data.get('outcome'),
                        'log_file': str(log_file)
                    })

                    if len(conversations) >= limit:
                        return conversations

                except Exception as e:
                    print(f"⚠️  Error reading {log_file}: {e}")
                    continue

        return conversations

    def get_statistics(
        self,
        agent_version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about logged conversations.

        Args:
            agent_version_id: Optional filter by agent version

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = logger.get_statistics("v0-abc123")
            >>> print(f"Total conversations: {stats['total_conversations']}")
        """
        all_conversations = self.list_conversations(
            agent_version_id=agent_version_id,
            limit=10000
        )

        if not all_conversations:
            return {
                'total_conversations': 0,
                'total_turns': 0,
                'avg_turns_per_conversation': 0
            }

        total_turns = sum(c['turn_count'] for c in all_conversations)

        return {
            'total_conversations': len(all_conversations),
            'total_turns': total_turns,
            'avg_turns_per_conversation': total_turns / len(all_conversations) if all_conversations else 0,
            'personas': list(set(c['persona_name'] for c in all_conversations)),
            'outcomes': {
                outcome: sum(1 for c in all_conversations if c.get('outcome') == outcome)
                for outcome in set(c.get('outcome') for c in all_conversations if c.get('outcome'))
            }
        }

    def __repr__(self):
        """String representation."""
        status = "active" if self.current_conversation else "idle"
        return f"<ConversationLogger(status={status}, log_dir={self.log_dir})>"
