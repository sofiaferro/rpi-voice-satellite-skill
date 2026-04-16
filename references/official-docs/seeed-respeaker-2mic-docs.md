# ReSpeaker 2-Mics Pi HAT - Official Documentation

This file contains the official Seeed Studio documentation for the ReSpeaker 2-Mics Pi HAT.

**Sources:**
- Overview: https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/
- Raspberry Pi Setup (v1): https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT_Raspberry/
- Raspberry Pi Setup (v2): https://wiki.seeedstudio.com/respeaker_2_mics_pi_hat_raspberry_v2/

---

# Overview

ReSpeaker 2-Mics Pi HAT is a dual-microphone expansion board for Raspberry Pi designed for AI and voice applications. This means that you can build a more powerful and flexible voice product that integrates Amazon Alexa Voice Service, Google Assistant, and so on.

The board is developed based on WM8960, a low power stereo codec. There are 2 microphones on both sides of the board for collecting sounds and it also provides 3 APA102 RGB LEDs, 1 User Button and 2 on-board Grove interfaces for expanding your applications. What is more, 3.5mm Audio Jack or JST 2.0 Speaker Out are both available for audio output.

## Features

- Raspberry Pi compatible (Support Raspberry Pi Zero and Zero W, Raspberry Pi B+, Raspberry Pi 2 B, Raspberry Pi 3 B, Raspberry Pi 3 B+, Raspberry Pi 3 A+ and Raspberry Pi 4)
- 2 Microphones
- 2 Grove Interfaces
- 1 User Button
- 3.5mm Audio Jack
- JST2.0 Speaker Out
- Max Sample Rate: 48Khz

## Application Ideas

- Voice Interaction Application
- AI Assistant

## Hardware Overview

```
+----------------------------------+
|  MIC_L                    MIC_R  |
|    O                        O    |
|                                  |
|  [Grove I2C]      [Grove GPIO]   |
|                                  |
|        +----------------+        |
|        |    WM8960      |        |
|        |   (Codec)      |        |
|        +----------------+        |
|                                  |
|  O O O  <- RGB LEDs (APA102)     |
|                                  |
|  [BUTTON]            [3.5mm JACK]|
|                                  |
|  [JST Speaker]    [Micro USB PWR]|
|                                  |
|  ||||||||||||||||||||||||||||||| |
|     40-Pin Raspberry Pi Header   |
+----------------------------------+
```

Component Details:
- **BUTTON**: User Button, connected to GPIO17
- **MIC_L and MIC_R**: 2 Microphones on both sides of the board
- **RGB LED**: 3 APA102 RGB LEDs, connected to SPI interface
- **WM8960**: Low power stereo codec
- **Raspberry Pi 40-Pin Headers**: Support Raspberry Pi Zero, Raspberry Pi 1 B+, Raspberry Pi 2 B, Raspberry Pi 3 B, Raspberry Pi 3 B+, Raspberry Pi 4
- **POWER**: Micro USB port for powering the ReSpeaker 2-Mics Pi HAT. Power the board for providing enough current when using the speaker.
- **I2C**: Grove I2C port, connected to I2C-1
- **GPIO12**: Grove digital port, connected to GPIO12 & GPIO13
- **JST 2.0 SPEAKER OUT**: For connecting speaker with JST 2.0 connector
- **3.5mm AUDIO JACK**: For connecting headphone or speaker with 3.5mm Audio Plug

---

# Getting Started with Raspberry Pi (v1 Hardware)

> **Note:** This documentation is for ReSpeaker 2-Mics Pi HAT **v1**. To distinguish v1 and v2 devices, see: https://wiki.seeedstudio.com/how-to-distinguish-respeaker_2-mics_pi_hat-hardware-revisions/

## Driver Installation and Configuration

### 1. Connect ReSpeaker 2-Mics Pi HAT to Raspberry Pi

Mount ReSpeaker 2-Mics Pi HAT on your Raspberry Pi, make sure that the pins are properly aligned when stacking the ReSpeaker 2-Mics Pi HAT.

