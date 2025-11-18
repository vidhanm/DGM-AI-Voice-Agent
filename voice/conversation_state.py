"""
Voice Conversation State Management

Tracks voice-specific conversation state including:
- Speaking status (who's talking)
- Interruption tracking
- Latency metrics
- Turn timing
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TurnMetrics:
    """Metrics for a single conversation turn"""
    turn_number: int
    speaker: str  # 'user' or 'agent'
    start_time: float
    end_time: Optional[float] = None
    stt_latency: Optional[float] = None  # Speech-to-text latency
    llm_latency: Optional[float] = None  # LLM response latency
    tts_latency: Optional[float] = None  # Text-to-speech latency
    total_latency: Optional[float] = None
    text_length: int = 0
    was_interrupted: bool = False

    def finalize(self):
        """Calculate total latency and end time"""
        if self.end_time is None:
            self.end_time = time.time()

        # Calculate total latency (sum of pipeline stages)
        latencies = []
        if self.stt_latency:
            latencies.append(self.stt_latency)
        if self.llm_latency:
            latencies.append(self.llm_latency)
        if self.tts_latency:
            latencies.append(self.tts_latency)

        self.total_latency = sum(latencies) if latencies else None

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return {
            'turn_number': self.turn_number,
            'speaker': self.speaker,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'stt_latency_ms': round(self.stt_latency * 1000, 2) if self.stt_latency else None,
            'llm_latency_ms': round(self.llm_latency * 1000, 2) if self.llm_latency else None,
            'tts_latency_ms': round(self.tts_latency * 1000, 2) if self.tts_latency else None,
            'total_latency_ms': round(self.total_latency * 1000, 2) if self.total_latency else None,
            'text_length': self.text_length,
            'was_interrupted': self.was_interrupted
        }


class VoiceConversationState:
    """
    Manages voice-specific conversation state.

    Tracks:
    - Current speaking state
    - Turn history and timing
    - Interruption events
    - Latency metrics
    - Conversation statistics
    """

    def __init__(self):
        """Initialize voice conversation state"""
        self.conversation_id: Optional[str] = None
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None

        # Speaking state
        self.is_agent_speaking: bool = False
        self.is_user_speaking: bool = False
        self.current_speaker: Optional[str] = None

        # Turn tracking
        self.turn_count: int = 0
        self.turns: List[TurnMetrics] = []
        self.current_turn: Optional[TurnMetrics] = None

        # Interruption tracking
        self.interruption_count: int = 0
        self.user_interrupted_agent_count: int = 0
        self.agent_interrupted_user_count: int = 0

        # Latency tracking
        self.latency_history: List[float] = []
        self.avg_stt_latency: float = 0.0
        self.avg_llm_latency: float = 0.0
        self.avg_tts_latency: float = 0.0
        self.avg_total_latency: float = 0.0

        # Conversation metrics
        self.total_user_words: int = 0
        self.total_agent_words: int = 0
        self.silence_periods: List[float] = []

    def start_conversation(self, conversation_id: str):
        """Start a new conversation"""
        self.conversation_id = conversation_id
        self.start_time = time.time()
        self.turn_count = 0
        self.turns = []

    def start_turn(self, speaker: str) -> int:
        """
        Start a new turn

        Args:
            speaker: 'user' or 'agent'

        Returns:
            Turn number
        """
        # Finalize previous turn if exists
        if self.current_turn and not self.current_turn.end_time:
            self.current_turn.finalize()

        # Create new turn
        self.turn_count += 1
        self.current_turn = TurnMetrics(
            turn_number=self.turn_count,
            speaker=speaker,
            start_time=time.time()
        )

        # Update speaking state
        if speaker == 'user':
            self.is_user_speaking = True
            self.is_agent_speaking = False
        else:
            self.is_agent_speaking = True
            self.is_user_speaking = False

        self.current_speaker = speaker

        return self.turn_count

    def end_turn(self, text: Optional[str] = None):
        """
        End the current turn

        Args:
            text: Optional text content of the turn
        """
        if self.current_turn:
            self.current_turn.finalize()

            if text:
                self.current_turn.text_length = len(text)
                word_count = len(text.split())

                if self.current_turn.speaker == 'user':
                    self.total_user_words += word_count
                else:
                    self.total_agent_words += word_count

            # Add to history
            self.turns.append(self.current_turn)
            self.current_turn = None

        # Reset speaking state
        self.is_user_speaking = False
        self.is_agent_speaking = False
        self.current_speaker = None

    def record_interruption(self, interrupter: str):
        """
        Record an interruption event

        Args:
            interrupter: 'user' or 'agent' - who interrupted
        """
        self.interruption_count += 1

        if interrupter == 'user':
            self.user_interrupted_agent_count += 1
            # Mark current agent turn as interrupted
            if self.current_turn and self.current_turn.speaker == 'agent':
                self.current_turn.was_interrupted = True
        else:
            self.agent_interrupted_user_count += 1
            # Mark current user turn as interrupted
            if self.current_turn and self.current_turn.speaker == 'user':
                self.current_turn.was_interrupted = True

    def record_latency(
        self,
        stt_latency: Optional[float] = None,
        llm_latency: Optional[float] = None,
        tts_latency: Optional[float] = None
    ):
        """
        Record latency metrics for current turn

        Args:
            stt_latency: Speech-to-text latency in seconds
            llm_latency: LLM processing latency in seconds
            tts_latency: Text-to-speech latency in seconds
        """
        if not self.current_turn:
            return

        if stt_latency:
            self.current_turn.stt_latency = stt_latency
        if llm_latency:
            self.current_turn.llm_latency = llm_latency
        if tts_latency:
            self.current_turn.tts_latency = tts_latency

    def end_conversation(self):
        """End the conversation and finalize metrics"""
        self.end_time = time.time()

        # Finalize current turn if active
        if self.current_turn:
            self.end_turn()

        # Calculate average latencies
        stt_latencies = [t.stt_latency for t in self.turns if t.stt_latency]
        llm_latencies = [t.llm_latency for t in self.turns if t.llm_latency]
        tts_latencies = [t.tts_latency for t in self.turns if t.tts_latency]
        total_latencies = [t.total_latency for t in self.turns if t.total_latency]

        self.avg_stt_latency = sum(stt_latencies) / len(stt_latencies) if stt_latencies else 0.0
        self.avg_llm_latency = sum(llm_latencies) / len(llm_latencies) if llm_latencies else 0.0
        self.avg_tts_latency = sum(tts_latencies) / len(tts_latencies) if tts_latencies else 0.0
        self.avg_total_latency = sum(total_latencies) / len(total_latencies) if total_latencies else 0.0

    def get_duration(self) -> float:
        """Get conversation duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_statistics(self) -> Dict:
        """
        Get conversation statistics

        Returns:
            Dictionary of statistics
        """
        duration = self.get_duration()

        return {
            'conversation_id': self.conversation_id,
            'duration_seconds': round(duration, 2),
            'total_turns': self.turn_count,
            'user_turns': len([t for t in self.turns if t.speaker == 'user']),
            'agent_turns': len([t for t in self.turns if t.speaker == 'agent']),
            'total_interruptions': self.interruption_count,
            'user_interrupted_agent': self.user_interrupted_agent_count,
            'agent_interrupted_user': self.agent_interrupted_user_count,
            'total_user_words': self.total_user_words,
            'total_agent_words': self.total_agent_words,
            'avg_user_words_per_turn': round(
                self.total_user_words / max(len([t for t in self.turns if t.speaker == 'user']), 1),
                2
            ),
            'avg_agent_words_per_turn': round(
                self.total_agent_words / max(len([t for t in self.turns if t.speaker == 'agent']), 1),
                2
            ),
            'latency_metrics': {
                'avg_stt_ms': round(self.avg_stt_latency * 1000, 2),
                'avg_llm_ms': round(self.avg_llm_latency * 1000, 2),
                'avg_tts_ms': round(self.avg_tts_latency * 1000, 2),
                'avg_total_ms': round(self.avg_total_latency * 1000, 2)
            }
        }

    def get_turn_history(self) -> List[Dict]:
        """Get turn history with metrics"""
        return [turn.to_dict() for turn in self.turns]

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"VoiceConversationState("
            f"id={self.conversation_id}, "
            f"turns={self.turn_count}, "
            f"duration={round(self.get_duration(), 1)}s, "
            f"interruptions={self.interruption_count})"
        )
