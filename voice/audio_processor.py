"""
Audio Processing Utilities

Handles text preprocessing for TTS, SSML formatting,
and audio post-processing for voice conversations.
"""

import re
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    use_ssml: bool = True
    max_response_length: int = 200
    add_pauses: bool = True
    emphasis_enabled: bool = True
    speed: float = 1.0
    pitch: str = "medium"


class AudioProcessor:
    """
    Processes text for optimal voice output.

    Handles:
    - Removing markdown/formatting
    - Adding SSML prosody tags
    - Formatting numbers and dates for speech
    - Truncating long responses
    - Adding natural pauses
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialize audio processor

        Args:
            config: Audio processing configuration
        """
        self.config = config or AudioConfig()

    def prepare_for_tts(self, text: str) -> str:
        """
        Prepare text for text-to-speech

        Args:
            text: Raw text from LLM

        Returns:
            Processed text ready for TTS
        """
        # Remove markdown formatting
        text = self.remove_markdown(text)

        # Format numbers for speech
        text = self.format_numbers_for_speech(text)

        # Truncate if too long
        if len(text) > self.config.max_response_length:
            text = self.truncate_response(text)

        # Add SSML if enabled
        if self.config.use_ssml:
            text = self.add_ssml_tags(text)

        # Clean up whitespace
        text = ' '.join(text.split())

        return text

    def remove_markdown(self, text: str) -> str:
        """
        Remove markdown formatting from text

        Args:
            text: Text with markdown

        Returns:
            Plain text
        """
        # Remove bold/italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
        text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_

        # Remove links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove headers (#)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Remove code blocks
        text = re.sub(r'```[^`]+```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Remove bullet points
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)

        # Remove numbered lists
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        return text

    def format_numbers_for_speech(self, text: str) -> str:
        """
        Format numbers for natural speech

        Args:
            text: Text with numbers

        Returns:
            Text with numbers formatted for speech
        """
        # Currency: $1,234.56 -> "one thousand, two hundred thirty-four dollars and fifty-six cents"
        # For simplicity, we'll keep dollar amounts readable
        # More sophisticated number-to-words conversion could be added

        # Format phone numbers: (123) 456-7890 -> spoken naturally
        # Keep formatted for now - TTS providers usually handle this well

        # Dates: 11/17/2025 -> "November seventeenth, twenty twenty-five"
        # Keep formatted for now - TTS providers usually handle this

        return text

    def truncate_response(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Truncate response to prevent voice fatigue

        Args:
            text: Full response text
            max_length: Maximum length (uses config default if not provided)

        Returns:
            Truncated text ending at sentence boundary
        """
        max_len = max_length or self.config.max_response_length

        if len(text) <= max_len:
            return text

        # Try to truncate at sentence boundary
        sentences = re.split(r'([.!?])\s+', text)

        truncated = ""
        for i in range(0, len(sentences), 2):  # Step by 2 to handle sentence + delimiter
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

            if len(truncated) + len(sentence) + len(delimiter) <= max_len:
                truncated += sentence + delimiter + " "
            else:
                break

        # If no complete sentence fits, hard truncate
        if not truncated.strip():
            truncated = text[:max_len].rsplit(' ', 1)[0] + "..."

        return truncated.strip()

    def add_ssml_tags(self, text: str) -> str:
        """
        Add SSML prosody tags for natural speech

        Args:
            text: Plain text

        Returns:
            Text with SSML tags
        """
        # For now, we'll add simple prosody tags
        # More sophisticated SSML could be added based on context

        # Wrap in speak tag
        text = f"<speak>{text}</speak>"

        # Add prosody for speed and pitch if configured
        if self.config.speed != 1.0 or self.config.pitch != "medium":
            prosody_attrs = []
            if self.config.speed != 1.0:
                prosody_attrs.append(f'rate="{self.config.speed}"')
            if self.config.pitch != "medium":
                prosody_attrs.append(f'pitch="{self.config.pitch}"')

            prosody_tag = f"<prosody {' '.join(prosody_attrs)}>"
            text = text.replace("<speak>", f"<speak>{prosody_tag}")
            text = text.replace("</speak>", "</prosody></speak>")

        return text

    def add_pause(self, text: str, pause_after: str, duration_ms: int = 300) -> str:
        """
        Add pause after specific text

        Args:
            text: Text to modify
            pause_after: Text after which to add pause
            duration_ms: Pause duration in milliseconds

        Returns:
            Text with pause tag
        """
        if not self.config.add_pauses:
            return text

        # Add SSML break tag
        pause_tag = f'<break time="{duration_ms}ms"/>'
        text = text.replace(pause_after, f"{pause_after}{pause_tag}")

        return text

    def add_emphasis(self, text: str, emphasize_text: str, level: str = "moderate") -> str:
        """
        Add emphasis to specific text

        Args:
            text: Text to modify
            emphasize_text: Text to emphasize
            level: Emphasis level (strong, moderate, reduced)

        Returns:
            Text with emphasis tag
        """
        if not self.config.emphasis_enabled:
            return text

        # Add SSML emphasis tag
        emphasized = f'<emphasis level="{level}">{emphasize_text}</emphasis>'
        text = text.replace(emphasize_text, emphasized)

        return text

    def format_for_interruption(self, text: str) -> str:
        """
        Format acknowledgment for interruption

        Args:
            text: Interruption acknowledgment text

        Returns:
            Formatted text
        """
        # Quick acknowledgments for interruptions
        # These should be brief and natural

        # Add slight pause before continuing
        if self.config.add_pauses:
            text = f'<break time="200ms"/>{text}'

        return text

    def split_long_response(self, text: str, max_chunk_length: int = 150) -> list[str]:
        """
        Split long response into smaller chunks for streaming

        Args:
            text: Full response text
            max_chunk_length: Maximum length per chunk

        Returns:
            List of text chunks
        """
        # Split at sentence boundaries
        sentences = re.split(r'([.!?])\s+', text)

        chunks = []
        current_chunk = ""

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

            if len(current_chunk) + len(sentence) + len(delimiter) <= max_chunk_length:
                current_chunk += sentence + delimiter + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + delimiter + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def strip_ssml(text: str) -> str:
        """
        Remove SSML tags from text (for logging/display)

        Args:
            text: Text with SSML tags

        Returns:
            Plain text
        """
        # Remove all SSML tags
        text = re.sub(r'<[^>]+>', '', text)
        return text

    @staticmethod
    def validate_ssml(text: str) -> bool:
        """
        Validate SSML syntax

        Args:
            text: Text with potential SSML tags

        Returns:
            True if valid SSML, False otherwise
        """
        # Basic validation - check for matching tags
        # More sophisticated validation could be added

        # Check for speak tags
        if '<speak>' in text and '</speak>' not in text:
            return False
        if '</speak>' in text and '<speak>' not in text:
            return False

        # Check for balanced prosody tags
        open_prosody = text.count('<prosody')
        close_prosody = text.count('</prosody>')
        if open_prosody != close_prosody:
            return False

        # Check for balanced emphasis tags
        open_emphasis = text.count('<emphasis')
        close_emphasis = text.count('</emphasis>')
        if open_emphasis != close_emphasis:
            return False

        return True

    def get_audio_config(self) -> Dict:
        """Get current audio configuration"""
        return {
            'use_ssml': self.config.use_ssml,
            'max_response_length': self.config.max_response_length,
            'add_pauses': self.config.add_pauses,
            'emphasis_enabled': self.config.emphasis_enabled,
            'speed': self.config.speed,
            'pitch': self.config.pitch
        }

    def update_config(self, **kwargs):
        """
        Update audio configuration

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