### 2. Setup the Driver on Raspberry Pi

Make sure that you are running the latest Raspberry Pi OS on your Pi.

**Step 1:** Get Device Tree Source (DTS) for the ReSpeaker 2-Mics Pi HAT (V1.0), compile it and install the device tree overlay.

```bash
git clone https://github.com/Seeed-Studio/seeed-linux-dtoverlays.git
cd seeed-linux-dtoverlays/
make overlays/rpi/respeaker-2mic-v1_0-overlay.dtbo
sudo cp overlays/rpi/respeaker-2mic-v1_0-overlay.dtbo /boot/firmware/overlays/respeaker-2mic-v1_0.dtbo
echo "dtoverlay=respeaker-2mic-v1_0" | sudo tee -a /boot/firmware/config.txt
```

**Step 2:** Reboot your Pi.

```bash
sudo reboot
```

**Step 3:** Check that the sound card name matches the source code seeed-voicecard by command `aplay -l` and `arecord -l`.

```
pi@raspberrypi:~/Desktop/mic_hat $ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
  Subdevices: 8/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7
card 1: vc4hdmi0 [vc4-hdmi-0], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 2: vc4hdmi1 [vc4-hdmi-1], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 3: seeed2micvoicec [seeed-2mic-voicecard], device 0: bcm2835-i2s-wm8960-hifi wm8960-hifi-0 [bcm2835-i2s-wm8960-hifi wm8960-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

pi@raspberrypi:~/Desktop/mic_hat $ arecord -l
**** List of CAPTURE Hardware Devices ****
card 3: seeed2micvoicec [seeed-2mic-voicecard], device 0: bcm2835-i2s-wm8960-hifi wm8960-hifi-0 [bcm2835-i2s-wm8960-hifi wm8960-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

**Step 4:** Test, you will hear what you say to the microphones (don't forget to plug in an earphone or a speaker):

```bash
arecord -D "plughw:3,0" -f S16_LE -r 16000 -d 5 -t wav test.wav
aplay -D "plughw:3,0" test.wav
```

> **Note:** "plughw:3,0" is the recording (or playback device number), depending on your system this number may differ (for example on Raspberry Pi Zero it will be 0, since it doesn't have audio jack). We can find it via `arecord -l` and `aplay -l`.

### 3. Configure Sound Settings with alsamixer

**alsamixer** is a graphical mixer program for the Advanced Linux Sound Architecture (ALSA) that is used to configure sound settings and adjust the volume.

```bash
pi@raspberrypi:~ $ alsamixer
```

The Left and right arrow keys are used to select the channel or device and the Up and Down Arrows control the volume for the currently selected device. Quit the program with ALT+Q, or by hitting the Esc key.

> **Important:** Please use F6 to select seeed-2mic-voicecard device first.

---

## Usage Overview

To run the following examples, clone the mic_hat repository to your Raspberry Pi:

```bash
git clone https://github.com/respeaker/mic_hat.git
cd mic_hat
```

All the Python scripts mentioned in the examples below can be found inside this repository. To install the necessary dependencies, from mic_hat repository folder, run:

```bash
sudo apt-get install portaudio19-dev libatlas-base-dev
pip3 install -r requirements.txt
```

### APA102 LEDs

Each on-board APA102 LED has an additional driver chip. The driver chip takes care of receiving the desired color via its input lines, and then holding this color until a new command is received.

```bash
python3 interfaces/pixels.py
```

### User Button

There is an on-board User Button, which is connected to GPIO17. Now we will try to detect it with python and RPi.GPIO.

Execute the following code from mic_hat folder repository:

```bash
python3 interfaces/button.py
```

It should display "on" when you press the button:

```
pi@raspberrypi:~ $ python3 button.py
off
off
on
on
off
```

---

## Record Sound with Python

We use PyAudio python library to record sound with Python.

First, run the following script to get the device index number of 2 Mic pi hat:

```bash
python3 recording_examples/get_device_index.py
```

You will see the device ID as below:

```
Input Device id  2  -  seeed-2mic-voicecard: - (hw:1,0)
```

To record the sound, open `recording_examples/record.py` file with nano or other text editor and change `RESPEAKER_INDEX = 2` to index number of ReSpeaker on your system. Then run python script record.py to make a recording:

```bash
python3 recording_examples/record.py
```

If you want to extract channel 0 data from 2 channels, have a look at the content of `record_one_channel.py`. For other channel X, please change `[0::2]` to `[X::2]`.

```bash
python3 recording_examples/record_one_channel.py
```

To play the recorded samples you can either use aplay system utility:

```bash
aplay -f cd -Dhw:1 output.wav        # for Stereo sound
aplay -D plughw:1,0 output_one_channel.wav  # for Mono sound from one channel
```

Alternatively you can use `recording_examples/play.py` script to play the .wav files with PyAudio.

```bash
python3 recording_examples/play.py path-to-wav-file
```

> **Note:** Make sure to specify the right output device index in play.py - otherwise PyAudio will freeze!

---

## Picovoice with ReSpeaker 2-Mic Pi HAT and Raspberry Pi

**Step 1.** Follow the above step-by-step tutorial of ReSpeaker 2-Mic Pi HAT with Raspberry Pi before the following.

> **Note:** Please make sure that the APA102 LEDs are working properly on the ReSpeaker 2-Mic Pi HAT with Raspberry Pi.

**Step 2.** Type the following command on the terminal to install the Picovoice demo for ReSpeaker 2-Mic Pi HAT.

```bash
pip3 install pvrespeakerdemo
```

> **Note:** On fresh Raspberry Pi OS installation you might notice the following warning when installing this demo:
> `The script picovoice_respeaker_demo is installed in '/home/pi/.local/bin' which is not on PATH.`
>
> It means that in order to run the demo, you need to add /home/pi/.local/bin to your system PATH:
> ```bash
> echo 'export PATH="$HOME/bin:$HOME/.local/bin:$PATH"' >> ~/.bashrc
> ```

### Demo Usage

The demo utilizes the ReSpeaker 2-Mic Pi HAT on a Raspberry Pi with Picovoice technology to control the LEDs. **This demo is triggered by the wake word "Picovoice"** and will be ready to take follow-on actions, such as turning LEDs on and off, and changing LED colors.

After the installation is finished, type this command to run the demo on the terminal:

```bash
picovoice_respeaker_demo
```

### Voice Commands

Here are voice commands for this demo:

- **"Picovoice"** - Wake word. The demo outputs: `wake word`

- **"Turn on the lights"** - You should see the lights turned on and the following message on the terminal:
  ```
  {
      is_understood : 'true',
      intent : 'turnLights',
      slots : {
          'state' : 'on',
      }
  }
  ```

The list of commands are shown on the terminal:

```
context:
  expressions:
    turnLights:
      - "[switch, turn] $state:state (all) (the) [light, lights]"
      - "[switch, turn] (all) (the) [light, lights] $state:state"
    changeColor:
      - "[change, set, switch] (all) (the) (light, lights) (color) (to) $color:color"
  slots:
    state:
      - "off"
      - "on"
    color:
      - "blue"
      - "green"
      - "orange"
      - "pink"
      - "purple"
      - "red"
      - "white"
      - "yellow"
