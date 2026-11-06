# Orchestron Quick Starts

Short, step-by-step guides: wiring, setup and a first test for one kind of build. Pick the one
that matches how your droid is controlled. The [user manual](../USER_MANUAL.md) has the details.

| Guide | Use it when |
|---|---|
| [QS-1: Sound board for another controller](QS1_SERIAL_SOUND_BOARD.md) | Your droid already has a main controller. It sends serial commands; Orchestron does the voice, the sounds and maybe a jaw |
| [QS-2: RC receiver (PWM)](QS2_RC_PWM.md) | A standard RC receiver with one lead per channel (up to 8): sticks move servos, switches and buttons play sounds |
| [QS-3: SBUS receiver](QS3_SBUS.md) | A receiver with an SBUS output: one wire, up to 24 channels, button boxes and pads |

**Where everything is:** the [board pinout](https://grnwave.com/teensy-vocalizer-v3-user-manual/)
on grnwave.com. The guides name pins as they are printed on the board.

<a href="https://grnwave.com/teensy-vocalizer-v3-user-manual/">
<img src="https://grnwave.com/wp-content/uploads/2026/11/v3-pinout-r2.png" alt="Board pinout" width="600">
</a>

**Every build:**
- Power: USB runs the board alone. Servos, LEDs and a receiver need a regulated **5 V** supply
  on J1 (not 6 V or 7.4 V).
- Sounds: WAV, 44.1 kHz, 16-bit, in the card's root, named with a number first
  (`1001-hello.wav`).
- Settings: [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp) over USB, or the serial
  menu (115200 baud, press `m`).
