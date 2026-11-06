# Quick Start 3: SBUS Receiver

**QS-3** · Firmware 2.46.0 · Grnwave Workshop · November 2026 · Draft

One SBUS lead from the receiver carries up to 24 channels. The sticks move servos, switches
change modes and voices, and buttons (a button box, or a 14-button pad on one channel) play
sounds and sequences. The [example SD card](../../SDCardExamples/) is set up for this.

```
  transmitter  ~~~ radio ~~~>  SBUS receiver  --- 1 signal wire --->  Orchestron  ===>  servos
                                                                                  ===>  speaker
```

---

## You need

- Orchestron board with firmware 2.46.0 or later ([how to update](../USER_MANUAL.md#17-updating-the-firmware))
- microSD card: FAT32, 32 GB or smaller
- An RC transmitter and a receiver with an **SBUS** output (most FrSky, Futaba, RadioMaster and
  FlySky receivers)
- Three jumper wires for the receiver (or a lead you can split: see the warning below)
- Servos, and an amplifier with a speaker (a mic is optional)
- A **regulated 5 V supply** for J1, big enough for every servo at once (1 A or more each).
  Not 6 V or 7.4 V: the same rail feeds the Teensy
- A PC with [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp) or a serial terminal

---

## 1. Connect it

```
  SBUS RECEIVER                         ORCHESTRON
  -------------                         ----------
  SBUS signal  ------------------------>  J5  RX
  GND          -------------------------  J5  G
  + 5 V        <------------------------  the middle row (+5 V) of any free S or IO header

                                          S1  =====>  servo 1
                                          S2  =====>  servo 2
                                          ...         up to S8
                                          J1  <=====  5 V regulated supply  (5V / GND)
                                          LINE OUT  ==>  amplifier  ==>  speaker
                                          Teensy USB <==  PC (for setup)

  =====  3-wire servo lead: GND, +5 V, signal
```

> **Don't plug a 3-wire servo-style lead into J5 as it is.** J5's middle pin is TX, not +5 V.
> Signal and GND go to J5; the receiver's + comes from another header.

Pins are named as printed on the board; the
[pinout photo](https://grnwave.com/teensy-vocalizer-v3-user-manual/) shows where each one is.

- **The receiver is powered from J1** through that header. USB alone won't power it, or the
  servos.
- **Sharing the receiver** with another board (a motor controller, say): the SBUS signal can go
  to both (a Y lead), with the grounds joined.

---

## 2. Prepare the card

The quickest start is the example card: copy everything in [`SDCardExamples/`](../../SDCardExamples/)
to the root of a FAT32 card. It has `config.ini` set for SBUS on J5, an `events.ini` with
switches, buttons, presets and activities, sequences, and four sounds. The top of its
`events.ini` lists which channel does what; change the numbers to your transmitter's.

Your own sounds: WAV, 44.1 kHz, 16-bit, named with a number first (`2001-hello.wav`), in the
card's root. The first digit is the bank: `randomA:2` plays a random file from bank 2.

---

## 3. Set it up

Connect the PC by USB and open ConfigApp (or a terminal at 115200 baud, then `m`). The example
card already has the first four:

| Setting | Value | ConfigApp page |
|---|---|---|
| `rc.inputMode` | **0** SBUS | `rc` |
| `rc.sbus.port` | **1** J5 (the default) | `rc` > `sbus` |
| `rc.sbus.invert` | **1** (the default; leave it) | `rc` > `sbus` |
| `serial.com1.port` | **3** J3, so COM1 keeps a port of its own (SBUS takes J5) | `serial` |
| `rc.sbus.channels` | **16** for most receivers; **24** for a 24-channel FrSky ACCESS receiver; fewer (e.g. 6) for a small radio | `rc` > `sbus` |
| `rc.failsafe` | 0 hold (default), 1 home, 2 IDLE (servos go limp) when the link drops | `rc` |

**Save, then reboot.** The input mode and port take effect at boot.

**Each servo** (tab `s1`..`s8`, or menu `C` -> `1`-`8`):

| Setting | Value |
|---|---|
| `servo.sN.enabled` | **1** (reboot after enabling a new one) |
| `servo.sN.channel` | The transmitter channel that drives it, 1-24 (0 = none) |
| `servo.sN.pwmMin` / `pwmMax` | Calibrate first: the pulses at the two ends of its real travel |
| `servo.sN.home` | Where it rests (0-180) |
| `servo.sN.easingSpeed` | Degrees per second; **0** = follow the stick exactly |

**Check the link:** menu `7` -> `V` shows the link **UP** and every channel live; ConfigApp's
**Inputs** tab shows the 24 channels. Move each stick and switch and watch its number.

---

## 4. Switches and buttons

What each control does goes in `events.ini`. ConfigApp's **Events** tab writes it for you
(**Learn**: move the switch and it picks the channel; **Capture** on the Buttons tab reads a
button's value). A start:

```ini
[inputs]
pad = none                      ; or pad = chN for a 14-button pad on one channel

[buttons]
happy = ch10 1100               ; a button box on ch10: each button sends its own value
sad   = ch10 1300               ; (hold it and press Capture in ConfigApp to read it)

[modifiers]
shift = ch9 high                ; a switch held up gives every button a second job

[events]
ch5 low      = mode:idle        ; a 3-position switch picks the mode
ch5 mid      = mode:auto
ch5 high     = mode:control
happy        = randomA:1        ; a random sound from bank 1
shift+happy  = seq:wave         ; with ch9 up: a sequence instead
sad          = seq:nod
link.lost    = stopseq, home    ; transmitter off or out of range
```

- **Mode rules act at power-up too**, so the droid starts in the mode its switch shows.
- **More:** gestures (`.double`, `.long`), voice presets, random chatter and music, idle motion
  in AUTO. The example card has them all, with comments; see also
  [manual §10](../USER_MANUAL.md#10-switches-sticks-and-buttons-eventsini).

**Save to robot** in ConfigApp loads the new rules at once. A row shows **fired** each time
its rule runs.

---

## 5. Test it

1. Power J1 and connect USB. LED_B comes on when Orchestron is ready.
2. Transmitter on: menu `7` -> `V` says the link is UP.
3. Mode switch to CONTROL: the servos follow the sticks.
4. Press a sound button: a sound plays.
5. Transmitter off: the link goes DOWN at once, and the servos do what `rc.failsafe` says.

---

## Optional: a talking jaw

A jaw servo can move to the sound instead of a stick: set `react.jaw.servo` to its number,
its `channel` to 0 and its `easingSpeed` to 0. See [manual §12](../USER_MANUAL.md#12-sound-reactive-jaw).

---

## If it doesn't work

| Problem | Check |
|---|---|
| Link stays DOWN | `rc.inputMode = 0` and rebooted? Receiver powered and bound? Signal on J5 **RX**? |
| Console says `bytes ... but no frame` | `rc.sbus.channels` doesn't match the receiver: try 16 |
| Channel values are garbage | `rc.sbus.invert` must be 1 |
| A switch rule never fires | Is its channel above `rc.sbus.channels`? Menu `Q` -> `8` shows the value; `low` is below 1250, `high` above 1750 |
| Servos don't move | J1 power; mode CONTROL; `servo.sN.enabled` (and a reboot); `servo.sN.channel` |
| Servo moves the wrong way | Reverse the channel on the transmitter |
| COM1 stopped working | It was on J5 with SBUS: set `serial.com1.port = 3` |

---

## Next

- SBUS and link loss in detail: [manual §9](../USER_MANUAL.md#9-rc-control)
- Sequences (timed moves with sound): [manual §11](../USER_MANUAL.md#11-sequences)
- Record your transmitter moves and turn them into a sequence: [manual §14](../USER_MANUAL.md#14-sbus-recorder)
