# Troubleshooting ReSpeaker 2-Mic HAT

This guide covers common issues and solutions for the ReSpeaker 2-Mic Pi HAT on Raspberry Pi Zero 2 W.

## Table of Contents
1. [Quick Diagnostics](#quick-diagnostics)
2. [HAT Not Detected](#hat-not-detected)
3. [Driver Installation Issues](#driver-installation-issues)
4. [Audio Problems](#audio-problems)
5. [LED Issues](#led-issues)
6. [Button Issues](#button-issues)
7. [Performance Issues](#performance-issues)
8. [Version-Specific Issues](#version-specific-issues)

---

## Quick Diagnostics

Run these commands to quickly assess your setup:

```bash
#!/bin/bash
# Save as diagnose.sh and run with: bash diagnose.sh

echo "=== System Info ==="
uname -a
cat /etc/os-release | grep PRETTY_NAME

echo -e "\n=== I2C Detection ==="
i2cdetect -y 1

echo -e "\n=== Audio Devices ==="
echo "Playback:"
aplay -l
echo -e "\nCapture:"
arecord -l

echo -e "\n=== Loaded Modules ==="
lsmod | grep -E "snd|wm8960|seeed|i2c"

echo -e "\n=== Device Tree Overlays ==="
cat /boot/firmware/config.txt | grep -E "dtoverlay|dtparam"

echo -e "\n=== ALSA Config ==="
cat /etc/asound.conf 2>/dev/null || echo "No asound.conf found"

echo -e "\n=== Seeed Service Status ==="
systemctl status seeed-voicecard.service 2>/dev/null || echo "Service not installed"

echo -e "\n=== Kernel Messages (audio related) ==="
dmesg | grep -iE "wm8960|seeed|i2c|codec|asoc" | tail -20
```

### What to Look For

**I2C Detection:**
- Should show `1a` at address 0x1a (WM8960 codec)
- If empty or no `1a`, HAT not properly connected or drivers not loaded

**Audio Devices:**
- Should show `seeed2micvoicec` or `seeed-2mic-voicecard`
- Card number varies (usually 0-3)

**Loaded Modules:**
- Should include: `snd_soc_wm8960`, `snd_soc_seeed_voicecard`

---

## HAT Not Detected

### Symptoms
- `aplay -l` / `arecord -l` show no seeed device
- `i2cdetect -y 1` shows no device at 0x1a

### Solutions

**1. Check Physical Connection**
```bash
# Power off
sudo shutdown -h now

# Physically inspect:
# - All 40 pins properly aligned
# - No bent pins
# - HAT seated firmly
# - No debris on contacts

# Power back on
```

**2. Enable I2C**
```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Reboot

# Verify
ls /dev/i2c*
# Should show /dev/i2c-1
```

**3. Check config.txt**
```bash
sudo nano /boot/firmware/config.txt

# Ensure these lines exist (uncommented):
dtparam=i2c_arm=on
dtparam=i2s=on
dtparam=spi=on

# If using device tree overlay method:
dtoverlay=respeaker-2mic-v1_0

# Reboot after changes
sudo reboot
```

**4. Reinstall Drivers**
```bash
# Remove old installation
cd ~/seeed-voicecard
sudo ./uninstall.sh
sudo reboot

# Fresh install
cd ~
rm -rf seeed-voicecard
git clone https://github.com/respeaker/seeed-voicecard
cd seeed-voicecard

# For 64-bit OS:
sudo ./install_arm64.sh

# For 32-bit OS:
# sudo ./install.sh

sudo reboot
```

---

## Driver Installation Issues

### Error: "Kernel headers not found"

```bash
# Install kernel headers
sudo apt-get update
sudo apt-get install raspberrypi-kernel-headers

# If that fails, ensure kernel and headers match
sudo apt-get install --reinstall raspberrypi-kernel raspberrypi-kernel-headers
sudo reboot

# Retry driver installation
```

### Error: "DKMS module not found"

```bash
# Check DKMS status
sudo dkms status

# Remove failed module
sudo dkms remove seeed-voicecard/0.3 --all 2>/dev/null

# Reinstall
cd ~/seeed-voicecard
sudo ./uninstall.sh
sudo ./install_arm64.sh  # or install.sh for 32-bit
```

### Error: "rpi-update was used"

If you ran `rpi-update`, kernel and headers may be mismatched:

```bash
# Revert to stable kernel
sudo apt-get install --reinstall raspberrypi-bootloader raspberrypi-kernel
sudo reboot
```

### Wyoming Driver Installation Takes Forever

On Pi Zero 2 W, the wyoming driver script can take 30-60 minutes. This is normal due to DKMS compilation.

```bash
# Run with verbose output
cd ~/wyoming-satellite
sudo bash -x etc/install-respeaker-drivers.sh 2>&1 | tee driver-install.log
```

---

## Audio Problems

### No Sound on Playback

```bash
# Check device exists
aplay -l | grep seeed

# Get card number (e.g., card 1)
# Test with explicit device
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 /usr/share/sounds/alsa/Front_Center.wav

# If file doesn't exist, create test tone
speaker-test -D plughw:CARD=seeed2micvoicec,DEV=0 -c 2 -t sine
```

### Volume Too Low / Muted

```bash
alsamixer
# Press F6, select seeed-2mic-voicecard
# Navigate to these controls and adjust:
# - Speaker (or Headphone): set to 80-100%
# - Speaker AC: unmute (M to toggle)
# - Output Mixer Speaker: enable
# - Playback: unmute

# Save settings
sudo alsactl store

# Make persistent
sudo alsactl --file=/etc/asound.state store
```

### No Recording / Microphone Not Working

```bash
# Test recording
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -f S16_LE -r 16000 -c 1 -d 5 test.wav

# Play back
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 test.wav

# If silent, adjust capture volume
alsamixer
# F6 → select card
# Tab to switch to Capture view
# Raise these:
# - Capture: 80%+
# - ADC PCM: 80%+

# Check if muted (MM = muted)
# Press M to unmute
```

### Audio Quality Issues (Noise/Distortion)

```bash
# Reduce capture volume if clipping
alsamixer  # Lower ADC PCM to 60-70%

# Check power supply - use 2.5A minimum
# USB power may be insufficient

# Check for electrical interference
# - Move away from motors, displays
# - Use shielded cables
```

### Wrong Sample Rate

ReSpeaker works best at these rates:
- Recording: 16000 Hz (16kHz)
- Playback: 22050 Hz or 44100 Hz

```bash
# Force correct rate
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t wav test.wav
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE test.wav
```

### "Device or resource busy"

```bash
# Find what's using audio
fuser -v /dev/snd/*

# Kill conflicting processes
sudo fuser -k /dev/snd/*

# Or stop services using audio
sudo systemctl stop pulseaudio
sudo systemctl stop wyoming-satellite
```

---

## LED Issues

### LEDs Not Working

```bash
# Enable SPI
sudo raspi-config
# Interface Options → SPI → Enable

# Check SPI device
ls /dev/spidev*
# Should show /dev/spidev0.0 and /dev/spidev0.1

# Test with Python
python3 << 'EOF'
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000

# Turn all LEDs white
data = [0,0,0,0]  # Start frame
data += [0xFF, 255, 255, 255] * 3  # 3 white LEDs
data += [0xFF, 0xFF, 0xFF, 0xFF]  # End frame
spi.xfer2(data)
print("LEDs should be white now")

import time
time.sleep(2)

# Turn off
data = [0,0,0,0]
data += [0xE0, 0, 0, 0] * 3
data += [0xFF, 0xFF, 0xFF, 0xFF]
spi.xfer2(data)
print("LEDs off")
spi.close()
EOF
```

### LEDs Flicker or Wrong Colors

- Check SPI speed (8MHz is standard)
- Ensure proper grounding
- Check for loose connections

---

## Button Issues

### Button Not Responding

```bash
# Test GPIO17
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

print("Press the button (Ctrl+C to exit)...")
try:
    while True:
        state = GPIO.input(17)
        if state == 0:
            print("PRESSED")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
EOF
```

### Button Detection Issues

The button is active-low (pressed = 0):
```python
if GPIO.input(17) == 0:  # Button pressed
    pass
```

---

## Performance Issues

### High CPU Usage

```bash
# Monitor CPU
htop

# For voice processing, CPU should be under 50%
# If higher:
# - Reduce sample rate to 16000
# - Use lighter wake word engine
# - Check for runaway processes
```

### Audio Lag/Latency

```bash
# Reduce buffer size in your application
# For arecord/aplay, adjust period size:
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 \
    --period-size=160 --buffer-size=640 \
    -r 16000 -c 1 -f S16_LE -t raw

# Use plughw: instead of hw: for automatic conversion
```

### System Freezes

- **Power issue**: Use 2.5A+ power supply
- **SD card issue**: Use high-quality Class 10 or A1/A2 card
- **Overheating**: Add heatsink or fan to Pi Zero 2 W

---

## Version-Specific Issues

### ReSpeaker 2-Mic HAT v2.0

Version 2.0 may need different overlay:

```bash
# Check your version (printed on PCB)
# v2.0 may need:
dtoverlay=respeaker-2mic-v2_0

# If not working, try the v1.0 overlay
# Both versions use same WM8960 codec
```

### Raspberry Pi OS Bookworm (12)

Bookworm changed config location:

```bash
# Config file moved to:
/boot/firmware/config.txt  # Bookworm
# Instead of:
/boot/config.txt  # Bullseye and older

# Use proper path when editing
sudo nano /boot/firmware/config.txt
```

### Kernel 6.x Compatibility

Some older driver versions don't work with kernel 6.x:

```bash
# Check kernel version
uname -r

# If 6.x, use newer driver method:
git clone https://github.com/Seeed-Studio/seeed-linux-dtoverlays.git
cd seeed-linux-dtoverlays/
make overlays/rpi/respeaker-2mic-v1_0-overlay.dtbo
sudo cp overlays/rpi/respeaker-2mic-v1_0-overlay.dtbo /boot/firmware/overlays/respeaker-2mic-v1_0.dtbo
echo "dtoverlay=respeaker-2mic-v1_0" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

---

## Getting Help

If problems persist:

1. **Collect diagnostics**: Run the script at the top of this file
2. **Check GitHub Issues**:
   - [seeed-voicecard issues](https://github.com/respeaker/seeed-voicecard/issues)
   - [wyoming-satellite issues](https://github.com/rhasspy/wyoming-satellite/issues)
3. **Community forums**:
   - [Rhasspy Community](https://community.rhasspy.org/)
   - [Home Assistant Community](https://community.home-assistant.io/)
   - [Raspberry Pi Forums](https://forums.raspberrypi.com/)

When asking for help, include:
- `uname -a` output
- `aplay -l` and `arecord -l` output
- `i2cdetect -y 1` output
- HAT version (v1.0 or v2.0)
- Exact error messages
