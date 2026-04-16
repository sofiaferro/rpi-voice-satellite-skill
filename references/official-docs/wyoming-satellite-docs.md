# Wyoming Satellite - Official Documentation

This file contains the official documentation from the rhasspy/wyoming-satellite repository.

**Source:** https://github.com/rhasspy/wyoming-satellite
**Tutorial:** https://github.com/rhasspy/wyoming-satellite/blob/master/docs/tutorial_2mic.md

---

## What is Wyoming?

Wyoming is a peer-to-peer protocol for voice assistants created by the Rhasspy project. It allows different voice components to communicate over a network:

- **Satellites** send/receive audio (your Pi with mic/speaker)
- **Wake word detectors** listen for trigger phrases
- **Speech-to-text** engines transcribe audio
- **Text-to-speech** engines generate spoken responses
- **Intent handlers** process commands

Home Assistant natively supports Wyoming, so satellites are auto-discovered.

---

# Tutorial: ReSpeaker 2Mic HAT with Raspberry Pi Zero 2 W

Create a voice satellite using a Raspberry Pi Zero 2 W and a ReSpeaker 2Mic HAT.

This tutorial should work for almost any Raspberry Pi and USB microphone. Audio enhancements and local wake word detection may require a 64-bit operating system, however.

## Install OS

Follow instructions to install Raspberry Pi OS using the Raspberry Pi Imager.

Under "Choose OS", pick "Raspberry Pi OS (other)" and "**Raspberry Pi OS (64-bit) Lite**".

When asking if you'd like to apply customization settings, choose "Edit Settings" and:
- Set a username/password
- Configure the wireless LAN
- Under the Services tab, enable SSH and use password authentication

## Install System Dependencies

After flashing and booting the satellite, connect to it over SSH using the username/password you configured during flashing.

On the satellite, make sure system dependencies are installed:

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends \
  git \
  python3-venv
```

Clone the wyoming-satellite repository:

```bash
git clone https://github.com/rhasspy/wyoming-satellite.git
```

## Install Drivers

If you have the ReSpeaker 2Mic or 4Mic HAT, recompile and install the drivers (this will take really long time):

```bash
cd wyoming-satellite/
sudo bash etc/install-respeaker-drivers.sh
```

After install the drivers, you must reboot the satellite:

```bash
sudo reboot
```

## Create Virtual Environment

After rebooting, create a Python virtual environment and install wyoming-satellite:

```bash
cd wyoming-satellite/
python3 -m venv .venv
.venv/bin/pip3 install --upgrade pip
.venv/bin/pip3 install --upgrade wheel setuptools
.venv/bin/pip3 install \
  -f 'https://synesthesiam.github.io/prebuilt-apps/' \
  -r requirements.txt \
  -r requirements_audio_enhancement.txt \
  -r requirements_vad.txt
```

If the installation was successful, you should be able to run:

```bash
.venv/bin/python3 -m wyoming_satellite --help
```

## Determine Audio Devices

Picking the correct microphone/speaker devices is critical for the satellite to work. We'll do a test recording and playback in this section.

List your available microphones with:

```bash
arecord -L
```

and look for devices that start with `plughw:`. You should see one like:

```
plughw:CARD=seeed2micvoicec,DEV=0
    seeed-2mic-voicecard, bcm2835-i2s-wm8960-hifi wm8960-hifi-0
    Hardware device with all software conversions
```

For other microphones, prefer ones that start with `plughw:` or just use `default` if you don't know what to use.

Record a 5 second sample from your chosen microphone:

```bash
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t wav -d 5 test.wav
```

Say something while arecord is running. If you get errors, try a different microphone device by changing `-D <device>`.

List your available speakers with:

```bash
aplay -L
```

and look for devices that start with `plughw:`. You should see one like:

```
plughw:CARD=seeed2micvoicec,DEV=0
    seeed-2mic-voicecard, bcm2835-i2s-wm8960-hifi wm8960-hifi-0
    Hardware device with all software conversions
