#!/usr/bin/env python3
"""verify_ibox2_kv_kvi_listing.py -- the IBOX-2 tape's LX DATA / KV AND
KVI CHECK (../decks/ibox2_kv_kvi.strap) against jb_ax2a p.13 (code)
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

prog = assemble(open("../decks/ibox2_kv_kvi.strap").read())

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
    ('006734.40', '6735.50 00', 'I023 B, $+1.0'),
    # -- p.14: the same three outcomes one bit down, LOW included
    ('006740.40', '6526.00 80', 'I024 SIC, I0010   test bit 1'),
    ('006741.00', '6523.10 00', 'B, I007'),
    ('006741.40', '17327.00 10', 'LX, $X0, BIT1'),
    ('006742.00', '17327.00 90', 'KV, $X0, BIT1   equal condition, KV'),
    ('006742.40', '1310.00 80', 'SIC, SEN'),
    ('006743.00', '1304.32 42', 'BXL, SERS'),
    ('006743.40', '1310.00 80', 'SIC, SEN'),
    ('006744.00', '1304.33 42', 'BXH, SERS'),
    ('006744.40', '6746.32 C2', 'BXE, I025'),
    ('006745.00', '1310.00 80', 'SIC, SEN'),
    ('006745.40', '1304.10 00', 'B, SERS'),
    ('006746.00', '200000.01 04', 'I025 KVI, $X0, (8)200000.0   equal condition, KVI'),
    ('006746.40', '1310.00 80', 'SIC, SEN'),
    ('006747.00', '1304.32 42', 'BXL, SERS'),
    ('006747.40', '1310.00 80', 'SIC, SEN'),
    ('006750.00', '1304.33 42', 'BXH, SERS'),
    ('006750.40', '6752.32 C2', 'BXE, I026'),
    ('006751.00', '1310.00 80', 'SIC, SEN'),
    ('006751.40', '1304.10 00', 'B, SERS'),
    ('006752.00', '17330.00 90', 'I026 KV, $X0, BIT2   index hi condition, KV'),
    ('006752.40', '1310.00 80', 'SIC, SEN'),
    ('006753.00', '1304.32 42', 'BXL, SERS'),
    ('006753.40', '1310.00 80', 'SIC, SEN'),
    ('006754.00', '1304.32 C2', 'BXE, SERS'),
    ('006754.40', '6756.33 42', 'BXH, I027'),
    ('006755.00', '1310.00 80', 'SIC, SEN'),
    ('006755.40', '1304.10 00', 'B, SERS'),
    ('006756.00', '100000.01 04', 'I027 KVI, $X0, (8)100000.0   index hi condition, KVI'),
    ('006756.40', '1310.00 80', 'SIC, SEN'),
    ('006757.00', '1304.32 42', 'BXL, SERS'),
    ('006757.40', '1310.00 80', 'SIC, SEN'),
    ('006760.00', '1304.32 C2', 'BXE, SERS'),
    ('006760.40', '6762.33 42', 'BXH, I028'),
    ('006761.00', '1310.00 80', 'SIC, SEN'),
    ('006761.40', '1304.10 00', 'B, SERS'),
    ('006762.00', '17326.00 90', 'I028 KV, $X0, BIT0   index LOW condition, KV'),
    ('006762.40', '1310.00 80', 'SIC, SEN'),
    ('006763.00', '1304.33 42', 'BXH, SERS'),
    ('006763.40', '1310.00 80', 'SIC, SEN'),
    ('006764.00', '1304.32 C2', 'BXE, SERS'),
    ('006764.40', '6766.32 42', 'BXL, I029'),
    ('006765.00', '1310.00 80', 'SIC, SEN'),
    ('006765.40', '1304.10 00', 'B, SERS'),
    ('006766.00', '400000.01 04', 'I029 KVI, $X0, (8)400000.0   index LOW condition, KVI'),
    ('006766.40', '1310.00 80', 'SIC, SEN'),
    ('006767.00', '1304.33 42', 'BXH, SERS'),
    ('006767.40', '1310.00 80', 'SIC, SEN'),
    ('006770.00', '1304.32 C2', 'BXE, SERS'),
    ('006770.40', '6772.32 42', 'BXL, I0210'),
    ('006771.00', '1310.00 80', 'SIC, SEN'),
    ('006771.40', '1304.10 00', 'B, SERS'),
    ('017330.00', '100000.00 00 000000.00 00', 'BIT2 XW, (8)100000.00, 0, 0'),
]

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
