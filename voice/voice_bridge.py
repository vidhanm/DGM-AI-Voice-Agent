"""
Voice Agent Bridge

Critical integration layer that bridges LiveKit's streaming voice system
with the existing text-based BaseAgent.

This adapter allows zero-modification integration - BaseAgent remains unchanged
while voice capabilities are added transparently.
"""

import time
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from core import Config, PromptManager
from core.agent import BaseAgent
from log_manager import ConversationLogger
from .conversation_state import VoiceConversationState
from .audio_processor import AudioProcessor, AudioConfig


class VoiceAgentBridge:
    """
    Bridges LiveKit voice system with text-based BaseAgent.

    This is the critical integration layer that:
    1. Receives text from STT (speech-to-text)
    2. Calls BaseAgent to generate response
    3. Formats response for TTS (text-to-speech)
    4. Logs all interactions
    5. Tracks conversation state

    Architecture:
        LiveKit STT → VoiceAgentBridge → BaseAgent (existing!)
                          ↓
        LiveKit TTS ← VoiceAgentBridge ← BaseAgent
    """

    def __init__(
        self,
        agent_version_id: str,
        config: Optional[Config] = None,
        use_voice_prompt: bool = True
    ):
        """
        Initialize the voice agent bridge

        Args:
            agent_version_id: Agent version ID to use (from AgentArchive)
            config: Configuration object
            use_voice_prompt: Use voice-optimized prompt (default: True)
        """
        self.agent_version_id = agent_version_id
        self.config = config or Config()

        # Load appropriate prompt
        prompt_manager = PromptManager()
        if use_voice_prompt:
            # Use voice-optimized prompt
            template_name = self.config.get('voice.prompt_template', 'voice_prompt.yaml')
        else:
            # Use standard prompt
            template_name = 'base_prompt.yaml'

        # Create prompt with variables
        self.system_prompt = prompt_manager.create_agent_prompt(
            template_name,
            company_name=self.config.get('company.name', 'Acme Financial'),
            agent_name=self.config.get('agent.name', 'Sarah'),
            tone=self.config.get('agent.tone', 'empathetic')
        )

        # Initialize BaseAgent (existing class - no modifications needed!)
        self.base_agent = BaseAgent(
            agent_version_id=agent_version_id,
            prompt=self.system_prompt,
            config=self.config
        )

        # Initialize audio processor
        audio_config = AudioConfig(
            use_ssml=self.config.get('voice.use_ssml', True),
            max_response_length=self.config.get('voice.max_response_length', 200),
            add_pauses=True,
            emphasis_enabled=True
        )
        self.audio_processor = AudioProcessor(audio_config)

        # Initialize conversation logger
        self.logger = ConversationLogger()
        self.conversation_id: Optional[str] = None
        self.conversation_started: bool = False

        # Initialize voice conversation state
        self.voice_state = VoiceConversationState()

        # Metrics tracking
        self.turn_count = 0
        self.last_user_message_time: Optional[float] = None
        self.last_agent_message_time: Optional[float] = None

        print(f"🎙️  Voice bridge initialized for agent: {agent_version_id}")
        print(f"   Using prompt: {template_name}")
        print(f"   Audio processing: SSML={audio_config.use_ssml}, "
              f"Max length={audio_config.max_response_length}")

    async def start_conversation(
        self,
        conversation_id: Optional[str] = None,
        persona_name: str = "live_user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new voice conversation

        Args:
            conversation_id: Optional conversation ID (generates one if None)
            persona_name: Persona name (default: "live_user" for real users)
            metadata: Additional metadata

        Returns:
            conversation_id
        """
        # Generate conversation ID if not provided
        if conversation_id is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            conversation_id = f"voice-{timestamp}"

        self.conversation_id = conversation_id

        # Prepare metadata
        conv_metadata = metadata or {}
        conv_metadata.update({
            'mode': 'voice',
            'stt_provider': self.config.get('voice.stt.provider', 'deepgram'),
            'tts_provider': self.config.get('voice.tts.provider', 'cartesia'),
            'voice_optimized': True,
            'started_at': datetime.now().isoformat()
        })

        # Start conversation in logger
        self.logger.start_conversation(
            conversation_id=conversation_id,
            agent_version_id=self.agent_version_id,
            persona_name=persona_name,
            metadata=conv_metadata
        )

        # Start voice state tracking
        self.voice_state.start_conversation(conversation_id)

        self.conversation_started = True
        self.turn_count = 0

        print(f"🎤 Started voice conversation: {conversation_id}")

        return conversation_id

    async def handle_user_speech(
        self,
        text: str,
        stt_latency: Optional[float] = None
    ) -> str:
        """
        Handle user speech input (from STT)

        This is the main method called when user speaks.

        Args:
            text: Transcribed text from STT
            stt_latency: STT processing latency in seconds

        Returns:
            Agent response text (ready for TTS)
        """
        if not self.conversation_started:
            raise RuntimeError("Conversation not started. Call start_conversation() first.")

        # Start timing for this turn
        turn_start = time.time()
        self.last_user_message_time = turn_start

        # Start user turn in voice state
        self.voice_state.start_turn('user')
        if stt_latency:
            self.voice_state.record_latency(stt_latency=stt_latency)

        # Log user turn
        self.logger.log_turn(
            conversation_id=self.conversation_id,
            speaker='user',
            message=text,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'turn_number': self.turn_count + 1,
                'stt_latency_ms': round(stt_latency * 1000, 2) if stt_latency else None
            }
        )

        # End user turn
        self.voice_state.end_turn(text)

        # Generate agent response using BaseAgent
        llm_start = time.time()
        agent_response = self.base_agent.generate_response(text)
        llm_latency = time.time() - llm_start

        # Start agent turn
        self.voice_state.start_turn('agent')
        self.voice_state.record_latency(llm_latency=llm_latency)

        # Format response for voice TTS
        tts_start = time.time()
        voice_response = self.audio_processor.prepare_for_tts(agent_response)
        tts_prep_latency = time.time() - tts_start

        # Log TTS preparation time (actual TTS latency will be recorded by TTS provider)
        self.voice_state.record_latency(tts_latency=tts_prep_latency)

        # Log agent turn
        self.logger.log_turn(
            conversation_id=self.conversation_id,
            speaker='agent',
            message=agent_response,  # Log original (un-processed) response
            metadata={
                'timestamp': datetime.now().isoformat(),
                'turn_number': self.turn_count + 1,
                'llm_latency_ms': round(llm_latency * 1000, 2),
                'voice_formatted': voice_response != agent_response,
                'response_length': len(agent_response),
                'voice_response_length': len(voice_response)
            }
        )

        # End agent turn
        self.voice_state.end_turn(voice_response)

        self.turn_count += 1
        self.last_agent_message_time = time.time()

        return voice_response

    async def handle_interruption(self, interrupted_by: str = 'user'):
        """
        Handle conversation interruption

        Called when user interrupts agent or vice versa

        Args:
            interrupted_by: Who interrupted ('user' or 'agent')
        """
        print(f"⚡ Interruption detected by {interrupted_by}")

        # Record interruption in voice state
        self.voice_state.record_interruption(interrupted_by)

        # Log interruption event
        if self.conversation_started:
            self.logger.log_turn(
                conversation_id=self.conversation_id,
                speaker='system',
                message=f"Interruption: {interrupted_by} interrupted",
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'event_type': 'interruption',
                    'interrupted_by': interrupted_by,
                    'interruption_count': self.voice_state.interruption_count
                }
            )

    async def handle_silence(self, duration_seconds: float):
        """
        Handle silence detection

        Args:
            duration_seconds: Duration of silence
        """
        if duration_seconds > self.config.get('voice.conversation.silence_timeout_seconds', 30):
            print(f"🔇 Silence detected for {duration_seconds:.1f}s - may end conversation")

            # Log silence event
            if self.conversation_started:
                self.logger.log_turn(
                    conversation_id=self.conversation_id,
                    speaker='system',
                    message=f"Silence detected for {duration_seconds:.1f}s",
                    metadata={
                        'timestamp': datetime.now().isoformat(),
                        'event_type': 'silence',
                        'duration_seconds': duration_seconds
                    }
                )

    async def end_conversation(
        self,
        outcome: str = 'completed',
        evaluation_scores: Optional[Dict[str, float]] = None
    ):
        """
        End the voice conversation

        Args:
            outcome: Conversation outcome (completed, timeout, user_hung_up, error)
            evaluation_scores: Optional evaluation scores
        """
        if not self.conversation_started:
            return

        # End voice state tracking
        self.voice_state.end_conversation()

        # Get voice statistics
        voice_stats = self.voice_state.get_statistics()

        # End conversation in logger
        self.logger.end_conversation(
            conversation_id=self.conversation_id,
            outcome=outcome,
            scores=evaluation_scores or {},
            metadata={
                'voice_stats': voice_stats,
                'duration_seconds': voice_stats['duration_seconds'],
                'total_turns': self.turn_count
            }
        )

        self.conversation_started = False

        print(f"✅ Voice conversation ended: {self.conversation_id}")
        print(f"   Outcome: {outcome}")
        print(f"   Duration: {voice_stats['duration_seconds']:.1f}s")
        print(f"   Turns: {self.turn_count}")
        print(f"   Interruptions: {voice_stats['total_interruptions']}")
        print(f"   Avg latency: {voice_stats['latency_metrics']['avg_total_ms']:.0f}ms")

    def get_greeting_message(self) -> str:
        """
        Get initial greeting message for conversation

        Returns:
            Greeting message
        """
        greeting = self.config.get(
            'voice.conversation.greeting_message',
            "Hello, this is an automated payment assistance call. May I have your name?"
        )

        # Format for TTS
        return self.audio_processor.prepare_for_tts(greeting)

    def format_for_voice(self, text: str) -> str:
        """
        Format text for voice output

        Args:
            text: Raw text

        Returns:
            Voice-formatted text
        """
        return self.audio_processor.prepare_for_tts(text)

    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return {
            'conversation_id': self.conversation_id,
            'conversation_started': self.conversation_started,
            'turn_count': self.turn_count,
            'is_agent_speaking': self.voice_state.is_agent_speaking,
            'is_user_speaking': self.voice_state.is_user_speaking,
            'voice_stats': self.voice_state.get_statistics() if self.conversation_started else {}
        }

    def get_latency_metrics(self) -> Dict[str, float]:
        """Get current latency metrics"""
        if not self.conversation_started:
            return {}

        stats = self.voice_state.get_statistics()
        return stats.get('latency_metrics', {})

    async def evaluate_conversation(self) -> Optional[Dict[str, float]]:
        """
        Evaluate the conversation using the evaluation system

        Returns:
            Evaluation scores (goal_completion, quality, compliance, composite)
            None if conversation not ended
        """
        if self.conversation_started:
            print("⚠️  Cannot evaluate: conversation still in progress")
            return None

        # Import evaluator (lazy import to avoid circular dependency)
        from evaluation import Evaluator

        try:
            # Create evaluator
            evaluator = Evaluator(config=self.config)

            # Get conversation log
            conversation = self.logger.get_conversation(self.conversation_id)

            # Evaluate
            scores = evaluator.evaluate_conversation(conversation)

            print(f"📊 Evaluation scores for {self.conversation_id}:")
            print(f"   Goal Completion: {scores['goal_completion_score']:.1f}/100")
            print(f"   Quality: {scores['conversational_quality_score']:.1f}/100")
            print(f"   Compliance: {scores['compliance_score']:.1f}/100")
            print(f"   Composite: {scores['composite_score']:.1f}/100")
            print(f"   Pass/Fail: {'PASSED' if scores['passed'] else 'FAILED'}")

            return scores

        except Exception as e:
            print(f"❌ Error evaluating conversation: {e}")
            return None

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"VoiceAgentBridge("
            f"agent_id={self.agent_version_id}, "
            f"conversation_id={self.conversation_id}, "
            f"turns={self.turn_count}, "
            f"active={self.conversation_started})"
        )
