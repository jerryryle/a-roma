# A-Roma Software Deployment Guide

This guide covers deploying the A-Roma software to a Raspberry Pi Zero 2 W.

## Prerequisites

### On Your Development Machine
- Python 3.13+
- SSH access to your Raspberry Pi
- `rsync` installed (usually available by default on macOS/Linux)

### On Your Raspberry Pi
- Raspberry Pi OS (latest)
- Internet connection
- SSH enabled

## Quick Deployment

### One-Command Deployment
```bash
# Deploy to default Pi (raspberrypi.local)
make deploy-pi

# Or specify custom Pi details
PI_USER=aroma PI_HOST=aroma.local make deploy-pi
```

## Configuration

### Environment Variables
You can customize the deployment by setting these environment variables:

```bash
export PI_USER="aroma"                    # SSH username (default: pi)
export PI_HOST="aroma.local"     # Pi hostname/IP (default: raspberrypi.local)
export PI_PATH="/opt/aroma-software"   # Installation path (default: /opt/aroma-software)
```

## Service Management

### Using Makefile Commands
```bash
# Check service status
ssh aroma@aroma.local 'cd /opt/aroma-software && make service-status'

# View logs
ssh aroma@aroma.local 'cd /opt/aroma-software && make logs'

# Stop service
ssh aroma@aroma.local 'cd /opt/aroma-software && make disable-service'

# Start service
ssh aroma@aroma.local 'cd /opt/aroma-software && make enable-service'
```

### Using systemctl Directly on Raspberry Pi
```bash
# Check status
sudo systemctl status aroma-software.service

# View logs
sudo journalctl -u aroma-software.service -f

# Restart service
sudo systemctl restart aroma-software.service
```

## Accessing the Application

Once deployed, you can access the application at:
- **Main Interface**: http://raspberrypi.local

## Troubleshooting

### Log Locations
- **Service logs**: `sudo journalctl -u aroma-software.service`
- **Application logs**: `/var/log/aroma.log` (configurable in main.py)
- **System logs**: `sudo journalctl -xe`
