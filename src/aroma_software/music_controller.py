# Standard Library Imports
import asyncio
import logging
import os
from typing import Any, Dict, Optional

import pygame

# Local Application Imports
from aroma_software.event_system import EventSystem


class MusicController:
    """Manages music playback using PyGame with status broadcasting."""

    def __init__(self, event_system: EventSystem, logger: logging.Logger) -> None:
        """Initialize the music controller.

        Args:
            event_system: Event system for broadcasting status updates
            logger: Logger instance for debugging and error reporting
        """
        self.event_system = event_system
        self.logger = logger.getChild("music_controller")

        # Music state tracking
        self.currently_playing: Optional[str] = None
        self.music_directory = "static/music"  # Directory containing MP3 files

        # Song ID to filename mapping
        self.song_mapping = {
            "1": "Tarantella_Napoletana.mp3",
            "2": "Mambo_Italiano.mp3",
            "3": "Luna_Mezzo_Mare.mp3",
            "4": "Thats_Amore.mp3",
        }

        # Lock for thread-safe access to music state
        self._music_state_lock = asyncio.Lock()

        # Queue for music control events
        self._music_events: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

        # Background task for status updates
        self._music_management_task: Optional[asyncio.Task[None]] = None

        # Initialize PyGame mixer
        self._setup_pygame()

    def _setup_pygame(self) -> None:
        """Setup PyGame mixer for audio playback."""
        try:
            pygame.mixer.init()
            self.logger.info("PyGame mixer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize PyGame mixer: {e}")
            raise

    async def start(self) -> None:
        """Start the background task that manages music and broadcasts status."""
        if self._music_management_task is None:
            # Reset music state
            async with self._music_state_lock:
                self.currently_playing = None

            # Start the background task
            self._music_management_task = asyncio.create_task(self._manage_music())
            self.logger.info("Started music management")

    async def stop(self) -> None:
        """Stop the background task and clean up music resources."""
        if self._music_management_task is not None:
            self._music_management_task.cancel()
            try:
                await self._music_management_task
            except asyncio.CancelledError:
                pass
            self._music_management_task = None
            self.logger.info("Stopped music management")

        # Clean up music resources
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.logger.info("Music controller cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def music_start(self, song_id: str) -> None:
        """Start playing a specific song.

        Args:
            song_id: Song identifier that maps to a filename in the song_mapping
        """
        if song_id not in self.song_mapping:
            raise ValueError(
                f"Invalid song_id: {song_id}. Available songs: {list(self.song_mapping.keys())}"
            )

        # Queue the music control event
        await self._music_events.put({"type": "start", "song_id": song_id})

    async def music_stop(self) -> None:
        """Stop the currently playing music."""
        # Queue the music control event
        await self._music_events.put({"type": "stop"})

    async def get_music_status(self) -> Dict[str, Any]:
        """Get current music status.

        Returns:
            Dictionary with music status information
        """
        async with self._music_state_lock:
            return {
                "currently_playing": self.currently_playing,
            }

    async def _manage_music(self) -> None:
        """Background task that manages music playback and broadcasts status updates."""
        while True:
            try:
                # Wait for either 1 second or a new event
                try:
                    event = await asyncio.wait_for(
                        self._music_events.get(), timeout=1.0
                    )
                    # Process the received event
                    await self._process_music_event(event)
                except asyncio.TimeoutError:
                    # Normal 1-second timeout, no event received
                    pass

                # Process any remaining events in the queue
                while not self._music_events.empty():
                    event = await self._music_events.get()
                    await self._process_music_event(event)

                # Check if music has finished playing
                if self.currently_playing and not pygame.mixer.music.get_busy():
                    async with self._music_state_lock:
                        self.currently_playing = None
                    self.logger.info("Music finished playing")

                # Broadcast current status (outside the lock to avoid blocking)
                status = await self.get_music_status()
                self.event_system.queue_event({"type": "music_status", "data": status})

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in music management: {e}")
                await asyncio.sleep(1)  # Continue despite errors

    async def _process_music_event(self, event: Dict[str, Any]) -> None:
        """Process a music control event."""
        async with self._music_state_lock:
            if event["type"] == "start":
                song_id = event["song_id"]
                await self._play_song(song_id)

            elif event["type"] == "stop":
                await self._stop_song()

    async def _play_song(self, song_id: str) -> None:
        """Play a specific song."""
        try:
            # Get the filename from the song mapping
            filename = self.song_mapping[song_id]

            # Construct the full path to the MP3 file
            song_path = os.path.join(self.music_directory, filename)

            if not os.path.exists(song_path):
                self.logger.error(f"Song file not found: {song_path}")
                return

            # Stop any currently playing music
            pygame.mixer.music.stop()

            # Load and play the new song
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()

            # Update the currently playing state
            self.currently_playing = song_id

            self.logger.info(f"Started playing: {song_id} ({filename})")

        except Exception as e:
            self.logger.error(f"Error playing song {song_id}: {e}")

    async def _stop_song(self) -> None:
        """Stop the currently playing song."""
        try:
            pygame.mixer.music.stop()
            self.currently_playing = None
            self.logger.info("Music stopped")
        except Exception as e:
            self.logger.error(f"Error stopping music: {e}")
