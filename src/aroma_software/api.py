# Standard Library Imports
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

# Third Party Imports
from fastapi import APIRouter, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Local Application Imports
from aroma_software.event_system import EventSystem
from aroma_software.fan_controller import FanController
from aroma_software.logger_setup import setup_logger
from aroma_software.music_controller import MusicController

AROMA_PATH = "static/aroma.html"
ESCALATE_PATH = "static/aroma_escalate.html"


def create_app(log_file_path: str) -> FastAPI:
    """Create and configure the FastAPI application."""
    logger = setup_logger(log_file_path)
    event_system = EventSystem(logger)
    fan_controller = FanController(event_system, logger)
    music_controller = MusicController(event_system, logger)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application startup and shutdown."""
        # Startup
        await event_system.start_dispatcher()
        await fan_controller.start()
        await music_controller.start()

        yield

        # Shutdown
        await music_controller.stop()
        await fan_controller.stop()
        await event_system.stop_dispatcher()

    app = FastAPI(title="A-Roma Software API", lifespan=lifespan)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions."""
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    # Create API router
    api_router = APIRouter(prefix="/api")

    @api_router.post("/fan/{fan_id}/on")
    async def fan_on(fan_id: int, duration_seconds: int) -> Dict[str, Any]:
        """Turn on a specific fan for a given duration."""
        try:
            await fan_controller.fan_on(fan_id, duration_seconds)
            return {
                "success": True,
                "message": f"Fan {fan_id} turned on for {duration_seconds} seconds",
            }
        except ValueError as e:
            raise ValueError(str(e))

    @api_router.post("/fan/{fan_id}/off")
    async def fan_off(fan_id: int) -> Dict[str, Any]:
        """Turn off a specific fan immediately."""
        try:
            await fan_controller.fan_off(fan_id)
            return {"success": True, "message": f"Fan {fan_id} turned off"}
        except ValueError as e:
            raise ValueError(str(e))

    @api_router.get("/fan/status")
    async def get_fan_status() -> Dict[str, Any]:
        """Get the current status of all fans."""
        return await fan_controller.get_fan_status()

    @api_router.post("/music/start/{song_id}")
    async def music_start(song_id: str) -> Dict[str, Any]:
        """Start playing a specific song."""
        try:
            await music_controller.music_start(song_id)
            return {
                "success": True,
                "message": f"Started playing song: {song_id}",
            }
        except Exception as e:
            raise ValueError(str(e))

    @api_router.post("/music/stop")
    async def music_stop() -> Dict[str, Any]:
        """Stop the currently playing music."""
        try:
            await music_controller.music_stop()
            return {"success": True, "message": "Music stopped"}
        except Exception as e:
            raise ValueError(str(e))

    @api_router.get("/music/status")
    async def get_music_status() -> Dict[str, Any]:
        """Get the current music status."""
        return await music_controller.get_music_status()

    @api_router.post("/music/volume")
    async def set_music_volume(request: Request) -> Dict[str, Any]:
        """Set the music volume.

        Expected JSON body: {"volume": 0.7}
        """
        try:
            body = await request.json()
            volume = body.get("volume")

            if volume is None:
                raise ValueError("Volume parameter is required")

            await music_controller.set_volume(volume)
            return {
                "success": True,
                "message": f"Volume set to {volume}",
            }
        except ValueError as e:
            raise ValueError(str(e))

    @api_router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time service status updates."""
        await websocket.accept()
        try:

            async def broadcast(event: Dict[str, Any]) -> None:
                await websocket.send_json(event)

            event_system.add_client(broadcast)
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    if message.get("type") == "subscribe":
                        # Handle subscription if needed
                        pass
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {data}")
        except WebSocketDisconnect:
            logger.debug("WebSocket client disconnected")
        finally:
            event_system.remove_client(broadcast)

    # Mount API router
    app.include_router(api_router)

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        with open(AROMA_PATH) as f:
            return HTMLResponse(content=f.read())

    @app.get("/escalate", response_class=HTMLResponse)
    async def escalate() -> HTMLResponse:
        with open(ESCALATE_PATH) as f:
            return HTMLResponse(content=f.read())

    return app
