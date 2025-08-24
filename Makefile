# A-Roma Software Makefile
# Targets for development, testing, and Raspberry Pi deployment

# Default configuration for Raspberry Pi deployment
PI_USER ?= aroma
PI_HOST ?= aroma.local
PI_PATH ?= /opt/aroma-software

.PHONY: help install install-dev test lint format clean run run-dev deploy-pi update-deploy

# Default target
help:
	@echo "A-Roma Software - Available targets:"
	@echo ""
	@echo "Raspberry Pi Deployment:"
	@echo "  deploy-pi      - Deploy to Raspberry Pi"
	@echo "  sync-deploy    - Sync changed files to Raspberry Pi"
	@echo ""
	@echo "System Service:"
	@echo "  install-service - Install systemd service"
	@echo "  enable-service  - Enable and start service"
	@echo "  disable-service - Stop and disable service"
	@echo "  service-status  - Check service status"

# System service management
install-service:
	@echo "Installing systemd service..."
	@sudo cp aroma-software.service /etc/systemd/system/
	@sudo systemctl daemon-reload
	@echo "Service installed!"

enable-service:
	@echo "Enabling and starting service..."
	sudo systemctl enable aroma-software.service
	sudo systemctl start aroma-software.service
	@echo "Service enabled and started!"

disable-service:
	@echo "Stopping and disabling service..."
	sudo systemctl stop aroma-software.service
	sudo systemctl disable aroma-software.service
	@echo "Service stopped and disabled!"

service-status:
	@echo "Service status:"
	sudo systemctl status aroma-software.service

# Log management
logs:
	@echo "Showing service logs..."
	sudo journalctl -u aroma-software.service -f

# Raspberry Pi deployment
deploy-pi:
	@echo "Deploying to Raspberry Pi..."
	@echo "Target: $(PI_USER)@$(PI_HOST):$(PI_PATH)"
	@echo ""
	@echo "Testing connection to Raspberry Pi..."
	@ping -c 1 $(PI_HOST) > /dev/null 2>&1 || (echo "Cannot reach $(PI_HOST). Please check your network connection." && exit 1)
	@echo "Deploying files to Raspberry Pi..."
	@ssh $(PI_USER)@$(PI_HOST) "sudo mkdir -p $(PI_PATH) && sudo chown $(PI_USER):$(PI_USER) $(PI_PATH)"
	@rsync -avz --delete \
		--exclude='.venv' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='.git' \
		--exclude='.vscode' \
		--exclude='*.log' \
		./ $(PI_USER)@$(PI_HOST):$(PI_PATH)/
	@echo "Setting up and deploying..."
	@ssh $(PI_USER)@$(PI_HOST) "cd $(PI_PATH) && sudo apt-get update && sudo apt-get install -y python3-pip python3-venv git python3-pygame python3-rpi.gpio && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -e . && pip install RPi.GPIO && make install-service && make enable-service && make service-status"
	@echo "Deployment complete!"
	@echo ""
	@echo "Your A-Roma software is now running on:"
	@echo "  http://$(PI_HOST)"
	@echo ""
	@echo "Useful commands:"
	@echo "  ssh $(PI_USER)@$(PI_HOST) 'cd $(PI_PATH) && make service-status'  # Check status"
	@echo "  ssh $(PI_USER)@$(PI_HOST) 'cd $(PI_PATH) && make logs'            # View logs"
	@echo "  ssh $(PI_USER)@$(PI_HOST) 'cd $(PI_PATH) && make disable-service' # Stop service"

# Quick file sync (no setup/installation)
sync-deploy:
	@echo "Syncing files to Raspberry Pi..."
	@echo "Target: $(PI_USER)@$(PI_HOST):$(PI_PATH)"
	@rsync -avz --delete \
		--exclude='.venv' \
		--exclude='venv' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='.git' \
		--exclude='.vscode' \
		--exclude='*.log' \
		./ $(PI_USER)@$(PI_HOST):$(PI_PATH)/
	@echo "File sync complete!"
