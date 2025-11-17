#!/usr/bin/env python3
"""Test e-Paper display initialization with verbose debugging."""

import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Find waveshare library - check multiple possible locations
possible_paths = [
    '/home/flint/e-Paper/RaspberryPi_JetsonNano/python/lib',
    str(Path.home() / 'e-Paper' / 'RaspberryPi_JetsonNano' / 'python' / 'lib'),
    '/home/flint/.local/lib/python3.13/site-packages',
]

waveshare_found = False
for path in possible_paths:
    if Path(path).exists():
        sys.path.insert(0, path)
        try:
            import waveshare_epd
            waveshare_found = True
            print(f"Found waveshare_epd at: {path}")
            break
        except ImportError:
            continue

if not waveshare_found:
    print("ERROR: waveshare_epd not found in any of these locations:")
    for path in possible_paths:
        print(f"  - {path} (exists: {Path(path).exists()})")
    sys.exit(1)

print("=" * 60)
print("E-Paper Display Initialization Test")
print("=" * 60)

print("\n1. Importing waveshare_epd...")
try:
    from waveshare_epd import epd7in3f
    print("   ✓ Module imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

print("\n2. Creating EPD instance...")
try:
    epd = epd7in3f.EPD()
    print("   ✓ Instance created")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n3. Calling epd.init()...")
print("   (This is where it typically hangs if there's a problem)")
try:
    # Set a timeout by using signal or threading
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("init() took too long - likely stuck in ReadBusy()")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    epd.init()
    signal.alarm(0)  # Cancel alarm
    print("   ✓ Display initialized successfully!")
    
except TimeoutError as e:
    print(f"   ✗ TIMEOUT: {e}")
    print("\n   This means the display is stuck waiting for BUSY pin.")
    print("   Possible causes:")
    print("   - Ribbon cable not properly connected")
    print("   - SPI jumper in wrong position (should be 4-line SPI)")
    print("   - Display panel defective")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Testing display command...")
try:
    print("   Creating test image...")
    from PIL import Image
    img = Image.new('RGB', (800, 480), color=(255, 255, 255))
    
    print("   Converting to buffer...")
    buffer = epd.getbuffer(img)
    
    print("   Sending to display...")
    signal.alarm(30)  # 30 second timeout for display
    epd.display(buffer)
    signal.alarm(0)
    print("   ✓ Display updated successfully!")
    
except TimeoutError:
    print("   ✗ TIMEOUT during display()")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Putting display to sleep...")
try:
    epd.sleep()
    print("   ✓ Display in sleep mode")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n" + "=" * 60)
print("SUCCESS: Display is working correctly!")
print("=" * 60)
