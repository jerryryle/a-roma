# A-Roma Software

Software for a Raspberry Pi-based scent dispenser with 4 independently controlled fans.

Read about why this exists here: [ABOUT.md](/ABOUT.md)

## Features

- **4 Fan Control**: Independently control 4 fans via GPIO pins 12, 13, 18, and 19
- **Web Interface**: Modern, responsive web interface with real-time progress tracking
- **Real-time Updates**: WebSocket-based status updates every second
- **Flexible Timing**: Pre-set durations (30s, 1m, 5m) or custom durations via API
- **Progress Tracking**: Visual progress bars showing remaining time as percentage

## Hardware Requirements

- Raspberry Pi Zero 2 W (or compatible)
- 4 fans connected to GPIO pins 12, 13, 18, and 19
- Power supply for fans (GPIO pins are set HIGH to turn on fans)

## Installation

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Run the Server**:
   ```bash
   # Option 1: Using the installed script
   uv run aroma-software
   
   # Option 2: Direct execution
   python main.py
   ```

3. **Access the Web Interface**:
   Open your browser to `http://your-pi-ip:8000`

## GPIO Handling

The system automatically handles GPIO access:
- **On Raspberry Pi**: Uses the real `RPi.GPIO` library
- **On Development Machines**: Uses `fake-rpigpio` for testing without hardware

This allows you to develop and test the software on any machine, while it will work seamlessly on the actual Raspberry Pi hardware.

## API Endpoints

### Fan Control
- `POST /api/fan/{fan_id}/turn_on?duration_seconds={seconds}` - Turn on a fan
- `POST /api/fan/{fan_id}/turn_off` - Turn off a fan immediately
- `GET /api/fan/status` - Get current status of all fans

### WebSocket
- `WS /api/ws` - Real-time status updates

## Web Interface

The web interface provides:
- 4 fan control panels with preset duration buttons
- Real-time progress bars showing remaining time
- Connection status indicator
- Responsive design that works on mobile and desktop

## Fan Mapping

- **Fan 0**: GPIO 12 (Blue theme)
- **Fan 1**: GPIO 13 (Green theme)  
- **Fan 2**: GPIO 18 (Purple theme)
- **Fan 3**: GPIO 19 (Orange theme)

## Development

### Code Quality
The project uses:
- **MyPy** for type checking
- **Flake8** for linting
- **Black** for code formatting

### Running Tests
```bash
uv run pytest
```

### Type Checking
```bash
uv run mypy src/
```

### Linting
```bash
uv run flake8 src/
```

## Architecture

- **FastAPI**: REST API and WebSocket server
- **Event System**: Asynchronous event broadcasting
- **Fan Controller**: GPIO management and timing control
- **Static HTML**: Modern web interface with Tailwind CSS

## License

BSD-3-Clause