```

For other speakers, prefer ones that start with `plughw:` or just use `default` if you don't know what to use.

Play back your recorded sample:

```bash
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 test.wav
```

You should hear your recorded sample. If there are problems, try a different speaker device by changing `-D <device>`.

Make note of your microphone and speaker devices for the next step.

## Running the Satellite

Run the satellite with your microphone/speaker devices:

```bash
script/run \
  --debug \
  --name 'my satellite' \
  --uri 'tcp://0.0.0.0:10700' \
  --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' \
  --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw'
```

Change the `-D <device>` for arecord and aplay to match the audio devices from the previous section.

You can set `--name <NAME>` to whatever you want, but it should stay the same every time you run the satellite.

In Home Assistant, check the "Devices & services" section in Settings. After some time, you should see your satellite show up as "Discovered" (Wyoming Protocol).

Click the "Configure" button and "Submit". Choose the area that your satellite is located, and click "Finish".

Your satellite should say "Streaming audio", and you can use the wake word of your preferred pipeline.

## Running as a Service

You can run wyoming-satellite as a systemd service by first creating a service file:

```bash
sudo systemctl edit --force --full wyoming-satellite.service
```

Paste in the following template, and change both `/home/pi` and the `script/run` arguments to match your set up:

```ini
[Unit]
Description=Wyoming Satellite
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/home/pi/wyoming-satellite/script/run --name 'my satellite' --uri 'tcp://0.0.0.0:10700' --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw'
WorkingDirectory=/home/pi/wyoming-satellite
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Save the file and exit your editor. Next, enable the service to start at boot and run it:

```bash
sudo systemctl enable --now wyoming-satellite.service
```

(you may need to hit CTRL+C to get back to a shell prompt)

With the service running, you can view logs in real-time with:

```bash
journalctl -u wyoming-satellite.service -f
```

Make sure to run `sudo systemctl daemon-reload` every time you make changes to the service.

---

## Local Wake Word Detection

NOTE: This will not work on the 32-bit version of Raspberry Pi OS.

Install a wake word detection service, such as wyoming-openwakeword and start it:

```bash
cd ~
git clone https://github.com/rhasspy/wyoming-openwakeword.git
cd wyoming-openwakeword

python3 -m venv .venv
.venv/bin/pip3 install --upgrade pip
.venv/bin/pip3 install --upgrade wheel setuptools
.venv/bin/pip3 install \
  -f 'https://synesthesiam.github.io/prebuilt-apps/' \
  -r requirements.txt
```

Run the wake word service:

```bash
script/run --uri 'tcp://0.0.0.0:10400' --preload-model 'ok_nabu' --debug
```

Add `--debug` to print additional logs. See `--help` for more information.

Community trained wake words are also available and can be included with `--custom-model-dir <DIR>` where `<DIR>` contains `.tflite` file(s).

Next, start the satellite with some additional arguments:

```bash
cd wyoming-satellite/
script/run \
  --name 'my satellite' \
  --uri 'tcp://0.0.0.0:10700' \
  --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' \
  --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw' \
  --wake-uri 'tcp://127.0.0.1:10400' \
  --wake-word-name 'ok_nabu'
```

Audio will only be streamed to the server after the wake word has been detected.

Once a wake word has been detected, it can not be detected again for several seconds (called the "refractory period"). You can change this with `--wake-refractory-seconds <SECONDS>`.

Note that `--vad` is unnecessary when connecting to a local instance of openwakeword.

### Audio Feedback

You can play a WAV file when the wake word is detected (locally or remotely), and when speech-to-text has completed:

- `--awake-wav <WAV>` - played when the wake word is detected
- `--done-wav <WAV>` - played when the voice command is finished
- `--timer-finished-wav <WAV>` - played when a timer is finished

If you want to play audio files other than WAV, use event commands.

---

## Wake Word Service Systemd

Create a systemd service for openWakeWord:

```bash
sudo systemctl edit --force --full wyoming-openwakeword.service
```

Paste this template:

