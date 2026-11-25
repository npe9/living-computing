#!/usr/bin/env python3
"""A word-level model of the Analog Devices AD1849K SoundPort stereo codec,
the codec on the BeBox audio card's DSP3210 serial port.

Why this part: Be's audio task build file (/system/vcos/be.oem/audio.tbd
on the Nov 1994 disk) says the frame control word "is exactly what the
AD1849 codec expects", and /be/headers/vcos/audio.h describes "the
AD1489's [sic] 64 bit data frame"; the driver (be.oem/audio) builds
control words in exactly the AD1849K's layout (docs/dsp3210.md).

Written from the AD1849K data sheet, REV. 0 (docs/dsp3210/MANIFEST.md;
pages are the printed ones):

  - control words (pp. 11-13) and data words (pp. 14-15), 64 bits, MSB
    first; bit 63 is bit 31 of the first 32-bit serial slot;
  - register defaults out of reset and at a control-to-data transition
    (p. 16);
  - control mode: the codec echoes each control word in the next frame;
    its first output word is the current registers with DCB = 1 (p. 20);
  - the DCB handshake (pp. 20-21): after a word with DCB = 0 is
    received, a later word with DCB = 1 is the last one taken; it is
    echoed, then SDTX is three-stated (read here as zero words);
  - D/C high: data mode; autocalibration takes 194 frames, with ADI = 1
    (pp. 11, 21); master mode (MS = 1) gives SCLK = 64 * FS for 64-bit
    frames (FSEL = 0), FS = crystal / divide factor (DFR, p. 12);
  - data formats (DF, p. 12): 16-bit linear, 8-bit mu-law, A-law and
    unsigned; mono (ST = 0) uses the left sample for both DACs and puts
    the left input on both ADC outputs (p. 12);
  - output attenuation LO/RO, 1.5 dB a step, 63 = mute (p. 14).

What this model leaves out, by choice: the analog mutes OM1/OM0/SM, input
gain LG/RG, mic select IS, monitor mix MA and the loopback modes are
stored and echoed but not applied: the WAV written is the DAC output
after digital attenuation, and the input WAV is taken as the ADC's input.
The 2 ms rate-settling rule (p. 21) applies only to SCLK/CLKIN clocking,
which fails loud here; the internal crystals give a next-frame echo.

The pins: RESET (active low), PDN (active high) and D/C.  The BeBox
drives them from DSP BIO pins; which pin is which is INFERRED from Be's
driver (docs/dsp3210.md): BIO0 RESET (released 50 ms after it is driven
low, the data sheet's minimum), BIO1 PDN (always low), BIO2 D/C (high
once the DCB handshake is done).

Interface to tools/dsp3210.py (the core's `sio_dev`): clock(),
exchange(word), sy; see DSP3210._sio_tick.
"""

import struct
import wave

XTAL = {1: 24576000, 2: 16934400}
DIVIDE = [3072, 1536, 896, 768, 448, 384, 512, 2560]      # DFR2:0, p. 12
AUTOCAL_FRAMES = 194                                       # p. 11

BEBOX_BIO = {0: "reset", 1: "pdn", 2: "dc"}                # INFERRED


class CodecError(Exception):
    """A state the model does not cover, reached by the program."""


def ulaw_decode(b):
    b = ~b & 0xFF
    t = ((b & 0x0F) << 3) + 0x84
    t <<= (b & 0x70) >> 4
    return (0x84 - t) if b & 0x80 else (t - 0x84)


def alaw_decode(b):
    b ^= 0x55
    t = (b & 0x0F) << 4
    seg = (b & 0x70) >> 4
    if seg == 0:
        t += 8
    elif seg == 1:
        t += 0x108
    else:
        t = (t + 0x108) << (seg - 1)
    return t if b & 0x80 else -t


def ulaw_encode(x):
    sign = 0x80 if x < 0 else 0
    x = min(abs(x), 32635) + 0x84
    seg = max(0, x.bit_length() - 8)
    return ~(sign | seg << 4 | (x >> (seg + 3)) & 0x0F) & 0xFF


