"""Turn a recorder take (/REC/REC_NNN.csv) into a [sequence.NAME] for sequences.ini.

A take is every frame of the sticks; a sequence is a few timed moves. This keeps, for each
servo, only the points the motion can't do without (the line between kept points stays within
--tolerance degrees of what was recorded) and makes each one a step that moves to the next point
over the time between them, so the servo's easing draws the curve back in.

    py tools/rec2seq.py REC_003.csv --info                       what's in the take
    py tools/rec2seq.py REC_003.csv --name wave                  print the sequence
    py tools/rec2seq.py REC_003.csv --name wave --from 2 --to 9 --servos s1,s2 --check
    py tools/rec2seq.py REC_003.csv --name nod --relative --append SDCardSparky/sequences.ini

Degrees come from the same sum CONTROL mode uses (Teensy's map(raw, sbusMin, sbusMax, 0, 180),
with the SBUS range from the take's header), so a converted move goes where the stick sent the
servo. Whole takes (a song) are too many steps for one sequence (256): play those as a `take`
step instead (SBUS recorder plan §2A, SBR-024). The button pad and other non-servo channels
can't become steps; they are listed and left out.

Plan: docs/SBUS_RECORDER_IMPLEMENTATION_PLAN.md §2A.4. Tests: tools/tests/test_rec2seq.py.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DROID_LIBS = ROOT.parent.parent.parent / "Software" / "droid-libs"   # Projects/Electronics/Software

MAX_STEPS = 256           # Sequencer: steps per sequence (MAX_STEPS_PER_SEQUENCE)
MAX_STEP_MS = 65535       # Sequencer: a step's duration is 16-bit
MAX_NAME = 31             # Sequencer: sequence name length
CONTROL_DEADBAND_DEG = 2  # src/motion/ServoModes.cpp SERVO_CONTROL_DEADBAND: the live robot ignores less
SERVOS = [f"s{n}" for n in range(1, 9)]


class TakeError(Exception):
    """A take that can't be read, or options that don't fit it."""


@dataclass
class Take:
    path: Path
    meta: dict[str, str]
    channels: list[int]                    # column order, 1-24
    times: list[int] = field(default_factory=list)            # ms from the take's start
    values: dict[int, list[int]] = field(default_factory=dict)  # channel -> raw SBUS per row

    def num(self, key: str, default: int) -> int:
        try:
            return int(self.meta[key])
        except (KeyError, ValueError):
            return default

    @property
    def duration_ms(self) -> int:
        return self.num("rec.durationMs", self.times[-1] if self.times else 0)

    def servo_map(self) -> dict[int, str]:
        """rec.servoMap=ch1:s1,ch3:s2 -> {1: 's1', 3: 's2'}"""
        out: dict[int, str] = {}
        for item in self.meta.get("rec.servoMap", "").split(","):
            m = re.fullmatch(r"ch(\d+):(s[1-8])", item.strip())
            if m:
                out[int(m.group(1))] = m.group(2)
        return out


# ---------------------------------------------------------------------------- reading
def read_take(path: Path) -> Take:
    """The recorder's CSV: '# key=value' header lines, the column line, then rows."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    meta: dict[str, str] = {}
    take: Take | None = None
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            for key, value in re.findall(r"([\w.]+)=(\S*)", line):
                meta[key] = value
            continue
        cells = [c.strip() for c in line.split(",")]
        if take is None:
            if cells[0] != "ms" or not all(re.fullmatch(r"ch\d+", c) for c in cells[1:]):
                raise TakeError(f"{path}: line {n}: expected the column line 'ms,chN,...', got {line!r}")
            chans = [int(c[2:]) for c in cells[1:]]
            take = Take(Path(path), meta, chans, [], {c: [] for c in chans})
            continue
        if len(cells) != len(take.channels) + 1:
            raise TakeError(f"{path}: line {n}: {len(cells)} values, expected {len(take.channels) + 1}")
        try:
            row = [int(c) for c in cells]
        except ValueError:
            raise TakeError(f"{path}: line {n}: not a number in {line!r}") from None
        take.times.append(row[0])
        for ch, v in zip(take.channels, row[1:]):
            take.values[ch].append(v)
    if take is None or not take.times:
        raise TakeError(f"{path}: no rows (is this a recorder take?)")
    return take


