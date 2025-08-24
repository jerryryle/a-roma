# Standard Library Imports
import asyncio
import logging
from typing import Any, Dict, Optional, Protocol, Set


class EventBroadcaster(Protocol):
    """Protocol for event broadcasting functions."""

    async def __call__(self, event: Dict[str, Any]) -> None: ...


class EventSystem:
    """Manages event queuing and broadcasting to WebSocket clients."""

    def __init__(self, logger: logging.Logger) -> None:
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._clients: Set[EventBroadcaster] = set()
        self._dispatcher_task: Optional[asyncio.Task[None]] = None
        self._logger = logger.getChild("event_system")

    def queue_event(self, event: Dict[str, Any]) -> None:
        """Add an event to the queue for broadcasting."""
        try:
            self._queue.put_nowait(event)
        except Exception as e:
            self._logger.error(f"Failed to queue event: {e}")

    def add_client(self, client: EventBroadcaster) -> None:
        """Add a WebSocket client to receive events."""
        self._clients.add(client)

    def remove_client(self, client: EventBroadcaster) -> None:
        """Remove a WebSocket client from receiving events."""
        self._clients.discard(client)

    async def start_dispatcher(self) -> None:
        """Start the event dispatcher task."""
        if self._dispatcher_task is None:
            self._dispatcher_task = asyncio.create_task(self._dispatch_events())

    async def stop_dispatcher(self) -> None:
        """Stop the event dispatcher task."""
        if self._dispatcher_task is not None:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass
            self._dispatcher_task = None

    async def _dispatch_events(self) -> None:
        """Continuously dispatch events to all connected clients."""
        while True:
            try:
                event = await self._queue.get()
                for client in list(self._clients):
                    try:
                        await client(event)
                    except Exception as e:
                        self._logger.error(f"Failed to broadcast event to client: {e}")
                        self._clients.discard(client)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in event dispatcher: {e}")
