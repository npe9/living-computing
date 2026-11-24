#!/usr/bin/env python3
"""SONIC traces: capture from the reference model, re-check against a fresh
model, and turn into vectors for the RTL testbench (SonicReplayTb.bsv).

    python3 sonic_trace.py capture TRACE.gz      (~4 min: the join to rc)
    python3 sonic_trace.py check TRACE.gz        (a fresh p9boot.Sonic)
    python3 sonic_trace.py vectors TRACE.gz DIR  (DIR/{events,dma,rx,tx}.hex)

capture runs s9term on the reference model through the replayed join of
tests/test_p9boot.py JoinReplayTest (BOOTP, ARP, IL to the recorded 1e
file server, init, rc, `echo hello`), with p9boot's Sonic tapped.  One
line per event, in the order the model made them:

    R off value irq       register read: the value returned; irq after
    W off data mask irq   register write (a command runs inside it)
    X irq hex             a frame offered to the receiver; irq after
    B irq hex             a frame whose last byte carries `bad` (a link CRC
                          error): the model is not called; the RTL must
                          drop it (no DMA, irq unchanged)
    D R addr value        a DMA read the SONIC made (one 32-bit word)
    D W addr value be     a DMA write
    T hex                 a frame the SONIC transmitted (no FCS)

D and T lines belong to the R/W/X line before them (a B line has
none).  Only sonic_directed.py writes B lines.  DMA is recorded at
word granularity, as the RTL makes it: the model's `_get`/`_put` are one
word each, its `_bytes(pa, n)` is the words covering [pa, pa+n) in
address order (the values the model's memory held), and its
`_write_bytes` is whole words (the receive buffer pointer and the padded
length are multiples of 4; capture checks it).  Those are the only DMA
paths in p9boot.Sonic.

check replays the events into a fresh p9boot.Sonic whose board serves the
DMA reads from the trace and compares every register read, irq level,
DMA write and transmitted frame with it: the trace is what the model does.
vectors writes the same events for $readmemh.
"""
import gzip
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOBBIT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HOBBIT, "tools"))
sys.path.insert(0, os.path.join(HOBBIT, "sem"))

S9TERM = os.path.join(HOBBIT, "tools", "plan9-1e", "hobbit", "s9term")
JOIN_PCAP = os.path.join(HOBBIT, "tests", "net", "join_echo.pcap")


def tap(sonic, board, log):
    """Record sonic's register accesses, frames and DMA into log."""
    g_get, g_put, g_bytes, g_wbytes = (sonic._get, sonic._put, sonic._bytes,
                                       sonic._write_bytes)
    g_read, g_write, g_receive = sonic.read, sonic.write, sonic.receive

    def _get(base, index):
        a = (base + 4 * index) & 0xFFFFFFFF
        assert a & 3 == 0, "unaligned descriptor word 0x%08x" % a
        log.append("D R %08x %08x" % (a, board.read(a)))
        return g_get(base, index)

    def _put(base, index, value):
        a = (base + 4 * index) & 0xFFFFFFFF
        assert a & 3 == 0, "unaligned descriptor word 0x%08x" % a
        log.append("D W %08x %08x f" % (a, value & 0xFFFF))
        return g_put(base, index, value)

    def _bytes(pa, n):
        if n:
            for w in range(pa & ~3, ((pa + n - 1) & ~3) + 4, 4):
                log.append("D R %08x %08x" % (w, board.read(w)))
        return g_bytes(pa, n)

    def _write_bytes(pa, data):
        assert pa & 3 == 0 and len(data) & 3 == 0, (pa, len(data))
        for i in range(0, len(data), 4):
            log.append("D W %08x %08x f" % (
                pa + i, int.from_bytes(data[i:i + 4], "little")))
        return g_wbytes(pa, data)

    def read(off):
        v = g_read(off)
        log.append("R %03x %04x %d" % (off, v, sonic.irq()))
        return v

    def write(off, data, mask):
        i = len(log)
        g_write(off, data, mask)
        log.insert(i, "W %03x %08x %x %d" % (off, data, mask, 0))
        log[i] = "W %03x %08x %x %d" % (off, data, mask, sonic.irq())

    def receive(frame):
        i = len(log)
        g_receive(frame)
        log.insert(i, "X %d %s" % (sonic.irq(), frame.hex()))

    sonic._get, sonic._put = _get, _put
    sonic._bytes, sonic._write_bytes = _bytes, _write_bytes
    sonic.read, sonic.write, sonic.receive = read, write, receive


