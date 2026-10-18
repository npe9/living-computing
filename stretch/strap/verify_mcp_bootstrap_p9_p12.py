#!/usr/bin/env python3
"""verify_mcp_bootstrap_p9_p12.py -- MCP's IPL bootstrap, printed
pages 9 through 12 (programs/mcp_bootstrap_p9_p12.strap), the AREA
CONTAINING ERROR MESSAGES.  docs/MCP_Mar63_001-249.pdf PDF pp.16-19,
headers "PAGE NUMBER 9" through "PAGE NUMBER 12".  AGENTS.md rule 3.

>>> READ THIS BEFORE TRUSTING A PASS FROM THIS FILE <<<

THE LISTING PRINTS NOTHING IN THE BINARY OUTPUT COLUMN FOR AN
(IQS*)DD ROW.  Every message line on these four pages has an empty
BINARY OUTPUT.  So nothing here checks a character code, and nothing
ever can from this listing: strap/charsets.py's IQS table rests on
Reference Manual printed p.166 alone.

WHAT A PASS DOES MEAN, and it is not nothing.  Two things:

  1. THE COUNTING, checked thirty-one times.  A converted DD advances
     the location counter eight bits per character with the
     end-of-statement character not compiled, so the next printed
     location states exactly how many characters the message has.
     Every text in the program file was read off the page and its
     length compared with the listing's own address delta.  That is
     what fixes the trailing blanks -- " EKJ ON CCW OF IPL CW" has
     none and " CBJ DETECTED IN IO TEST ROUTINE " has one, and no
     amount of staring at a drum printer settles that; the page's own
     arithmetic does.

  2. THE THIRTY-SIX LABELS, each at the location the page prints for
     it.  Five messages carry more than one name -- X MSG 15, X MSG
     16, X MS 16A and X MS 16B are four names for one text -- and
     X MSG 25 is deliberately NOT word-aligned, at 000513.30, because
     printed p.12 puts its SYN before the CNOP rather than after.

The rows below are the three DD(BU,8) control codes around each
message, which DO print (375, 002, 376), and the NOP half word a CNOP
lays down when it has to realign.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("programs/mcp_bootstrap_p9_p12.strap").read())

SYMBOLS = {
    "XMSG00": "000254.00",
    "XMSG01": "000260.00",
    "XMSG02": "000266.00",
    "XMSG03": "000274.00",
    "XMSG04": "000302.00",
    "XMSG05": "000310.00",
    "XMS05A": "000315.00",
    "XMS05B": "000322.00",
    "XMS05C": "000327.00",
    "XMS05D": "000334.00",
    "XMS05E": "000342.00",
    "XMSG06": "000347.00",
    "XMSG07": "000354.00",
    "XMSG08": "000361.00",
    "XMSG09": "000366.00",
    "XMSG10": "000374.00",
    "XMSG11": "000403.00",
    "XMSG12": "000410.00",
    "XMSG13": "000415.00",
    "XMSG14": "000424.00",
    "XMSG15": "000432.00",
    "XMSG16": "000432.00",
    "XMS16A": "000432.00",
    "XMS16B": "000432.00",
    "XMS16C": "000440.00",
    "XMSG17": "000444.00",
    "XMSG18": "000451.00",
    "XMSG19": "000460.00",
    "XMSG20": "000464.00",
    "XMS21A": "000464.00",
    "XMSG22": "000473.00",
    "XMSG21": "000501.00",
    "XMSG23": "000501.00",
    "XMSG24": "000506.00",
    "XMSG25": "000513.30",
    "XMSG26": "000521.00",}

ROWS = [
    ("000254.00", "375", "X MSG 00  -CONTROL CODE * CARRIAGE RETURN"),
    ("000254.10", "002", "X MSG 00  -RED$"),
    ("000257.70", "376", "X MSG 00  -CONTROL CODE * END OF MESSAGE"),
    ("000260.00", "375", "X MSG 01  -CONTROL CODE * CARRIAGE RETURN"),
    ("000260.10", "002", "X MSG 01  -RED$"),
    ("000265.30", "376", "X MSG 01  -CONTROL CODE * END OF MESSAGE"),
    ("000265.40", "000000.30 00", "X MSG 01  CNOP -- the NOP half word it fills with"),
    ("000266.00", "375", "X MSG 02  -CONTROL CODE * CARRIAGE RETURN"),
    ("000266.10", "002", "X MSG 02  -RED$"),
    ("000273.30", "376", "X MSG 02  -CONTROL CODE * END OF MESSAGE"),
    ("000273.40", "000000.30 00", "X MSG 02  CNOP -- the NOP half word it fills with"),
    ("000274.00", "375", "X MSG 03  -CONTROL CODE * CARRIAGE RETURN"),
    ("000274.10", "002", "X MSG 03  -RED$"),
    ("000301.30", "376", "X MSG 03  -CONTROL CODE * END OF MESSAGE"),
    ("000301.40", "000000.30 00", "X MSG 03  CNOP -- the NOP half word it fills with"),
    ("000302.00", "375", "X MSG 04  -CONTROL CODE * CARRIAGE RETURN"),
    ("000302.10", "002", "X MSG 04  -RED$"),
    ("000307.10", "376", "X MSG 04  -CONTROL CODE * END OF MESSAGE"),
    ("000307.40", "000000.30 00", "X MSG 04  CNOP -- the NOP half word it fills with"),
    ("000310.00", "375", "X MSG 05  -CONTROL CODE * CARRIAGE RETURN"),
    ("000310.10", "002", "X MSG 05  -RED$"),
    ("000314.30", "376", "X MSG 05  -CONTROL CODE * END OF MESSAGE"),
    ("000314.40", "000000.30 00", "X MSG 05  CNOP -- the NOP half word it fills with"),
    ("000315.00", "375", "X MS 05A  -CONTROL CODE * CARRIAGE RETURN"),
    ("000315.10", "002", "X MS 05A  -RED$"),
    ("000321.20", "376", "X MS 05A  -CONTROL CODE * END OF MESSAGE"),
    ("000321.40", "000000.30 00", "X MS 05A  CNOP -- the NOP half word it fills with"),
    ("000322.00", "375", "X MS 05B  -CONTROL CODE * CARRIAGE RETURN"),
    ("000322.10", "002", "X MS 05B  -RED$"),
    ("000326.30", "376", "X MS 05B  -CONTROL CODE * END OF MESSAGE"),
    ("000326.40", "000000.30 00", "X MS 05B  CNOP -- the NOP half word it fills with"),
    ("000327.00", "375", "X MS 05C  -CONTROL CODE * CARRIAGE RETURN"),
    ("000327.10", "002", "X MS 05C  -RED$"),
    ("000333.20", "376", "X MS 05C  -CONTROL CODE * END OF MESSAGE"),
    ("000333.40", "000000.30 00", "X MS 05C  CNOP -- the NOP half word it fills with"),
    ("000334.00", "375", "X MS 05D  -CONTROL CODE * CARRIAGE RETURN"),
    ("000334.10", "002", "X MS 05D  -RED$"),
    ("000341.30", "376", "X MS 05D  -CONTROL CODE * END OF MESSAGE"),
    ("000341.40", "000000.30 00", "X MS 05D  CNOP -- the NOP half word it fills with"),
    ("000342.00", "375", "X MS 05E  -CONTROL CODE * CARRIAGE RETURN"),
    ("000342.10", "002", "X MS 05E  -RED$"),
    ("000346.70", "376", "X MS 05E  -CONTROL CODE * END OF MESSAGE"),
    ("000347.00", "375", "X MSG 06  -CONTROL CODE * CARRIAGE RETURN"),
    ("000347.10", "002", "X MSG 06  -RED$"),
    ("000353.60", "376", "X MSG 06  -CONTROL CODE * END OF MESSAGE"),
    ("000354.00", "375", "X MSG 07  -CONTROL CODE * CARRIAGE RETURN"),
    ("000354.10", "002", "X MSG 07  -RED$"),
    ("000360.70", "376", "X MSG 07  -CONTROL CODE * END OF MESSAGE"),
    ("000361.00", "375", "X MSG 08  -CONTROL CODE * CARRIAGE RETURN"),
    ("000361.10", "002", "X MSG 08  -RED$"),
    ("000365.60", "376", "X MSG 08  -CONTROL CODE * END OF MESSAGE"),
    ("000366.00", "375", "X MSG 09  -CONTROL CODE * CARRIAGE RETURN"),
    ("000366.10", "002", "X MSG 09  -RED$"),
    ("000373.50", "376", "X MSG 09  -CONTROL CODE * END OF MESSAGE"),
    ("000374.00", "375", "X MSG 10  -CONTROL CODE * CARRIAGE RETURN"),
    ("000374.10", "002", "X MSG 10  -RED$"),
    ("000402.20", "376", "X MSG 10  -CONTROL CODE * END OF MESSAGE"),
    ("000402.40", "000000.30 00", "X MSG 10  CNOP -- the NOP half word it fills with"),
    ("000403.00", "375", "X MSG 11  -CONTROL CODE * CARRIAGE RETURN"),
    ("000403.10", "002", "X MSG 11  -RED$"),
    ("000407.10", "376", "X MSG 11  -CONTROL CODE * END OF MESSAGE"),
    ("000407.40", "000000.30 00", "X MSG 11  CNOP -- the NOP half word it fills with"),
    ("000410.00", "375", "X MSG 12  -CONTROL CODE * CARRIAGE RETURN"),
    ("000410.10", "002", "X MSG 12  -RED$"),
    ("000414.20", "376", "X MSG 12  -CONTROL CODE * END OF MESSAGE"),
    ("000414.40", "000000.30 00", "X MSG 12  CNOP -- the NOP half word it fills with"),
    ("000415.00", "375", "X MSG 13  -CONTROL CODE * CARRIAGE RETURN"),
    ("000415.10", "002", "X MSG 13  -RED$"),
    ("000423.40", "376", "X MSG 13  -CONTROL CODE * END OF MESSAGE"),
    ("000424.00", "375", "X MSG 14  -CONTROL CODE * CARRIAGE RETURN"),
    ("000424.10", "002", "X MSG 14  -RED$"),
    ("000431.00", "376", "X MSG 14  -CONTROL CODE * END OF MESSAGE"),
    ("000431.40", "000000.30 00", "X MSG 14  CNOP -- the NOP half word it fills with"),
    ("000432.00", "375", "X MSG 15  -CONTROL CODE * CARRIAGE RETURN"),
    ("000432.10", "002", "X MSG 15  -RED$"),
    ("000437.00", "376", "X MSG 15  -CONTROL CODE * END OF MESSAGE"),
    ("000437.40", "000000.30 00", "X MSG 15  CNOP -- the NOP half word it fills with"),
    ("000440.00", "375", "X MS 16C  -CONTROL CODE * CARRIAGE RETURN"),
    ("000443.70", "376", "X MS 16C  -CONTROL CODE * END OF MESSAGE"),
    ("000444.00", "375", "X MSG 17  -CONTROL CODE * CARRIAGE RETURN"),
    ("000444.10", "002", "X MSG 17  -RED$"),
    ("000450.00", "376", "X MSG 17  -CONTROL CODE * END OF MESSAGE"),
    ("000450.40", "000000.30 00", "X MSG 17  CNOP -- the NOP half word it fills with"),
    ("000451.00", "375", "X MSG 18  -CONTROL CODE * CARRIAGE RETURN"),
    ("000451.10", "002", "X MSG 18  -RED$"),
    ("000457.00", "376", "X MSG 18  -CONTROL CODE * END OF MESSAGE"),
    ("000457.40", "000000.30 00", "X MSG 18  CNOP -- the NOP half word it fills with"),
    ("000460.00", "375", "X MSG 19  -CONTROL CODE * CARRIAGE RETURN"),
    ("000460.10", "002", "X MSG 19  -RED$"),
    ("000463.70", "376", "X MSG 19  -CONTROL CODE * END OF MESSAGE"),
    ("000464.00", "375", "X MSG 20  -CONTROL CODE * CARRIAGE RETURN"),
    ("000464.10", "002", "X MSG 20  -RED$"),
    ("000472.10", "376", "X MSG 20  -CONTROL CODE * END OF MESSAGE"),
    ("000472.40", "000000.30 00", "X MSG 20  CNOP -- the NOP half word it fills with"),
    ("000473.00", "375", "X MSG 22  -CONTROL CODE * CARRIAGE RETURN"),
    ("000473.10", "002", "X MSG 22  -RED$"),
    ("000500.30", "376", "X MSG 22  -CONTROL CODE * END OF MESSAGE"),
    ("000500.40", "000000.30 00", "X MSG 22  CNOP -- the NOP half word it fills with"),
    ("000501.00", "375", "X MSG 21  -CONTROL CODE * CARRIAGE RETURN"),
    ("000505.30", "376", "X MSG 21  -CONTROL CODE * END OF MESSAGE"),
    ("000505.40", "000000.30 00", "X MSG 21  CNOP -- the NOP half word it fills with"),
    ("000506.00", "375", "X MSG 24  -CONTROL CODE * CARRIAGE RETURN"),
    ("000506.10", "002", "X MSG 24  -RED$"),
    ("000513.20", "376", "X MSG 24  -CONTROL CODE * END OF MESSAGE"),
    ("000514.00", "375", "X MSG 25  -CONTROL CODE * CARRIAGE RETURN"),
    ("000514.10", "002", "X MSG 25  -RED$"),
    ("000520.70", "376", "X MSG 25  -CONTROL CODE * END OF MESSAGE"),
    ("000521.00", "375", "X MSG 26  -CONTROL CODE * CARRIAGE RETURN"),
    ("000521.10", "002", "X MSG 26  -RED$"),
    ("000525.50", "376", "X MSG 26  -CONTROL CODE * END OF MESSAGE"),]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP pp.9-12 "))
