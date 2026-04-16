# Picovoice Wake Word Setup

This guide covers using Picovoice Porcupine for wake word detection on Raspberry Pi Zero 2 W with ReSpeaker 2-Mic HAT. Picovoice offers highly accurate, low-latency wake word detection that runs efficiently even on Pi Zero.

## Table of Contents
1. [Overview](#overview)
2. [Getting Access Key](#getting-access-key)
3. [Python Setup](#python-setup)
4. [Basic Wake Word Detection](#basic-wake-word-detection)
5. [ReSpeaker Integration](#respeaker-integration)
6. [Custom Wake Words](#custom-wake-words)
7. [LED Feedback](#led-feedback)
8. [Speech-to-Intent with Rhino](#speech-to-intent-with-rhino)

---

## Overview

Picovoice provides several voice AI engines:

| Engine | Purpose | Pi Zero Support |
|--------|---------|-----------------|
| **Porcupine** | Wake word detection | ✅ Yes |
| **Rhino** | Speech-to-Intent | ✅ Yes |
| **Leopard** | Speech-to-Text (batch) | Pi 3/4/5 only |
| **Cheetah** | Speech-to-Text (streaming) | Pi 3/4/5 only |
| **Cobra** | Voice Activity Detection | ✅ Yes |

For Pi Zero 2 W, Porcupine and Rhino are the primary options.

## Getting Access Key

Picovoice requires a free Access Key:

1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Sign up for a free account (no credit card required)
3. Copy your **AccessKey** from the dashboard
4. Save it securely - you'll need it in your code

**Free tier limits:**
- Unlimited devices for development
- Built-in wake words (Alexa, Computer, Jarvis, etc.)
- Custom wake words for personal use

## Python Setup

```bash
# Install system dependencies
sudo apt-get install -y python3-pip python3-venv portaudio19-dev

# Create project directory
mkdir -p ~/picovoice-project
cd ~/picovoice-project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Picovoice packages
pip install pvporcupine pvporcupinedemo pyaudio
```

## Basic Wake Word Detection

### Built-in Wake Words

Porcupine includes these built-in wake words:
- alexa, americano, blueberry, bumblebee
- computer, grapefruit, grasshopper, hey google
- hey siri, jarvis, ok google, picovoice
- porcupine, terminator

```python
#!/usr/bin/env python3
"""Basic Porcupine wake word detection"""

import pvporcupine
import pyaudio
import struct

# Replace with your AccessKey from Picovoice Console
ACCESS_KEY = "YOUR_ACCESS_KEY_HERE"

# Create Porcupine instance with built-in keywords
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=["picovoice", "computer", "jarvis"]
)

# Setup audio stream
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length,
    input_device_index=None  # Use default or specify ReSpeaker index
)

print(f"Listening for wake words: picovoice, computer, jarvis")
print(f"Sample rate: {porcupine.sample_rate}, Frame length: {porcupine.frame_length}")
print("Say a wake word...")

try:
    while True:
        # Read audio frame
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        # Process frame
        keyword_index = porcupine.process(pcm)
        
        if keyword_index >= 0:
            keywords = ["picovoice", "computer", "jarvis"]
            print(f"Detected: {keywords[keyword_index]}")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
```

## ReSpeaker Integration

For ReSpeaker 2-Mic HAT, you need to specify the correct audio device.

### Find Device Index

```python
#!/usr/bin/env python3
"""List available audio devices"""

import pyaudio

pa = pyaudio.PyAudio()
print("Available audio input devices:\n")

for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"Index {i}: {info['name']}")
        print(f"  Sample Rate: {int(info['defaultSampleRate'])}")
        print(f"  Input Channels: {info['maxInputChannels']}")
        print()

pa.terminate()
```

Look for `seeed-2mic-voicecard` or `seeed2micvoicec` in the output.

### Full ReSpeaker Example

```python
#!/usr/bin/env python3
"""Porcupine with ReSpeaker 2-Mic HAT and LED feedback"""

import pvporcupine
import pyaudio
import struct
import spidev
import time

ACCESS_KEY = "YOUR_ACCESS_KEY_HERE"
RESPEAKER_DEVICE_INDEX = 2  # Adjust based on your system

# APA102 LED class
class APA102:
    def __init__(self, num_leds=3):
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 8000000
        self.pixels = [(0, 0, 0, 0)] * num_leds
        
    def set_all(self, r, g, b, brightness=15):
        for i in range(self.num_leds):
            self.pixels[i] = (brightness, b, g, r)
        self.show()
        
    def show(self):
        data = [0x00] * 4
        for brightness, b, g, r in self.pixels:
            data.extend([0xE0 | brightness, b, g, r])
        data.extend([0xFF] * 4)
        self.spi.xfer2(data)
        
    def clear(self):
        self.set_all(0, 0, 0, 0)
        
    def close(self):
        self.clear()
        self.spi.close()

def find_respeaker_index():
    """Auto-detect ReSpeaker device index"""
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if 'seeed' in info['name'].lower() and info['maxInputChannels'] > 0:
            pa.terminate()
            return i
    pa.terminate()
    return None

def main():
    # Initialize LEDs
    leds = APA102(num_leds=3)
    leds.clear()
    
    # Find ReSpeaker
    device_index = find_respeaker_index()
    if device_index is None:
        print("ReSpeaker not found! Using default device.")
        device_index = None
    else:
        print(f"Found ReSpeaker at index {device_index}")
    
    # Create Porcupine
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keywords=["jarvis", "computer"]
    )
    
    # Setup audio
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        input_device_index=device_index
    )
    
    # LED colors for each keyword
    keyword_colors = {
        0: (255, 0, 255),    # jarvis = magenta
        1: (255, 255, 255),  # computer = white
    }
    
    print("Listening for 'Jarvis' or 'Computer'...")
    leds.set_all(0, 50, 0, 5)  # Dim green = listening
    
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                r, g, b = keyword_colors.get(keyword_index, (255, 255, 255))
                keywords = ["jarvis", "computer"]
                print(f"Detected: {keywords[keyword_index]}")
                
                # Flash LEDs
                leds.set_all(r, g, b, 31)
                time.sleep(0.5)
                leds.set_all(0, 50, 0, 5)  # Back to listening
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
        leds.close()

if __name__ == "__main__":
    main()
```

## Custom Wake Words

### Training Custom Wake Words

1. Log into [Picovoice Console](https://console.picovoice.ai/)
2. Navigate to **Porcupine** section
3. Select language and type your wake phrase
4. Select **Raspberry Pi** as target platform
5. Click **Download** - training takes seconds
6. Save the `.ppn` file to your Pi

### Using Custom Wake Words

```python
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keyword_paths=[
        "/home/pi/models/hey_assistant_raspberry-pi.ppn",
        "/home/pi/models/activate_raspberry-pi.ppn"
    ],
    sensitivities=[0.5, 0.5]  # 0.0 to 1.0, higher = more sensitive
)
```

### Wake Word Best Practices

**Good wake words:**
- 2-4 syllables
- Uncommon in daily speech
- Clear consonants
- Examples: "Hey Jarvis", "Computer", "OK Assistant"

**Avoid:**
- Single syllables ("Hey", "Go")
- Common phrases ("OK", "Hello")
- Similar to background noise

## LED Feedback

### Color Codes for Voice States

```python
class VoiceStateLEDs:
    def __init__(self):
        self.leds = APA102(num_leds=3)
        
    def idle(self):
        """Ready and waiting"""
        self.leds.set_all(0, 0, 50, 3)  # Dim blue
        
    def listening(self):
        """Wake word detected, listening for command"""
        self.leds.set_all(0, 0, 255, 20)  # Bright blue
        
    def processing(self):
        """Processing command"""
        self.leds.set_all(128, 0, 128, 15)  # Purple
        
    def speaking(self):
        """Playing response"""
        self.leds.set_all(0, 255, 0, 15)  # Green
        
    def error(self):
        """Error occurred"""
        self.leds.set_all(255, 0, 0, 20)  # Red
        
    def wake_detected(self, keyword_index):
        """Flash on wake word detection"""
        colors = [
            (255, 255, 0),   # Yellow
            (0, 255, 255),   # Cyan
            (255, 0, 255),   # Magenta
        ]
        r, g, b = colors[keyword_index % len(colors)]
        self.leds.set_all(r, g, b, 31)
```

## Speech-to-Intent with Rhino

Rhino converts spoken commands directly to structured intents, perfect for IoT control.

```bash
pip install pvrhino
```

### Create Intent Context

1. Go to [Picovoice Console](https://console.picovoice.ai/) → Rhino
2. Define your intents and slots:

```yaml
# Example: Smart Home Context
intents:
  turnOnLight:
    - "turn on the $room:room light"
    - "switch on $room:room"
  turnOffLight:
    - "turn off the $room:room light"
    - "lights off in $room:room"
  setTemperature:
    - "set temperature to $temperature:number degrees"

slots:
  room:
    - living room
    - bedroom
    - kitchen
  number:
    - type: integer
      range: [60, 80]
```

3. Download the `.rhn` context file for Raspberry Pi

### Rhino Example

```python
#!/usr/bin/env python3
"""Porcupine + Rhino: Wake word then intent recognition"""

import pvporcupine
import pvrhino
import pyaudio
import struct

ACCESS_KEY = "YOUR_ACCESS_KEY"

# Initialize engines
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=["jarvis"]
)

rhino = pvrhino.create(
    access_key=ACCESS_KEY,
    context_path="/home/pi/models/smart_home_raspberry-pi.rhn"
)

# Audio setup
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

state = "WAITING"  # WAITING, LISTENING

print("Say 'Jarvis' to wake, then give a command...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        if state == "WAITING":
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected! Listening for command...")
                state = "LISTENING"
                
        elif state == "LISTENING":
            is_finalized = rhino.process(pcm)
            if is_finalized:
                inference = rhino.get_inference()
                if inference.is_understood:
                    print(f"Intent: {inference.intent}")
                    print(f"Slots: {inference.slots}")
                    
                    # Act on intent
                    if inference.intent == "turnOnLight":
                        room = inference.slots.get("room", "unknown")
                        print(f"→ Turning on {room} light")
                else:
                    print("Command not understood")
                
                state = "WAITING"
                print("\nSay 'Jarvis' to wake...")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
    rhino.delete()
```

## Systemd Service

```bash
sudo systemctl edit --force --full picovoice-assistant.service
```

```ini
[Unit]
Description=Picovoice Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/picovoice-project
Environment="PATH=/home/pi/picovoice-project/.venv/bin"
ExecStart=/home/pi/picovoice-project/.venv/bin/python3 assistant.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable picovoice-assistant.service
sudo systemctl start picovoice-assistant.service
```

## Performance Tips

1. **Reduce sensitivity** if getting false positives: `sensitivities=[0.3]`
2. **Use exception_on_overflow=False** to prevent crashes on buffer overruns
3. **Adjust frame buffer size** if experiencing latency
4. **Run at startup** using systemd for headless operation
5. **Monitor CPU** usage: Porcupine should use <5% on Pi Zero 2 W
