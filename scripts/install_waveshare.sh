#!/bin/bash
# Install Waveshare e-Paper library manually
# Uses the official installation approach from the Waveshare manual

set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pil python3-numpy
pip install spidev

echo "Downloading Waveshare e-Paper Python library..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python"

# Create directory structure
mkdir -p waveshare_epd

# Download setup files
wget -q "$BASE_URL/setup.py" -O setup.py 2>/dev/null || {
    echo "Error: Failed to download setup.py"
    exit 1
}

# Download the lib directory structure
mkdir -p lib/waveshare_epd

# Download all necessary driver files
echo "Downloading e-Paper driver modules..."
cd lib/waveshare_epd

for file in __init__.py epdconfig.py epd7in3f.py; do
    echo "  Downloading $file..."
    wget -q "$BASE_URL/lib/waveshare_epd/$file" -O "$file" 2>/dev/null || {
        echo "Error: Failed to download $file"
        exit 1
    }
done

cd "$TEMP_DIR"

echo "Installing Waveshare e-Paper library..."
python setup.py install

echo "Cleaning up..."
rm -rf "$TEMP_DIR"

echo "Waveshare e-Paper library installed successfully!"
