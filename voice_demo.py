#!/usr/bin/env python3
"""
Voice Agent Demo - Interactive Voice Agent Testing

This script runs the LiveKit voice agent for testing and demonstration.

Usage:
    python voice_demo.py dev                    # Run in development mode
    python voice_demo.py start                  # Run in production mode
    python voice_demo.py --agent-id v1-abc123   # Use specific agent version
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import Config
from evolution import AgentArchive


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print(" " * 15 + "DARWIN-GÖDEL MACHINE VOICE AGENT")
    print(" " * 20 + "Interactive Voice Demo")
    print("=" * 70)
    print()


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    missing = []

    try:
        import livekit
        print("✅ livekit")
    except ImportError:
        missing.append("livekit-agents")
        print("❌ livekit-agents")

    try:
        from livekit.plugins import deepgram
        print("✅ livekit-plugins-deepgram")
    except ImportError:
        missing.append("livekit-plugins-deepgram")
        print("❌ livekit-plugins-deepgram")

    try:
        from livekit.plugins import cartesia
        print("✅ livekit-plugins-cartesia")
    except ImportError:
        missing.append("livekit-plugins-cartesia")
        print("❌ livekit-plugins-cartesia")

    try:
        from livekit.plugins import silero
        print("✅ livekit-plugins-silero")
    except ImportError:
        missing.append("livekit-plugins-silero")
        print("❌ livekit-plugins-silero")

    if missing:
        print()
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print()
        print("Install with:")
        print("  pip install 'livekit-agents[deepgram,cartesia,silero]'")
        return False

    return True


def check_env_vars():
    """Check if required environment variables are set"""
    print("\nChecking environment variables...")

    required = {
        'LIVEKIT_URL': 'LiveKit server URL (e.g., wss://your-project.livekit.cloud)',
        'LIVEKIT_API_KEY': 'LiveKit API key',
        'LIVEKIT_API_SECRET': 'LiveKit API secret',
        'DEEPGRAM_API_KEY': 'Deepgram API key for STT',
        'CARTESIA_API_KEY': 'Cartesia API key for TTS'
    }

    missing = []

    for var, description in required.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display = value
            print(f"✅ {var}: {display}")
        else:
            missing.append((var, description))
            print(f"❌ {var}: Not set")

    if missing:
        print("\nMissing environment variables:")
        for var, description in missing:
            print(f"  - {var}: {description}")
        print("\nSet these in your .env file")
        return False

    return True


def select_agent():
    """Select which agent version to use"""
    print("\nSelecting agent version...")

    try:
        archive = AgentArchive()
        best_agent = archive.get_best_agent()

        if best_agent:
            print(f"✅ Found best evolved agent:")
            print(f"   ID: {best_agent['id']}")
            print(f"   Generation: {best_agent.get('generation', 0)}")
            print(f"   Score: {best_agent.get('composite_score', 0):.1f}/100")
            return best_agent['id']
        else:
            print("⚠️  No evolved agents found, using baseline")
            return "voice-baseline-v1"

    except Exception as e:
        print(f"⚠️  Error loading agent from archive: {e}")
        print("   Using baseline agent")
        return "voice-baseline-v1"


def print_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 70)
    print("VOICE AGENT STARTED!")
    print("=" * 70)
    print()
    print("The voice agent is now running and waiting for connections.")
    print()
    print("To test the agent:")
    print()
    print("1. Join the LiveKit room via web browser:")
    print("   • Go to https://cloud.livekit.io/projects/<your-project>/rooms")
    print("   • Or use the LiveKit Playground: https://meet.livekit.io/")
    print()
    print("2. Allow microphone access when prompted")
    print()
    print("3. Start speaking! The agent will:")
    print("   • Listen to your voice (STT with Deepgram)")
    print("   • Generate responses (LLM via BaseAgent)")
    print("   • Speak back to you (TTS with Cartesia)")
    print()
    print("4. Test features:")
    print("   • Try interrupting the agent mid-sentence")
    print("   • Test different conversation scenarios")
    print("   • Observe latency and naturalness")
    print()
    print("5. All conversations are automatically logged to:")
    print("   data/conversations/YYYY-MM-DD/")
    print()
    print("=" * 70)
    print()
    print("Press Ctrl+C to stop the agent")
    print()


def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description='Run the Darwin-Gödel Machine Voice Agent')
    parser.add_argument(
        'mode',
        nargs='?',
        default='dev',
        choices=['dev', 'start', 'prod'],
        help='Run mode: dev (development) or start/prod (production)'
    )
    parser.add_argument(
        '--agent-id',
        type=str,
        help='Specific agent version ID to use'
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip dependency and environment checks'
    )

    args = parser.parse_args()

    print_banner()

    if not args.skip_checks:
        # Check dependencies
        if not check_dependencies():
            print("\n❌ Dependencies not satisfied")
            return 1

        # Check environment variables
        if not check_env_vars():
            print("\n❌ Environment not configured")
            return 1

    # Select agent
    if args.agent_id:
        agent_id = args.agent_id
        print(f"\nUsing specified agent: {agent_id}")
    else:
        agent_id = select_agent()

    # Print instructions
    print_instructions()

    # Import and run voice agent
    try:
        from voice.voice_agent import main as run_voice_agent

        # Set mode
        os.environ['LIVEKIT_MODE'] = args.mode

        # Run agent
        run_voice_agent(agent_version_id=agent_id)

    except KeyboardInterrupt:
        print("\n\n👋 Voice agent stopped by user")
        return 0

    except Exception as e:
        print(f"\n❌ Error running voice agent: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
