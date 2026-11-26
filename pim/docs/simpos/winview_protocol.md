# The window viewer's protocol (`tools/winview`, OURS, 2026-11-26)

On 2026-11-26 the owner asked: "Figure out how to do emulate the mouse, keyboard and screen in
bluesim." The same day the owner added: "It's okay to make an emulator to go with this so we can
test look and feel".

`../../tools/winview/winview.c` is a standalone SDL2 program that acts as the emulated monitor,
keyboard and mouse. It is a separate program so that two kinds of client can use it:
- the Bluesim window hardware, through `../../bsv/WinHostDev.c`, which this repo already has;
- the fast software window stack, kl0 with `../../psi/windev.py`. That client is left to a later
  agent, and `psi/` is not touched here.

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
| `M` | X (2), Y (2) | the mouse is at (X, Y), in screen dots (the window's pixels divided by `--scale`) |
| `B` | BUTTON (1: 0 left, 1 middle, 2 right), DOWN (1), X (2), Y (2) | a button |
| `Q` | none | the window was closed |

- Events are raw: no click classification and no key translation. A client maps them:
  - `WinHostDev.c` turns keys into PS/2 set 2 bytes (its HOST table, checked against
    `../../tools/wininput.py`) and the mouse into PS/2 packets, so the RTL receivers do the rest;
  - a software client would apply `wininput.py`'s two tables itself.
- With the 2:1 view of mode 3 (640×480), `WinHostDev.c` doubles X and Y into frame coordinates.

## Running it

```
tools/winview/build.sh OUT                    # cc + pkg-config sdl2 (Homebrew 2.32.10)
OUT SOCKET [--scale N] [--dump F.pbm] [--fake-events] [--frames N]
python3 -I tools/winview_client.py SOCKET FRAME.pbm [SECONDS]
bsv/run_win_live.sh live [MODE]               # the Bluesim hardware on it (the owner's run)
```

Headless check, used by `bsv/run_win_live.sh` (its `viewer` case):
- `SDL_VIDEODRIVER=dummy` with `--fake-events`. After the first frame, the viewer pushes a key A
  press and release, a move to (10, 20) and a left click into SDL's own queue, so they leave by
  the same code as a user's.
- `--dump` writes each frame received as a PBM.

The check made on 2026-11-26:
- `winview_client.py` sent the H7s console frame and printed `key down 04`, `key up 04`,
  `move 10 20`, `button l down 10 20`, `button l up 10 20`;
- the dump was byte-identical to the frame sent (`cmp`).
