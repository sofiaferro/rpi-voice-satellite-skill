# ReSpeaker 2-Mic Pi HAT Voice Satellite Skill

Build voice assistants with **Raspberry Pi Zero 2 W** and **ReSpeaker 2-Mic Pi HAT** for Home Assistant or standalone use.

This repository serves two purposes:
1. **AI Agent Skill** - Drop into any AI assistant (Claude, opencode, Codex, Conductor, Cursor, etc.) for AI-assisted setup
2. **Standalone Documentation** - Complete guides you can follow manually

## What's Inside

| File | Purpose |
|------|---------|
| `SKILL.md` | Main entry point for AI assistants |
| `references/official-docs/` | Verbatim documentation from Seeed Studio and Wyoming Satellite |
| `references/wyoming-setup.md` | Quick guide: Home Assistant voice satellite |
| `references/picovoice-setup.md` | Quick guide: Local wake word with Picovoice |
| `references/troubleshooting.md` | Common issues and fixes |
| `scripts/diagnose_respeaker.sh` | Hardware diagnostic script |
| `scripts/led_demo.py` | APA102 LED demo for the HAT |

## Hardware Requirements

- Raspberry Pi Zero 2 W (64-bit capable)
- ReSpeaker 2-Mic Pi HAT (v1 or v2)
- MicroSD card (16GB+)
- 5V 2.5A power supply
- Speaker (3.5mm or JST connector)

## Quick Start

### Option A: Wyoming Satellite (Home Assistant)

Your Pi becomes a voice satellite that connects to Home Assistant for processing.

```bash
# Install OS: Raspberry Pi OS 64-bit Lite

# Install dependencies
sudo apt-get update
sudo apt-get install git python3-venv

# Clone and install Wyoming Satellite
git clone https://github.com/rhasspy/wyoming-satellite.git
cd wyoming-satellite
sudo bash etc/install-respeaker-drivers.sh
sudo reboot

# After reboot, test audio
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -d 5 test.wav
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 test.wav

# Run satellite (auto-discovered by Home Assistant)
script/run --name 'my satellite' --uri 'tcp://0.0.0.0:10700' \
  --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' \
  --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw'
```

See `references/wyoming-setup.md` for complete setup including wake word detection and LED feedback.

### Option B: Picovoice (Standalone)

Everything runs locally on the Pi - no server needed.

```bash
# After driver installation
pip3 install pvporcupine pyaudio

# Run wake word detection with built-in keywords
python3 -c "
import pvporcupine
import pyaudio
import struct

porcupine = pvporcupine.create(access_key='YOUR_KEY', keywords=['jarvis', 'computer'])
pa = pyaudio.PyAudio()
stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
                 input=True, frames_per_buffer=porcupine.frame_length)

print('Listening for jarvis/computer...')
while True:
    pcm = struct.unpack_from('h' * porcupine.frame_length, 
                              stream.read(porcupine.frame_length))
    if porcupine.process(pcm) >= 0:
        print('Wake word detected!')
"
```

Get your free access key at [Picovoice Console](https://console.picovoice.ai/).

See `references/picovoice-setup.md` for complete setup including LED feedback and Speech-to-Intent.

## Using with AI Assistants

This repository works with any AI assistant that supports skill/context injection. Here are examples for popular tools:

### Claude (Desktop / Code / API)

**macOS:**
```bash
mkdir -p ~/Library/Application\ Support/Claude/skills
cp -r rpi-voice-satellite ~/Library/Application\ Support/Claude/skills/
```

**Linux:**
```bash
mkdir -p ~/.config/claude/skills
cp -r rpi-voice-satellite ~/.config/claude/skills/
```

### opencode

```bash
mkdir -p ~/.agents/skills/
cp -r rpi-voice-satellite ~/.agents/skills/
ln -s ~/.agents/skills/rpi-voice-satellite ~/.config/opencode/skills/rpi-voice-satellite
```

### Codex

```bash
# Codex supports MCP servers and custom instructions
# Copy the skill to your Codex context directory:
mkdir -p ~/.codex/skills
cp -r rpi-voice-satellite ~/.codex/skills/

# Or reference SKILL.md directly in your Codex project
```

### Conductor

```bash
# Conductor (if using local skill directories):
mkdir -p ~/.conductor/skills
cp -r rpi-voice-satellite ~/.conductor/skills/
```

### Other Tools

Most AI coding assistants (Cursor, GitHub Copilot, Windsurf, etc.) support loading context from markdown files. Point your tool to `SKILL.md` as the primary context file, or clone the repository to your tool's skills directory.

### Usage Examples

Once loaded, ask your AI assistant things like:
- "Help me set up my ReSpeaker 2-Mic HAT"
- "The audio isn't working on my Pi Zero voice satellite"
- "How do I add LED feedback to Wyoming Satellite?"
- "Create a Python script for LED control"

## Troubleshooting

Run the diagnostic script:

```bash
bash scripts/diagnose_respeaker.sh
```

Common issues:

| Problem | Solution |
|---------|----------|
| HAT not detected | Check I2C enabled: `sudo raspi-config` → Interface Options → I2C |
| No audio devices | Reinstall drivers, check physical connection |
| Driver install fails | Ensure kernel headers match: `sudo apt install raspberrypi-kernel-headers` |
| Quiet audio | Run `alsamixer`, press F6, select seeed card, raise volumes |

See `references/troubleshooting.md` for detailed diagnostics.

## Sources & Credits

This skill aggregates documentation from:

- [Seeed Studio Wiki - ReSpeaker 2-Mics Pi HAT](https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/)
- [Wyoming Satellite](https://github.com/rhasspy/wyoming-satellite) by Michael Hansen / Rhasspy
- [Picovoice](https://picovoice.ai/) - Porcupine wake word engine
- [Home Assistant Voice](https://www.home-assistant.io/voice_control/)

## License

MIT License - See [LICENSE](LICENSE)

The included documentation excerpts retain their original licenses:
- Seeed Studio Wiki: CC BY-SA 4.0
- Wyoming Satellite: MIT
- Picovoice examples: Apache 2.0
