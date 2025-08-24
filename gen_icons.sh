#!/bin/sh
# This script requires a modern version of ImageMagick installed (v7 or later)

# Stop execution of script if a command or pipeline has an error
set -e

# Set a default icon source file if none passed in environment.
# This source file should have fairly large dimensions such as 600x600
ICON_SOURCE="${ICON_SOURCE:-static/favicon.png}"

echo "Creating favicon.ico..."
magick ${ICON_SOURCE} -define icon:auto-resize=256,128,64,48,32,24,16 static/favicon.ico

echo "Creating PNG icons..."
magick ${ICON_SOURCE} -units PixelsPerInch -density 300 -resize 16x16 static/favicon-16x16.png
magick ${ICON_SOURCE} -units PixelsPerInch -density 300 -resize 32x32 static/favicon-32x32.png
magick ${ICON_SOURCE} -units PixelsPerInch -density 300 -resize 180x180 static/apple-touch-icon.png
magick ${ICON_SOURCE} -units PixelsPerInch -density 300 -resize 192x192 static/android-chrome-192x192.png
magick ${ICON_SOURCE} -units PixelsPerInch -density 300 -resize 512x512 static/android-chrome-512x512.png
echo "Done!"
