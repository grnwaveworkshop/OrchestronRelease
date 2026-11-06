# Quick Start 1: Sound Board for Another Controller

**QS-1** · Firmware 2.46.0 · Grnwave Workshop · November 2026 · Draft

Your droid's main controller (a control board, an Arduino, a Teensy, an ESP32...) sends short
text commands down a serial wire. Orchestron plays the sounds, changes the voice and can move a
talking jaw. Orchestron needs no RC receiver of its own.

```
  main controller  ---- serial: <CA1001> ---->  Orchestron  ---- LINE OUT ---->  amplifier
                   <--- replies (optional) ----             <---- mic / line in
```

---

## You need

- Orchestron board with firmware 2.46.0 or later ([how to update](../USER_MANUAL.md#17-updating-the-firmware))
- microSD card: FAT32, 32 GB or smaller, with your sounds (step 2)
- A main controller with a free serial port (UART), set to 115200 baud
- Three wires: TX, RX, GND (two if the controller only sends)
- A mic or a line source (wireless mic receiver), and an amplifier with a speaker
- Power: USB is enough for the board alone; add a 5 V supply on J1 if you use servos or LEDs
- A PC with [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp) or a serial terminal, for setup

---

## 1. Connect it

**Choose the connector** by your controller's serial voltage:

| Your controller | Orchestron connector | Set |
|---|---|---|
| Any UART, 3.3 V or 5 V (most builds) | **J5** | Nothing, if the controller only sends. If it reads replies, fit jumper **J4**: VIO to **5V** for a 5 V Arduino, to **3V3** for a Teensy or ESP32 |
| 3.3 V UART, and J5 is needed for something else | **J3** | `serial.com1.port = 3` (step 3) |
| A long cable, or a droid full of motor noise | **J2**, RS-485 (COM2) | Nothing: COM2 is on by default. Your controller needs an RS-485 transceiver |

**Wire it.** TX goes to RX, RX to TX, and the grounds are always joined. Pins are named as
printed on the board ([pinout photo](https://grnwave.com/teensy-vocalizer-v3-user-manual/)).

```
  MAIN CONTROLLER                    ORCHESTRON  J5 (UART input)
  ---------------                    ---------------------------
  TX   ----------------------------->  RX
  RX   <-----------------------------  TX    (only if it reads replies)
  GND  ------------------------------  G

                                     J4 jumper (only for replies on TX):
                                     VIO to 5V or to 3V3, the controller's voltage

  Mic  ----------------------------->  MIC IN        or   wireless mic receiver --> LINE IN
                                       LINE OUT  ------>  amplifier  ------>  speaker
  5 V supply (+ / -)  -------------->  J1  5V / GND  (or just USB, for the board alone)
  PC (for setup)  ------ USB ------->  Teensy USB
```

The other two connectors, if you chose them:

| J3 (3.3 V only) | | J2 RS-485 | |
|---|---|---|---|
| Controller TX | **RX3** | Transceiver A | **A** |
| Controller RX | **TX3** | Transceiver B | **B** |
| GND | **G** | GND | **G** |

> **J3 is 3.3 V, straight to the Teensy.** Never connect a 5 V TX to it: use J5 instead.

---

## 2. Put your sounds on the card

- **Format:** WAV, 44.1 kHz, 16-bit, uncompressed (Audacity: *Export > WAV, Signed 16-bit PCM*).
- **Names start with a number:** `1001-hello.wav`, `1002-yes.wav`, `2001-music.wav`. The
  controller plays a file by its number. The first digit is the **bank** (`1xxx` = bank 1),
  for random picks.
- **Where:** the root of the card, not a folder.

On first boot Orchestron writes `config.ini` (its settings) and a blank `events.ini`. Leave
`events.ini` as it is: in this setup the controller decides what plays.

---

## 3. Set it up

Connect the PC by USB and open ConfigApp (or a terminal at 115200 baud and press `m` for the
menu). Check these settings:

| Setting | Value | ConfigApp page |
|---|---|---|
| `rc.inputMode` | **2** None (the default): no receiver | `rc` |
| `serial.com1.port` | **1** J5 (the default), or **3** for J3 | `serial` |
| `serial.com1.baudRate` | **115200** (the default); the same as your controller | `serial` |
| `audio.in.source` | **0** line in, or **1** mic | `audio` |
| `servo.s1.enabled`, `servo.s2.enabled` | **0** if nothing is plugged into S1 / S2 | `servo` |

**Save**, then reboot (ConfigApp's Reboot button, or power off and on). Port changes take
effect at boot.

---

## 4. Test from the PC first

Before wiring the controller, prove the card and the audio work. In a terminal on the USB port
(menu closed, press `X` to leave it), type:

```
<CA1001>
```

The sound numbered 1001 plays. `<PSX>` stops it. Talk into the mic: you hear the voice with the
default effects (ring modulator and reverb; change them on ConfigApp's `fx` page).

---

## 5. Send commands from your controller

Each command is a few letters in angle brackets. These cover most droids:

| Send | Does |
|---|---|
| `<CA1001>` / `<CB2001>` | Play WAV 1001 on player A / WAV 2001 on player B (both can play at once) |
| `<PSA>` / `<PSB>` / `<PSX>` | Stop player A / B / both |
| `<PVV75>` / `<PVA80>` / `<PVB50>` | Volume 0-100 of the voice / player A / player B |
| `<PP140>` | Pitch: 100 normal, 140 higher, 80 deeper |
| `<ES4>` / `<EC4>` | Switch one effect on / off (4 = pitch shift; the bits are in the [manual](../USER_MANUAL.md#effects)) |
| `<QPA>` | Is player A playing? Replies `<QPA1>` or `<QPA0>` |
| `<KA,preset:deep>` | Apply a voice preset from `events.ini` |
| `<KA,seq:wave>` | Play a sequence from `sequences.ini` (servos and sounds) |
| `<KA,set:audio.mix.master=60>` | Change any setting, here the master volume |

**Arduino example** (`Serial1` is the UART wired to Orchestron):

```cpp
void playSound(int number) {
  Serial1.print("<CA");
  Serial1.print(number);
  Serial1.print(">");
}

void setup() {
  Serial1.begin(115200);
  delay(3000);              // let Orchestron finish booting
  playSound(1001);          // say hello
}

void loop() {}
```

**Mouth lights:** while someone talks into the mic, Orchestron sends `<QVPnn>` (voice level
0-70) to the controller, often enough to light a mouth in time with the voice.

---

## 6. Optional: a talking jaw

A jaw servo moves to the sound on its own, with no commands:

1. Plug the servo into **S1**, and power J1 with 5 V.
2. Set `react.jaw.servo = 1` and `servo.s1.easingSpeed = 0` (ConfigApp `react` and `servo` pages).
3. Calibrate `servo.s1.pwmMin` / `pwmMax` to the jaw's closed and open positions.

Details: [manual §12](../USER_MANUAL.md#12-sound-reactive-jaw).

---

## If it doesn't work

| Problem | Check |
|---|---|
| Nothing plays, even from the PC | The WAV format and the number in its name; the levels (`audio.mix.master`, `audio.mix.wavA`); the amplifier |
| Plays from the PC, not from the controller | TX to RX crossed over? Grounds joined? Same baud? `serial.com1.port` matches the connector, and you rebooted? |
| Garbled or partly works | The baud rate (115200 by default) |
| The controller never sees replies | Controller RX wired to J5 **TX** (or J3 **TX3**)? J4 fitted, at the controller's voltage? |
| Worked, then stopped when a receiver was added | SBUS on J5 takes COM1 over: move COM1 to J3 (`serial.com1.port = 3`) |

The boot messages on the USB port say which port COM1 opened on.

---

## Next

- Every command: [manual §16, The Command Protocol](../USER_MANUAL.md#16-the-command-protocol)
- Voice effects and mixing: [manual §7, Audio](../USER_MANUAL.md#7-audio)
- Recording audio to the card: [manual §7](../USER_MANUAL.md#recording-audio-2410)
