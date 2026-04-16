#!/bin/bash
# diagnose_respeaker.sh - Diagnostic script for ReSpeaker 2-Mic HAT
# Run with: bash diagnose_respeaker.sh

set -e

echo "=============================================="
echo "ReSpeaker 2-Mic HAT Diagnostic Report"
echo "=============================================="
echo "Date: $(date)"
echo ""

echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
cat /etc/os-release | grep -E "^(PRETTY_NAME|VERSION)" | head -2
echo ""

echo "=== Raspberry Pi Model ==="
cat /proc/cpuinfo | grep -E "^(Model|Hardware|Revision)" || echo "Could not detect Pi model"
echo ""

echo "=== I2C Bus Status ==="
if [ -e /dev/i2c-1 ]; then
    echo "I2C-1 device: EXISTS"
    echo "I2C Detection (looking for 0x1a - WM8960 codec):"
    i2cdetect -y 1 2>/dev/null || echo "  i2cdetect failed - install i2c-tools"
else
    echo "I2C-1 device: NOT FOUND"
    echo "Run: sudo raspi-config -> Interface Options -> I2C -> Enable"
fi
echo ""

echo "=== SPI Bus Status ==="
if [ -e /dev/spidev0.0 ]; then
    echo "SPI device: EXISTS (for LED control)"
else
    echo "SPI device: NOT FOUND"
    echo "Run: sudo raspi-config -> Interface Options -> SPI -> Enable"
fi
echo ""

echo "=== Audio Playback Devices ==="
aplay -l 2>/dev/null || echo "aplay not available"
echo ""

echo "=== Audio Capture Devices ==="
arecord -l 2>/dev/null || echo "arecord not available"
echo ""

echo "=== ALSA Device List ==="
aplay -L 2>/dev/null | grep -E "(seeed|plughw:CARD=seeed)" | head -10 || echo "No seeed devices found"
echo ""

echo "=== Loaded Sound Modules ==="
lsmod | grep -E "^snd" | head -20
echo ""

echo "=== Seeed/WM8960 Modules ==="
lsmod | grep -iE "wm8960|seeed" || echo "No seeed/wm8960 modules loaded"
echo ""

echo "=== Config.txt Audio Settings ==="
CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi
if [ -f "$CONFIG_FILE" ]; then
    grep -E "dtoverlay|dtparam=i2c|dtparam=i2s|dtparam=spi" "$CONFIG_FILE" 2>/dev/null || echo "No relevant entries"
else
    echo "Config file not found"
fi
echo ""

echo "=== ASOUND Configuration ==="
if [ -f /etc/asound.conf ]; then
    echo "Content of /etc/asound.conf:"
    head -30 /etc/asound.conf
else
    echo "/etc/asound.conf: NOT FOUND (using defaults)"
fi
echo ""

echo "=== Seeed Voicecard Service ==="
systemctl status seeed-voicecard.service 2>/dev/null | head -10 || echo "Service not installed"
echo ""

echo "=== Recent Kernel Messages (Audio) ==="
dmesg | grep -iE "wm8960|seeed|asoc|codec|i2s" | tail -15 || echo "No relevant messages"
echo ""

echo "=== Quick Health Check ==="
SEEED_FOUND=false
if aplay -l 2>/dev/null | grep -qi seeed; then
    SEEED_FOUND=true
fi

I2C_FOUND=false
if i2cdetect -y 1 2>/dev/null | grep -q "1a"; then
    I2C_FOUND=true
fi

if $SEEED_FOUND && $I2C_FOUND; then
    echo "✓ ReSpeaker HAT appears to be working correctly"
    echo ""
    echo "Test recording with:"
    echo "  arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -d 5 test.wav"
    echo ""
    echo "Test playback with:"
    echo "  aplay -D plughw:CARD=seeed2micvoicec,DEV=0 test.wav"
elif $I2C_FOUND && ! $SEEED_FOUND; then
    echo "⚠ HAT detected on I2C but drivers not loaded"
    echo "  Try reinstalling drivers - see troubleshooting guide"
elif ! $I2C_FOUND; then
    echo "✗ HAT not detected on I2C bus"
    echo "  1. Check physical connection (power off first)"
    echo "  2. Ensure I2C is enabled: sudo raspi-config"
    echo "  3. Check for bent pins"
fi

echo ""
echo "=============================================="
echo "Report complete"
echo "=============================================="
