# Changelog

User-facing changes in each Orchestron release. The firmware for the current release is in
[`firmware/`](firmware/); the [user manual](docs/USER_MANUAL.md) describes how to use each
feature.

## 2.32.1 - October 2026

- **The same trigger on several lines: every line runs**, in file order, each with its own
  `when=`. That's how to do more than three things at once, for example `link.lost = stopseq,
  stopaudio, home` plus `link.lost = mode:idle`. Before, a repeated line replaced the earlier one.
- **Fixed: a pad button can do different things in different modes**, for example
  `pad.3 = home, when=mode.idle` and `pad.3 = seq:nod, when=mode.auto`. Before, only one of them
  ever worked.
- **User manual:** several actions on one line, repeated triggers, and how to turn sounds off
  (`audio:manual`, `stopaudio`).

## 2.32.0 - October 2026

- **Activities:** things the droid does by itself, set in `events.ini`:
  - random chatter at random intervals
  - music playlists, in order or shuffled
  - a sequence picked now and then, weighted, without repeating itself
  - lifelike idle motion in AUTO: servos drift, pause and take turns
- **New `events.ini` actions:**
  - change one setting from a switch or button (`set:audio.mix.master=50`)
  - play the next file in a bank (`nextA:3`)
  - a random file from a number range (`randomA:2001-2013`)
  - a music sound mode (`audio:music`)
- **Sequences can end by going home** (`end = home`). In CONTROL the servo goes straight back
  to its stick.
- **Example SD card** (`SDCardExamples/`): works out of the box, with a hello at power-up, test
  sequences, two droid sounds and two music tracks. `config.ini` lists every setting with its
  description, range and default.
- **With ConfigApp 0.9.0:** an Activities page, and rules can be moved up and down in the Events
  editor.

## 2.31.0 - October 2026

- **ConfigApp's Events tab** edits `events.ini` on the board without removing the SD card:
  - rules in plain words, edited with drop-downs
  - Learn: move a control and it picks the channel and position
  - Test runs a rule's actions now
  - the board checks the file when it's saved and shows any line it didn't accept
  - each rule lights up when it fires

## 2.30.0 - October 2026

- **`events.ini`:** one file for every switch, stick value, button and link event. It covers
  modes, presets and random sounds, and converts the older `buttons.ini` and switch settings.

## Earlier releases

| Version | Date | New for users |
|---|---|---|
| 2.29.0 | Oct 2026 | Sequences can call other sequences as clips (`seq nod 2x 50%`) |
| 2.26.0 | Oct 2026 | Channels numbered 1-24 as on the transmitter everywhere (RC PWM: IO pin = channel); old settings convert |
| 2.25.0 | Oct 2026 | Settings regrouped into 10 ConfigApp pages, with descriptions and scaled values in the app; older settings files convert automatically |
| 2.24.0 | Oct 2026 | One on/off switch per effect, applied instantly; post-filter switch works; stormtrooper radio sounds rebuilt |
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
