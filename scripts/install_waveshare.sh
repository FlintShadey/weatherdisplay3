#!/bin/bash
# Install Waveshare e-Paper library manually
# This avoids pip's git clone issues with the repo

set -e

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "Cloning Waveshare e-Paper repository..."
git clone --depth 1 https://github.com/waveshare/e-Paper.git

echo "Installing Waveshare e-Paper Python library..."
cd e-Paper/RaspberryPi_JetsonNano/python
python setup.py install

echo "Cleaning up..."
cd ~
rm -rf "$TEMP_DIR"

echo "Waveshare e-Paper library installed successfully!"