# ---------------------------------------------------------------------------- the maths
def _cdiv(a: int, b: int) -> int:
    """C's integer division: truncates toward zero (Python's // floors)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def teensy_map(x: int, in_min: int, in_max: int, out_min: int, out_max: int) -> int:
    """Teensy 4's integer map() (cores/teensy4/wiring.h): rounds instead of truncating."""
    in_range, out_range = in_max - in_min, out_max - out_min
    if in_range == 0:
        return out_min + _cdiv(out_range, 2)
    num = (x - in_min) * out_range
    num += _cdiv(in_range, 2) if out_range >= 0 else -_cdiv(in_range, 2)
    result = _cdiv(num, in_range) + out_min
    if out_range >= 0:
        if in_range * num < 0:
            return result - 1
    elif in_range * num >= 0:
        return result + 1
    return result


def to_degrees(raw: int, sbus_min: int, sbus_max: int) -> int:
    """What CONTROL mode sends a servo for this stick value (0-180)."""
    return max(0, min(180, teensy_map(raw, sbus_min, sbus_max, 0, 180)))


def keyframes(times: list[int], degs: list[int], tolerance: float, min_gap_ms: int) -> list[int]:
    """Indices of the points to keep: straight lines between them stay within `tolerance`
    degrees of every recorded point (Douglas-Peucker on the error in degrees), and no two kept
    points are closer than `min_gap_ms` (the last always stays)."""
    n = len(times)
    if n <= 2:
        return list(range(n))
    keep = {0, n - 1}
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        ta, tb, da, db = times[a], times[b], degs[a], degs[b]
        worst, worst_i = -1.0, -1
        for i in range(a + 1, b):
            line = da if tb == ta else da + (db - da) * (times[i] - ta) / (tb - ta)
            err = abs(degs[i] - line)
            if err > worst:
                worst, worst_i = err, i
        if worst > tolerance:
            keep.add(worst_i)
            stack.extend([(a, worst_i), (worst_i, b)])
    kept = sorted(keep)
    out = [kept[0]]
    for i in kept[1:-1]:
        if times[i] - times[out[-1]] >= min_gap_ms:
            out.append(i)
    if times[kept[-1]] - times[out[-1]] < min_gap_ms and len(out) > 1:
        out.pop()                                     # the last point beats one just before it
    out.append(kept[-1])
    return out


# ---------------------------------------------------------------------------- building
@dataclass
class Step:
    start: int
    servo: str          # s1..s8, or audioA / audioB
    target: int         # degrees (absolute), delta (relative) or the track
    duration: int = 0
    relative: bool = False


@dataclass
class Options:
    name: str
    servos: list[str] | None = None        # None = every servo the take recorded
    start_s: float = 0.0
    end_s: float | None = None
    tolerance: float = CONTROL_DEADBAND_DEG
    min_gap_ms: int = 40
    relative: bool = False
    speed: float = 1.0
    song: int | None = None                 # track number, 0 = the take's rec.audioTrack
    bank: str = "A"
    end: str = "hold"
    lead_in_ms: int = 0
    fit: bool = False


@dataclass
class Result:
    steps: list[Step]
    tolerance: float
    notes: list[str]