```

Also, you can try this command to change the colour:
- **"Picovoice, set the lights to orange"**

Turn off the lights by:
- **"Picovoice, turn off all lights"**

### Demo Source Code

The demo is built with the **Picovoice SDK**. The demo source code is available on GitHub at https://github.com/Picovoice/picovoice/tree/master/demo/respeaker

### Different Wake Words

The Picovoice SDK includes free sample wake words licensed under Apache 2.0, including major voice assistants (e.g. "Hey Google", "Alexa") and fun ones like "Computer" and "Jarvis".

### Custom Voice Commands

The lighting commands are defined by a Picovoice *Speech-to-Intent context*. You can design and train contexts by typing in the allowed grammar using Picovoice Console. You can test your changes in-browser as you edit with the microphone button. Go to Picovoice Console (https://picovoice.ai/console/) and sign up for an account. Use the **Rhino Speech-to-Intent editor** to make contexts, then train them for Raspberry Pi.

---

## Multiple Wake Word Examples with Porcupine

**Porcupine** is a highly-accurate and lightweight wake word engine. It enables building always-listening voice-enabled applications. It is:

- Using deep neural networks trained in real-world environments.
- Compact and computationally-efficient. It is perfect for IoT.
- Cross-platform. Raspberry Pi, BeagleBone, Android, iOS, Linux (x86_64), macOS (x86_64), Windows (x86_64), and web browsers are supported.
- Scalable. It can detect multiple always-listening voice commands with no added runtime footprint.
- Self-service. Developers can train custom wake word models using Picovoice Console.

### Multi Wake Word Getting Started

Running the following command in terminal to install demo driver:

```bash
pip3 install ppnrespeakerdemo
```

### Multi Wake Word Usage

Run the following in terminal after the driver installation:

```bash
porcupine_respeaker_demo
```

Wait for the demo to initialize and print `[Listening]` in the terminal. Say:

> Picovoice

The demo outputs:
```
detected 'Picovoice'
```

The lights are now set to green. Say:

> Alexa

The lights are set to yellow now. Say:

> Terminator

to turn off the lights.

### Wake Word to Colors

Below are the colors associated with supported wake words for this demo:

| Wake Word | Color | Hex |
|-----------|-------|-----|
| Alexa | Yellow | #ffff33 |
| Bumblebee | Orange | #ff8000 |
| Computer | White | #ffffff |
| Hey Google | Red | #ff0000 |
| Hey Siri | Purple | #800080 |
| Jarvis | Pink | #ff3399 |
| Picovoice | Green | #00ff00 |
| Porcupine | Blue | #0000ff |
| Terminator | Off | #000000 |

### Multiple Wake Word Example Source Code

Please see the complete source code of this example here: https://github.com/Picovoice/porcupine/tree/master/demo/respeaker

---

## Keyword Spotting with Mycroft Precise

Mycroft Precise is a completely open-source keyword detection engine. While it has more limited functionality comparing to Picovoice, it also has more permissive license (Apache 2.0), which allows modification and redistribution, including closed-source and commercial, as long as license is preserved.

To get started with Mycroft Precise, install latest stable version of Seeed's Mycroft Precise fork:

```bash
sudo apt-get install libatlas-base-dev
pip3 install git+https://github.com/respeaker/mycroft_runner_simple.git
```

> **Note:** On fresh Raspberry Pi OS installation you might notice the following warning when installing this demo:
> `The script picovoice_respeaker_demo is installed in '/home/pi/.local/bin' which is not on PATH.`
>
> It means that in order to run the demo, you need to add /home/pi/.local/bin to your system PATH:
> ```bash
> echo 'export PATH="$HOME/bin:$HOME/.local/bin:$PATH"' >> ~/.bashrc
> ```

Then you can test Mycroft Precise installation simply by running:

```bash
mycroft-precise --model hey-mycroft
```

If you'd like to integrate Mycroft Precise into your own project, check Github repository README file for more information on the API.

---

## Picovoice with ReSpeaker 2-Mic Pi HAT and Raspberry Pi Zero

**Step 1.** Install the drivers and configure the device as described in Driver installation and configuration.

Then git clone Picovoice github repository:

```bash
git clone --recurse-submodules https://github.com/Picovoice/picovoice.git
cd picovoice
```

> **Note:** Please make sure that the APA102 LEDs are working properly on the ReSpeaker 2-Mic Pi HAT with Raspberry Pi Zero.

**Step 2.** Install the `wiringpi` library by typing the following on the terminal.

```bash
sudo apt-get install wiringpi
```

**Step 3.** From the root of the repository, type the following command on the terminal to install the Picovoice demo for ReSpeaker 2-Mic Pi HAT.

```bash
gcc -std=c99 -O3 -o demo/respeaker-rpi0/picovoice_demo_mic \
-I sdk/c/include/ demo/respeaker-rpi0/picovoice_demo_mic.c \
-ldl -lasound -lwiringPi
```

### Demo Usage

The demo utilizes the ReSpeaker 2-Mic Pi HAT on a Raspberry Pi Zero with Picovoice technology to control the LEDs. **This demo is triggered by the wake word "Picovoice"** and will be ready to take follow-on actions, such as turning LEDs on and off, and changing LED colors.

After the installation is finished, type this command from the root of the repository, to run the demo on the terminal:

```bash
./demo/respeaker-rpi0/picovoice_demo_mic \
sdk/c/lib/raspberry-pi/arm11/libpicovoice.so \
resources/porcupine/lib/common/porcupine_params.pv \
resources/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn \
0.65 \
resources/rhino/lib/common/rhino_params.pv \
demo/respeaker/pvrespeakerdemo/respeaker_raspberry-pi.rhn \
0.5 \
plughw:CARD=seeed2micvoicec,DEV=0
```

### Voice Commands (same as above)

- **"Picovoice"** - Wake word
- **"Turn on the lights"** - Turns on LEDs
- **"Picovoice, set the lights to orange"** - Changes color
- **"Picovoice, turn off all lights"** - Turns off LEDs

### Demo Source Code

The demo is built with the **Picovoice SDK**. The demo source code is available on GitHub at https://github.com/Picovoice/picovoice/tree/master/demo/respeaker-rpi0

---

## FAQ

**Q1: #include "portaudio.h" Error when run "sudo pip install pyaudio".**

A1: Please run below command to solve the issue.
```bash
sudo apt-get install portaudio19-dev
```

**Q2: How to change the Raspbian Mirrors source?**

A2: Please refer to Raspbian Mirrors (http://www.raspbian.org/RaspbianMirrors) and follow below instructions to modify the source at beginning.

```bash
pi@raspberrypi ~ $ sudo nano /etc/apt/sources.list
```

For example, we suggest use the Tsinghua source for China users. So please modify the sources.list as below.

```
deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib
deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib
```

---

## Resources

- **[Eagle]** Respeaker_2_Mics_Pi_HAT_SCH: https://files.seeedstudio.com/wiki/MIC_HATv1.0_for_raspberrypi/src/ReSpeaker%202-Mics%20Pi%20HAT_SCH.zip
- **[Eagle]** Respeaker_2_Mics_Pi_HAT_PCB: https://files.seeedstudio.com/wiki/MIC_HATv1.0_for_raspberrypi/src/ReSpeaker%202-Mics%20Pi%20HAT_PCB.zip
- **[PDF]** Respeaker_2_Mics_Pi_HAT_SCH: https://files.seeedstudio.com/wiki/MIC_HATv1.0_for_raspberrypi/src/ReSpeaker%202-Mics%20Pi%20HAT_SCH.pdf
- **[PDF]** Respeaker_2_Mics_Pi_HAT_PCB: https://files.seeedstudio.com/wiki/MIC_HATv1.0_for_raspberrypi/src/ReSpeaker%202-Mics%20Pi%20HAT_PCB.pdf
- **[3D]** ReSpeaker 2 Mics Pi HAT 3D: https://files.seeedstudio.com/wiki/MIC_HATv1.0_for_raspberrypi/src/ReSpeaker%202-Mics%20Pi%20HAT.zip
- **[Driver]** Seeed-Voice Driver: https://github.com/respeaker/seeed-voicecard
- **[Algorithms]** Algorithms includes DOA, VAD, NS: https://github.com/respeaker/mic_array
- **[Voice Engine]** Voice Engine project: https://github.com/voice-engine/voice-engine
- **[Algorithms]** AEC: https://github.com/voice-engine/ec
