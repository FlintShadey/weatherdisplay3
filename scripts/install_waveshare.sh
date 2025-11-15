#!/bin/bash
# Install Waveshare e-Paper library manually
# Downloads specific files via raw GitHub URLs to avoid git checkout issues

set -e

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python"

echo "Downloading Waveshare e-Paper Python library files..."

# Download the essential files
mkdir -p waveshare_epd
wget -q "$BASE_URL/setup.py" -O setup.py
wget -q "$BASE_URL/README.md" -O README.md

# Download the lib directory
mkdir -p lib/waveshare_epd
cd lib/waveshare_epd

# Download all the epd driver files we need
for file in __init__.py epdconfig.py epd7in3f.py; do
    wget -q "$BASE_URL/lib/waveshare_epd/$file" -O "$file"
done

cd "$TEMP_DIR"

echo "Installing Waveshare e-Paper Python library..."
python setup.py install

echo "Cleaning up..."
cd ~
rm -rf "$TEMP_DIR"

echo "Waveshare e-Paper library installed successfully!"