def capture(path):
    import p9boot
    boot = p9boot.Boot(S9TERM)
    boot.script = [(b"il]: ", b"\r"), (b"user[none]: ", b"\r"),
                   (b"% ", b"echo hello\r")]
    replay = p9boot.Replay(JOIN_PCAP, p9boot.EEPROM_EA)
    boot.attach(p9boot.Wire(boot.sonic.clock, replay=replay))
    log = []
    tap(boot.sonic, boot.board, log)
    w = boot.sonic.wire
    g_tx = w.transmit

    def transmit(frame, t):
        log.append("T %s" % frame.hex())
        return g_tx(frame, t)
    w.transmit = transmit
    boot.until = b"% echo hello\nhello\n% "
    status = boot.run(800000000)
    if "echo hello" not in status or replay.mismatch is not None:
        raise SystemExit("sonic_trace: the run did not reach echo hello "
                         "as recorded: %s, mismatch %r"
                         % (status, replay.mismatch))
    with gzip.open(path, "wt") as f:
        f.write("# p9boot.Sonic events from the JoinReplayTest run of "
                "s9term to `echo hello` (%d steps); sonic_trace.py\n"
                % boot.steps)
        for line in log:
            f.write(line + "\n")
    print("sonic_trace: %d events, %d steps" % (len(log), boot.steps))


