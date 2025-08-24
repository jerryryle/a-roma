# Standard Library Imports
import asyncio
import logging
from typing import Any, Dict, Optional

import RPi.GPIO as GPIO

# Local Application Imports
from aroma_software.event_system import EventSystem


class FanController:
    """Manages 4 fan GPIO pins with runtime tracking and progress broadcasting."""

    # GPIO pins for the 4 fans
    FAN_PINS = [19, 13, 12, 18]

    def __init__(self, event_system: EventSystem, logger: logging.Logger) -> None:
        """Initialize the fan controller.

        Args:
            event_system: Event system for broadcasting progress updates
            logger: Logger instance for debugging and error reporting
        """
        self.event_system = event_system
        self.logger = logger.getChild("fan_controller")

        # Track fan states: {fan_id: {"remaining_seconds": int, "total_seconds": int, "gpio_on": bool}}
        # Initialize all fans with 0 remaining seconds (off)
        self.fan_states = {
            fan_id: {"remaining_seconds": 0, "total_seconds": 0, "gpio_on": False}
            for fan_id in range(4)
        }

        # Lock for thread-safe access to fan_states
        self._fan_states_lock = asyncio.Lock()

        # Queue for fan control events
        self._fan_events: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

        # Background task for progress updates
        self._fan_management_task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Start the background task that manages fans and broadcasts progress."""
        if self._fan_management_task is None:
            # Reset fan states
            async with self._fan_states_lock:
                for fan_id in range(4):
                    self.fan_states[fan_id] = {
                        "remaining_seconds": 0,
                        "total_seconds": 0,
                        "gpio_on": False,
                    }

            # Setup GPIO pins
            self._setup_gpio()

            # Start the background task
            self._fan_management_task = asyncio.create_task(self._manage_fans())
            self.logger.info("Started fan management")

    async def stop(self) -> None:
        """Stop the background task and clean up GPIO resources."""
        if self._fan_management_task is not None:
            self._fan_management_task.cancel()
            try:
                await self._fan_management_task
            except asyncio.CancelledError:
                pass
            self._fan_management_task = None
            self.logger.info("Stopped fan management")

        # Clean up GPIO resources
        try:
            # Turn off all fans
            for fan_id in range(4):
                GPIO.output(self.FAN_PINS[fan_id], GPIO.LOW)

            # Clean up GPIO
            GPIO.cleanup()

            self.logger.info("Fan controller cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def fan_on(self, fan_id: int, duration_seconds: int) -> None:
        """Set a fan to run for a given duration.

        Args:
            fan_id: Fan number (0-3)
            duration_seconds: How long to run the fan in seconds
        """
        if fan_id not in range(4):
            raise ValueError(f"Invalid fan_id: {fan_id}. Must be 0-3")

        if duration_seconds <= 0:
            raise ValueError(f"Duration must be positive, got: {duration_seconds}")

        # Queue the fan control event
        await self._fan_events.put(
            {"type": "turn_on", "fan_id": fan_id, "duration_seconds": duration_seconds}
        )

    async def fan_off(self, fan_id: int) -> None:
        """Turn off a specific fan immediately.

        Args:
            fan_id: Fan number (0-3)
        """
        if fan_id not in range(4):
            raise ValueError(f"Invalid fan_id: {fan_id}. Must be 0-3")

        # Queue the fan control event
        await self._fan_events.put({"type": "turn_off", "fan_id": fan_id})

    async def get_fan_status(self) -> Dict[str, Any]:
        """Get current status of all fans.

        Returns:
            Dictionary with fan status information
        """
        async with self._fan_states_lock:
            status = {}
            for fan_id in range(4):
                state = self.fan_states[fan_id]
                status[f"fan_{fan_id}"] = {
                    "remaining_seconds": state["remaining_seconds"],
                    "total_seconds": state["total_seconds"],
                }

            return status

    async def _manage_fans(self) -> None:
        """Background task that manages fan GPIO control, timing, and broadcasts status updates."""
        while True:
            try:
                # Wait for either 1 second or a new event
                try:
                    event = await asyncio.wait_for(self._fan_events.get(), timeout=1.0)
                    # Process the received event
                    await self._process_fan_event(event)
                except asyncio.TimeoutError:
                    # Normal 1-second timeout, no event received
                    pass

                # Process any remaining events in the queue
                while not self._fan_events.empty():
                    event = await self._fan_events.get()
                    await self._process_fan_event(event)

                async with self._fan_states_lock:
                    # Manage GPIO state for fans that need to be turned on
                    for fan_id, state in self.fan_states.items():
                        if not state["gpio_on"] and state["remaining_seconds"] > 0:
                            # Turn on the fan GPIO
                            pin = self.FAN_PINS[fan_id]
                            GPIO.output(pin, GPIO.HIGH)
                            state["gpio_on"] = True
                            self.logger.info(f"Turned on fan {fan_id} (GPIO {pin})")

                    # Update remaining time for active fans and turn off finished ones
                    for fan_id, state in self.fan_states.items():
                        state["remaining_seconds"] -= 1
                        if state["gpio_on"] and state["remaining_seconds"] <= 0:
                            state["remaining_seconds"] = 0
                            # Turn off the fan GPIO
                            pin = self.FAN_PINS[fan_id]
                            GPIO.output(pin, GPIO.LOW)
                            state["gpio_on"] = False
                            self.logger.info(f"Turned off fan {fan_id} (GPIO {pin})")

                # Broadcast current status (outside the lock to avoid blocking)
                status = await self.get_fan_status()
                self.event_system.queue_event({"type": "fan_status", "data": status})

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in fan management: {e}")
                await asyncio.sleep(1)  # Continue despite errors

    async def _process_fan_event(self, event: Dict[str, Any]) -> None:
        """Process a fan control event."""
        async with self._fan_states_lock:
            if event["type"] == "turn_on":
                fan_id = event["fan_id"]
                duration_seconds = event["duration_seconds"]
                self.fan_states[fan_id]["remaining_seconds"] = duration_seconds
                self.fan_states[fan_id]["total_seconds"] = duration_seconds

            elif event["type"] == "turn_off":
                fan_id = event["fan_id"]
                self.fan_states[fan_id]["remaining_seconds"] = 0

    def _setup_gpio(self) -> None:
        """Setup GPIO pins for fan control."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Setup all fan pins as outputs and turn them off
            for pin in self.FAN_PINS:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

            self.logger.info("GPIO pins initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup GPIO: {e}")
            raise
