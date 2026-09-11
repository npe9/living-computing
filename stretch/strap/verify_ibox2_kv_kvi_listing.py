#!/usr/bin/env python3
"""verify_ibox2_kv_kvi_listing.py -- the IBOX-2 tape's LX DATA / KV AND
KVI CHECK (programs/ibox2_kv_kvi.strap) against jb_ax2a p.13 (code)
and p.200 (index words).

Nothing in the suite uses KV, KVI, BXL, BXH or BXE: index comparison
and its three result indicators (XL, XE, XH) are untouched by anything
transcribed before this.

It was chosen over the refill-field sweep, and the choice was
measured: dropping the refill field's bottom bit already fails
twenty-nine sections of the existing suite, and p.13 has no refill
sweep anyway -- it leaves the sweeps behind and opens this.

$X0 is loaded with BIT0 (value 400000.00) and compared four ways --
KV and KVI against an equal operand, then KV and KVI against BIT1
(200000.00) where the index is higher.  Each check names the
indicator that must be OFF as well as the one that must be on.  The
LOW outcome is not reached by this block.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox2_kv_kvi.strap").read())

CODE_ROWS = [
    ('017326.00', '400000.00 00 000000.00 00', 'BIT0 XW, (8)400000.00, 0, 0'),
    ('017327.00', '200000.00 00 000000.00 00', 'BIT1 XW, (8)200000.00, 0, 0'),
    # -- the subroutine it calls
    ('006523.00', '17306.00 10', 'I007 LX, $X0, I00Z'),
    ('006523.40', '6524.70 42', 'BXCZ, I008'),
    ('006524.00', '6525.10 00', 'B, I009'),
    ('006524.40', '6526.31 42', 'I008 BXVZ, I0010'),
    ('006525.00', '1310.00 80', 'I009 SIC, SEN'),
    ('006525.40', '1304.10 00', 'B, SERS'),
    ('006526.00', '0.10 00', 'I0010 B, 0.0'),
    # -- I020: KV, equal
    ('006713.00', '6526.00 80', 'I020 SIC, I0010   test bit 0'),
    ('006713.40', '6523.10 00', 'B, I007'),
    ('006714.00', '17326.00 10', 'LX, $X0, BIT0'),
    ('006714.40', '17326.00 90', 'KV, $X0, BIT0   equal condition, KV'),
    ('006715.00', '1310.00 80', 'SIC, SEN'),
    ('006715.40', '1304.32 42', 'BXL, SERS'),
    ('006716.00', '1310.00 80', 'SIC, SEN'),
    ('006716.40', '1304.33 42', 'BXH, SERS'),
    ('006717.00', '6720.72 C2', 'BXE, I021'),
    ('006717.40', '1310.00 80', 'SIC, SEN'),
    ('006720.00', '1304.10 00', 'B, SERS'),
    # -- I021: KVI, equal
    ('006720.40', '400000.01 04', 'I021 KVI, $X0, (8)400000.0   equal condition, KVI'),
    ('006721.00', '1310.00 80', 'SIC, SEN'),
    ('006721.40', '1304.32 42', 'BXL, SERS'),
    ('006722.00', '1310.00 80', 'SIC, SEN'),
    ('006722.40', '1304.33 42', 'BXH, SERS'),
    ('006723.00', '6724.72 C2', 'BXE, I022'),
    ('006723.40', '1310.00 80', 'SIC, SEN'),
    ('006724.00', '1304.10 00', 'B, SERS'),
    # -- I022: KV then KVI, index high
    ('006724.40', '17327.00 90', 'I022 KV, $X0, BIT1   index hi condition, KV'),
    ('006725.00', '1310.00 80', 'SIC, SEN'),
    ('006725.40', '1304.32 42', 'BXL, SERS'),
    ('006726.00', '1310.00 80', 'SIC, SEN'),
    ('006726.40', '1304.32 C2', 'BXE, SERS'),
    ('006727.00', '6734.73 42', 'BXH, I023'),
    ('006727.40', '1310.00 80', 'SIC, SEN'),
    ('006730.00', '1304.10 00', 'B, SERS'),
    ('006730.40', '200000.01 04', 'KVI, $X0, (8)200000.0   index hi condition, KVI'),
    ('006731.00', '1310.00 80', 'SIC, SEN'),
    ('006731.40', '1304.32 42', 'BXL, SERS'),
    ('006732.00', '1310.00 80', 'SIC, SEN'),
    ('006732.40', '1304.32 C2', 'BXE, SERS'),
    ('006733.00', '6734.73 42', 'BXH, I023'),
    ('006733.40', '1310.00 80', 'SIC, SEN'),
    ('006734.00', '1304.10 00', 'B, SERS'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
