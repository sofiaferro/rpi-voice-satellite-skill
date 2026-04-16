---
name: rpi-voice-satellite
description: Build voice assistants and satellites using Raspberry Pi Zero 2 W with ReSpeaker 2-Mic Pi HAT. Use this skill whenever the user mentions Raspberry Pi voice assistant, ReSpeaker HAT, Wyoming satellite, voice satellite, Pi Zero voice control, wake word detection on Pi, Home Assistant voice, Picovoice on Raspberry Pi, seeed-voicecard drivers, or any DIY voice-controlled device using a Pi Zero. Also trigger for troubleshooting audio issues with ReSpeaker, LED control on voice HATs, or integrating Pi-based voice devices with smart home systems.
---

# Raspberry Pi Zero 2 W + ReSpeaker 2-Mic Voice Satellite

This skill covers building local voice assistants and satellites using the Raspberry Pi Zero 2 W with the ReSpeaker 2-Mic Pi HAT. It includes driver installation, audio configuration, wake word detection, Home Assistant integration, LED feedback, and troubleshooting.

## What is Wyoming?

**Wyoming** is a lightweight peer-to-peer protocol created by the Rhasspy project that lets voice components communicate over a network. It's named arbitrarily (like Bluetooth) - the name doesn't mean anything specific.

Components that speak Wyoming:
- **Satellites** - devices with mic/speaker that send/receive audio (your Pi Zero)
- **Wake word detectors** - listen for trigger phrases like "ok nabu" or "hey jarvis"
- **Speech-to-text engines** - transcribe spoken audio to text
- **Text-to-speech engines** - convert text responses to spoken audio
- **Intent handlers** - process commands and take actions

**Why it matters:** Home Assistant natively supports Wyoming, so your Pi automatically shows up as a discoverable voice device. Your Pi becomes a "satellite" microphone/speaker that connects to Home Assistant for processing.

**Alternative approach:** Picovoice does everything locally on the Pi itself - no server needed, but more limited functionality.

## Hardware Overview

**Required Components:**
- Raspberry Pi Zero 2 W (64-bit capable, required for audio enhancements)
- ReSpeaker 2-Mic Pi HAT (v1.0 or v2.0)
- MicroSD card (16GB+ recommended)
- 5V 2.5A power supply (via micro USB)
- Speaker (3.5mm jack or JST 2.0 connector)

**ReSpeaker 2-Mic HAT Features:**
- 2x MEMS microphones (for stereo capture)
- WM8960 low-power stereo codec
- 3x APA102 RGB LEDs (SPI-controlled)
- 1x user button (GPIO17)
- 3.5mm audio jack + JST speaker output
- Grove I2C and GPIO connectors

## Quick Start Decision Tree

Choose your path based on what you want to build:

| Goal | Recommended Approach | Reference |
|------|---------------------|-----------|
| Home Assistant voice satellite | Wyoming Satellite | See `references/wyoming-setup.md` |
| Custom wake word device | Picovoice Porcupine | See `references/picovoice-setup.md` |
| General voice recording/playback | Direct ALSA usage | Continue below |
| Troubleshooting audio issues | Diagnostics | See `references/troubleshooting.md` |

## Initial Setup (All Approaches)

### 1. Flash Raspberry Pi OS

**CRITICAL: Use 64-bit OS for audio enhancements and wake word detection.**

1. Download Raspberry Pi Imager
2. Choose OS → Raspberry Pi OS (other) → **Raspberry Pi OS (64-bit) Lite**
3. Configure settings:
   - Set hostname (e.g., `voice-satellite`)
   - Enable SSH
   - Set username/password
   - Configure WiFi
   - Set locale/timezone

4. Flash and boot the Pi (do NOT attach HAT yet)

### 2. Initial System Update

```bash
# Connect via SSH
ssh pi@voice-satellite.local

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y git python3-venv python3-pip \
    libasound2-dev portaudio19-dev libatlas-base-dev
```

### 3. Install ReSpeaker Drivers

**Power off the Pi before attaching the HAT:**
```bash
sudo shutdown -h now
```

Attach the ReSpeaker 2-Mic HAT, ensuring pins align properly. Power back on and reconnect via SSH.

**Method A: Wyoming Satellite Driver Script (Recommended)**
```bash
git clone https://github.com/rhasspy/wyoming-satellite.git
cd wyoming-satellite
sudo bash etc/install-respeaker-drivers.sh
# This takes 20-60 minutes on Pi Zero 2 W
sudo reboot
```

**Method B: Seeed Official Drivers**
```bash
git clone https://github.com/respeaker/seeed-voicecard
cd seeed-voicecard

# For 64-bit OS:
sudo ./install_arm64.sh

# For 32-bit OS (not recommended):
# sudo ./install.sh

sudo reboot
```