```ini
[Unit]
Description=Wyoming openWakeWord

[Service]
Type=simple
ExecStart=/home/pi/wyoming-openwakeword/script/run --uri 'tcp://127.0.0.1:10400' --preload-model 'ok_nabu'
WorkingDirectory=/home/pi/wyoming-openwakeword
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Then enable and start:

```bash
sudo systemctl enable --now wyoming-openwakeword.service
```

Update the satellite service to depend on and connect to openWakeWord:

```bash
sudo systemctl edit --force --full wyoming-satellite.service
```

```ini
[Unit]
Description=Wyoming Satellite
Wants=network-online.target
After=network-online.target
Requires=wyoming-openwakeword.service

[Service]
Type=simple
ExecStart=/home/pi/wyoming-satellite/script/run --name 'my satellite' --uri 'tcp://0.0.0.0:10700' --mic-command 'arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t raw' --snd-command 'aplay -D plughw:CARD=seeed2micvoicec,DEV=0 -r 22050 -c 1 -f S16_LE -t raw' --wake-uri 'tcp://127.0.0.1:10400' --wake-word-name 'ok_nabu'
WorkingDirectory=/home/pi/wyoming-satellite
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart wyoming-satellite.service
```

Check status:

```bash
sudo systemctl status wyoming-satellite.service wyoming-openwakeword.service
```

They should all be "active (running)" and green.

Test out your satellite by saying "ok, nabu" and a voice command.

Use journalctl to check the logs of services for errors:

```bash
journalctl -u wyoming-satellite.service -u wyoming-openwakeword.service -f
```

---

## LED Feedback Service

Example event services for the ReSpeaker 2Mic and 4Mic HATs are included in `wyoming-satellite/examples` that will change the LED color depending on the satellite state.

The example below is for the 2Mic HAT, using `2mic_service.py`. If you're using the 4Mic HAT, use `4mic_service.py` instead as the LEDs and GPIO pins are slightly different.

Install the requirements:

```bash
cd wyoming-satellite/examples
python3 -m venv --system-site-packages .venv
.venv/bin/pip3 install --upgrade pip
.venv/bin/pip3 install --upgrade wheel setuptools
.venv/bin/pip3 install 'wyoming==1.5.2'
```

You may also need to install GPIO packages:

```bash
sudo apt-get install python3-spidev python3-gpiozero
```

Create a systemd service for the LED service:

```bash
sudo systemctl edit --force --full 2mic_leds.service
```

Paste this template:

```ini
[Unit]
Description=2Mic LEDs
Wants=wyoming-satellite.service
After=wyoming-satellite.service

[Service]
Type=simple
ExecStart=/home/pi/wyoming-satellite/examples/.venv/bin/python3 2mic_service.py --uri 'tcp://127.0.0.1:10500'
WorkingDirectory=/home/pi/wyoming-satellite/examples
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
```

Update the satellite service to include `--event-uri`:

```bash
sudo systemctl edit wyoming-satellite.service
```

Add `--event-uri 'tcp://127.0.0.1:10500'` to the ExecStart line.

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now 2mic_leds.service
sudo systemctl restart wyoming-satellite.service
```

The LEDs should now change color based on the satellite state:
- **Idle** - LEDs off
- **Listening** - LEDs blue
- **Processing** - LEDs purple
- **Speaking** - LEDs green

---

## Troubleshooting

### Satellite Not Appearing in Home Assistant

- Check network connectivity between Pi and Home Assistant
- Verify the satellite service is running: `sudo systemctl status wyoming-satellite`
- Check firewall settings
- Verify mDNS/Avahi is installed: `sudo apt install avahi-daemon`

### Wake Word Not Detecting

- Check openWakeWord service: `journalctl -u wyoming-openwakeword -f`
- Adjust microphone volume with `alsamixer`
- Try different sensitivity with `--threshold 0.3`

### Audio Problems

- Run `arecord -l` and `aplay -l` to verify devices
- Test recording/playback manually
- Check power supply (use 2.5A+ for Pi Zero 2 W)
- Adjust volumes with `alsamixer` (press F6 to select sound card)

### Services Won't Start

- Check logs: `journalctl -u <service-name> -b`
- Verify paths in service files are correct
- Run `sudo systemctl daemon-reload` after editing services
