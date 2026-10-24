"""MCP INITIALIZATION, printed p.64 -- THE REQUEST VALIDITY CHECK
TABLE AND THE MULTI-UNIT COUNT TABLE.

Forty-six lines; twenty-nine compile.
decks/mcp_bootstrap_p64.strap carries the derivations.

>>> THIS PAGE ENDS EXACTLY AT T ASIGN. <<<  Line 39's
"T CHCUC DRZ(BU,32),(32)" at 003661.00 is thirty-two 32-bit items --
SIXTEEN words, printed 000020.00 -- so it ends at 003701.00, which
is printed p.65 line 6 and the symbol the boot run branches to.

>>> "(8)" IS AN OCTAL ENTRY MODE AND ONE ROW PROVES IT. <<<  Lines
6, 9, 12, 15, 18, 21, 24 and 27 are each "(8)DD(BU,8),n,m,0" -- ONE
statement compiling THREE eight-bit bytes, printed on three rows at
three consecutive addresses.  Seven of the eight cannot tell the
radix, because their type codes are 1 through 7.  LINE 27 CAN: it is
"(8)DD(BU,8),10,0,0" commented "-SAME AS ABOVE - TAPE" and prints
010.  Tape's equipment code is EIGHT; ten OCTAL is eight, ten
DECIMAL would print 012.

THE ASSEMBLER GAINED TWO THINGS FOR THIS PAGE, both in strap_asm.py:
a numeric entry mode now takes the ORDINARY field parse instead of
the converted-datum one (it is a radix, not a character set), and
the DD emitter applies that radix to each field.  C22-6531 defines
"(R)" as an entry mode and eval_expr has always honoured it on a
VALUE; this is the same mode written on the OPERATION.

AN XW's VALUE FIELD IS SIGNED, AND LINE 38 IS THE FIRST MINUS.
"T RCHSC XW,-T CHCUC-32.0,0,0" prints 003721.00- where every XW
transcribed before it printed "+".  T CHCUC is 003661.0 and
thirty-two words on is 0o3721.

ALL TWENTY-NINE ROWS PASSED ONCE THE ASSEMBLER LEARNED THE RADIX.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  Line 27 loses its "(8)" -- 1 FAIL, reading 012 for 010.  THAT IS
  THE WHOLE PROOF OF THE RADIX, in one row: ten decimal prints 012,
  ten octal prints 010, and the listing says 010 for an equipment
  code the comment calls TAPE.
  Line 38's "-T CHCUC-32.0" loses its sign -- 1 FAIL, reading
  003621.00+ for 003721.00-.  Both the magnitude and the printed
  sign character change, because 003661-32 and -(003661+32) are
  different words.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p64.strap").read())

SYMBOLS = {
    "TDISK":  "003652.00",   # printed p.63 line 20's XW predicted it
    "TMUCTX": "003655.00",
    "TYSCAN": "003656.00",
    "TFCHSC": "003657.00",
    "TRCHSC": "003660.00",
    "TCHCUC": "003661.00",
    "TCHADD": "000000.00",   # 0.0
    "TCHCNT": "000000.24",   # 0.20, and 0o24 is 20
}

ROWS = [
    ("003651.40", "000000.30 00",
     "line 5   CNOP"),
    ("003652.00", "001",
     "line 6   T DISK   (8)DD", 8),
    ("003652.10", "001",
     "line 7", 8),
    ("003652.20", "000",
     "line 8", 8),
    ("003652.30", "002",
     "line 9   CONSOLE", 8),
    ("003652.40", "000",
     "line 10", 8),
    ("003652.50", "000",
     "line 11", 8),
    ("003652.60", "003",
     "line 12  CARD READER", 8),
    ("003652.70", "000",
     "line 13", 8),
    ("003653.00", "000",
     "line 14", 8),
    ("003653.10", "004",
     "line 15  PUNCH", 8),
    ("003653.20", "000",
     "line 16", 8),
    ("003653.30", "000",
     "line 17", 8),
    ("003653.40", "005",
     "line 18  PRINTER", 8),
    ("003653.50", "000",
     "line 19", 8),
    ("003653.60", "000",
     "line 20", 8),
    ("003653.70", "006",
     "line 21  IQS", 8),
    ("003654.00", "000",
     "line 22", 8),
    ("003654.10", "000",
     "line 23", 8),
    ("003654.20", "007",
     "line 24  EXTRA", 8),
    ("003654.30", "000",
     "line 25", 8),
    ("003654.40", "000",
     "line 26", 8),
    ("003654.50", "010",
     "line 27  TAPE = 8", 8),
    ("003654.60", "000",
     "line 28", 8),
    ("003654.70", "000",
     "line 29", 8),
    ("003655.00", "003661.00+ 000 000000 000000",
     "line 35  T MUCTX XW"),
    ("003656.00", "003657.00+ 000 000002 000000",
     "line 36  T YSCAN XW"),
    ("003657.00", "003661.00+ 000 000000 000000",
     "line 37  T FCHSC XW"),
    ("003660.00", "003721.00- 000 000000 000000",
     "line 38  T RCHSC XW"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.64 ")
finish(fails)