def alaw_encode(x):
    sign = 0x80 if x >= 0 else 0
    x = min(abs(x), 32767) >> 3
    if x < 32:
        v = x >> 1
    else:
        seg = x.bit_length() - 5
        v = seg << 4 | (x >> seg) & 0x0F
    return (sign | v) ^ 0x55


class AD1849K:
    """One codec.  `cki_hz` is the DSP's CKI (vcos.cfg DspClock 50000000),
    used to express the codec's own clock in DSP clocks."""

    def __init__(self, cki_hz=50000000, control_phase=1):
        self.cki_hz = cki_hz
        # In control mode the codec is a slave and its 64-bit word starts
        # at TSIN (p. 20), which the controller side places; where TSIN
        # falls on the BeBox is not known.  control_phase = 1: the first
        # 32-bit slot after RESET or D/C goes low is the second half of a
        # word.  Be's driver (get_in_frame_sync, audio 0xa1c) keeps
        # whatever alignment it starts with, so the right value depends
        # on the DSP's timing: 1 works for the model's timing of Be's
        # init; delaying the driver by one slot (480 cycles) after RESET
        # needs 0.  A "MCK=0" CodecError at D/C high means: flip it.
        # This is a stand-in for the board's TSIN wiring, not a fact.
        self.control_phase = control_phase
        self.pins = dict(reset=0, pdn=0, dc=0)
        self.played = []           # [rate, channels, bytearray of int16]
        self.record = []           # (left, right) int16 pairs to play into the ADC
        self.rec_pos = 0
        self.log = []              # (frame, event) for tests and debugging
        self.frames = 0
        self._power_on()

    # ---------------------------------------------- pins and state

    def _power_on(self):
        """Defaults out of reset or power down (p. 16)."""
        self.mb = self.olb = self.ac = 0
        self.dcb = 1
        self.dfr, self.st, self.df = 0, 0, 1
        self.its, self.mck, self.fsel, self.ms, self.txdis = 0, 0, 2, 0, 1
        self.enl = self.adl = 0
        self.pio = 3
        self._data_defaults()
        self.adi = 1
        self.mode = "reset"
        self._enter()

    def _data_defaults(self):
        """The registers a control-to-data transition resets (p. 16)."""
        self.om, self.lo, self.sm, self.ro = 0, 63, 0, 63
        self.ovr, self.is_, self.lg, self.ma, self.rg = 0, 0, 0, 15, 0

    def _enter(self):
        """Out of reset/power down, or on a D/C edge: the mode follows D/C
        (p. 20)."""
        if self.pins["reset"] == 0 or self.pins["pdn"] == 1:
            self.mode = "reset"
            return
        self.slot = 0
        self.inw = [0, 0]
        if not self.pins["dc"]:
            self.slot = self.control_phase
        if self.pins["dc"]:
            self.mode = "data"
            self._data_defaults()
            self.autocal = AUTOCAL_FRAMES
            self.adi = 1
            self.outw = [0, self._status()]
            if self.mck not in XTAL:
                raise CodecError("data mode with MCK=%d (SCLK/CLKIN clocking) "
                                 "not modelled" % self.mck)
            if self.fsel != 0:
                raise CodecError("data mode with FSEL=%d (%d-bit frames) not "
                                 "modelled" % (self.fsel, 64 << self.fsel))
            rate = XTAL[self.mck] / DIVIDE[self.dfr]
            self.log.append((self.frames, "data %s %g Hz %s DF=%d" % (
                "master" if self.ms else "slave", rate,
                "stereo" if self.st else "mono", self.df)))
            self.played.append([rate, 2 if self.st else 1, bytearray()])
        else:
            self.mode = "control"
            self.got_dcb0 = False
            self.locked = False     # the second interlock is done
            self.tristate = False
            self.outw = self._control_word(dcb=1)   # first word: DCB = 1
            self.log.append((self.frames, "control"))

    def pin(self, name, level):
        level = int(bool(level))
        if self.pins[name] == level:
            return
        old_off = self.pins["reset"] == 0 or self.pins["pdn"] == 1
        self.pins[name] = level
        now_off = self.pins["reset"] == 0 or self.pins["pdn"] == 1
        if now_off:
            if not old_off:
                self._power_on()
            return
        if old_off or name == "dc":
            self._enter()

    def bio(self, pins, mapping=BEBOX_BIO):
        """The DSP's BIO outputs changed (DSP3210.on_bio)."""
        for bit, name in mapping.items():
            self.pin(name, pins >> bit & 1)

    # ---------------------------------------------- the serial port

    @property
    def sy(self):
        """Frame sync for the slot about to start: high in a frame's first
        slot.  INFERRED: the BeBox's SY wiring is not known; Be's driver
        waits for SY high then low before it reprograms the port."""
        return self.mode != "reset" and self.slot == 0

    def clock(self):
        """CKI per bit, as (num, den), while the codec drives SCLK: data
        mode, master (MS = 1), SCLK = 64 bits * FS (p. 17)."""
        if self.mode == "data" and self.ms:
            return (self.cki_hz * DIVIDE[self.dfr], 64 * XTAL[self.mck])
        return None

    def exchange(self, word):
        """One 32-bit slot: `word` came in on SDRX, the result goes out on
        SDTX."""
        if self.mode == "reset":
            return 0
        out = self.outw[self.slot]
        self.inw[self.slot] = word & 0xFFFFFFFF
        self.slot ^= 1
        if self.slot == 0:
            self.frames += 1
            if self.mode == "control":
                self._control_frame()
            else:
                self._data_frame()
        return out

    # ---------------------------------------------- control mode

    def _control_word(self, dcb):
        b1 = 0x20 | self.mb << 4 | self.olb << 3 | dcb << 2 | self.ac
        b2 = self.dfr << 3 | self.st << 2 | self.df
        b3 = (self.its << 7 | self.mck << 4 | self.fsel << 2 | self.ms << 1
              | self.txdis)
        b4 = self.enl << 1 | self.adl
        b5 = self.pio << 6
        b7 = 0x20 | 0x2                                    # REVID 0010
        return [b1 << 24 | b2 << 16 | b3 << 8 | b4, b5 << 24 | b7 << 8]

    def _control_frame(self):
        w0, w1 = self.inw
        if self.tristate:
            self.outw = [0, 0]
            return
        if self.locked:            # the DCB = 1 word went out: three-state
            self.tristate = True
            self.outw = [0, 0]
            return
        b1, b2, b3, b4 = w0 >> 24, w0 >> 16 & 0xFF, w0 >> 8 & 0xFF, w0 & 0xFF
        self.mb, self.olb, self.dcb, self.ac = b1 >> 4 & 1, b1 >> 3 & 1, b1 >> 2 & 1, b1 & 1
        self.dfr, self.st, self.df = b2 >> 3 & 7, b2 >> 2 & 1, b2 & 3
        self.its, self.mck, self.fsel = b3 >> 7, b3 >> 4 & 7, b3 >> 2 & 3
        self.ms, self.txdis = b3 >> 1 & 1, b3 & 1
        self.enl, self.adl = b4 >> 1 & 1, b4 & 1
        self.pio = w1 >> 30 & 3
        self.outw = [w0, w1]       # the echo, bit for bit, next frame
        if not self.dcb:
            if not self.got_dcb0:
                self.log.append((self.frames, "dcb0"))
            self.got_dcb0 = True
        elif self.got_dcb0:
            self.locked = True
            self.log.append((self.frames, "dcb1"))

    # ---------------------------------------------- data mode

    def _sample_in(self, s):
        """DAC input code -> int16 (DF, p. 12)."""
        if self.df == 0:
            return s - 0x10000 if s & 0x8000 else s
        b = s >> 8
        if self.df == 1:
            return ulaw_decode(b)
        if self.df == 2:
            return alaw_decode(b)
        return (b - 128) << 8

    def _sample_out(self, x):
        """int16 -> ADC output code, left-justified in 16 bits."""
        if self.df == 0:
            return x & 0xFFFF
        if self.df == 1:
            return ulaw_encode(x) << 8
        if self.df == 2:
            return alaw_encode(x) << 8
        return ((x >> 8) + 128) << 8

    @staticmethod
    def _attenuate(x, a):
        if a == 63:
            return 0
        return int(round(x * 10 ** (-1.5 * a / 20)))

    def _data_frame(self):
        w0, w1 = self.inw
        # Data bytes 5-8 (pp. 14-15), taken for this frame's samples.
        self.om, self.lo = w1 >> 30, w1 >> 24 & 0x3F
        self.sm, self.ro = w1 >> 22 & 1, w1 >> 16 & 0x3F
        if not w1 >> 13 & 1:
            self.ovr = 0           # writing 0 clears; 1 is ignored (p. 15)
        self.is_, self.lg = w1 >> 12 & 1, w1 >> 8 & 0xF
        self.ma, self.rg = w1 >> 4 & 0xF, w1 & 0xF
        seg = self.played[-1]
        if self.autocal:
            self.autocal -= 1
            if self.autocal == 0:
                self.adi = 0
                self.log.append((self.frames, "calibrated"))
            left = right = 0
        else:
            left = self._attenuate(self._sample_in(w0 >> 16), self.lo)
            right = (self._attenuate(self._sample_in(w0 & 0xFFFF), self.ro)
                     if self.st else None)
        seg[2] += struct.pack("<h", max(-32768, min(32767, left)))
        if self.st:
            seg[2] += struct.pack("<h", max(-32768, min(32767, right)))
        # The next frame's output word: the ADC samples and the registers.
        if self.adi:
            l_in = r_in = 0
        else:
            l_in, r_in = self._next_record()
            if not self.st:
                r_in = l_in
        self.outw = [self._sample_out(l_in) << 16 | self._sample_out(r_in),
                     self._status()]

    def _status(self):
        """Data bytes 5-8 as the codec sends them (pp. 14-15)."""
        return (self.om << 30 | self.lo << 24 | self.adi << 23 | self.sm << 22
                | self.ro << 16 | self.pio << 14 | self.ovr << 13
                | self.is_ << 12 | self.lg << 8 | self.ma << 4 | self.rg)

    def _next_record(self):
        if self.rec_pos < len(self.record):
            v = self.record[self.rec_pos]
            self.rec_pos += 1
            return v
        return 0, 0

    # ---------------------------------------------- WAV files

    def load_wav(self, path):
        """Samples for the ADC, one per frame, from a 16-bit PCM WAV (mono
        or stereo).  The file's rate is not converted: frame n takes
        sample n."""
        with wave.open(path, "rb") as w:
            if w.getsampwidth() != 2 or w.getnchannels() not in (1, 2):
                raise CodecError("%s: 16-bit mono or stereo PCM only" % path)
            ch = w.getnchannels()
            raw = w.readframes(w.getnframes())
        v = struct.unpack("<%dh" % (len(raw) // 2), raw)
        if ch == 1:
            self.record = [(x, x) for x in v]
        else:
            self.record = list(zip(v[0::2], v[1::2]))
        self.rec_pos = 0

    def save_wav(self, path):
        """The DAC output of every data-mode stretch, autocalibration
        frames included (silent), as 16-bit PCM.  Returns the frame count.
        Stretches at different rates or channel counts fail loud."""
        segs = [s for s in self.played if s[2]]
        if not segs:
            segs = self.played[-1:] or [[8000, 1, bytearray()]]
        rate, ch = segs[0][0], segs[0][1]
        if any((s[0], s[1]) != (rate, ch) for s in segs):
            raise CodecError("data mode changed rate or channels between "
                             "stretches; one WAV cannot hold them")
        data = b"".join(bytes(s[2]) for s in segs)
        with wave.open(path, "wb") as w:
            w.setnchannels(ch)
            w.setsampwidth(2)
            w.setframerate(int(round(rate)))
            w.writeframes(data)
        return len(data) // (2 * ch)