def _servo_columns(take: Take, servos: list[str] | None) -> tuple[dict[str, int], list[str]]:
    """{servo: channel} for the servos to convert, plus notes on what's left out."""
    by_channel = take.servo_map()
    if not by_channel:
        raise TakeError("the take has no rec.servoMap header line, so its channels can't be matched to servos")
    notes = []
    chosen: dict[str, int] = {}
    for ch in take.channels:
        servo = by_channel.get(ch)
        if servo is None:
            what = "the button pad" if str(ch) == take.meta.get("rec.buttonCh") else "not a servo's channel"
            notes.append(f"ch{ch} left out ({what}: sequences only move servos)")
            continue
        if servos is None or servo in servos:
            chosen[servo] = ch
    for s in servos or []:
        if s not in chosen:
            raise TakeError(f"{s} isn't in this take (servos recorded: {', '.join(sorted(by_channel.values())) or 'none'})")
    if not chosen:
        raise TakeError("no servo to convert")
    return chosen, notes


def build(take: Take, opt: Options) -> Result:
    """The sequence's steps for these options, at the smallest tolerance that fits when fit."""
    if not 0 < opt.speed <= 10:
        raise TakeError("--speed must be above 0 and at most 10")
    t_from = int(round(opt.start_s * 1000))
    t_to = take.duration_ms if opt.end_s is None else int(round(opt.end_s * 1000))
    rows = [i for i, t in enumerate(take.times) if t_from <= t <= t_to]
    if len(rows) < 2:
        raise TakeError(f"fewer than 2 rows between {t_from} and {t_to} ms (the take is {take.duration_ms} ms)")
    columns, notes = _servo_columns(take, opt.servos)
    sbus_min, sbus_max = take.num("rec.sbusMin", 172), take.num("rec.sbusMax", 1811)
    times = [take.times[i] - t_from for i in rows]

    track = None
    if opt.song is not None:
        track = opt.song or take.num("rec.audioTrack", 0)
        if not track:
            raise TakeError("--song with no number, and the take has no rec.audioTrack")
        if t_from > 0 or opt.speed != 1:
            notes.append("the song starts from its beginning: with --from or --speed it won't line up with the moves")

    tolerance = opt.tolerance
    while True:
        steps = _steps(take, opt, rows, times, columns, sbus_min, sbus_max, tolerance, track)
        if len(steps) <= MAX_STEPS or not opt.fit or tolerance >= 20:
            break
        tolerance = round(tolerance * 1.5, 1)
    if len(steps) > MAX_STEPS:
        raise TakeError(
            f"{len(steps)} steps, more than a sequence holds ({MAX_STEPS}). Try --fit, a larger "
            f"--tolerance or --min-gap, fewer --servos, or a shorter --from/--to; or play the whole "
            f"take as a `take` step")
    if any(s.duration >= MAX_STEP_MS for s in steps):
        notes.append(f"some moves were longer than {MAX_STEP_MS} ms, a step's limit: they arrive early, then hold")
    return Result(steps, tolerance, notes)


def _steps(take, opt, rows, times, columns, sbus_min, sbus_max, tolerance, track) -> list[Step]:
    lead = max(0, opt.lead_in_ms)

    def at(ms: float) -> int:
        return int(round(ms / opt.speed)) + lead

    steps: list[Step] = []
    if track:
        steps.append(Step(lead, "audio" + opt.bank, track))
    for servo, ch in sorted(columns.items()):
        degs = [to_degrees(take.values[ch][i], sbus_min, sbus_max) for i in rows]
        keep = keyframes(times, degs, tolerance, opt.min_gap_ms)
        if lead and not opt.relative:
            steps.append(Step(0, servo, degs[keep[0]], lead))       # glide to the first pose
        prev = degs[keep[0]]
        for a, b in zip(keep, keep[1:]):
            target = degs[b] - prev if opt.relative else degs[b]
            dur = min(MAX_STEP_MS, at(times[b]) - at(times[a]))
            steps.append(Step(at(times[a]), servo, target, dur, opt.relative))
            prev = degs[b]
    steps.sort(key=lambda s: (s.start, not s.servo.startswith("audio"), s.servo))
    return steps