**Method C: Device Tree Overlay (Newer Kernels)**
```bash
git clone https://github.com/Seeed-Studio/seeed-linux-dtoverlays.git
cd seeed-linux-dtoverlays/
make overlays/rpi/respeaker-2mic-v1_0-overlay.dtbo
sudo cp overlays/rpi/respeaker-2mic-v1_0-overlay.dtbo /boot/firmware/overlays/respeaker-2mic-v1_0.dtbo
echo "dtoverlay=respeaker-2mic-v1_0" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

### 4. Verify Audio Device

After reboot, verify the sound card is detected:

```bash
# List playback devices
aplay -l

# Expected output should include:
# card X: seeed2micvoicec [seeed-2mic-voicecard], device 0: ...

# List recording devices
arecord -l

# Note the card number (usually 0, 1, 2, or 3)
```

The device name should be `seeed2micvoicec` or `seeed-2mic-voicecard`.

### 5. Test Audio

```bash
# Record 5 seconds of audio
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t wav -d 5 test.wav

# Play it back
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 test.wav

# Or for mono playback:
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE test.wav
```

### 6. Adjust Volume with alsamixer

```bash
alsamixer
# Press F6 to select seeed-2mic-voicecard
# Adjust Speaker/Headphone volume (playback)
# Adjust Capture/ADC volume (recording)
# Press ESC to exit
```

## LED Control (APA102)

The ReSpeaker 2-Mic HAT has 3 APA102 RGB LEDs controlled via SPI.

```python
#!/usr/bin/env python3
"""Simple APA102 LED control for ReSpeaker 2-Mic HAT"""

import spidev
import time

class APA102:
    def __init__(self, num_leds=3):
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 8000000
        
    def set_pixel(self, index, red, green, blue, brightness=31):
        """Set a single LED color (0-255 for RGB, 0-31 for brightness)"""
        self.pixels = getattr(self, 'pixels', [(0,0,0,0)] * self.num_leds)
        self.pixels[index] = (brightness, blue, green, red)
        
    def show(self):
        """Update the LEDs"""
        # Start frame: 32 bits of zeros
        data = [0x00] * 4
        
        # LED frames
        for brightness, b, g, r in self.pixels:
            data.append(0xE0 | (brightness & 0x1F))
            data.append(b)
            data.append(g)
            data.append(r)
        
        # End frame
        data.extend([0xFF] * 4)
        self.spi.xfer2(data)
        
    def clear(self):
        """Turn off all LEDs"""
        self.pixels = [(0,0,0,0)] * self.num_leds
        self.show()
        
    def close(self):
        self.spi.close()

# Example usage
if __name__ == "__main__":
    leds = APA102(num_leds=3)
    
    # Set LED 0 to red, LED 1 to green, LED 2 to blue
    leds.set_pixel(0, 255, 0, 0)
    leds.set_pixel(1, 0, 255, 0)
    leds.set_pixel(2, 0, 0, 255)
    leds.show()
    
    time.sleep(2)
    leds.clear()
    leds.close()
```

## User Button (GPIO17)

```python
#!/usr/bin/env python3
"""User button detection on ReSpeaker 2-Mic HAT"""

import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)

try:
    while True:
        if GPIO.input(BUTTON_PIN) == 0:  # Button pressed (active low)
            print("Button pressed!")
            while GPIO.input(BUTTON_PIN) == 0:
                time.sleep(0.01)  # Debounce
            print("Button released!")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
```

## Reference Documentation

This skill includes the following reference materials:

### Official Documentation (verbatim from source)
- `references/official-docs/seeed-respeaker-2mic-docs.md` - Complete Seeed Studio wiki for ReSpeaker 2-Mic HAT (source: wiki.seeedstudio.com)
- `references/official-docs/wyoming-satellite-docs.md` - Complete Wyoming Satellite tutorial and README (source: github.com/rhasspy/wyoming-satellite)

### Quick Reference Guides
- `references/wyoming-setup.md` - Condensed Wyoming Satellite setup guide
- `references/picovoice-setup.md` - Picovoice/Porcupine wake word setup guide
- `references/troubleshooting.md` - Common issues and solutions

### Scripts
- `scripts/diagnose_respeaker.sh` - Diagnostic script for hardware/driver issues
- `scripts/led_demo.py` - APA102 LED control demonstration

## Quick Reference: Audio Device Strings

For ReSpeaker 2-Mic HAT, use these device strings:

```bash
# Recording (16kHz mono, required for most speech engines)
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw

# Playback (22.05kHz mono, common for TTS output)
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw

# Alternative device names (check with aplay -L):
# plughw:CARD=seeed2micvoicec,DEV=0
# hw:seeed2micvoicec
# default (if configured in /etc/asound.conf)
```

## Common Issues Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| `No such device` | Check HAT seated properly, rerun driver install |
| No sound on speaker | Run `alsamixer`, unmute and raise Speaker volume |
| Quiet recording | Run `alsamixer`, raise Capture/ADC volume to 80%+ |
| Driver install fails | Ensure kernel headers match: `sudo apt install raspberrypi-kernel-headers` |
| HAT v2.0 not detected | May need different dtoverlay, check troubleshooting guide |

See `references/troubleshooting.md` for detailed diagnostics.
