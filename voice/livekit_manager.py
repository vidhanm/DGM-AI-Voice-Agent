"""
LiveKit Room Management

Handles LiveKit room creation, connection management,
participant tracking, and audio track management.
"""

import os
import asyncio
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import secrets

try:
    from livekit import api, rtc
    from livekit.api import AccessToken, VideoGrants
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    print("⚠️  LiveKit not installed. Run: pip install livekit-agents")

from core import Config


class LiveKitManager:
    """
    Manages LiveKit room operations.

    Handles:
    - Room creation and deletion
    - Access token generation
    - Room connection
    - Participant tracking
    - Audio track management
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize LiveKit manager

        Args:
            config: Configuration object
        """
        if not LIVEKIT_AVAILABLE:
            raise RuntimeError("LiveKit not installed. Run: pip install livekit-agents")

        self.config = config or Config()

        # Load LiveKit configuration
        self.livekit_url = os.getenv('LIVEKIT_URL') or self.config.get('voice.livekit.url')
        self.api_key = os.getenv('LIVEKIT_API_KEY') or self.config.get('voice.livekit.api_key')
        self.api_secret = os.getenv('LIVEKIT_API_SECRET') or self.config.get('voice.livekit.api_secret')

        if not all([self.livekit_url, self.api_key, self.api_secret]):
            raise ValueError(
                "LiveKit credentials not configured. "
                "Set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in .env"
            )

        # Initialize LiveKit API client
        self.api_client = api.LiveKitAPI(
            url=self.livekit_url,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

        # Room state
        self.current_room: Optional[rtc.Room] = None
        self.current_room_name: Optional[str] = None
        self.participants: Dict[str, rtc.RemoteParticipant] = {}

        print(f"🔗 LiveKit manager initialized")
        print(f"   URL: {self.livekit_url}")

    async def create_room(
        self,
        room_name: Optional[str] = None,
        empty_timeout_seconds: int = 300,
        max_participants: int = 10
    ) -> str:
        """
        Create a new LiveKit room

        Args:
            room_name: Room name (generates one if None)
            empty_timeout_seconds: Auto-delete room after being empty for this long
            max_participants: Maximum number of participants

        Returns:
            Room name
        """
        # Generate room name if not provided
        if room_name is None:
            prefix = self.config.get('voice.livekit.room_prefix', 'dgm-voice-')
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            random_suffix = secrets.token_hex(4)
            room_name = f"{prefix}{timestamp}-{random_suffix}"

        try:
            # Create room via LiveKit API
            room_opts = api.CreateRoomRequest(
                name=room_name,
                empty_timeout=empty_timeout_seconds,
                max_participants=max_participants
            )

            room_info = await self.api_client.room.create_room(room_opts)

            print(f"✅ Created LiveKit room: {room_name}")
            print(f"   SID: {room_info.sid}")
            print(f"   Empty timeout: {empty_timeout_seconds}s")

            return room_name

        except Exception as e:
            print(f"❌ Error creating room: {e}")
            raise

    async def delete_room(self, room_name: str):
        """
        Delete a LiveKit room

        Args:
            room_name: Name of room to delete
        """
        try:
            await self.api_client.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            print(f"🗑️  Deleted room: {room_name}")

        except Exception as e:
            print(f"❌ Error deleting room: {e}")
            raise

    def generate_access_token(
        self,
        room_name: str,
        identity: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_hours: int = 24
    ) -> str:
        """
        Generate an access token for joining a room

        Args:
            room_name: Room name
            identity: Participant identity
            metadata: Optional metadata
            ttl_hours: Token time-to-live in hours

        Returns:
            JWT access token
        """
        # Create access token
        token = AccessToken(self.api_key, self.api_secret)

        # Set identity and metadata
        token.identity = identity
        if metadata:
            token.metadata = str(metadata)

        # Set grants (permissions)
        grants = VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        )
        token.add_grant(grants)

        # Set TTL
        token.ttl = timedelta(hours=ttl_hours)

        # Generate JWT
        jwt = token.to_jwt()

        print(f"🎫 Generated access token for {identity} (room: {room_name})")
        return jwt

    async def connect_to_room(
        self,
        room_name: str,
        identity: str = "voice-agent",
        token: Optional[str] = None
    ) -> rtc.Room:
        """
        Connect to a LiveKit room

        Args:
            room_name: Room name
            identity: Agent identity
            token: Access token (generates one if None)

        Returns:
            Connected Room object
        """
        # Generate token if not provided
        if token is None:
            token = self.generate_access_token(room_name, identity)

        # Create room instance
        room = rtc.Room()

        # Connect to room
        try:
            await room.connect(self.livekit_url, token)

            self.current_room = room
            self.current_room_name = room_name

            print(f"🎤 Connected to room: {room_name}")
            print(f"   Identity: {identity}")
            print(f"   Participants: {len(room.remote_participants)}")

            return room

        except Exception as e:
            print(f"❌ Error connecting to room: {e}")
            raise

    async def disconnect_from_room(self):
        """Disconnect from current room"""
        if self.current_room:
            await self.current_room.disconnect()
            self.current_room = None
            self.current_room_name = None
            self.participants.clear()
            print("👋 Disconnected from room")

    def on_participant_connected(self, callback: Callable):
        """
        Register callback for participant connection

        Args:
            callback: Function to call when participant connects
        """
        if not self.current_room:
            raise RuntimeError("Not connected to a room")

        @self.current_room.on("participant_connected")
        def _on_participant_connected(participant: rtc.RemoteParticipant):
            self.participants[participant.identity] = participant
            print(f"👤 Participant connected: {participant.identity}")
            callback(participant)

    def on_participant_disconnected(self, callback: Callable):
        """
        Register callback for participant disconnection

        Args:
            callback: Function to call when participant disconnects
        """
        if not self.current_room:
            raise RuntimeError("Not connected to a room")

        @self.current_room.on("participant_disconnected")
        def _on_participant_disconnected(participant: rtc.RemoteParticipant):
            if participant.identity in self.participants:
                del self.participants[participant.identity]
            print(f"👋 Participant disconnected: {participant.identity}")
            callback(participant)

    def on_track_subscribed(self, callback: Callable):
        """
        Register callback for track subscription

        Args:
            callback: Function to call when track is subscribed
        """
        if not self.current_room:
            raise RuntimeError("Not connected to a room")

        @self.current_room.on("track_subscribed")
        def _on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant
        ):
            print(f"🎧 Subscribed to track: {track.kind} from {participant.identity}")
            callback(track, publication, participant)

    async def list_rooms(self) -> list:
        """
        List all active rooms

        Returns:
            List of room info
        """
        try:
            rooms = await self.api_client.room.list_rooms(api.ListRoomsRequest())
            return list(rooms.rooms)

        except Exception as e:
            print(f"❌ Error listing rooms: {e}")
            return []

    async def get_room_info(self, room_name: str) -> Optional[Any]:
        """
        Get information about a room

        Args:
            room_name: Room name

        Returns:
            Room info or None if not found
        """
        try:
            rooms = await self.list_rooms()
            for room in rooms:
                if room.name == room_name:
                    return room
            return None

        except Exception as e:
            print(f"❌ Error getting room info: {e}")
            return None

    async def list_participants(self, room_name: str) -> list:
        """
        List participants in a room

        Args:
            room_name: Room name

        Returns:
            List of participant info
        """
        try:
            participants = await self.api_client.room.list_participants(
                api.ListParticipantsRequest(room=room_name)
            )
            return list(participants.participants)

        except Exception as e:
            print(f"❌ Error listing participants: {e}")
            return []

    def get_room_url(self, room_name: str, use_cloud: bool = True) -> str:
        """
        Get web URL to join room

        Args:
            room_name: Room name
            use_cloud: Use LiveKit Cloud URL (default: True)

        Returns:
            URL to join room
        """
        if use_cloud:
            # Parse cloud URL from livekit_url
            # wss://your-project.livekit.cloud -> https://your-project.livekit.cloud
            base_url = self.livekit_url.replace('wss://', 'https://').replace('ws://', 'http://')
            return f"{base_url}/rooms/{room_name}"
        else:
            # For local development
            return f"http://localhost:3000/rooms/{room_name}"

    async def cleanup(self):
        """Cleanup resources"""
        if self.current_room:
            await self.disconnect_from_room()

        # Close API client
        await self.api_client.aclose()

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"LiveKitManager("
            f"url={self.livekit_url}, "
            f"current_room={self.current_room_name}, "
            f"participants={len(self.participants)})"
        )
