"""
Unit Tests for Voice Integration - Phase 5

Tests the voice components:
- VoiceConversationState
- AudioProcessor
- VoiceAgentBridge
- LiveKitManager (structure only, requires actual LiveKit connection for full tests)
"""

import pytest
import asyncio
import time
from pathlib import Path

# Test imports
from voice.conversation_state import VoiceConversationState, TurnMetrics
from voice.audio_processor import AudioProcessor, AudioConfig
from core import Config


class TestVoiceConversationState:
    """Test VoiceConversationState class"""

    def test_initialization(self):
        """Test state initialization"""
        state = VoiceConversationState()

        assert state.conversation_id is None
        assert state.turn_count == 0
        assert state.interruption_count == 0
        assert state.is_agent_speaking is False
        assert state.is_user_speaking is False

    def test_start_conversation(self):
        """Test starting a conversation"""
        state = VoiceConversationState()
        state.start_conversation("test-conv-001")

        assert state.conversation_id == "test-conv-001"
        assert state.turn_count == 0

    def test_turn_tracking(self):
        """Test turn start/end tracking"""
        state = VoiceConversationState()
        state.start_conversation("test-conv-001")

        # Start user turn
        turn_num = state.start_turn('user')
        assert turn_num == 1
        assert state.is_user_speaking is True
        assert state.current_speaker == 'user'

        # End user turn
        state.end_turn("Hello, I need help with my payment")
        assert state.is_user_speaking is False
        assert len(state.turns) == 1
        assert state.turns[0].speaker == 'user'

        # Start agent turn
        turn_num = state.start_turn('agent')
        assert turn_num == 2
        assert state.is_agent_speaking is True

        # End agent turn
        state.end_turn("I understand. Let me help you with that.")
        assert len(state.turns) == 2

    def test_interruption_tracking(self):
        """Test interruption recording"""
        state = VoiceConversationState()
        state.start_conversation("test-conv-001")

        # Start agent turn
        state.start_turn('agent')

        # User interrupts
        state.record_interruption('user')

        assert state.interruption_count == 1
        assert state.user_interrupted_agent_count == 1
        assert state.current_turn.was_interrupted is True

    def test_latency_recording(self):
        """Test latency metric recording"""
        state = VoiceConversationState()
        state.start_conversation("test-conv-001")

        state.start_turn('user')
        state.record_latency(stt_latency=0.3, llm_latency=0.8, tts_latency=0.2)
        state.end_turn("test message")

        turn = state.turns[0]
        assert turn.stt_latency == 0.3
        assert turn.llm_latency == 0.8
        assert turn.tts_latency == 0.2
        assert turn.total_latency == 1.3

    def test_statistics(self):
        """Test conversation statistics"""
        state = VoiceConversationState()
        state.start_conversation("test-conv-001")

        # Simulate conversation
        state.start_turn('user')
        state.end_turn("Hello")

        state.start_turn('agent')
        state.end_turn("Hi there, how can I help you?")

        state.start_turn('user')
        state.record_interruption('user')
        state.end_turn("I need help")

        state.end_conversation()

        stats = state.get_statistics()

        assert stats['conversation_id'] == "test-conv-001"
        assert stats['total_turns'] == 3
        assert stats['user_turns'] == 2
        assert stats['agent_turns'] == 1
        assert stats['total_interruptions'] == 1


class TestAudioProcessor:
    """Test AudioProcessor class"""

    def test_initialization(self):
        """Test processor initialization"""
        processor = AudioProcessor()

        assert processor.config.use_ssml is True
        assert processor.config.max_response_length == 200

    def test_remove_markdown(self):
        """Test markdown removal"""
        processor = AudioProcessor()

        # Bold
        text = "This is **bold** text"
        result = processor.remove_markdown(text)
        assert result == "This is bold text"

        # Italic
        text = "This is *italic* text"
        result = processor.remove_markdown(text)
        assert result == "This is italic text"

        # Links
        text = "Click [here](https://example.com)"
        result = processor.remove_markdown(text)
        assert result == "Click here"

        # Code
        text = "Use `print()` function"
        result = processor.remove_markdown(text)
        assert result == "Use print() function"

    def test_truncate_response(self):
        """Test response truncation"""
        processor = AudioProcessor(AudioConfig(max_response_length=50))

        # Short text - should not truncate
        short_text = "This is short."
        result = processor.truncate_response(short_text)
        assert result == short_text

        # Long text - should truncate at sentence boundary
        long_text = "This is a long sentence. This is another sentence. And one more."
        result = processor.truncate_response(long_text)
        assert len(result) <= 50
        assert "." in result  # Should end at sentence

    def test_prepare_for_tts(self):
        """Test full TTS preparation"""
        processor = AudioProcessor()

        text = "**Hello!** I can help you with [payment](link)."
        result = processor.prepare_for_tts(text)

        # Should remove markdown
        assert "**" not in result
        assert "[" not in result

        # Should have SSML tags if enabled
        if processor.config.use_ssml:
            assert "<speak>" in result or result == text  # May wrap in speak tags

    def test_strip_ssml(self):
        """Test SSML stripping"""
        text_with_ssml = "<speak><prosody rate='slow'>Hello there</prosody></speak>"
        result = AudioProcessor.strip_ssml(text_with_ssml)
        assert result == "Hello there"

    def test_validate_ssml(self):
        """Test SSML validation"""
        # Valid SSML
        valid = "<speak>Hello</speak>"
        assert AudioProcessor.validate_ssml(valid) is True

        # Invalid SSML (missing closing tag)
        invalid = "<speak>Hello"
        assert AudioProcessor.validate_ssml(invalid) is False


