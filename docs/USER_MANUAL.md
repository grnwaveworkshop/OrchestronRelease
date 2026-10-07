# Orchestron User Manual

**Firmware 2.32.1** · October 2026 · Board: T4VOC-301 R3.1.D (Teensy 4.1)

Orchestron is an all-in-one audio and motion controller for droids and animatronics. One board
takes a live voice and two WAV players, and mixes all three to one output. It changes the voice
in real time, and drives up to eight servos from an RC transmitter, buttons, sequences or the
sound itself. Everything is set from a PC app, a serial menu or a text file on the SD card. No
reflashing needed.

This manual is about using the product. The latest firmware, this manual and an example SD card
are at [https://github.com/grnwaveworkshop/OrchestronRelease](https://github.com/grnwaveworkshop/OrchestronRelease).

---

## Contents

1. [Features](#1-features)
2. [What You Need](#2-what-you-need)
3. [The Board](#3-the-board)
4. [Getting Started](#4-getting-started)
5. [Configuring Orchestron](#5-configuring-orchestron)
6. [Operating Modes](#6-operating-modes)
7. [Audio](#7-audio)
8. [Servos](#8-servos)
9. [RC Control](#9-rc-control)
10. [Switches, Sticks and Buttons](#10-switches-sticks-and-buttons-eventsini)
11. [Sequences](#11-sequences)
12. [Sound-Reactive Jaw](#12-sound-reactive-jaw)
13. [NeoPixel Strip](#13-neopixel-strip)
14. [SBUS Recorder](#14-sbus-recorder)
15. [Pin Types](#15-pin-types)
16. [Connecting Other Controllers](#16-connecting-other-controllers)
17. [Updating the Firmware](#17-updating-the-firmware)
18. [Menu Reference](#18-menu-reference)
19. [Troubleshooting](#19-troubleshooting)
20. [Specifications](#20-specifications)
21. [Firmware History](#21-firmware-history)

---

## 1. Features

**Audio**
- **Three sources, one output:** the live voice (mic or line in) and two independent WAV players
  (A and B), each with its own volume, mixed to the line out.
- **Real-time voice changing:** pitch shift (0.5x to 3x without changing speed), ring
  modulator, stormtrooper helmet filter, reverb, noise gate, and high/low-pass filters before
  and after the effects.
  - Each effect switches on and off on its own, and changes apply instantly.
- **Stormtrooper radio sounds:** a "radio on" sound when you start talking and a "radio off"
  sound when you stop. Pauses between words don't trigger them.
- **WAV playback** from the SD card, by number, from buttons, sequences or serial commands.
  Random picks from a bank are supported.

**Motion**
- **8 servo outputs** with per-servo calibration, speed and easing curves (linear, cubic, sine,
  and more).
- **RC control** from an SBUS receiver or up to 8 RC PWM channels, with link-loss detection and a
  choice of failsafe action.
- **Four operating modes:** IDLE, MANUAL, CONTROL (sticks) and AUTO (random lifelike movement).
- **Sequences:** timed servo moves and sounds in a text file. They add to the sticks (a nod on
  top of where you're pointing the head) or override them.
- **Button pad and switches:** click, double, triple, long press and shift-style combinations,
  each able to start sequences, sounds or mode changes.
- **SBUS recorder:** records your transmitter moves, with a song, to a file on the SD card.

**Sound-reactive**
- **Talking jaw:** any servo can move to the sound of a WAV or the live voice. An FFT picks out
  the vowels and ignores the "s" sounds, so the jaw looks like it's speaking, even over music.
- **NeoPixel strip:** LEDs that follow the voice: throb, bar, VU, rings or a spectrum display.

**Setup**
- **ConfigApp:** a PC app that connects over USB, lists every setting on tidy pages with
  sliders and descriptions, and saves to the card.
- **Serial menu:** works from any terminal program, no app needed.
- **`config.ini`:** a plain text file on the SD card, written automatically.
- **USB drive mode:** the SD card appears on your PC so you can copy sounds and files without
  removing it.

**Good for:** DJ-R3X and other RX droids, smaller astromechs, BB-style droids, mouse droids,
talking heads and skulls, helmets, and props.

---

## 2. What You Need

- **Orchestron board:** the [Vocalizer V3 with Teensy](https://grnwave.com/product/vocalizer-v3-with-teensy/)
  from Grnwave Workshop (board T4VOC-301 R3.1.D, with a Teensy 4.1).
- **microSD card:** FAT32, 32 GB or smaller, Class 10.
- **5 V power:** USB is enough for the board alone. Servos and LEDs need their own 5 V supply
  through the power connector, sized for them (a typical servo can draw 1 A or more when it
  stalls).
- **Audio:**
  - in: an electret mic on MIC IN, or a line-level source (wireless mic receiver, mixer) on
    LINE IN
  - out: an amplifier or powered speaker on LINE OUT
- **For control (optional):** an SBUS receiver, or an RC receiver with PWM outputs.
- **A PC with:**
  - [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp) (recommended; Python, Windows / Mac /
    Linux), or
  - any serial terminal: PuTTY, Tera Term or the Arduino Serial Monitor on Windows; `screen` or
    `picocom` on Mac/Linux.

---

## 3. The Board

```
+------------------------------------------+
|           ORCHESTRON  (T4VOC-301)        |
|                                          |
|  [S1][S2][S3][S4][S5][S6][S7][S8]        |  servo outputs (3.3 V signal)
|  [IO1][IO2][IO3][IO4][IO5][IO6][IO7][IO8]|  level-shifted I/O (5 V signal)
|                                          |
|  MIC IN   LINE IN   LINE OUT             |  audio
|  J5 UART IN   J3 UART   J2 RS-485        |  serial / SBUS
|  SW2 (USB drive button)   LED_A  LED_B   |
+------------------------------------------+
        USB                 SD card
```

### Audio connectors

| Connector | Use |
|---|---|
| **MIC IN** (2-pin) | Electret microphone |
| **LINE IN** (3.5 mm) | Line-level source, such as a wireless mic receiver |
| **LINE OUT** (3.5 mm) | The mixed output, to an amplifier |

### Servo outputs S1-S8

Standard servo headers with a 3.3 V signal, which almost every servo accepts. Any one of them
can drive a NeoPixel strip instead (§13).

### I/O pins IO1-IO8

Level-shifted to 5 V. By default they read RC PWM receiver channels. Any one can drive a
NeoPixel strip (§13). IO5 and IO6 can instead carry a serial port (§16).

### Serial ports

| Port | Connector | Use |
|---|---|---|
| **USB** | Teensy USB | Menu, ConfigApp, commands, power |
| **COM1** | J5 (default), J3, or IO5/IO6 | Commands from another controller; J5 is also the best input for SBUS |
| **COM2** | J2, RS-485 | Commands over a long or noisy cable |

### LEDs and button

| | Meaning |
|---|---|
| **LED_B** | On: booted and running |
| **LED_A** | Fading: USB drive mode is on |
| **SW2** | Hold for half a second: USB drive mode on/off |

---

## 4. Getting Started

1. **Prepare the SD card.** Format it FAT32 and put it in the Teensy's card slot. Copy any WAV
   files to the root (see [WAV files](#wav-files)). The `SDCardExamples/` folder (in [OrchestronRelease](https://github.com/grnwaveworkshop/OrchestronRelease)) is
   a ready-made starting card (2.32.0). Copy it all to the card and the droid says hello at
   power-up, with no transmitter. It has `config.ini` with every setting described, an
   `events.ini` and a `sequences.ini` with test sequences (all with instructions inside), and four
   sounds: two droid sounds and two music tracks. Try ConfigApp's Actions tab: each sequence
   button, "Music on", "Mode AUTO".
2. **Connect audio:** a mic or line source in, an amplifier on LINE OUT.
3. **Power up over USB.** On the first boot Orchestron creates `config.ini` with factory
   settings. LED_B comes on when it's ready.
4. **Connect from the PC:**
   - **ConfigApp:** pick the board's COM port and Connect. It recognises Orchestron and shows its
     settings pages.
   - **Terminal:** open the board's COM port (115200 baud, 8N1) and press `m` for the menu
     (main menu `A` shows the system status).
5. **Talk.** The default setup is the effects chain with pitch shift off, ring modulator and
   reverb on. Turn effects on and off in ConfigApp's `fx` page or menu `1`.
6. **Save** with ConfigApp's Save, or `S` in the menu. Settings live in `config.ini`.

**RC input is off at first** (`rc.inputMode` = 2, None), so a board with nothing connected keeps
all its serial ports free. Set it to 0 (SBUS) or 1 (RC PWM) when you connect a receiver, then
reboot (§9).

---

## 5. Configuring Orchestron

Every setting has a name like `fx.pitch.amount` or `servo.s1.home`. The three ways to change
settings all edit the same values, and changes apply at once (the few that need a reboot say
so).

### ConfigApp (recommended)

ConfigApp shows the settings as pages, with a slider and a description for each. The first part
of a name is the page and the second is the tab:

| Page | What's on it |
|---|---|
| `audio` | Input source and gain; mix levels (master, voice, WAV A, WAV B, line out); effects or passthrough |
| `fx` | The voice effects, one tab each: `pre`, `amp`, `gate`, `pitch`, `ring`, `trooper`, `clicks` (radio sounds), `reverb`, `post` |
| `servo` | Tabs `s1`..`s8`: calibration, speed, easing, AUTO-mode ranges, detach |
| `react` | The talking jaw: `jaw`, `band`, `level`, `motion` |
| `neo` | NeoPixel look, plus the `strip` hardware settings |
| `rc` | Input mode, link loss, `sbus`, `pwm` (what the switches do is the Events tab, §10) |
| `button` | Button pad levels and gesture timing |
| `rec` | SBUS recorder |
| `pin` | What each servo and IO pin is used for |
| `serial` | COM ports |

Edits apply live. **Save** writes them to `config.ini`; **Load** discards unsaved edits.
ConfigApp can also put the board into USB drive mode.

ConfigApp's **Events** tab (2.31.0, ConfigApp 0.8.0) edits `events.ini`, what the transmitter's
controls do (§10), without taking the card out.

### Serial menu

Press `m` in a terminal; nothing else does anything outside the menu. Keys select rows; `U`
goes back, `S` saves and exits, `X` exits (asking about unsaved changes), and `?` redraws.

**Every setting works the same way:** select it, type the value, press Enter (or use `+` / `-`;
`U` cancels). On/off settings take **1** (on) or **0** (off). The editor shows the setting's
description and range, and the change applies at once, exactly as from ConfigApp.

Menu `B` -> `0` lists every setting with a number, and `B` -> `7` edits any of them by that
number. The full tree is in §18.

**`<...>` commands** (HCR commands and ConfigApp's `<K...>`) work on the USB port only while the
menu is closed: a frame that arrives while someone is in the menu is ignored, so nothing changes
behind their back. COM1 and COM2 always take commands.

### `config.ini`

A text file in the root of the SD card, one `name=value` per line. Edit it on the PC (USB drive
mode, §4, or a card reader) and reboot. Each save keeps the previous file as `config.ini.bak`.
Settings files from older firmware load automatically; renamed settings are converted, and the
next save writes the current names.

> Saving and loading don't interrupt a WAV that's playing. During a recorder take, saving answers
> "busy" instead, because the card is kept free for the take.

### USB drive mode

The SD card appears on the PC as a drive, for copying WAVs and editing files.
- **Start:** hold SW2, press `T` in the menu, or use ConfigApp.
- **While on:** LED_A fades in and out, and audio is muted.
- **Finish:** eject the drive on the PC, then press `U` (or use ConfigApp) and choose whether to
  reboot.

---

## 6. Operating Modes

The mode decides what moves the servos.

| Mode | Servos |
|---|---|
| **IDLE** | Detached (limp) |
| **MANUAL** | Only the menu's servo tests move them |
| **CONTROL** (default) | Follow their RC channels |
| **AUTO** | Move randomly within each servo's AUTO range, for lifelike idle movement; or, with an `[activity.alive]` (§10), drift and pause and take turns |

Sequences play in MANUAL, CONTROL and AUTO; IDLE stops them.
- **From the menu:** `C`, then `M`, `C`, `I` or `A`.
- **From the transmitter:** rules in `events.ini`, e.g. a 3-position switch: `ch13 low =
  mode:idle`, `ch13 mid = mode:auto`, `ch13 high = mode:control` (§10).
- **From a button:** the `mode:` action (§10).

---

## 7. Audio

### The mix

```
 Voice (mic / line) --> effects chain --+
 WAV player A ---------------------------+--> master volume --> LINE OUT
 WAV player B ---------------------------+
```

| Setting | Default | |
|---|---|---|
| `audio.in.source` | 0 | 0 line in, 1 microphone |
| `audio.in.micGainDb` | 20 | Mic gain 0-63 dB: raise if quiet, lower if it distorts |
| `audio.in.gain` | 100 | Voice input gain (x0.01) |
| `audio.mode` | 1 | 0 passthrough (voice untouched), 1 effects chain |
| `audio.mix.voice` / `wavA` / `wavB` | 100 | Level of each source in the mix (0-100) |
| `audio.mix.master` | 100 | Overall volume |
| `audio.mix.lineOut` | 13 | Codec output level, 13-31; lower is louder |

### Voice effects

In effects mode the voice passes through these in order. Each has an `on` switch (`fx.<tab>.on`)
and its own settings, and you can switch it on or off while talking (ConfigApp `fx` page or
menu `1`).

```
pre-filter -> amp -> noise gate -> pitch -> ring mod -> stormtrooper filter -> reverb -> post-filter
```

| Effect | What it does | Main settings |
|---|---|---|
| **Pre-filter** (`fx.pre`) | Cleans the input: a high-pass removes rumble and handling noise, a low-pass removes hiss | `hpfOn`, `hpfHz` (80), `lpfOn`, `lpfHz` (8000) |
| **Amp** (`fx.amp`) | Fixed boost | `gain` (x0.01, 100) |
| **Noise gate** (`fx.gate`) | Mutes the mic between words (breathing, background) | `threshold`, `floor`, `releaseMs`, `holdMs` |
| **Pitch** (`fx.pitch`) | Shifts the pitch without changing speed | `amount` (x0.01): 100 = unchanged, 140 = higher droid voice, 70 = deeper |
| **Ring modulator** (`fx.ring`) | Metallic, robotic tone (Dalek, battle droid) | `freqHz` (30), `waveform` (sine, triangle, square) |
| **Stormtrooper filter** (`fx.trooper`) | Helmet-radio tone: separate bass and treble around a crossover | `bass`, `treble`, `resonance`, `crossoverHz` (1000) |
| **Reverb** (`fx.reverb`) | Room or helmet space | `roomSize` %, `damping` % |
| **Post-filter** (`fx.post`) | Shapes the final sound, such as a narrow "radio" band | `hpfOn`, `hpfHz`, `lpfOn`, `lpfHz` |

**Pitch tips:** start around 140 for a droid. Raise the input gain a little when you shift up,
and lower it when you shift down.

### Stormtrooper radio sounds (`fx.clicks`)

With `fx.clicks.on`, a sound plays when you start talking ("radio on") and another when you stop
("radio off"), as on a helmet radio.

| Setting | Default | |
|---|---|---|
| `thresholdDb` | -30 dBFS | How loud counts as talking |
| `minDurationMs` | 100 ms | Talk this long before the start sound plays. Shorter bumps and coughs play nothing |
| `hangMs` | 600 ms | Quiet this long ends the transmission. Pauses between words are shorter, so they don't end it |
| `floorSec` | 3 s | Learns steady background noise (a fan, a hum), so it stops counting as talking. 0 = off |
| `startSound` / `endSound` | 0 | WAV file number to play; 0 = the built-in `break.wav` / `click.wav` |
| `volume` | 75 | Volume of the two sounds |

**Tuning:** menu `8` -> `L` shows a live meter of your voice, with the threshold (`|`) and
background (`f`) marked, and the state:
- **The meter:** words should cross the `|`. Raise the threshold if background noise reaches it;
  lower it if quiet speech misses.
- **Mid-sentence end sounds:** if the end sound comes in the middle of sentences, raise the hang
  time.

The sounds never cut off a WAV you're playing. They use whichever player is free, and are
skipped if both are busy.

### WAV files

- **Format:** 44.1 kHz, 16-bit, uncompressed PCM, mono or stereo. Audacity can export this.
- **Names:** start with a number, e.g. `2001-happy-0.wav`. The number is how you play it, and the
  first digit is its **bank** (2xxx = bank 2) for random picks.
- **Where:** the root of the SD card.
- **Two players** (A and B) play at the same time, over the live voice. For a talking head, put
  the speech on one player and the music on the other.
- **Playing a file:**

  | From | How |
  |---|---|
  | Menu | `3`, then `A` or `B` and the number |
  | Buttons | `wavA:N`, `randomA:2`, ... (§10) |
  | Sequences | `audioA N` (§11) |
  | Another controller | `<CA2001>` (§16) |

---

## 8. Servos

### Setting up a servo

For each servo, on ConfigApp's `servo` page (tab `s1`..`s8`) or menu `C` -> `1`-`8`:

| Setting | Default | |
|---|---|---|
| `enabled` | S1, S2 on | Turn the output on (a newly enabled servo needs a reboot) |
| `channel` | 1-8 | Which input channel drives it, 1-24 as on the transmitter (RC PWM: the IO pin); 0 = none |
| `pwmMin` / `pwmMax` | 1000 / 2000 us | Pulse at 0 and 180 degrees. **Calibrate these first**: they set the servo's real travel, and everything else works in 0-180 within them |
| `home` | 90 | Where it rests and returns on Home |
| `easingSpeed` | 50 deg/s | How fast it moves, including following the stick. **0 = as fast as possible** |
| `easingType` | 0 | Shape of each move: 0 linear, 1 cubic, 2 quadratic, 3 quartic, 4 sine, 5 circular |
| `detachTimeoutMs` | 250 ms | Stop driving it after this long still, so it stays quiet and cool. **0 = never**, for a servo holding a load against gravity (a detached servo goes limp) |
| `autoMin` / `autoMax`, `autoIntMin` / `autoIntMax`, `autoSpeedMin` / `autoSpeedMax` | 45-135 deg, 1-5 s, 20-100 deg/s | Range, pause and speed of AUTO mode's random moves |

**Easing off** (the servo goes straight to each position, no lag): `easingSpeed` 0 and
`easingType` 0. Use it for servos that must track a stick exactly, and for a talking jaw.

Moves run in the background: several servos move together, and the board keeps responding
while they do. At power-up all enabled servos go home together, so make sure the supply can
handle the peak current.

### Testing

In MANUAL mode (`C` -> `M`), menu `C` -> `T`:
1. `N` picks the servo.
2. Then `C` centres it, `W` sweeps it, or `P` moves it to an angle.

`C` -> `H` homes all servos, and `C` -> `D` shows their status.

---

## 9. RC Control

Choose the receiver type with `rc.inputMode`: 0 SBUS, 1 RC PWM, 2 none (factory default). Then
reboot.

### SBUS

- Connect the receiver's SBUS output to **J5** (`rc.sbus.port` 1, best), J3 (3), or IO5/IO6 (6).
- Leave `rc.sbus.invert` at 1. The board has no hardware inverter, so the Teensy inverts the
  signal. If channel values look like garbage, check this first.
- **Port conflict:** if COM1 is set to the same port, SBUS wins and COM1 is off for that boot.
- Up to 24 channels.
- Menu `7` -> `V` shows them live.

### RC PWM

- Connect receiver channels to **IO1-IO8**. IO1 is channel 1, IO2 channel 2, and so on.
- Each pin must be enabled with type 5 (RC PWM), which is the default (§15).
- The pulse range is `rc.pwm.minUs` / `maxUs` (1000-2000 us).

### Channels

**Every channel uses the transmitter's numbers, 1-24** (0 = none): `servo.sN.channel`, and
`chN` in `events.ini`. With RC PWM the number is the IO pin (IO1 = channel 1), and only
channels 1-8 exist; the boot log warns if something points higher. What the switches do (the
mode switch, the button pad, sounds, presets) is in `events.ini` (§10).

### Link loss and failsafe

**When the link counts as up:** after `rc.sbus.maxOkCount` (20) good frames in a row.

**When it goes down:**
- at once, on a receiver failsafe frame (transmitter off or out of range)
- after a run of bad frames
- if nothing valid arrives for `rc.timeoutMs` (100 ms), which catches unplugged receivers and
  broken wires

**While the link is down:**
- servos stop following the sticks
- buttons and switches are ignored
- `rc.failsafe` runs once:

| `rc.failsafe` | On link loss |
|---|---|
| 0 (default) | Hold: servos stay where they are |
| 1 | Home all servos |
| 2 | IDLE (servos go limp); the previous mode returns with the link |

AUTO mode doesn't use the link, so with 0 or 1 it keeps moving; use 2 if the droid must stop
when the transmitter is lost. The channel view (`7` -> `V`) shows the link state and frame
counts.

---

## 10. Switches, Sticks and Buttons (`events.ini`)

What every transmitter control does is set in one file, `events.ini` in the root of the SD card.
ConfigApp's Events tab edits it for you (below). A commented example comes with the firmware
(`SDCardExamples/events.ini`).

### In ConfigApp (2.31.0+)

1. **Load from robot.** Each rule shows in words: *ch13 low: Set the motion mode idle*.
2. **Add rule** or **Edit.** Pick what happens, then what to do:
   - **When:** a pad button and gesture, a channel and position, the RC link, or a mode change.
   - **Learn:** press it, then move the switch or stick on the transmitter to where it should
     trigger and hold it there. ConfigApp picks the channel that moved and the position. The
     bar under it shows the channel live and says *condition met* when it would trigger.
   - **Do:** up to three actions, with lists of the card's sequences, WAV files, modes and
     presets.
   - **Only while** modifiers are held, or only in some modes.
   - **Test now** runs the actions straight away.
3. **Save to robot.** The robot keeps the old file as `events.ini.bak`, loads the new one at
   once and reports any line it didn't accept. That row turns red; hover over it for why.
4. In use, a row shows **fired** each time its rule runs.

The **Modifiers**, **Presets** and **Settings** tabs edit those sections. **Inputs** shows all
24 channels live. **Text** shows the whole file, for those who prefer typing. **Open file...**
and **Save file...** work without a robot (a card in a card reader).

### The file

Each line is a **rule**: *when this happens, do that*.

```ini
ch13 low      = mode:idle, audio:manual   ; switch on ch13 moved down: two things at once
ch13 mid      = mode:auto
ch13 high     = mode:control
pad.1         = seq:wave           ; button 1 on the button pad, clicked
pad.1.double  = seq:nod
shift+pad.1   = toggle:look        ; ... while "shift" is held
ch10 >1800    = seq:look           ; stick pushed past 1800 us
ch10 >1800.exit = stopseq          ; ... and let go again
link.lost     = stopseq            ; the RC link dropped ...
link.lost     = home               ; ... a second line for the same trigger: both run
```

A rule fires when its trigger **happens**: a switch moves, a stick crosses a value, a button
is clicked. It never fires again and again while the condition holds.

**Doing several things.** A line can list up to three actions, separated by commas. For more,
write the same trigger on another line. **Every line for a trigger runs**, in the order they're
in the file, and each line can have its own `when=` (2.32.1; before that, a repeated line
replaced the earlier one):

```ini
link.lost  = stopseq, stopaudio, home
link.lost  = mode:idle             ; a fourth thing: another line
pad.3      = home,    when=mode.idle      ; the same button does different things
pad.3      = seq:nod, when=mode.auto      ; ... in different modes
```

### Triggers

| Trigger | Fires when |
|---|---|
| `chN low` / `mid` / `high` | Channel N moves into that third of its range |
| `chN 1500` | ... moves to 1500 us, give or take the deadband (`[settings] deadband`, 50 us) |
| `chN 1500~80` | ... within 80 us of 1500 |
| `chN >1700`, `chN <1300`, `chN 1300-1700` | ... rises above, drops below, or moves into the range |
| `...exit` | Add `.exit` to fire when it *leaves* instead: `chN >1700.exit` |
| `pad.N[.gesture]` | Button N (1-14) on the button pad: `.press`, `.click` (default), `.double`, `.triple`, `.long` |
| `link.lost` / `link.up` | The RC link drops / returns |
| `mode.idle` / `manual` / `control` / `auto` | The motion mode changed to that mode, whatever changed it |

**Channel numbers and values:**
- **Numbers:** as on the transmitter, `ch1`-`ch24`. With RC PWM the IO pin is the channel (IO1
  = `ch1`), and only `ch1`-`ch8` exist; the boot log warns about a rule for a higher one.
- **Values:** microseconds, 1000-2000 with centre 1500, as an RC PWM receiver sends them. SBUS is
  converted the same way (`rc.sbus.min`..`max` = `rc.pwm.minUs`..`maxUs`).
- **Seeing them:** menu `Q` -> `8` shows the live value of every channel the rules use.

### Actions

Up to 3 per line, separated by commas; for more, repeat the trigger on another line (above).
`stop` covers `stopseq` and `stopaudio` in one, and there is no `audio:off`: `audio:manual`
turns off random sounds and music, and `stopaudio` stops what is playing now.

| Action | Does |
|---|---|
| `seq:NAME` (or `NAME`) | Play a sequence (nothing if it's already playing) |
| `toggle:NAME` | Play it, or stop it if it's playing |
| `stopseq` / `stopaudio` / `stop` | Stop sequences / both WAV players / both |
| `wavA:N`, `wavB:N` | Play WAV number N on player A or B |
| `randomA:B`, `randomB:B` | A random WAV from bank B |
| `randomA:2001-2013` | A random WAV numbered in that range (2.32.0) |
| `nextA:B`, `nextB:B` | The next WAV in bank B, in number order, wrapping (2.32.0) |
| `mode:idle` / `manual` / `control` / `auto` | Change the motion mode |
| `audio:manual` / `random` / `music` | The sound mode: only when asked / random sounds / music. What random and music play is set by activities (below); with none, random sounds are bank 2 every 30 s to 5 min |
| `preset:NAME` | Apply a `[preset.NAME]` section (below) |
| `set:KEY=VALUE` | Change one setting, e.g. `set:audio.mix.master=50` (2.32.0) |
| `home` | Home all servos |
| `rec:start` / `rec:stop` / `rec:toggle` | The SBUS recorder |

### Conditions on a rule: `when=`

`when=` limits a rule to when something else is true:
- **A modifier:** `when=gate`
- **Modes:** `when=mode.idle|manual`
- **Both:** join them with `+`

```ini
pad.3     = home, when=mode.idle|manual       ; homing only while stopped
ch3 low   = mode:control, when=gate           ; the mode switch works only with the gate open
```

A line whose `when=` doesn't hold simply doesn't run; other lines for the same trigger still
do.

### Modifiers: buttons at once

The pad sends one button at a time, so combinations use other channels as modifiers, like a
shift key: a switch, or a stick held over. Name them in `[modifiers]`, then use them as
`name+pad.N` or in `when=`:

```ini
[modifiers]
shift = ch9 high        ; zones: low, mid, high
left  = ch4 <1200       ; or a value in us: <N, >N, N-M, N, N~W
```

When several pad rules match, the ones needing the most held modifiers win, and all of them
run: with shift held, `shift+pad.1` runs and plain `pad.1` doesn't. A line whose `when=` doesn't
hold doesn't count, so `shift+pad.4 = seq:look, when=mode.auto` leaves `pad.4` working with
shift held in the other modes. Up to 8 modifiers and 96 rule lines.

### Rules that set a mode, the audio state, a preset or a setting

These also apply **at power-up and whenever the RC link comes back**, for where the switch
already is. So the droid starts in the mode its mode switch shows. A `when=` on such a rule
counts as part of its condition: with `ch3 low = mode:control, when=gate`, opening the gate
with ch3 already low switches to CONTROL at once. Other rules never fire for where a switch
happens to sit at power-up.

### Presets

A preset is a set of settings applied together, for example a voice:

```ini
[preset.deep]
fx.pitch.on = 1
fx.pitch.amount = 85
fx.ring.on = 1

[events]
ch18 high = preset:deep
```

- **Settings:** any setting by its name. Each change applies at once, as if you changed it in
  ConfigApp.
- **Not saved:** a preset doesn't save to `config.ini`. Save from ConfigApp or the menu if you
  want it kept.
- **Limits:** up to 8 presets of 16 settings.

### Activities: things the droid does by itself (2.32.0)

An activity runs on its own while its `when=` holds:

```ini
[activity.chatter]                 ; a random line every 20 s to 2 min
play  = randomA:1
every = 20-120s
when  = audio.random               ; while the sound mode is random

[activity.music]                   ; a music bank, shuffled
play    = playlistB:3
shuffle = 1
every   = 2s                       ; the gap between tracks
when    = audio.music              ; turned off: the track stops

[activity.fidget]                  ; in AUTO, a sequence now and then
play     = pick(nod 3, look 2, shrug 1)   ; weighted: nod is picked most
every    = 10-40s
cooldown = 60s                     ; the same one not again within a minute
when     = mode.auto

[activity.alive]                   ; idle motion in AUTO
servos    = s1, s2, s3
rest      = 50                     ; % of each servo's AUTO range (servo.sN.autoMin..autoMax)
swing     = 60                     ; % of that range the moves cover
period    = 3s                     ; one move
dwell     = 800ms                  ; pause at each end
duty      = 70                     ; % of the time each servo takes part
s3.swing  = 30                     ; one servo differently
when      = mode.auto
```

- **`play`:** any action above; `playlistA:BANK` / `playlistB:BANK`; or `pick(...)` of
  sequences with weights.
- **Timing:**
  - `every` is a time or a range, in `ms`, `s` or `m`.
  - `start = now` fires the moment the activity becomes active (otherwise after one gap).
  - `seed = 42` makes the random choices the same every time, for testing.
- **`when`:** `audio.manual|random|music`, `mode.NAME|NAME`, modifier names, joined with `+`.
- **Alive:**
  - It replaces AUTO's plain random moves for those servos.
  - Servos take turns; `minActive` is how many move at once at least, `intensity` (%) scales
    every swing, and `slew` (deg/s) limits speed.
  - It never moves a servo a sequence is playing on, or the sound-reactive jaw.
- **Limit:** up to 8 activities.

### The button pad

`[inputs] pad = chN` names the pad's channel (`pad = none` if you have none).
- **Calibrate it first:** menu `Q` -> `8` shows its live value and which button it reads.
  Adjust `button.value.1`..`14` and `button.deadband` until every button reads right.
- **Gestures:**
  - `.press` fires at once on every press; `.click` on release after a short press.
  - `.double` and `.triple` need each click within `button.doubleClickMs` (350 ms).
  - `.long` fires while held, after `button.longPressMs` (800 ms).
  - A button with no double or triple rule fires the moment you let go; one with them waits
    out the double-click window first.

### Checking it

- **Menu `Q` -> `2`** lists the settings, modifiers, presets and rules that loaded.
- **Menu `Q` -> `5`** reloads after an edit.
- **Boot log:** each bad line shows with its line number.
- **The console** prints each rule as it fires, e.g. `[EVT] shift+pad.1.click -> toggle:look`.

### Coming from `buttons.ini` (firmware before 2.30)

On the first boot of 2.30, if there is no `events.ini`, Orchestron writes one that does what the
droid did before:
- the mode switch (`rc.ch.opMode`, with its gate if one was set) becomes `mode:` rules
- the audio switch (`rc.ch.audioMode`) becomes `audio:` rules
- the pad channel (`rc.ch.buttonPad`) becomes `[inputs] pad`
- `buttons.ini` is converted: `buttonN` becomes `pad.N`, `chN.high` becomes `chN high`, and its
  raw `<600`-style values become microseconds. `buttons.ini` is then renamed
  `buttons.ini.old`.

Check the result with `Q` -> `2`.

---

## 11. Sequences

A sequence is a timed list of servo moves and sounds in `sequences.ini` on the SD card. The
format is RX-80B's.

```ini
[sequence.wave]
s0 = 0    audioA 1001     ; at 0 ms: play WAV 1001 on player A
s1 = 0    s1 120 300      ; at 0 ms: servo S1 to 120 degrees over 300 ms
s2 = 400  s1 60  300
s3 = 800  s1 90           ; no duration: use S1's easing speed
r4 = 1200 s2 -20 200      ; relative: S2 20 degrees down from where it is, over 200 ms
```

- **Step** (`sN`): `start servo target [duration]`. Start is in ms from the beginning, target
  in degrees (0-180), duration is how long the move takes.
- **Relative step** (`rN`): moves *by* the target instead of *to* it.
- **Servo names:** `s1`..`s8`.
- **Sounds:** `audioA N` / `audioB N` play the WAV numbered N.
- **Clips:** `seq NAME [speed] [scale]` plays another sequence from that time, so short
  pieces (a nod, a blink) are written once and reused:

  ```ini
  [sequence.greet]
  s0 = 0    audioA 1001
  s1 = 400  seq nod            ; the whole nod
  s2 = 1700 seq nod 2x 50%     ; twice as fast, half the travel
  ```

  - **Speed:** `2x`, `0.5x`.
  - **Scale:** `50%`, or `-100%` to mirror. It changes only relative (`rN`) steps, so write
    clips with `rN` and they work wherever the servo is.
  - **Nesting:** clips can call clips 4 deep.
  - **Errors:** a missing clip or a loop shows in the boot log as a load error.
- **Order and limits:** steps play in time order, whatever their order in the file. Up to 256
  steps and 8 sequences at once.
- **How it ends** (2.32.0): `end = hold` (the default) leaves the servos where the sequence left
  them; `end = home` sends them home (`servo.sN.home`). In CONTROL "home" is the stick: the
  servo eases straight back onto it. It also applies when the sequence is stopped.

  ```ini
  [sequence.wave]
  end = home
  s0 = 0 s1 120 300
  ```

**With the sticks:**
- **Relative steps add to the stick.** In CONTROL a nod rides on top of where you're pointing
  the head, and the stick keeps working.
- **Absolute steps take over** and go to that exact angle.
- **At the end the servo stays put.** In CONTROL, when you move the stick it eases back onto it
  over `servo.releaseEaseMs` (300 ms); in AUTO the next random move takes over.

**Playing:** start from buttons (§10), or menu `Q`, which can list, play by name, stop, reload
after editing, and trace each step.

---

## 12. Sound-Reactive Jaw

Any servo can move to sound: a jaw that talks along with a WAV or the live voice. An FFT splits
the sound into bands every 12 ms. Vowel energy (300-1000 Hz) opens the jaw, and "s", "sh", "f"
sounds (2.5-6 kHz, said with the teeth shut) hold it closed, so it looks like speech rather than
a VU meter.

### Setup (menu `J`, or ConfigApp's `react` page)

1. **The servo:** `react.jaw.servo` (1-8). Calibrate its `pwmMin` / `pwmMax` to the jaw's real
   closed and open positions, and set its `easingSpeed` to 0 so it doesn't lag.
2. **What it listens to:** `react.source`. 0 WAV A (default), 1 WAV B, 2 both, 3 the live voice,
   4 everything. For best results put the speech on one player and the music on the other, and
   listen to the speech player.
3. **The travel:** `react.jaw.closedDeg` / `openDeg` (0 and 180 = the full calibrated range).
4. **Tune it:** play a WAV and open the live view (`J` -> `1`), which shows the level, the
   opening and the jaw angle.

### Tuning

| Tab | Setting | Default | |
|---|---|---|---|
| `band` | `useFft` | on | Vowel band minus sibilants; off = the whole band |
| | `vowelLowHz` / `vowelHighHz` | 300-1000 | The band that opens the jaw |
| | `sibilantCut`, `sibLowHz` / `sibHighHz` | 65, 2500-6000 | How much "s" sounds hold it shut (0 = not at all) |
| `level` | `agc`, `agcDecaySec` | on, 20 s | Auto level, so quiet and loud files both use the full travel |
| | `headroom` | 125 | Keeps ordinary peaks short of fully open, leaving room for loud syllables |
| | `floorSec` | 3 s | Ignores steady background (hiss, music bleed) |
| | `squelch` | 10 | Below this is silence; raise it if room noise moves the jaw |
| | `gain` | 100 | Extra sensitivity |
| `motion` | `attackMs` / `holdMs` / `releaseMs` | 10 / 30 / 60 | How fast it opens, holds and closes. Longer release is smoother but blurs syllables |
| | `curve` | 170 | Higher = snappier on loud sounds |
| | `steps` | 0 | 2-8 = that many positions, less servo chatter |

The jaw servo ignores its stick and AUTO's random moves. A sequence step for it takes over while
the sequence plays. When silent it rests closed.

---

## 13. NeoPixel Strip

One WS2812-type (NeoPixel) strip that follows the voice, like the jaw.

1. **Pick the pin:**
   - IO1-IO8 give a 5 V data signal: set `pin.io.ioN.type` to 4 and enable it.
   - Or use a servo header S1-S8 (3.3 V data): set `pin.servo.sN.type` to 4, and turn that servo
     off.
   - Only one pin can drive a strip.
2. **The strip:** `neo.strip.count` (number of LEDs) and `neo.strip.order` (0 GRB for WS2812B,
   1 RGB, 2 BRG, 3 GRBW, 4 RGBW for SK6812). Save and reboot.
3. **Test:** menu `J` -> `O` shows red, green, blue and white:
   - wrong colours: change the order
   - nothing lit: check the strip's 5 V supply, a shared ground and the data wire
4. **Pick a pattern** and play some sound.

| Setting | Default | |
|---|---|---|
| `neo.pattern` | 2 | 0 off, 1 throb, 2 bar from the centre, 3 bar from the start (VU), 4 rings, 5 spectrum |
| `neo.brightness` | 64 | Maximum, 0-255. Each LED can draw about 60 mA at full white, so size the supply |
| `neo.hue` / `neo.hue2` | 20 / 0 | Colour when quiet (or at the start) and when loud (or at the end): 0 red, 30 orange, 60 yellow, 120 green, 240 blue |
| `neo.saturation` | 100 | % colour; 0 = white |
| `neo.idle` | 1 | When silent: 0 off, 1 dim glow, 2 slow breathe |
| `neo.rings` | 5 | Pattern 4: number of equal rings, innermost first |

All patterns follow the jaw's sound level, so tune the jaw first (§12). The spectrum shows one
frequency band per LED, from 100 Hz to 8 kHz. If a strip on an IO pin flickers or shows random
colours, add a 74AHCT125 buffer or try a servo header.

---

## 14. SBUS Recorder

Records your transmitter moves to a file, to turn into a sequence later.

- **Start / stop**, any of:
  - **ConfigApp:** the **Record** button at the top (it turns into **Stop recording** and shows
    the take time), or the Actions tab.
  - **A transmitter switch or button**, set in ConfigApp's `rec` page: `rec.switchCh` = its
    channel (1-24, as numbered on the radio). With `rec.switchMode` 0 (a switch), high starts and
    low stops. With 1 (a momentary button), each press starts or stops. Where the switch sits
    when the robot powers up or the radio link comes up does nothing.
  - **`events.ini`**, for pad buttons, gestures and modifiers: e.g. `pad.14.long = rec:toggle`,
    or `ch10 high = rec:start` / `ch10 low = rec:stop`.
  - Menu `E` -> `1`.
- **What's recorded:** every enabled servo's channel plus the button pad, unless you choose
  channels in `rec.chMask1to16` / `17to24`. `E` -> `4` fills them in to edit.
- **Rate:** `rec.rateHz`, 50 per second.
- **Length:** a take is held in memory until it ends: about 4-5 minutes at 8 channels and 50 Hz.
  The start message says how long this take can run. `rec.maxSeconds` ends it sooner (0 = only
  when memory is full).
- **To music:** set `rec.audioTrack` to a WAV number; it plays on player A with each take.
- **After the take** it's written to `/REC/REC_NNN.csv`, which opens in a spreadsheet. A power
  cut before then loses it.

---

## 15. Pin Types

Each servo header and IO pin has a type, on ConfigApp's `pin` page.

| Type | Use | Where |
|---|---|---|
| 0 | Off | Any |
| 1 | Servo | S1-S8 (default); turned on and off with `servo.sN.enabled` |
| 4 | NeoPixel strip | Any one pin (§13) |
| 5 | RC PWM input | IO1-IO8 (default) |
| 2 / 3 | Digital input / output | Planned, not yet working |

Type changes apply after a reboot.

---

## 16. Connecting Other Controllers

Another controller (a droid's main board, an HCR-style sound system, an RX-80B) can drive
Orchestron over USB, COM1 or COM2 with short text commands in angle brackets. The COM ports run
at 115200 baud by default (`serial` page).

| Command | Example | Does |
|---|---|---|
| `CA` / `CB` | `<CA2001>` | Play the WAV numbered 2001 on player A / B |
| `PSA` / `PSB` / `PSX` | `<PSX>` | Stop A / B / both |
| `PVV` / `PVA` / `PVB` | `<PVV75>` | Voice / WAV A / WAV B volume (0-100) |
| `PP` | `<PP140>` | Pitch x0.01 (070 = 0.70x, 140 = 1.40x) |
| `PG` | `<PG100>` | Voice input gain x0.01 |
| `EX` | `<EX49>` | Set every effect switch at once from a bitmask (bits below) |
| `ES` / `EC` / `ET` | `<ES5>` | Switch one effect on / off / over, by its bit number |
| `RE` | `<RE1>` | Ring modulator on (1) or off (0) |
| `RF` / `RW` | `<RF30>` | Ring modulator frequency (Hz) / waveform (0 sine, 1 triangle, 2 sawtooth, 3 square) |
| `RS` | `<RS>` | Ring modulator status (printed on the USB console) |
| `PN` | `<PN100>` | Accepted for HCR compatibility; Orchestron has no noise reduction and says so |
| `QPA` | `<QPA>` -> `<QPA1>` | Is player A playing? (1 / 0) |
| `QF` | `<QF>` -> `<QF2000:143>` | WAV files per bank (bank start : count, comma separated) |
| `QE` | `<QE>` -> `<QE817>` | Which effects are on, as a bitmask |

Effect bits: 0 pre-filter, 1 voice amp, 2 noise gate, 4 pitch shift, 5 ring modulator,
6 stormtrooper filter, 7 stormtrooper radio sounds, 8 reverb, 9 post-filter. Menu `9` -> `8`
on the board prints the same list.

While the voice is above the radio threshold, Orchestron sends `<QVPnn>` (level 0-70) to all
ports, which RX-80B uses to light a mouth. It also reports `<QPA1>` / `<QPA0>` as player A
starts and stops.

**ConfigApp and scripts** use a second set of commands, `<K...>`. These list every setting with
its range, scale and description, get and set values live, save and reload, stream telemetry
(servo angles, channels, status), and switch USB drive mode. Any script can use them; the key
ones are `<KC>` (count), `<KN##>` (describe setting ##), `<KD##>` (its description), `<KG##>` /
`<KS##,v>` (get / set), `<KW>` (save) and `<KR##>` (stream telemetry at ## Hz).

**Actions** (2.27.2): `<KA,action>` runs any `events.ini` action, e.g.
`<KA,rec:toggle>`, `<KA,seq:wave>`, `<KA,mode:control>`, `<KA,wavA:2001>`, and replies
`<KA,1,message>` (or `<KA,0,why>`). `seq:NAME` also plays sequences that `events.ini` doesn't
use. `<KA>` gives the number of entries in the robot's action list, and `<KA##>` gives entry ##
as `group,label,action`; ConfigApp turns these into buttons. The `rec` telemetry group (`0x40`)
streams the recorder's state (0 idle, 1 recording, 2 writing), frames, take time, auto-stop time
and write progress.

**Editing events.ini** (2.31.0):

| Command | Does |
|---|---|
| `<KFR,name,offset>` | Reads `events.ini`, `sequences.ini` or `config.ini`, 96 bytes as hex |
| `<KFO,name,size>`, `<KFW,hex>`, `<KFC,crc32>` | Upload `events.ini` or `sequences.ini` (CRC-checked, old file kept as `.bak`) |
| `<KFL>` | Lists the WAV files |
| `<KU>` / `<KUR>` | The last load's rule count and problems, each with its line (`<KUR>` reloads first) |
| `<KV1>` | Sends `<KV,line>` each time a rule fires |
| `<KI>` | Link, pad button and all 24 channels in us |

---

## 17. Updating the Firmware

Firmware comes as a `.hex` file.
1. Install **Teensy Loader** (part of Teensyduino, from pjrc.com).
2. Connect the board by USB and open the `.hex` in Teensy Loader (File -> Open HEX File).
3. Press the white button on the Teensy, or turn on Auto mode. The loader programs it and the
   board reboots.

Your `config.ini`, sounds and other files on the SD card are kept. Settings from an older
version are converted on the first boot; save once to write them in the new form.

---

## 18. Menu Reference

Press `m`. Every screen also accepts `U` (back), `S` (save and exit), `X` (exit) and `?`
(redraw). Settings are edited by typing a value (on/off: 1 or 0).

```
MAIN MENU
+-- [1] Audio Mode & Effects
|   +-- [A] Audio mode (0 passthrough, 1 effects)
|   `-- [1] Pre-Filter  [2] Voice Amp  [3] Noise Gate  [5] Pitch Shift  [6] Ring Mod
|       [7] Stormtrooper Filter  [8] Stormtrooper Sounds  [9] Reverb  [0] Post-Filter
+-- [2] Audio Levels
|   +-- [1] Pitch  [2] Voice  [3] WAV A  [4] WAV B  [5] Master  [6] Line Out
|   `-- [7] Input (0 line, 1 mic)  [9] Mic gain  [8] -> menu 1
+-- [3] Playback: [A]/[B] play a WAV number  [1]/[2]/[3] stop A / B / all  [M] mute  [L] list files
+-- [4] Voice Effects: [F] filter  [A] amp  [G] input gain  [1] fixed gain
+-- [5] Filters, Reverb & Ring Mod: pre/post HPF and LPF on + cutoff, reverb on/room/damping,
|       ring mod on/freq/wave
+-- [6] Noise Gate: [G] on  [1] threshold  [2] floor  [3] release  [4] hold  [D] debug messages
+-- [7] Control Input: [M] mode details  [V] channel values  [I] input mode (reboot)  [N] SBUS invert
|       [D] debug output  [A] analog read test
+-- [8] Stormtrooper: [1]/[2] start/end sound  [3] volume  [4]-[7] filter  [8] threshold
|       [9] min duration  [H] hang  [F] noise floor  [L] live view  [T]/[C] test sounds
+-- [9] COM Ports: COM1/COM2 on, baud, port; SBUS port (reboot); [7] routing; [8] HCR commands
+-- [C] Servo Control
|   +-- [M]/[C]/[I]/[A] mode   [D] status   [H] home all   [G] save
|   +-- [T] Test: [N] servo  [C] centre  [W] sweep  [P] position
|   `-- [1..8] Servo setup: enabled, channel, home, PWM min/max, speed, easing, detach,
|                           [A] AUTO ranges
+-- [B] Configuration File: show, load, save, SD status, compare, [0] list all settings,
|       [7] change a setting by number, [8] reset to defaults, [9] SD stress test
+-- [Q] Sequences: list, show events.ini (rules), play by name, stop, reload, status, trace,
|       [8] input monitor (pad, channels in us)
+-- [J] Sound Reactive: [1] live view, servo, source, angles, band, AGC, envelope, ...
|       [O] NeoPixel test, pattern, brightness, hues, saturation, idle, rings, count
+-- [E] SBUS Recorder: [1] start/stop  [2] status  [3] list  [4] record servos + pad
|       [5] rate  [6] max length  [7] song  [8]/[9] channel masks  [0] SD stream test
+-- [A] System Status   [L] List SD Files   [T] USB Drive Mode   [R] Reboot
```

Outside the menu the console only answers `m` (and `<...>` commands).

---

## 19. Troubleshooting

**No sound**
1. Check cables and the input source (`audio.in.source`).
2. Check the levels: `audio.mix.master`, `audio.mix.voice`.
3. With the mic: `audio.in.micGainDb`.
4. If the noise gate is on, it may be shut; turn it off to test.

**Voice distorted or harsh:** lower `audio.in.micGainDb` or `audio.in.gain`; turn the amp off.

**Servos don't move**
1. Mode: CONTROL for sticks, MANUAL for menu tests.
2. Is the servo enabled? (A newly enabled one needs a reboot.)
3. Is `rc.inputMode` not 2? Is the link up? (Menu `7` -> `V`.)
4. Is the servo's `channel` right? (1-24 as on the transmitter; RC PWM: the IO pin.)
5. Power: servos need their own 5 V supply, not USB.

**Servo jitters or buzzes:** check `pwmMin` / `pwmMax` and the supply; a short
`detachTimeoutMs` (250) lets it rest.

**Servo lags the stick:** set its `easingSpeed` to 0.

**SBUS values are garbage:** `rc.sbus.invert` should be 1. Check the port and wiring.

**COM1 stopped working after enabling SBUS:** they're on the same port; move one of them.

**Radio sounds play in the middle of sentences:** raise `fx.clicks.hangMs`. **They don't play
at all:** check `fx.clicks.on`, then watch the live view (`8` -> `L`).

**Jaw flaps on music:** listen to the voice player only (`react.source`); raise
`react.band.sibilantCut` or `react.level.squelch`.

**NeoPixels wrong colours:** `neo.strip.order`. **Flicker:** add a buffer or use a servo header
(§13).

**SD card not found:** reseat it, reformat FAT32, try another card, and watch the boot messages.

**Settings don't stick:** save (`S` or ConfigApp Save), and check the card isn't
write-protected.

**PC doesn't see the USB drive:** wait a few seconds after starting drive mode; try another
cable (it must carry data) or port.

**No serial connection:** 115200 baud; a data USB cable; close other programs using the port.

---

## 20. Specifications

| | |
|---|---|
| Processor | Teensy 4.1, ARM Cortex-M7 600 MHz |
| Audio codec | SGTL5000, 44.1 kHz, 16-bit |
| Audio in | Electret mic (2-pin), line in (3.5 mm) |
| Audio out | Line out (3.5 mm): live voice + 2 WAV players mixed |
| Voice effects | Pitch 0.5x-3x, ring modulator, stormtrooper filter, reverb, noise gate, pre/post HPF and LPF |
| Sound analysis | FFT 1024 points (43 Hz bins), new frame every 11.6 ms |
| Servo outputs | 8 (S1-S8), 3.3 V signal, 6 easing curves |
| I/O pins | 8 (IO1-IO8), 5 V level-shifted |
| RC input | SBUS (up to 24 channels) or RC PWM (up to 8) |
| LEDs | One WS2812/SK6812 strip, up to 300 LEDs |
| Serial | USB, COM1 (TTL, 3 port choices), COM2 (RS-485); 115200 baud default |
| Storage | microSD, FAT32 (32 GB or smaller) |
| Power | 5 V via USB or the power connector |
| Settings | 263, on 10 ConfigApp pages |

---

## 21. Firmware History

| Version | Date | New for users |
|---|---|---|
| 2.32.1 | Oct 2026 | The same trigger on several lines: every line runs (it used to replace the earlier one); a pad button can do different things in different modes |
| 2.32.0 | Oct 2026 | Activities: random chatter, music playlists, sequences picked now and then, lifelike idle motion in AUTO; `set:`, `next`, sound ranges, `audio:music`; sequences can end by going home; sample SD cards |
| 2.31.0 | Oct 2026 | ConfigApp's Events tab: edit what the switches, sticks and buttons do, with Learn, Test and a live view of which rule fired |
| 2.30.0 | Oct 2026 | `events.ini`: one file for every switch, stick value, button and link event, with modes, presets and random sounds; converts `buttons.ini` and the old switch settings |
| 2.29.0 | Oct 2026 | Sequences can call other sequences as clips (`seq nod 2x 50%`) |
| 2.26.0 | Oct 2026 | Channels numbered 1-24 as on the transmitter everywhere (RC PWM: IO pin = channel); old settings convert |
| 2.25.0 | Oct 2026 | Settings regrouped into 10 ConfigApp pages, with descriptions and scaled values in the app; older settings files convert automatically |
| 2.24.0 | Oct 2026 | One on/off switch per effect, applied instantly; post-filter switch works; stormtrooper radio sounds rebuilt (hang time, chosen files, volume, noise learning, live view) |
| 2.23.0 | Oct 2026 | NeoPixel strip that follows the voice |
| 2.22.0 | Oct 2026 | Talking jaw uses an FFT: vowels open, "s" sounds hold it shut; works over music |
| 2.21.0 | Oct 2026 | Sound-reactive jaw servo |
| 2.20.0 | Oct 2026 | SBUS recorder; the robot keeps running while menu prompts wait |
| 2.19.0 | Oct 2026 | Servo speed 0 = instant; sticks follow at the servo's speed |
| 2.18.0 | Oct 2026 | Sequences add to the sticks or override them |
| 2.17.0 | Sep 2026 | Button gestures, combinations, switch triggers and actions |
| 2.16.0 | Sep 2026 | Sequences from `sequences.ini`, started by buttons |
| 2.14.0 | Sep 2026 | RC link-loss detection and failsafe |
| 2.11.0 | Sep 2026 | Per-servo detach time |
| 2.10.0 | Sep 2026 | Settings apply live; servos move smoothly in the background |
| 2.9.0 | Sep 2026 | Safer SD card use during playback; SBUS invert setting |
| 2.8.0 | Sep 2026 | ConfigApp |
| 2.0 | Jul 2026 | Orchestron: servos, RC input, I/O added to the vocalizer |
| 1.0 | Jan 2026 | RX Audio PitchShift (voice only) |
