#!/usr/bin/env python3
"""Lockstep: the IPL file decoder on a whole real file of three modules.

    python3 ref/pimm/lockstep_file3.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_file3.py compare

lockstep_file.py's test (read its header: what is run, checked, stood
in for and left waiting) on pimm_patch_shutl360E.sav, 7139 words, 3
modules, so load_modules/8 recurses and the modules come out in file
order.  A test of its own because the two files do not fit one heap:
this one alone takes 1035497 of the 1048576 cells.
"""
import sys

import lockstep_file

lockstep_file.PINNED = dict(parts=1, lines=637025, cells=1365)
lockstep_file.FILES = ('pimm_patch_shutl360E.sav',)
lockstep_file.NAME = 'file3'

if __name__ == '__main__':
    sys.exit(lockstep_file.main(sys.argv))