class TestVoiceAgentBridge:
    """Test VoiceAgentBridge class"""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test bridge initialization"""
        from voice.voice_bridge import VoiceAgentBridge

        config = Config()

        # This may fail if API keys not set, but should test structure
        try:
            bridge = VoiceAgentBridge(
                agent_version_id="test-v1",
                config=config,
                use_voice_prompt=True
            )

            assert bridge.agent_version_id == "test-v1"
            assert bridge.config is not None
            assert bridge.base_agent is not None
            assert bridge.audio_processor is not None
            assert bridge.logger is not None
            assert bridge.voice_state is not None

            print("✅ VoiceAgentBridge initialization successful")

        except ValueError as e:
            # API key not set - that's ok for structure test
            if "API" in str(e) or "key" in str(e).lower():
                print("⚠️  Skipping bridge test - API keys not configured")
                pytest.skip("API keys not configured")
            else:
                raise

    @pytest.mark.asyncio
    async def test_conversation_lifecycle(self):
        """Test conversation start/end"""
        from voice.voice_bridge import VoiceAgentBridge

        config = Config()

        try:
            bridge = VoiceAgentBridge(
                agent_version_id="test-v1",
                config=config
            )

            # Start conversation
            conv_id = await bridge.start_conversation(
                conversation_id="test-conv-001",
                persona_name="test_user"
            )

            assert conv_id == "test-conv-001"
            assert bridge.conversation_started is True

            # End conversation
            await bridge.end_conversation(outcome="test_completed")

            assert bridge.conversation_started is False

            print("✅ Conversation lifecycle test passed")

        except ValueError as e:
            if "API" in str(e) or "key" in str(e).lower():
                pytest.skip("API keys not configured")
            else:
                raise

    def test_get_greeting_message(self):
        """Test greeting message generation"""
        from voice.voice_bridge import VoiceAgentBridge

        config = Config()

        try:
            bridge = VoiceAgentBridge(
                agent_version_id="test-v1",
                config=config
            )

            greeting = bridge.get_greeting_message()
            assert isinstance(greeting, str)
            assert len(greeting) > 0

            print(f"✅ Greeting: {greeting}")

        except ValueError as e:
            if "API" in str(e) or "key" in str(e).lower():
                pytest.skip("API keys not configured")
            else:
                raise


class TestLiveKitManager:
    """Test LiveKitManager structure (requires LiveKit connection for full tests)"""

    def test_initialization(self):
        """Test manager initialization"""
        from voice.livekit_manager import LiveKitManager

        try:
            config = Config()
            manager = LiveKitManager(config)

            assert manager.livekit_url is not None
            assert manager.api_key is not None
            assert manager.api_secret is not None

            print("✅ LiveKitManager initialization successful")
            print(f"   URL: {manager.livekit_url}")

        except ValueError as e:
            if "LiveKit" in str(e):
                print("⚠️  Skipping LiveKit test - credentials not configured")
                pytest.skip("LiveKit credentials not configured")
            else:
                raise

        except RuntimeError as e:
            if "not installed" in str(e):
                print("⚠️  Skipping LiveKit test - package not installed")
                pytest.skip("LiveKit not installed")
            else:
                raise


def main():
    """Run all voice tests"""
    print("=" * 60)
    print("VOICE INTEGRATION TESTS - PHASE 5")
    print("=" * 60)
    print()

    # Test 1: VoiceConversationState
    print("Test 1: VoiceConversationState")
    print("-" * 40)
    test_state = TestVoiceConversationState()
    test_state.test_initialization()
    test_state.test_start_conversation()
    test_state.test_turn_tracking()
    test_state.test_interruption_tracking()
    test_state.test_latency_recording()
    test_state.test_statistics()
    print("✅ All VoiceConversationState tests passed\n")

    # Test 2: AudioProcessor
    print("Test 2: AudioProcessor")
    print("-" * 40)
    test_processor = TestAudioProcessor()
    test_processor.test_initialization()
    test_processor.test_remove_markdown()
    test_processor.test_truncate_response()
    test_processor.test_prepare_for_tts()
    test_processor.test_strip_ssml()
    test_processor.test_validate_ssml()
    print("✅ All AudioProcessor tests passed\n")

    # Test 3: VoiceAgentBridge
    print("Test 3: VoiceAgentBridge")
    print("-" * 40)
    test_bridge = TestVoiceAgentBridge()
    asyncio.run(test_bridge.test_initialization())
    asyncio.run(test_bridge.test_conversation_lifecycle())
    test_bridge.test_get_greeting_message()
    print("✅ All VoiceAgentBridge tests passed\n")

    # Test 4: LiveKitManager
    print("Test 4: LiveKitManager")
    print("-" * 40)
    test_manager = TestLiveKitManager()
    test_manager.test_initialization()
    print("✅ LiveKitManager structure validated\n")

    print("=" * 60)
    print("ALL VOICE TESTS COMPLETED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Set up API keys (LiveKit, Deepgram, Cartesia) in .env")
    print("2. Run voice_demo.py for interactive testing")
    print("3. Test full voice conversation flow")


if __name__ == "__main__":
    main()