# ---------------------------------------------------------------------------- writing
def format_sequence(take: Take, opt: Options, res: Result) -> str:
    servos = sorted({s.servo for s in res.steps if not s.servo.startswith("audio")})
    span_to = f"{opt.end_s:g}" if opt.end_s is not None else f"{take.duration_ms / 1000:g}"
    lines = [
        f"; {opt.name}: from {take.path.name}, {opt.start_s:g}-{span_to} s"
        + (f" at {opt.speed:g}x" if opt.speed != 1 else "") + f", {' '.join(servos)}"
        + (" (relative)" if opt.relative else ""),
        f"; rec2seq.py: within {res.tolerance:g} deg, moves at least {opt.min_gap_ms} ms apart, "
        f"{len(res.steps)} steps (limit {MAX_STEPS}). Smoothest with easingType 0 (linear) on these servos.",
        f"[sequence.{opt.name}]",
    ]
    if opt.end != "hold":
        lines.append(f"end = {opt.end}")
    width = max(len(str(s.start)) for s in res.steps)
    for i, s in enumerate(res.steps):
        key = ("r" if s.relative else "s") + str(i)
        if s.servo.startswith("audio"):
            lines.append(f"{key} = {s.start:<{width}} {s.servo} {s.target}")
        else:
            lines.append(f"{key} = {s.start:<{width}} {s.servo} {s.target} {s.duration}")
    return "\n".join(lines) + "\n"


def append_to(path: Path, name: str, block: str, replace: bool) -> str:
    """Add the block to a sequences.ini (or replace a section of the same name)."""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.splitlines(keepends=True)
    header = re.compile(r"\s*\[sequence\." + re.escape(name) + r"\]\s*$", re.IGNORECASE)
    start = next((i for i, l in enumerate(lines) if header.match(l)), None)
    if start is None:
        sep = "" if not text or text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        path.write_text(text + sep + block, encoding="utf-8")
        return "added"
    if not replace:
        raise TakeError(f"{path} already has [sequence.{name}]: use --replace, or another --name")
    end = start + 1
    # The two comment lines rec2seq wrote above it go too
    while start > 0 and (lines[start - 1].startswith(f"; {name}:") or "; rec2seq.py:" in lines[start - 1]):
        start -= 1
    while end < len(lines) and not lines[end].lstrip().startswith("["):
        end += 1                                      # the section runs to the next [header]
    while end - 1 > start and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith((";", "#"))):
        end -= 1                                      # comments just above that header are the next one's
    rest = "".join(lines[end:]).lstrip("\n")
    path.write_text("".join(lines[:start]) + block + ("\n" + rest if rest else ""), encoding="utf-8")
    return "replaced"


