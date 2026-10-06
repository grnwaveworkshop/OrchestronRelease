# Orchestron

Orchestron is firmware for an all-in-one audio and motion controller for droids and
animatronics. One board takes a live voice and two WAV players and mixes them to one output,
changes the voice in real time, and drives up to eight servos from an RC transmitter, a button
pad, timed sequences or the sound itself. Everything is set from a PC app, a serial menu or text
files on the SD card, without reflashing.

This repository holds the released firmware, the user manual and an example SD card.

Current release: **2.32.1** (October 2026). See [CHANGELOG.md](CHANGELOG.md).

## The board

<a href="https://grnwave.com/product/vocalizer-v3-with-teensy/">
<img src="https://grnwave.com/wp-content/uploads/2025/12/PXL_20251203_001538426_NB-scaled.jpg"
     alt="Vocalizer V3 with Teensy" width="420">
</a>

Orchestron runs on the **[Vocalizer V3 with Teensy](https://grnwave.com/product/vocalizer-v3-with-teensy/)**
from [Grnwave Workshop](https://grnwave.com): a Teensy 4.1 on a board with the audio codec
built in (no separate Teensy audio board needed). It is the board T4VOC-301 R3.1.D in the manual.
Add a FAT32 microSD card (32 GB or smaller) for the settings and sounds.

## What it does

**Audio**
- The live voice (microphone or line in) and two WAV players, each with its own volume, mixed
  to the line out.
- Real-time voice effects: pitch shift, ring modulator, stormtrooper helmet filter, reverb,
  noise gate, filters. Each switches on and off on its own.
- Stormtrooper "radio on / off" clicks when you start and stop talking.
- WAV playback by number, a random file from a bank or a number range, or the next file in a
  bank.

**Motion**
- Eight servo outputs with per-servo calibration, speed and easing curves.
- RC control from an SBUS receiver or up to eight RC PWM channels, with link-loss detection
  and a choice of failsafe.
- Four operating modes: IDLE, MANUAL, CONTROL (sticks) and AUTO (the droid moves by itself).
- Sequences: timed servo moves and sounds in a text file, which add to the sticks or override
  them, and can call each other as reusable clips.

**Switches, sticks and buttons** (`events.ini`)
- One file says what every control does: a switch position, a stick past a value, a click,
  double click or long press on a 14-button pad, the RC link dropping, a mode change.
- Rules can start sequences and sounds, change the mode, apply voice presets or change any
  setting.

**Things it does by itself** (activities)
- Random chatter, music playlists (in order or shuffled), a sequence picked now and then, and
  lifelike idle motion in AUTO, where servos drift, pause and take turns.

**Sound-reactive**
- A talking jaw on any servo that follows the voice or a WAV, and a NeoPixel strip that follows
  the voice.

**Setup**
- [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp), a PC app over USB: every setting
  as a slider with a description, live telemetry, buttons for every action, and an editor for
  `events.ini` with Learn (move a control and it picks the channel), Test, and a live view of
  which rule fired.
- A serial menu that works from any terminal program.
- USB drive mode: the SD card appears on the PC so files can be copied without removing it.

## What's in this repository

| Path | Contents |
|---|---|
| [`firmware/`](firmware/) | The firmware as a `.hex` file for Teensy Loader (the latest release; earlier ones are in the repository history) |
| [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md) | The user manual |
| [`SDCardExamples/`](SDCardExamples/) | An example SD card: `config.ini` with every setting described, `events.ini`, `sequences.ini` with test sequences, two droid sounds and two music tracks |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed in each release |
| [`LICENSE`](LICENSE) | The license (non-commercial use) |

## Getting started

1. **Load the firmware.** Install Teensy Loader (part of Teensyduino, from
   [pjrc.com](https://www.pjrc.com/teensy/loader.html)). Connect the board by USB, open
   `firmware/Orchestron_v2.32.1.hex` in Teensy Loader (File > Open HEX File), and press the
   button on the Teensy. The board reboots when it's done.
2. **Prepare the SD card.** Format a microSD card FAT32 and copy everything in
   `SDCardExamples/` to the root of the card (not into a folder). Put it in the Teensy's card
   slot.
3. **Connect audio.** An amplifier or powered speaker on LINE OUT; a microphone on MIC IN or a
   line source on LINE IN.
4. **Power up over USB.** The droid says hello: the example card plays a sound at power-up.
5. **Try it without a transmitter.** In ConfigApp, connect to the board's COM port and open the
   Actions tab:
   - each sequence button (wave, nod, look, greet, dance) plays sounds and moves servos S1-S4
   - "Music on" plays the music tracks; "Random sounds off" stops them
   - "Mode AUTO" makes the droid move by itself

   Or open the COM port in a serial terminal (115200 baud) and press `m` for the menu.
6. **Connect a receiver.** The example card expects SBUS on J5. The top of
   `SDCardExamples/events.ini` lists which channel does what; change the numbers to match your
   transmitter, or edit it in ConfigApp's Events tab.

The manual's [Getting Started](docs/USER_MANUAL.md#4-getting-started) section has more detail,
and each file on the example card explains its own format in its comments.

## Updating

Load the new `.hex` the same way. Your `config.ini`, sounds and other files on the SD card are
kept, and settings from an older version are converted on the first boot.

## Documentation

- [User manual](docs/USER_MANUAL.md): the board, settings, audio, servos, RC control,
  `events.ini`, sequences, the sound-reactive jaw, NeoPixels, the SBUS recorder, the serial menu
  and command set, troubleshooting.
- [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp): the PC app, with its own setup
  instructions.

## Support

- Problems and questions: open an issue in this repository. Include the firmware version and
  the boot log from the serial console if you can.
- The board: [grnwave.com](https://grnwave.com).

## License

The Orchestron firmware, this manual and the example files are free for personal, educational,
research and non-profit use. Commercial use is not permitted. See [LICENSE](LICENSE).

Copyright (c) 2026 Trevor Z, Grnwave Workshop.