def read_trace(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [ln.split() for ln in f if ln.strip() and ln[0] != "#"]


def groups(ev):
    """[(head, [D/T lines])]"""
    out = []
    for e in ev:
        if e[0] in ("R", "W", "X", "B"):
            out.append((e, []))
        else:
            out[-1][1].append(e)
    return out


class TraceBoard:
    """A board for a fresh model: DMA reads come from the trace, DMA
    writes are compared with it (word by word, as captured)."""

    def __init__(self, err):
        self.q = []
        self.err = err
        self.cur = None             # (word address, value) for byte reads
        self.pend = {}              # word address -> (value, mask)

    def _next(self, kind, addr):
        if not self.q:
            self.err("model made a DMA %s at 0x%08x the trace does not have"
                     % (kind, addr))
            return None
        d = self.q.pop(0)
        if d[1] != kind or int(d[2], 16) != addr:
            self.err("DMA: model %s 0x%08x, trace %s" % (kind, addr,
                                                          " ".join(d)))
        return d

    def read(self, pa):
        d = self._next("R", pa & ~3)
        return int(d[3], 16) if d else 0

    def byte(self, pa):
        w = pa & ~3
        if self.cur is None or self.cur[0] != w:
            self.cur = (w, self.read(w))
        return (self.cur[1] >> (8 * (pa & 3))) & 0xFF

    def write(self, pa, data, mask):
        w = pa & ~3
        v, m = self.pend.get(w, (0, 0))
        for b in range(4):
            if mask & (1 << b):
                v = (v & ~(0xFF << 8 * b)) | (data & (0xFF << 8 * b))
        m |= mask
        if m != 0xF:
            self.pend[w] = (v, m)
            return
        self.pend.pop(w, None)
        d = self._next("W", w)
        if d and int(d[3], 16) != v:
            self.err("DMA write 0x%08x: model %08x, trace %s"
                     % (w, v, d[3]))


def check(path):
    import p9boot
    ev = read_trace(path)
    errs = []
    t = [0]

    def err(msg):
        if len(errs) < 20:
            print("MISMATCH event %d: %s" % (t[0], msg))
        errs.append(msg)

    board = TraceBoard(err)
    s = p9boot.Sonic(board, lambda: 0)
    sent = []

    class W:
        def transmit(self, frame, now):
            sent.append(frame)
    s.wire = W()
    n = {"R": 0, "W": 0, "X": 0, "B": 0, "D": 0, "T": 0}
    for t[0], (head, rest) in enumerate(groups(ev)):
        board.q = [d for d in rest if d[0] == "D"]
        board.cur = None
        txs = [bytes.fromhex(d[1]) for d in rest if d[0] == "T"]
        del sent[:]
        n[head[0]] += 1
        n["D"] += len(board.q)
        n["T"] += len(txs)
        if head[0] == "R":
            v = s.read(int(head[1], 16))
            if v != int(head[2], 16):
                err("read %s: model %04x, trace %s" % (head[1], v, head[2]))
            irq = head[3]
        elif head[0] == "W":
            s.write(int(head[1], 16), int(head[2], 16), int(head[3], 16))
            irq = head[4]
        elif head[0] == "X":
            s.receive(bytes.fromhex(head[2]))
            irq = head[1]
        else:
            irq = head[1]                   # dropped by the link: no call
        if int(s.irq()) != int(irq):
            err("irq: model %d, trace %s" % (s.irq(), irq))
        if board.q:
            err("trace has %d more DMA records" % len(board.q))
        if sent != txs:
            err("transmitted frames differ")
    bad = ", %d bad" % n["B"] if n["B"] else ""
    print("sonic_trace: %d register reads, %d writes, %d frames offered%s, "
          "%d DMA words, %d frames sent; %d mismatches"
          % (n["R"], n["W"], n["X"], bad, n["D"], n["T"], len(errs)))
    return not errs


def vectors(path, out):
    """events.hex: 96-bit records, one per R/W/X event, then a 0 record:
         [95:92] op (1 read, 2 write, 3 frame, 4 bad frame, 0 end)
         [91] irq after
         [90:79] offset  [78:47] data (write) or value (read)
         [46:43] mask  [42:32] frame length  [31:0] DMA records after it
       plus the running number of transmitted frames in dma? no: tx count
       is in txidx.hex (one word per event).
       dma.hex: 66-bit records {write, addr, data} with be f implied;
       rx.hex / tx.hex: frame bytes back to back; txlen.hex: tx lengths."""
    ev = groups(read_trace(path))
    os.makedirs(out, exist_ok=True)
    fe = open(os.path.join(out, "events.hex"), "w")
    fx = open(os.path.join(out, "txidx.hex"), "w")
    fd = open(os.path.join(out, "dma.hex"), "w")
    fr = open(os.path.join(out, "rx.hex"), "w")
    ft = open(os.path.join(out, "tx.hex"), "w")
    fl = open(os.path.join(out, "txlen.hex"), "w")
    nd = ntx = 0
    for head, rest in ev:
        op = {"R": 1, "W": 2, "X": 3, "B": 4}[head[0]]
        off = data = mask = flen = 0
        if op == 1:
            off, data, irq = int(head[1], 16), int(head[2], 16), int(head[3])
        elif op == 2:
            off, data, mask = (int(head[1], 16), int(head[2], 16),
                               int(head[3], 16))
            irq = int(head[4])
        else:
            irq = int(head[1])
            frame = bytes.fromhex(head[2])
            flen = len(frame)
            for b in frame:
                fr.write("%02x\n" % b)
        for d in rest:
            if d[0] == "D":
                assert d[1] == "R" or d[4] == "f"
                fd.write("%017x\n" % ((int(d[1] == "W") << 64)
                                      | (int(d[2], 16) << 32)
                                      | int(d[3], 16)))
                nd += 1
            else:
                frame = bytes.fromhex(d[1])
                fl.write("%03x\n" % len(frame))
                for b in frame:
                    ft.write("%02x\n" % b)
                ntx += 1
        rec = ((op << 92) | (irq << 91) | (off << 79) | (data << 47)
               | (mask << 43) | (flen << 32) | nd)
        fe.write("%024x\n" % rec)
        fx.write("%08x\n" % ntx)
    fe.write("%024x\n" % 0)
    fx.write("%08x\n" % ntx)
    for f in (fe, fx, fd, fr, ft, fl):
        f.close()
    print("sonic_trace: %d events, %d DMA words, %d frames sent"
          % (len(ev), nd, ntx))


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "capture":
        capture(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "check":
        sys.exit(0 if check(sys.argv[2]) else 1)
    elif len(sys.argv) >= 4 and sys.argv[1] == "vectors":
        vectors(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