def check_with_loader(block: str) -> tuple[bool, str]:
    """Load the sequence with droid-libs' Sequencer (its host test), as the robot would."""
    runner = DROID_LIBS / "libs" / "Sequencer" / "test" / "run.sh"
    if not runner.exists():
        return False, f"skipped: no {runner}"
    if not shutil.which("sh") or not shutil.which("g++"):
        return False, "skipped: needs sh and g++ (Git Bash) on the PATH"
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "sequences.ini"
        f.write_text(block, encoding="utf-8")
        p = subprocess.run(["sh", str(runner), str(f)], capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip()
    return p.returncode == 0, out.splitlines()[-1] if p.returncode == 0 else out


def describe(take: Take) -> str:
    sbus_min, sbus_max = take.num("rec.sbusMin", 172), take.num("rec.sbusMax", 1811)
    smap = take.servo_map()
    rate = take.meta.get("rec.rateHz", "?")
    out = [f"{take.path.name}: {take.duration_ms / 1000:.1f} s, {len(take.times)} rows at {rate} Hz, "
           f"firmware {take.meta.get('fw.version', '?')}, song {take.num('rec.audioTrack', 0) or 'none'}"]
    for ch in take.channels:
        degs = [to_degrees(v, sbus_min, sbus_max) for v in take.values[ch]]
        what = smap.get(ch) or ("button pad" if str(ch) == take.meta.get("rec.buttonCh") else "-")
        out.append(f"  ch{ch:<3} {what:<11} {min(degs):3d}-{max(degs):3d} deg"
                   f"   raw {min(take.values[ch])}-{max(take.values[ch])}")
    return "\n".join(out)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Turn a recorder take into a [sequence.NAME] for sequences.ini.")
    p.add_argument("take", type=Path, help="a /REC/REC_NNN.csv from the card")
    p.add_argument("--info", action="store_true", help="show what the take holds, then stop")
    p.add_argument("--name", help="the sequence name (lower_case words, under 32 characters)")
    p.add_argument("--from", dest="start_s", type=float, default=0.0, help="start at this time in the take (s)")
    p.add_argument("--to", dest="end_s", type=float, help="end at this time in the take (s)")
    p.add_argument("--servos", help="only these, e.g. s1,s3 (default: every servo recorded)")
    p.add_argument("--tolerance", type=float, default=CONTROL_DEADBAND_DEG,
                   help=f"how far (deg) the moves may stray from the take (default {CONTROL_DEADBAND_DEG}, "
                        "the stick deadband)")
    p.add_argument("--min-gap", type=int, default=40, help="ms between one servo's moves at least (default 40)")
    p.add_argument("--fit", action="store_true", help=f"raise the tolerance until it fits in {MAX_STEPS} steps")
    p.add_argument("--relative", action="store_true",
                   help="rN steps (move BY): a gesture that works from wherever the servo is, for clips")
    p.add_argument("--speed", type=float, default=1.0, help="2 = twice as fast, 0.5 = half (default 1)")
    p.add_argument("--song", type=int, nargs="?", const=0,
                   help="start a WAV at the beginning: the take's rec.audioTrack, or the number given")
    p.add_argument("--bank", choices=["A", "B"], default="A", help="the player for --song (default A)")
    p.add_argument("--end", choices=["hold", "home"], default="hold", help="what the servos do after it")
    p.add_argument("--lead-in", type=int, default=0,
                   help="ms to glide to the first pose before the moves (and the song) start")
    p.add_argument("--append", type=Path, help="add the sequence to this sequences.ini")
    p.add_argument("--replace", action="store_true", help="with --append: replace a sequence of the same name")
    p.add_argument("--check", action="store_true", help="load it with the droid-libs Sequencer, as the robot would")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        take = read_take(a.take)
        if a.info:
            print(describe(take))
            return 0
        if not a.name or not re.fullmatch(r"[A-Za-z0-9_]+", a.name) or len(a.name) > MAX_NAME:
            raise TakeError(f"--name: letters, digits and _ only, at most {MAX_NAME} characters")
        servos = [s.strip().lower() for s in a.servos.split(",")] if a.servos else None
        for s in servos or []:
            if s not in SERVOS:
                raise TakeError(f"--servos: {s!r} isn't s1..s8")
        opt = Options(a.name, servos, a.start_s, a.end_s, a.tolerance, a.min_gap, a.relative, a.speed,
                      a.song, a.bank, a.end, a.lead_in, a.fit)
        res = build(take, opt)
    except (OSError, TakeError) as e:
        print(f"rec2seq: {e}", file=sys.stderr)
        return 1
    block = format_sequence(take, opt, res)
    for note in res.notes:
        print(f"; note: {note}", file=sys.stderr)
    if a.check:
        ok, msg = check_with_loader(block)
        print(f"; check: {msg}", file=sys.stderr)
        if not ok and not msg.startswith("skipped"):
            return 1
    if a.append:
        try:
            how = append_to(a.append, a.name, block, a.replace)
        except (OSError, TakeError) as e:
            print(f"rec2seq: {e}", file=sys.stderr)
            return 1
        print(f"; {how} [sequence.{a.name}] in {a.append} ({len(res.steps)} steps)", file=sys.stderr)
    else:
        print(block, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
