"""Runtime-state layouts shared by the reference model and the Bluespec
core (docs/pimm_semantics.md "Runtime state").  They are this project's
design: how the PIM/m firmware laid these out is lost with it.

A goal record is G_ARGS + argn cells:
    +G_LINK    {INT, the next record in the ready queue, or 0}
    +G_STATUS  {INT, READY | SUSPENDED | TAKEN}
    +G_CODE    {INT, code address}
    +G_ARGN    {INT, number of arguments}
    +G_ARGS..  the arguments
A suspension record is S_SIZE cells, one per (goal, variable) wait:
    +S_NEXT    {INT, the next suspension record on this variable, or 0}
    +S_GOAL    {INT, the goal record}
An unbound variable with goals waiting is {HOOK, its first suspension
record}; without, {UNDF, 0}.  Addresses in cells are absolute.
"""
G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS = 0, 1, 2, 3, 4
READY, SUSPENDED, TAKEN = 0, 1, 2
S_NEXT, S_GOAL, S_SIZE = 0, 1, 2

ADDR_BITS = 27                  # memory size in cells = 1 << ADDR_BITS
MEMORY_CELLS = 1 << ADDR_BITS
HEAP = 0x8000                   # first heap cell, from the load address
