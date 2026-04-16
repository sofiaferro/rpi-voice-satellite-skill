#!/usr/bin/env python3
"""
led_demo.py - APA102 LED demo for ReSpeaker 2-Mic HAT

Demonstrates LED control patterns for voice assistant states.
Run with: python3 led_demo.py

Requires: pip install spidev
"""

import spidev
import time
import math


class APA102:
    """APA102 RGB LED controller for ReSpeaker 2-Mic HAT (3 LEDs)"""
    
    def __init__(self, num_leds=3):
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 8000000
        self.pixels = [(0, 0, 0, 0)] * num_leds  # (brightness, b, g, r)
        
    def set_pixel(self, index, red, green, blue, brightness=31):
        """Set single LED. RGB: 0-255, brightness: 0-31"""
        if 0 <= index < self.num_leds:
            self.pixels[index] = (min(31, max(0, brightness)), 
                                   min(255, max(0, blue)),
                                   min(255, max(0, green)),
                                   min(255, max(0, red)))
            
    def set_all(self, red, green, blue, brightness=31):
        """Set all LEDs to same color"""
        for i in range(self.num_leds):
            self.set_pixel(i, red, green, blue, brightness)
            
    def show(self):
        """Update physical LEDs"""
        # Start frame: 32 zero bits
        data = [0x00] * 4
        
        # LED frames: 111 + 5-bit brightness + BGR
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
        self.set_all(0, 0, 0, 0)
        self.show()
        
    def close(self):
        """Cleanup"""
        self.clear()
        self.spi.close()


def demo_basic_colors(leds):
    """Show basic color test"""
    print("Basic colors test...")
    colors = [
        ("Red", 255, 0, 0),
        ("Green", 0, 255, 0),
        ("Blue", 0, 0, 255),
        ("Yellow", 255, 255, 0),
        ("Cyan", 0, 255, 255),
        ("Magenta", 255, 0, 255),
        ("White", 255, 255, 255),
    ]
    
    for name, r, g, b in colors:
        print(f"  {name}")
        leds.set_all(r, g, b, 20)
        leds.show()
        time.sleep(0.5)
    
    leds.clear()
    time.sleep(0.3)


def demo_individual_leds(leds):
    """Light each LED individually"""
    print("Individual LED test...")
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    
    for i in range(leds.num_leds):
        leds.clear()
        r, g, b = colors[i % len(colors)]
        leds.set_pixel(i, r, g, b, 25)
        leds.show()
        print(f"  LED {i}")
        time.sleep(0.5)
    
    leds.clear()
    time.sleep(0.3)


def demo_breathing(leds, color=(0, 100, 255), duration=3):
    """Breathing effect - simulates idle/listening state"""
    print("Breathing effect (simulates 'listening')...")
    r, g, b = color
    steps = 50
    
    for _ in range(int(duration * 2)):
        # Fade in
        for i in range(steps):
            brightness = int((i / steps) * 31)
            leds.set_all(r, g, b, brightness)
            leds.show()
            time.sleep(0.02)
        
        # Fade out
        for i in range(steps, 0, -1):
            brightness = int((i / steps) * 31)
            leds.set_all(r, g, b, brightness)
            leds.show()
            time.sleep(0.02)
    
    leds.clear()


def demo_spin(leds, color=(255, 255, 0), duration=2):
    """Spinning effect - simulates 'processing'"""
    print("Spinning effect (simulates 'processing')...")
    r, g, b = color
    start_time = time.time()
    
    while time.time() - start_time < duration:
        for i in range(leds.num_leds):
            leds.clear()
            leds.set_pixel(i, r, g, b, 25)
            leds.set_pixel((i + 1) % leds.num_leds, r, g, b, 10)
            leds.show()
            time.sleep(0.1)
    
    leds.clear()


def demo_pulse(leds, color=(0, 255, 0), pulses=3):
    """Quick pulse - simulates 'acknowledged'"""
    print("Pulse effect (simulates 'acknowledged')...")
    r, g, b = color
    
    for _ in range(pulses):
        leds.set_all(r, g, b, 31)
        leds.show()
        time.sleep(0.1)
        leds.clear()
        time.sleep(0.1)


def demo_voice_states(leds):
    """Simulate voice assistant state transitions"""
    print("\nSimulating voice assistant states...")
    
    # Idle - dim blue
    print("  State: IDLE (dim blue)")
    leds.set_all(0, 0, 50, 5)
    leds.show()
    time.sleep(2)
    
    # Wake word detected - bright blue pulse
    print("  State: WAKE WORD DETECTED (blue flash)")
    for _ in range(2):
        leds.set_all(0, 100, 255, 31)
        leds.show()
        time.sleep(0.1)
        leds.set_all(0, 100, 255, 10)
        leds.show()
        time.sleep(0.1)
    
    # Listening - breathing blue
    print("  State: LISTENING (breathing blue)")
    for _ in range(3):
        for brightness in range(5, 25, 2):
            leds.set_all(0, 100, 255, brightness)
            leds.show()
            time.sleep(0.05)
        for brightness in range(25, 5, -2):
            leds.set_all(0, 100, 255, brightness)
            leds.show()
            time.sleep(0.05)
    
    # Processing - spinning purple
    print("  State: PROCESSING (spinning purple)")
    for _ in range(10):
        for i in range(leds.num_leds):
            leds.clear()
            leds.set_pixel(i, 150, 0, 200, 25)
            leds.show()
            time.sleep(0.1)
    
    # Speaking - solid green
    print("  State: SPEAKING (solid green)")
    leds.set_all(0, 255, 0, 20)
    leds.show()
    time.sleep(2)
    
    # Done - fade out
    print("  State: DONE (fade out)")
    for brightness in range(20, 0, -2):
        leds.set_all(0, 255, 0, brightness)
        leds.show()
        time.sleep(0.05)
    
    leds.clear()


def demo_rainbow(leds, duration=3):
    """Rainbow cycle effect"""
    print("Rainbow effect...")
    start_time = time.time()
    
    while time.time() - start_time < duration:
        for hue in range(0, 360, 5):
            for i in range(leds.num_leds):
                # Offset each LED's hue
                h = (hue + i * 120) % 360
                r, g, b = hsv_to_rgb(h, 1.0, 1.0)
                leds.set_pixel(i, int(r * 255), int(g * 255), int(b * 255), 20)
            leds.show()
            time.sleep(0.02)
    
    leds.clear()


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB (h: 0-360, s/v: 0-1)"""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return r + m, g + m, b + m


def main():
    print("=" * 50)
    print("ReSpeaker 2-Mic HAT LED Demo")
    print("=" * 50)
    print()
    
    try:
        leds = APA102(num_leds=3)
        leds.clear()
        
        demo_basic_colors(leds)
        demo_individual_leds(leds)
        demo_breathing(leds)
        demo_spin(leds)
        demo_pulse(leds)
        demo_rainbow(leds)
        demo_voice_states(leds)
        
        print("\nDemo complete!")
        
    except PermissionError:
        print("ERROR: Permission denied accessing SPI")
        print("Run with sudo or add user to spi group:")
        print("  sudo usermod -a -G spi $USER")
        print("  (then logout and login)")
    except FileNotFoundError:
        print("ERROR: SPI device not found")
        print("Enable SPI: sudo raspi-config -> Interface Options -> SPI -> Enable")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        try:
            leds.close()
        except:
            pass


if __name__ == "__main__":
    main()
