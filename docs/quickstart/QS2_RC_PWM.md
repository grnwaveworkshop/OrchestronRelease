# Quick Start 2: RC Receiver (PWM)

**QS-2** · Firmware 2.46.0 · Grnwave Workshop · November 2026 · Draft

A standard RC receiver, one lead per channel, plugged straight into Orchestron. The sticks move
servos (a head, a dome), switches change what the droid does, and buttons play sounds. Up to 8
channels. For more channels, or one wire instead of eight, see [QS-3, SBUS](QS3_SBUS.md).

```
  transmitter  ~~~ radio ~~~>  receiver  === 1 lead per channel ===>  Orchestron  ===>  servos
                                                                                   ===>  speaker
```

---

## You need

- Orchestron board with firmware 2.46.0 or later ([how to update](../USER_MANUAL.md#17-updating-the-firmware))
- microSD card: FAT32, 32 GB or smaller
- An RC transmitter and a receiver with PWM (servo) outputs
- Female-to-female servo leads, one per receiver channel you use
- Servos, and an amplifier with a speaker (a mic is optional)
- A **regulated 5 V supply** for J1, big enough for every servo at once (1 A or more each).
  Not 6 V or 7.4 V: the same rail feeds the Teensy
- A PC with [ConfigApp](https://github.com/grnwaveworkshop/ConfigApp) or a serial terminal

---

## 1. Connect it

```
  RC RECEIVER                  ORCHESTRON
  -----------                  ----------
  CH1  =====================>  IO1           S1  =====>  servo 1  (e.g. head turn)
  CH2  =====================>  IO2           S2  =====>  servo 2  (e.g. head nod)
  CH3  =====================>  IO3           S3  =====>  servo 3  (e.g. jaw, dome)
  CH5  (a switch)  =========>  IO5
  CH6  (a button)  =========>  IO6
                               J1  <=======  5 V regulated supply  (5V / GND)
                               LINE OUT  ==>  amplifier  ==>  speaker
                               Teensy USB <==  PC (for setup)

  =====  3-wire servo lead: GND, +5 V, signal
```

- **Receiver channel N goes to IO N.** That number is the channel in every setting and rule.
- **Same way round as a servo:** signal on the inside row, +5 V in the middle, the lead's GND
  wire (black or brown) on the row at the board's edge. S and IO headers are all the same; the
  [pinout photo](https://grnwave.com/teensy-vocalizer-v3-user-manual/) shows where each one is.
- **The receiver is powered through the leads**, from J1. USB alone won't power it, or the
  servos.

---

## 2. Prepare the card

1. Format the card FAT32.
2. Copy your sounds to the root: WAV, 44.1 kHz, 16-bit, named with a number first
   (`2001-hello.wav`). The first digit is the bank: `randomA:2` plays a random file from bank 2.
3. Put the card in and power up. Orchestron writes `config.ini` and a blank `events.ini`.

---

## 3. Set it up

Connect the PC by USB and open ConfigApp (or a terminal at 115200 baud, then `m`).

**Receiver:**

| Setting | Value | ConfigApp page |
|---|---|---|
| `rc.inputMode` | **1** RC PWM, then **reboot** | `rc` |
| `rc.failsafe` | 0 hold (default), 1 home, 2 IDLE (servos go limp) when the signal is lost | `rc` |

IO1-IO8 are RC PWM inputs by default: nothing else to set.

**Each servo** (tab `s1`..`s8`, or menu `C` -> `1`-`8`):

| Setting | Value |
|---|---|
| `servo.sN.enabled` | **1** (reboot after enabling a new one) |
| `servo.sN.channel` | The receiver channel that drives it (0 = none, e.g. a sequence-only servo) |
| `servo.sN.pwmMin` / `pwmMax` | Calibrate first: the pulses at the two ends of its real travel |
| `servo.sN.home` | Where it rests (0-180) |
| `servo.sN.easingSpeed` | Degrees per second; **0** = follow the stick exactly |

**Save** when done.

**Check the receiver:** ConfigApp's **Inputs** tab (or menu `7` -> `V`) shows every channel live.
Move each stick and switch: its channel moves between about 1000 and 2000. A channel with
nothing plugged in shows no value.

---

## 4. Switches and buttons

What each switch and button does goes in `events.ini`: ConfigApp's **Events** tab writes it for
you (**Learn**: move the switch and it picks the channel). Or edit the file. A start:

```ini
[inputs]
pad = none                      ; no button pad on an RC PWM receiver

[buttons]
sound = ch6 high                ; a push button on receiver channel 6

[events]
ch5 low     = mode:idle, audio:manual   ; switch down: servos limp, quiet
ch5 high    = mode:control              ; switch up: the sticks drive the servos
sound       = randomA:2                 ; click: a random sound from bank 2
sound.long  = toggleaudio:random        ; hold: random chatter on, hold again: off
link.lost   = stopseq                   ; signal lost: stop any sequence

[activity.chatter]                      ; what "random chatter" plays
play  = randomA:2
every = 30-120s
when  = audio.random
```

- **Mode switches act at power-up too**, so the droid starts in the mode its switch shows.
- **A 3-position switch** gives `low`, `mid` and `high`. Add `ch5 mid = mode:auto` and the droid
  moves by itself in the middle position.
- **Buttons** can also `.double` click, `.long` press, and act only while another switch is
  held. See [manual §10](../USER_MANUAL.md#10-switches-sticks-and-buttons-eventsini).

**Save to robot** in ConfigApp loads the new rules at once. A row shows **fired** each time
its rule runs.

---

## 5. Test it

1. Power J1 and connect USB. LED_B comes on when Orchestron is ready.
2. Transmitter on: the Inputs tab shows the channels moving.
3. Switch to CONTROL (`ch5 high` above): the servos follow the sticks.
4. Press the sound button: a sound plays.
5. Transmitter off: the servos do what `rc.failsafe` says.

---

## Optional: a talking jaw

A jaw servo can move to the sound instead of a stick: set `react.jaw.servo` to its number,
its `channel` to 0 and its `easingSpeed` to 0. See [manual §12](../USER_MANUAL.md#12-sound-reactive-jaw).

---

## If it doesn't work

| Problem | Check |
|---|---|
| No channel moves in Inputs | `rc.inputMode = 1` and rebooted? J1 powered (the receiver's light on)? Receiver bound to the transmitter? |
| One channel shows nothing | Its lead, the right way round, on the IO number matching the channel |
| Servos don't move | J1 power; mode CONTROL; `servo.sN.enabled` (and a reboot); `servo.sN.channel` |
| Servo moves the wrong way | Reverse the channel on the transmitter |
| Servo jitters | `pwmMin` / `pwmMax` beyond its travel; supply too small |
| A switch rule never fires | Menu `Q` -> `8` shows the channel's value; `low` is below 1250, `high` above 1750 |

---

## Next

- Servos in detail: [manual §8](../USER_MANUAL.md#8-servos)
- Sequences (timed moves with sound): [manual §11](../USER_MANUAL.md#11-sequences)
- Things the droid does by itself (chatter, music, idle motion): [manual §10, Activities](../USER_MANUAL.md#activities-things-the-droid-does-by-itself-2320)
