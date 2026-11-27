# The window viewer's protocol (`tools/winview`, OURS, 2026-11-26)

On 2026-11-26 the owner asked: "Figure out how to do emulate the mouse, keyboard and screen in
bluesim." The same day the owner added: "It's okay to make an emulator to go with this so we can
test look and feel".

`../../tools/winview/winview.c` is a standalone SDL2 program that acts as the emulated monitor,
keyboard and mouse. It is a separate program so that two kinds of client can use it:
- the Bluesim window hardware, through `../../bsv/WinHostDev.c`, which this repo already has;
- the fast software window stack, kl0 with `../../psi/windev.py`: `../../tools/simpos_live.py`
  (window M11, 2026-11-26; `../../psi/README.md` "Window M11: the live view").

`../../tools/winview_client.py` is a 70-line stdlib client. It is the protocol's check, and the
pattern for the software stack's client.

Everything here is OURS. The PSI had no such protocol: its display and keyboard hung off its own
buses (`window_hardware_plan.md` §1.1).

## Transport

- A Unix-domain stream socket. The viewer listens; one client is served at a time.
- The path is the viewer's first argument. It must be shorter than `sun_path`, which is 104 bytes
  on macOS. The viewer refuses a longer path rather than cutting it. A relative path is relative
  to the viewer's working directory.
- **A message** is one type byte, then a 4-byte big-endian length, then that many payload bytes.
  All multi-byte fields are big-endian. Unknown types are skipped by their length.

## Client to viewer

| type | payload | meaning |
|---|---|---|
| `H` | W (2), H (2), title (the rest, UTF-8) | hello: the screen's size in dots, the window title |
| `F` | W (2), H (2), H rows of ceil(W/8) bytes | a whole frame |
| `R` | X (2), Y (2), W (2), H (2), H rows of ceil(W/8) bytes | a dirty rectangle at (X, Y) |
| `T` | title | a new title |

- **Rows** are 1 bit a dot, MSB first, each row padded to a byte. **1 is a black dot** on white
  paper. This is PBM P4's raster: the frame of `../../psi/winfb.py` and the PSI's bit order
  (TM-115 p74-76).
- An `F` whose size differs from the current one resizes the window.
- `R` parts outside the screen are clipped.

## Viewer to client

| type | payload | meaning |
|---|---|---|
| `K` | DOWN (1), USAGE (2) | a key went down (1) or up (0). USAGE is the USB HID usage ID (HID Usage Tables §10, page 7), which is SDL2's `SDL_Scancode` number. A held key repeats its downs (typematic) |
| `M` | X (2), Y (2) | the mouse is at (X, Y), in screen dots (the window's pixels scaled by the window's real size to the frame's) |
| `B` | BUTTON (1: 0 left, 1 middle, 2 right), DOWN (1), X (2), Y (2) | a button |
| `Q` | none | the window was closed |
| `W` | T (4) | the time of the next `K`, `M` or `B`: SDL's event timestamp, ms (added 2026-11-26) |
| `E` | none | a `--play` file has ended (added 2026-11-26) |

- Events are raw: no click classification and no key translation. A client maps them:
  - `WinHostDev.c` turns keys into PS/2 set 2 bytes (its HOST table, checked against
    `../../tools/wininput.py`) and the mouse into PS/2 packets, so the RTL receivers do the rest;
  - `simpos_live.py` applies `wininput.py`'s two tables itself (HOST, then the keyboard
    receiver's KEYS), then the H7s adapter's click and move rules (`win_kl0_host.py`), with the
    stand-ins' key codes (`espc.KEY_CODES`).
- With the 2:1 view of mode 3 (640×480), `WinHostDev.c` doubles X and Y into frame coordinates
  and adds the scan configuration's pan (mode 3 shows the frame from row 24).
- X and Y are clamped to the screen. SDL reports positions outside the window while a button is
  held; before 2026-11-26 a negative one went out as about 65,000.
- `W` and `E` were added for the live view's real-time PS/2 model: `WinHostDev.c` keeps the gaps
  between a person's events, whatever the simulation's speed. A client that does not know them
  skips them by their length, as the rule above says; `winview_client.py` does.
- `simpos_live.py` classifies double clicks by `W`'s time, so two clicks stay two even when it
  reads them late, after a long kl0 run. (Window M11 first appended a 4-byte time to K, M and B;
  at the merge with the Bluesim live-view fix, both clients took `W` instead, 2026-11-26.)

## Running it

```
tools/winview/build.sh OUT                    # cc + pkg-config sdl2 (Homebrew 2.32.10)
OUT SOCKET [--scale N] [--dump F.pbm] [--fake-events] [--frames N] [--play F]
    [--events F.events] [--linger MS] [--no-fit]
python3 -I tools/winview_client.py SOCKET FRAME.pbm [SECONDS]
bsv/run_win_live.sh live [MODE]               # the Bluesim hardware on it (the owner's run)
python3 -I tools/simpos_live.py live          # the software window stack on it (window M11)
```

The window (window M11, 2026-11-26): it can be resized, and one larger than the display's usable
area is made smaller to fit (not with `--no-fit` or the dummy driver). The mouse is always
reported in frame dots, from the window's real size. With `--scale N` and a window that fits,
that is the window's pixels divided by N, as before. `--play`, `--events` and `--fake-events`
place their events by the inverse mapping.

Keys with Cmd (SDL's GUI modifier) are the viewer's own and are not sent. Cmd-S writes the frame
shown as `winview_N.pbm` next to the socket. On exit, the frame shown is written there as
`winview_last.pbm`. Every PBM is written as `F.tmp` and renamed, so a reader never sees half a
frame.

`--play FILE` pushes a scripted user's input into SDL's own queue at its wall-clock times, after
the first frame. The format is in `winview.c`'s header: `wait`, `move`, `glide`, `drift`,
`down`/`up`, `click`, `key`, `type` and `end`. `end` sends `E`. `bsv/run_win_live.sh` `flood`
plays `bsv/win_live/flood.play` this way.

`--events FILE` (window M11): after the first frame, the file's `MS K DOWN USAGE`, `MS M X Y`
and `MS B BUTTON DOWN X Y` lines (`simpos_live.py`'s event file; X and Y in dots) are pushed into
SDL's own queue at their times, so a recorded session leaves by the same code as a user's.
`--linger MS` (default 3000): once all are pushed and no frame has come for MS, the viewer sends
`Q` and exits.

The software stack's client sends `H` and `F` first, then one `R` per flush: the band of full
rows from the first changed row to the last. It flushes at every quiet moment of the PSI, and
every 40 ms while a long run draws.

Headless check, used by `bsv/run_win_live.sh` (its `viewer` and `flood` cases):
- `SDL_VIDEODRIVER=dummy` with `--fake-events`. After the first frame, the viewer pushes a key A
  press and release, a move to (10, 20) and a left click into SDL's own queue, so they leave by
  the same code as a user's.
- `--dump` writes each frame received as a PBM.

The check made on 2026-11-26:
- `winview_client.py` sent the H7s console frame and printed `key down 04`, `key up 04`,
  `move 10 20`, `button l down 10 20`, `button l up 10 20`;
- the dump was byte-identical to the frame sent (`cmp`).
