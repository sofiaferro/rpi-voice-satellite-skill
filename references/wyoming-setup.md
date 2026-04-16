# Wyoming Satellite Setup for Home Assistant

This guide covers setting up a Wyoming voice satellite on Raspberry Pi Zero 2 W with ReSpeaker 2-Mic HAT for Home Assistant integration.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Install Wyoming Satellite](#install-wyoming-satellite)
3. [Install OpenWakeWord](#install-openwakeword)
4. [Configure Systemd Services](#configure-systemd-services)
5. [LED Feedback Service](#led-feedback-service)
6. [Home Assistant Integration](#home-assistant-integration)
7. [Custom Wake Words](#custom-wake-words)

---

## Prerequisites

Before starting, ensure you have completed the initial setup from the main SKILL.md:
- Raspberry Pi OS 64-bit Lite installed
- ReSpeaker drivers installed and working
- Audio tested with `arecord` and `aplay`

## Install Wyoming Satellite

```bash
cd ~
git clone https://github.com/rhasspy/wyoming-satellite.git
cd wyoming-satellite

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
.venv/bin/pip3 install --upgrade pip wheel setuptools

# Install with all optional features (audio enhancement, VAD)
.venv/bin/pip3 install \
    -f 'https://synesthesiam.github.io/prebuilt-apps/' \
    -r requirements.txt \
    -r requirements_audio_enhancement.txt \
    -r requirements_vad.txt
```

### Test Wyoming Satellite Manually

```bash
cd ~/wyoming-satellite
script/run \
    --debug \
    --name 'my satellite' \
    --uri 'tcp://0.0.0.0:10700' \
    --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' \
    --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw'
```

You should see `[Streaming audio]` in the output. Press Ctrl+C to stop.

## Install OpenWakeWord

OpenWakeWord provides local wake word detection (e.g., "ok nabu", "hey jarvis").

```bash
cd ~
git clone https://github.com/rhasspy/wyoming-openwakeword.git
cd wyoming-openwakeword

python3 -m venv .venv
source .venv/bin/activate

.venv/bin/pip3 install --upgrade pip wheel setuptools
.venv/bin/pip3 install \
    -f 'https://synesthesiam.github.io/prebuilt-apps/' \
    -r requirements.txt
```

### Test OpenWakeWord

```bash
cd ~/wyoming-openwakeword
script/run --uri 'tcp://0.0.0.0:10400' --preload-model 'ok_nabu' --debug
```

Say "ok nabu" and watch for detection in the logs.

## Configure Systemd Services

### Wyoming Satellite Service

```bash
sudo systemctl edit --force --full wyoming-satellite.service
```

Paste the following (adjust paths and device names as needed):

```ini
[Unit]
Description=Wyoming Satellite
Wants=network-online.target
After=network-online.target
Requires=wyoming-openwakeword.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wyoming-satellite
ExecStart=/home/pi/wyoming-satellite/script/run \
    --name 'living room satellite' \
    --uri 'tcp://0.0.0.0:10700' \
    --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' \
    --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw' \
    --wake-uri 'tcp://127.0.0.1:10400' \
    --wake-word-name 'ok_nabu'
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

### OpenWakeWord Service

```bash
sudo systemctl edit --force --full wyoming-openwakeword.service
```

Paste:

```ini
[Unit]
Description=Wyoming openWakeWord

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wyoming-openwakeword
ExecStart=/home/pi/wyoming-openwakeword/script/run \
    --uri 'tcp://127.0.0.1:10400' \
    --preload-model 'ok_nabu'
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start at boot
sudo systemctl enable wyoming-openwakeword.service
sudo systemctl enable wyoming-satellite.service

# Start services
sudo systemctl start wyoming-openwakeword.service
sudo systemctl start wyoming-satellite.service

# Check status
sudo systemctl status wyoming-satellite.service wyoming-openwakeword.service
```

Both should show `active (running)` in green.

### View Logs

```bash
# Live logs for satellite
journalctl -u wyoming-satellite.service -f

# Live logs for wake word
journalctl -u wyoming-openwakeword.service -f

# Combined recent logs
journalctl -u wyoming-satellite.service -u wyoming-openwakeword.service --since "10 minutes ago"
```

## LED Feedback Service

The wyoming-satellite repo includes example LED services for visual feedback.

```bash
cd ~/wyoming-satellite/examples

# Create virtual environment for LED service
python3 -m venv --system-site-packages .venv
.venv/bin/pip3 install --upgrade pip wheel setuptools
.venv/bin/pip3 install 'wyoming==1.5.2'

# Install GPIO and SPI libraries
sudo apt-get install -y python3-spidev python3-gpiozero
.venv/bin/pip3 install spidev gpiozero
```

### LED Service Systemd Unit

```bash
sudo systemctl edit --force --full wyoming-satellite-leds.service
```

Paste:

```ini
[Unit]
Description=Wyoming Satellite LEDs
Wants=wyoming-satellite.service
After=wyoming-satellite.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wyoming-satellite/examples
ExecStart=/home/pi/wyoming-satellite/examples/.venv/bin/python3 2mic_service.py \
    --uri 'tcp://127.0.0.1:10500'
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Update the satellite service to include `--event-uri`:

```bash
sudo systemctl edit wyoming-satellite.service
```

Add to ExecStart:
```
    --event-uri 'tcp://127.0.0.1:10500'
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wyoming-satellite-leds.service
sudo systemctl restart wyoming-satellite.service
sudo systemctl start wyoming-satellite-leds.service
```

### LED State Colors (Default)

| State | Color | Meaning |
|-------|-------|---------|
| Idle | Off | Waiting for wake word |
| Listening | Blue | Wake word detected, listening |
| Processing | Purple | Processing command |
| Speaking | Green | Playing response |
| Error | Red | Error occurred |

## Home Assistant Integration

### Automatic Discovery

1. In Home Assistant, go to **Settings → Devices & Services**
2. Look for "Discovered" section - Wyoming Protocol should appear
3. Click **Configure** → **Submit**
4. Select the area where your satellite is located
5. Click **Finish**

### Manual Integration

If not auto-discovered:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Wyoming Protocol**
4. Enter satellite IP address and port 10700
5. Complete setup

### Configure Voice Pipeline

1. Go to **Settings → Voice Assistants**
2. Create or edit a pipeline
3. Select your satellite as the wake word device
4. Configure STT (Speech-to-Text) engine
5. Configure TTS (Text-to-Speech) engine
6. Set conversation agent (e.g., Home Assistant, OpenAI)

### Test Voice Commands

Say "ok nabu" followed by a command:
- "Ok Nabu, turn on the living room lights"
- "Ok Nabu, what's the weather"
- "Ok Nabu, set a timer for 5 minutes"

## Custom Wake Words

### Using OpenWakeWord Community Models

```bash
# Download community wake words
cd ~/wyoming-openwakeword
mkdir -p custom_models

# Example: Download from community
# wget -O custom_models/hey_jarvis.tflite <URL>

# Update service to use custom model directory
sudo systemctl edit wyoming-openwakeword.service
```

Add to ExecStart:
```
    --custom-model-dir '/home/pi/wyoming-openwakeword/custom_models'
```

### Training Custom Wake Words

Use [OpenWakeWord Training](https://github.com/dscripka/openWakeWord) to train your own models. This requires a more powerful computer for training, then deploy the `.tflite` file to your Pi.

## Troubleshooting

### Satellite Not Appearing in Home Assistant

1. Check network connectivity: `ping <home-assistant-ip>`
2. Verify satellite is running: `sudo systemctl status wyoming-satellite`
3. Check firewall: `sudo ufw allow 10700/tcp` (if UFW enabled)
4. Verify mDNS/Avahi: `sudo apt install avahi-daemon`

### Wake Word Not Detecting

1. Check OpenWakeWord service: `journalctl -u wyoming-openwakeword -f`
2. Verify microphone volume: `alsamixer` → F6 → select card → raise Capture
3. Test recording quality: Record and play back a test file
4. Try different sensitivity (add `--threshold 0.3` to OpenWakeWord)

### Audio Cuts Out

1. Check power supply (use 2.5A+ adapter)
2. Add `--vad` flag to satellite for voice activity detection
3. Check for USB interference if using external devices

### Services Won't Start After Reboot

1. Enable services: `sudo systemctl enable <service-name>`
2. Check dependencies: Ensure network is up before services start
3. View boot logs: `journalctl -b -u wyoming-satellite`
