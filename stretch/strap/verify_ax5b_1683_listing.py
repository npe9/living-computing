#!/usr/bin/env python3
"""verify_ax5b_1683_listing.py -- jb_ax5b "I-Box 5", routine 1268's
TEST 2 (programs/ax5b_1683_df_close_to_ds.strap) against the listing's
printed machine code, PDF p.111, octal 024363.40-024375.40.

WHAT ROUTINE 1268 IS, because docs/NEXT.md had it wrong.  Item 2 called
it "the only known deck test" of the DF and IF ADDRESS-MONITORING
indicators.  It is not.  The routine's own header on PDF p.110 reads
"1268 -- IF AND DF CLOSE TO DS", and its error messages are decisive:
"EXECUTED OLD INSTRUCTION FROM EXT." for test 1 and "LOADED OLD DATA
FROM EXT MEM." for test 2.  Routine 1260's indicator blocks say
"UNABLE TO TURN AD ON." when an INDICATOR fails; these say the wrong
VALUE arrived.  DF and IF here are the Data Fetch and Instruction
Fetch PATHS, "close to DS" means close to a Data Store, and 1268 is a
look-ahead store-to-fetch / store-to-load forwarding test.  Nothing in
it writes a mask, sets a boundary register, branches on DF or IF, or
touches protected storage.

docs/archival_inventory.md carried BOTH readings, twenty lines apart.
The one calling 1268 "Look-Ahead store-to-fetch/store-to-load
forwarding" was right.  So the DF and IF indicators have NO deck
oracle in this document.

PROVEN DISCRIMINATING.  Observed failure sets:

  DIR_INDEX_CODES["Z"]... Z is MISC_CODES, code 0b100 -> 0b101 (RCZ)
      024363.40, 024364.40, 024367.00, 024370.00, 024372.40,
      024373.40 -- all six Store Zero rows          (6 rows)
  enc_branch_or_misc's misc literal 100000 -> 000000
      the same six rows, differently                (6 rows)
  INDICATOR_BITS["XVZ"] 50 -> 51
      024366.40, 024372.00, 024375.40 -- the three BXVZ rows (3 rows)

WHAT THIS FILE CANNOT SEE, measured rather than assumed: it is an
ENCODING oracle only.  The companion RUN of the same program passes,
but does NOT witness store-to-load forwarding on this model --
removing StretchStorage.bsv's "&& !storeQ.notEmpty" store-queue drain
leaves both this block and store_close_to_fetch.strap green while
ebox_register_close_to_fetch.strap fails.  The deck spaces its store
and load one instruction apart, which was tight enough for the real
machine's look-ahead and is not tight enough for this model's
shallower pipeline.  See the program's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_1683_df_close_to_ds.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the listing's own print for it.
ROWS = [
    ('024363.40', '24411.22 00', 'I683 Z,I68K3        (ext) "-TEST 2A,DF CLOSE TO DS IN EXT MEM."'),
    ('024364.00', '24503.02 10', 'LX,$X1,I00O          (ext) the index word of ones'),
    ('024364.40', '22.22 00',    'Z,$X2                 word 18'),
    ('024365.00', '24411.03 10', 'SX,$X1,I68K3         (ext) store...'),
    ('024365.40', '24411.04 10', 'LX,$X2,I68K3         (ext) ...and load straight back'),
    ('024366.00', '1310.00 80',  'SIC,SEN               (ext)'),
    ('024366.40', '1304.31 42',  'BXVZ,SERS             (ext) "LOADED OLD DATA FROM EXT MEM."'),
    ('024367.00', '24.22 00',    'Z,$X4                 word 20, index storage'),
    ('024367.40', '24503.02 10', 'LX,$X1,I00O          (ext)'),
    ('024370.00', '22.22 00',    'Z,$X2'),
    ('024370.40', '24.03 10',    'SX,$X1,$X4'),
    ('024371.00', '24.04 10',    'LX,$X2,$X4'),
    ('024371.40', '1310.00 80',  'SIC,SEN               (ext)'),
    ('024372.00', '1304.31 42',  'BXVZ,SERS             (ext) "LOADED OLD DATA FROM IX STG."'),
    ('024372.40', '11.22 00',    'Z,$R                  word 9, internal memory'),
    ('024373.00', '24503.02 10', 'LX,$X1,I00O          (ext)'),
    ('024373.40', '22.22 00',    'Z,$X2                 vestigial -- see the header'),
    ('024374.00', '11.03 10',    'SX,$X1,$R'),
    ('024374.40', '11.02 10',    'LX,$X1,$R             $X1 as printed, not $X2'),
    ('024375.00', '1310.00 80',  'SIC,SEN               (ext)'),
    ('024375.40', '1304.31 42',  'BXVZ,SERS             (ext) "LOADED OLD DATA FROM INT MEM."'),
]

SYMBOLS = {'I683': '024363.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1268 T2 '))
