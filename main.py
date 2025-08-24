#!/usr/bin/env python3

# Standard Library Imports
import argparse
import os
import platform
import sys
from argparse import Namespace

import uvicorn

if platform.system() == "Darwin":  # macOS
    import fake_rpi

    sys.modules['RPi'] = fake_rpi.RPi  # Fake RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO  # Fake GPIO
    sys.modules['smbus'] = fake_rpi.smbus  # Fake smbus (I2C)

    _DEFAULT_LOG_FILE_PATH = os.path.expanduser("~/Library/Logs/aroma.log")
else:
    _DEFAULT_LOG_FILE_PATH = "/var/log/aroma.log"

# Local Application Imports
from aroma_software.api import create_app


def parse_args() -> Namespace:

    parser = argparse.ArgumentParser(description='A-Roma API Server')
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        help=f'Path to log file (default: {_DEFAULT_LOG_FILE_PATH})',
    )
    args = parser.parse_args()
    args.log_file = args.log_file or _DEFAULT_LOG_FILE_PATH
    return args


def main(log_file_path: str) -> None:
    app = create_app(log_file_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    args = parse_args()
    main(args.log_file)
