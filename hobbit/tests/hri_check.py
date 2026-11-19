#!/usr/bin/env python3
"""Compare an HRI retirement trace against a reference trace.

HRI is the Hobbit Retirement Interface: one record per retired instruction,
modelled on riscv-formal's RVFI (the RISC-V Formal Interface) but with the
fields a memory-to-memory stack machine needs. The check here is a
line-by-line comparison of a Bluesim run against the independent
one-instruction model; it is not a formal proof.

The only accepted line format is the project-wide fixed format:

    HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d

A line that does not match that format exactly is a malformed line and is
reported with its 1-based line number; it is never skipped.

Exit status:
    0  every field of every compared line matched
    1  malformed line, field divergence, length divergence, or command failure
    2  command-line usage error
"""

import argparse
import re
import subprocess
import sys

# Field order in the fixed line format.  The first divergence in this order is
# reported.  "sp" and "msp" each cover the whole before>after pair.
FIELD_ORDER = ("pc", "insn", "sp", "msp", "we", "addr", "data", "mask", "trap")

# Exactly the fixed format.  Hex is lower-case and fixed-width; we/trap are
# decimal.  Anything else is malformed.
_HRI_RE = re.compile(
    r"^HRI "
    r"pc=([0-9a-f]{4}) "
    r"insn=([0-9a-f]{4})([0-9a-f]{4}) "
    r"sp=([0-9a-f]{8})>([0-9a-f]{8}) "
    r"msp=([0-9a-f]{8})>([0-9a-f]{8}) "
    r"we=(\d+) "
    r"addr=([0-9a-f]{8}) "
    r"data=([0-9a-f]{8}) "
    r"mask=([0-9a-f]{2}) "
    r"trap=(\d+)$"
)


def parse_hri_line(line):
    """Return a dict of parsed fields, or None if the line is malformed."""
    m = _HRI_RE.match(line.strip())
    if m is None:
        return None
    (
        pc,
        insn_hi,
        insn_lo,
        sp_before,
        sp_after,
        msp_before,
        msp_after,
        we,
        addr,
        data,
        mask,
        trap,
    ) = m.groups()
    return {
        "pc": int(pc, 16),
        "insn": int(insn_hi + insn_lo, 16),
        "sp": (int(sp_before, 16), int(sp_after, 16)),
        "msp": (int(msp_before, 16), int(msp_after, 16)),
        "we": int(we, 10),
        "addr": int(addr, 16),
        "data": int(data, 16),
        "mask": int(mask, 16),
        "trap": int(trap, 10),
    }


def _format_field(field, value):
    """Render a parsed field value in the report's 0x notation."""
    if field == "pc":
        return "0x%04x" % value
    if field == "insn":
        return "0x%08x" % value
    if field in ("sp", "msp"):
        return "0x%08x>0x%08x" % value
    if field == "we":
        return "0x%x" % value
    if field == "addr":
        return "0x%08x" % value
    if field == "data":
        return "0x%08x" % value
    if field == "mask":
        return "0x%02x" % value
    if field == "trap":
        return "0x%x" % value
    raise ValueError("unknown field %r" % (field,))


def _read_file(path):
    """Read a trace file as a list of lines; no line is discarded."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def _read_command(cmd):
    """Run an opaque command and capture its stdout as a list of lines."""
    proc = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        sys.stderr.write(
            "Error: command failed with exit status %d: %s\n"
            % (proc.returncode, cmd)
        )
        if proc.stderr:
            sys.stderr.write(proc.stderr)
            if not proc.stderr.endswith("\n"):
                sys.stderr.write("\n")
        sys.exit(1)
    return proc.stdout.splitlines()


def _malformed(side, line_number, line):
    sys.stderr.write(
        "Error: malformed HRI line at line %d in %s: %s\n"
        % (line_number, side, line)
    )
    sys.exit(1)


def compare(dut_lines, spec_lines, ignore_fields):
    """Compare traces and report the first divergence.

    Returns (ok, instructions_compared).  Exits 1 on malformed lines.
    """
    ignore = set(f.lower() for f in ignore_fields.split())
    unknown = ignore - set(FIELD_ORDER)
    if unknown:
        sys.stderr.write(
            "Error: unknown --ignore-fields field(s): %s\n"
            % ", ".join(sorted(unknown))
        )
        sys.exit(2)

    common = min(len(dut_lines), len(spec_lines))

    for i in range(common):
        dut = parse_hri_line(dut_lines[i])
        if dut is None:
            _malformed("DUT", i + 1, dut_lines[i])
        spec = parse_hri_line(spec_lines[i])
        if spec is None:
            _malformed("SPEC", i + 1, spec_lines[i])

        for field in FIELD_ORDER:
            if field in ignore:
                continue
            if dut[field] != spec[field]:
                print(
                    "line %d field %s: dut=%s spec=%s pc=0x%04x"
                    % (
                        i + 1,
                        field.upper(),
                        _format_field(field, dut[field]),
                        _format_field(field, spec[field]),
                        dut["pc"],
                    )
                )
                return False, i + 1

    if len(dut_lines) != len(spec_lines):
        line_number = common + 1
        if len(dut_lines) > len(spec_lines):
            extra = parse_hri_line(dut_lines[common])
            if extra is None:
                _malformed("DUT", line_number, dut_lines[common])
            extra_pc = extra["pc"]
        else:
            extra = parse_hri_line(spec_lines[common])
            if extra is None:
                _malformed("SPEC", line_number, spec_lines[common])
            extra_pc = extra["pc"]
        print(
            "line %d field LENGTH: dut=%d spec=%d pc=0x%04x"
            % (line_number, len(dut_lines), len(spec_lines), extra_pc)
        )
        return False, common

    return True, common


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare HRI retirement traces line by line."
    )
    parser.add_argument("--dut", help="opaque command producing the DUT trace")
    parser.add_argument("--spec", help="opaque command producing the spec trace")
    parser.add_argument("--dut-lines", help="file containing the DUT trace")
    parser.add_argument("--spec-lines", help="file containing the spec trace")
    parser.add_argument(
        "--ignore-fields",
        default="",
        help="space-separated field names to ignore (default: empty)",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=None,
        help="compare at most this many lines from each trace",
    )
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines < 0:
        parser.error("--max-lines must be non-negative")

    if args.dut is not None or args.spec is not None:
        if args.dut is None or args.spec is None:
            parser.error("--dut and --spec must be given together")
        if args.dut_lines is not None or args.spec_lines is not None:
            parser.error("use either --dut/--spec or --dut-lines/--spec-lines")
        dut_lines = _read_command(args.dut)
        spec_lines = _read_command(args.spec)
    elif args.dut_lines is not None or args.spec_lines is not None:
        if args.dut_lines is None or args.spec_lines is None:
            parser.error("--dut-lines and --spec-lines must be given together")
        dut_lines = _read_file(args.dut_lines)
        spec_lines = _read_file(args.spec_lines)
    else:
        parser.error(
            "give --dut CMD --spec CMD or --dut-lines FILE --spec-lines FILE"
        )

    if args.max_lines is not None:
        dut_lines = dut_lines[: args.max_lines]
        spec_lines = spec_lines[: args.max_lines]

    ok, compared = compare(dut_lines, spec_lines, args.ignore_fields)
    print(
        "Summary: instructions compared=%d result=%s"
        % (compared, "PASS" if ok else "FAIL")
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
