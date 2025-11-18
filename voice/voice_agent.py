"""
Voice Agent - Main LiveKit Orchestrator

This is the main entry point for the LiveKit voice agent.
Uses LiveKit's Agents framework with STT/TTS/VAD plugins.

Architecture:
    LiveKit Room → AgentSession (STT→LLM→TTS) → VoiceAgentBridge → BaseAgent
"""

import os
import asyncio
from typing import Optional
import logging

try:
    from livekit import agents, rtc
    from livekit.agents import JobContext, WorkerOptions, cli
    from livekit.plugins import deepgram, cartesia, openai, silero
    LIVEKIT_AGENTS_AVAILABLE = True
except ImportError:
    LIVEKIT_AGENTS_AVAILABLE = False
    print("⚠️  LiveKit Agents not installed")
    print("   Run: pip install 'livekit-agents[deepgram,cartesia,openai,silero]'")

from core import Config
from evolution import AgentArchive
from .voice_bridge import VoiceAgentBridge


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BridgedLLM(agents.llm.LLM):
    """
    Custom LLM wrapper that calls VoiceAgentBridge instead of a real LLM.

    This allows us to use our existing BaseAgent within LiveKit's
    AgentSession framework without modification.
    """

    def __init__(self, bridge: VoiceAgentBridge):
        """
        Initialize bridged LLM

        Args:
            bridge: VoiceAgentBridge instance
        """
        super().__init__()
        self.bridge = bridge

    async def chat(
        self,
        chat_ctx: agents.llm.ChatContext,
        conn_options: Optional[agents.llm.LLMConnOptions] = None
    ) -> agents.llm.LLMStream:
        """
        Generate response using VoiceAgentBridge

        Args:
            chat_ctx: Chat context from LiveKit
            conn_options: Connection options (ignored)

        Returns:
            LLM stream with response
        """
        # Get last user message
        messages = chat_ctx.messages
        last_message = messages[-1] if messages else None

        if not last_message or last_message.role != "user":
            # No user message, return empty response
            return self._create_empty_stream()

        user_text = last_message.content

        try:
            # Call VoiceAgentBridge to get response
            # This calls BaseAgent under the hood!
            response_text = await self.bridge.handle_user_speech(user_text)

            # Create stream with response
            return self._create_stream(response_text)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._create_empty_stream()

    def _create_stream(self, text: str) -> agents.llm.LLMStream:
        """Create LLM stream with text response"""
        # Create a simple stream that yields the response
        class SimpleStream(agents.llm.LLMStream):
            def __init__(self, text: str):
                super().__init__()
                self.text = text
                self._done = False

            async def __anext__(self):
                if self._done:
                    raise StopAsyncIteration

                self._done = True
                return agents.llm.ChatChunk(
                    choices=[
                        agents.llm.Choice(
                            delta=agents.llm.ChoiceDelta(
                                role="assistant",
                                content=self.text
                            )
                        )
                    ]
                )

        return SimpleStream(text)

    def _create_empty_stream(self) -> agents.llm.LLMStream:
        """Create empty LLM stream"""
        return self._create_stream("")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for LiveKit agent.

    Called by LiveKit when agent joins a room.

    Args:
        ctx: Job context from LiveKit
    """
    logger.info("🎙️  Voice agent starting...")

    # Load configuration
    config = Config()

    # Get agent version to use
    # Try to get best agent from archive, fallback to baseline
    try:
        archive = AgentArchive()
        best_agent = archive.get_best_agent()

        if best_agent:
            agent_version_id = best_agent['id']
            logger.info(f"Using best evolved agent: {agent_version_id}")
            logger.info(f"  Score: {best_agent.get('composite_score', 0):.1f}/100")
        else:
            agent_version_id = "voice-baseline-v1"
            logger.info("No evolved agent found, using baseline")

    except Exception as e:
        logger.warning(f"Error loading agent from archive: {e}")
        agent_version_id = "voice-baseline-v1"

    # Initialize VoiceAgentBridge
    bridge = VoiceAgentBridge(
        agent_version_id=agent_version_id,
        config=config,
        use_voice_prompt=True
    )

    # Connect to room
    await ctx.connect()
    logger.info(f"Connected to room: {ctx.room.name}")

    # Create bridged LLM that calls our VoiceAgentBridge
    llm = BridgedLLM(bridge)

    # Set up STT (Speech-to-Text)
    stt_provider = config.get('voice.stt.provider', 'deepgram')
    if stt_provider == 'deepgram':
        stt = deepgram.STT(
            model=config.get('voice.stt.model', 'nova-3'),
            language=config.get('voice.stt.language', 'en-US')
        )
    elif stt_provider == 'whisper':
        stt = openai.STT(model='whisper-1')
    else:
        raise ValueError(f"Unsupported STT provider: {stt_provider}")

    logger.info(f"STT: {stt_provider}")

    # Set up TTS (Text-to-Speech)
    tts_provider = config.get('voice.tts.provider', 'cartesia')
    if tts_provider == 'cartesia':
        tts = cartesia.TTS(
            model=config.get('voice.tts.model', 'sonic'),
            voice=config.get('voice.tts.voice_id', 'default'),
            speed=config.get('voice.tts.speed', 1.0)
        )
    elif tts_provider == 'openai':
        tts = openai.TTS(
            model=config.get('voice.tts.model', 'tts-1'),
            voice=config.get('voice.tts.voice_id', 'nova')
        )
    else:
        raise ValueError(f"Unsupported TTS provider: {tts_provider}")

    logger.info(f"TTS: {tts_provider}")

    # Set up VAD (Voice Activity Detection)
    vad = silero.VAD.load(
        min_speech_duration=config.get('voice.vad.min_speech_duration', 0.1),
        min_silence_duration=config.get('voice.vad.min_silence_duration', 0.3),
        activation_threshold=config.get('voice.vad.sensitivity', 0.5)
    )

    logger.info("VAD: Silero")

    # Create agent session
    assistant = agents.VoiceAssistant(
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
        chat_ctx=agents.llm.ChatContext(
            messages=[
                agents.llm.ChatMessage(
                    role="system",
                    content=bridge.system_prompt
                )
            ]
        )
    )

    # Start conversation in bridge
    conversation_id = f"voice-{ctx.room.name}-{asyncio.get_event_loop().time():.0f}"
    await bridge.start_conversation(
        conversation_id=conversation_id,
        persona_name="live_user",
        metadata={
            'room_name': ctx.room.name,
            'room_sid': ctx.room.sid if hasattr(ctx.room, 'sid') else None
        }
    )

    # Set up event handlers
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(f"👤 Participant joined: {participant.identity}")

    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        logger.info(f"👋 Participant left: {participant.identity}")

        # End conversation when user leaves
        asyncio.create_task(
            bridge.end_conversation(outcome="user_disconnected")
        )

    # Handle interruptions
    @assistant.on("agent_speech_interrupted")
    def on_agent_interrupted():
        logger.info("⚡ Agent was interrupted by user")
        asyncio.create_task(bridge.handle_interruption('user'))

    # Handle errors
    @assistant.on("error")
    def on_error(error: Exception):
        logger.error(f"❌ Agent error: {error}")

    # Start the assistant
    assistant.start(ctx.room)

    # Greet the user
    greeting = bridge.get_greeting_message()
    await assistant.say(greeting)

    logger.info("✅ Voice agent ready and listening...")

    # Keep agent running
    await asyncio.sleep(float('inf'))


def main(
    agent_version_id: Optional[str] = None,
    config_path: Optional[str] = None
):
    """
    Main function to run the voice agent

    Args:
        agent_version_id: Specific agent version to use
        config_path: Path to config file
    """
    if not LIVEKIT_AGENTS_AVAILABLE:
        print("❌ LiveKit Agents not installed")
        print("   Run: pip install 'livekit-agents[deepgram,cartesia,openai,silero]'")
        return

    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv('LIVEKIT_API_KEY'),
            api_secret=os.getenv('LIVEKIT_API_SECRET'),
            ws_url=os.getenv('LIVEKIT_URL')
        )
    )


if __name__ == "__main__":
    main()
