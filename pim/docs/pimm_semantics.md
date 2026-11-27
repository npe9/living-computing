# PIM/m KL1-B instruction semantics, from paired source and object

What each instruction does, settled one at a time from object code in
the PIMOS binaries whose KL1 source we have. This is the table both
the host reference model (`ref/pimm/pimm.py`) and the Bluespec model
are to follow. An instruction is listed only when a runnable check
depends on the reading; "inferred" marks what the check does not
exercise.

**Operand directions from source.** PIMOS's compiler
(`library/compiler/blt.kl1`) has a clause per built-in naming the
instruction it emits and which operands are read and written.
`asm/bltdir.py` reads all 87 guard and 120 body built-ins out of it;
every operand is marked. It agrees with each reading below that a run
has checked (`b_add`, `b_subtract`, `new_string`, `b_string_element`,
`set_string_element`, `string`, and `not_less_than a,b` = `a >= b`,
which the compiler emits for `X1 >= X2` and, operands swapped, for
`X1 =< X2`). The source is the 1992 release and the binaries are from
1994, so a run still outranks the table where the two could differ.

Notation: an instruction cell is `tag:op x y z`, with `x` = bits
23-16, `y` = bits 15-8, `z` = bits 7-0, `c16` = bits 15-0 signed.
`r[n]` is register n; the first argument of a goal is `r[0]`.
A label is `here + 2 + c16`, in cells.

Evidence so far: module `jis_to_ascii` in `pimm_ipl.kbn` against
`bios/boot/jtoa.kl1` (`ref/pimm/test_jtoa.py`): `convert_element/2` on
all 65,536 keys, and `convert/2` (through `convert_loop/4`) on five
strings, with eleven observed fault injections, one of which the test
does not catch (noted at `subtract`). A second module's predicate,
`scsi_common:get_4_bytes/4` against `bios/scsi/scsi_common.kl1`, is run
by `ref/pimm/lockstep_get4.py`, its oracle the source's own
`Int := ...` expression; `check_completion_code/4`, the first to build
structures, by `ref/pimm/lockstep_ccode.py`, its oracle the three
source clauses parsed from the text; `analyze_standard_format/5`, the
first to call another predicate, by `ref/pimm/lockstep_asf.py`. From a
third module, `exception_table:replace_argument/3`, the first to read
structures, by `ref/pimm/lockstep_repl.py`, its oracle the seven
source clauses parsed from the text. From a fourth, `shoen:ground_term/2`
with `ground_term/4`, `wait_vector/6` and `wait_and_unify/3`, on lists
and vectors, the first to run several goals at once, by
`ref/pimm/lockstep_ground.py`. The whole `jis_to_ascii` module also runs on the
Bluespec core in lockstep with the reference model (see Trace): every
instruction in the table is implemented there. Three readings no run
of this module can check, on either model, and injections confirm it:
`subtract`'s destination, `less_than` at equality, and whether
`execute` clears the alternative clause (`ref/pimm/lockstep_conv.py`).

| Instruction | Encoding | Meaning | Evidence |
|---|---|---|---|
| `try_me_else` | `23:68 _ c16` | the next clause is at the label; a failing guard goes there | checked |
| `jump` | `23:67 _ c16` | an unconditional branch to the label, the label as `try_me_else`'s (assembler `klb_opr.kl1` `p(c16_exe)`, `cal_location_address`: Label - (pc + 2)); the compiler writes it after a branch of register shortage (`compiler/regass.kl1` `insertBranch`). VPIM `klb_control.psl.c` `klb_jump` and PDSS `emulate.c` `KL1B_JUMP` branch with nothing else | checked on five cells of the bench, a branch forward and back (`lockstep_alt.py` part jump, 2026-11-24) |
| `get_constant` | `23:B8 x`, the constant the whole next cell (r_c40, `inst_tab.kl1`:174) | `r[x]` unified with the constant, as `put_constant` takes it; the compiler writes it for an atomic constant other than an atom or `[]` (`library/compiler/comp.kl1` `compile_put_valuable`, `instrtbl.kl1` `convert_instr`). Two cells | checked on three cells of the bench (`lockstep_alt.py` part constant, 2026-11-24): unbound, equal, other |
| `b_vector` | `22:CA x y z` (r_r_r, `inst_tab.kl1`:298; X in, Size and NewVector out, `blt.kl1` `active_builtin(vector(X1,X2,X3))`) | body `vector(X, ^Size, ^NewVector)`: "The size of the vector X is unified with Size, and X is unified with NewVector. Exception: If X is anything other than a vector" (manual `e-builtin.tex` 750-755): refused. `r[y]` := the size, then `r[z]` := X; an unbound X waits at its stub. VPIM (`klb_body_blt_struct.psl.c` `kblt_b_vector_size`) copies a vector whose MRB is on, so NewVector has a single reference; it is the same term, so OURS: X itself. Bluespec: a vector of 7 or more reads its length from the descriptor (the vector box) | checked at its stub (`lockstep_alt.py` part body vector, 2026-11-24): {1, 2, 3}, {}, the vector of 8, X waited for |
| `code_to_predicate` | `22:F4 x y z`, the fourth and fifth operands the next cell's top two bytes (r5, `inst_tab.kl1`:353; Code in, the rest out, `blt.kl1`) | `code_to_predicate(Code, ^Module, ^Name, ^Arity, ^Info)`: "Unifies a module to which Code belongs with Module, a predicate atom with Name, argument count with Arity, and 1-word information (contents of <Code address - 3>) for software with Info ... for the Multi-PSI and PIM/m" (manual `e-builtin.tex` 1304-1311). A predicate is laid out Name, 0, the head, the length, then the code (`assembler/assemble.kl1` `make_pred_head`), so Name is Code - 4 and Info Code - 3; the module as the guard `code` finds it. Name the atom tag and Arity the integer tag, MRB off (VPIM `klb_body_blt_cont.psl.c` `kblt_b_code_to_predicate`). Anything but a code is the exception: refused; an unbound Code waits | checked at its stub (`lockstep_alt.py` part code to predicate, 2026-11-24): two predicates of `scsi_fep_util`, Code waited for |
| `wait_vector` | `23:AF x n` (r_vector; n the low 16 bits) | the general form of `wait_vector_N` for a vector of 7 or more (assembler `klb_opr.kl1` `p(r_vector, ..)`: Length>6 writes `Op \/ Reg<<16 \/ Length`, below 7 the opcode `wait_vector_N`): r[x] a vector of n elements, the structure pointer at its first element, as `wait_vector_N`; the length read from the vector's descriptor (`pimm.py` `vsize`). An unbound r[x] is noted, anything else fails. n below 7: refused | checked on six cells of the bench (`lockstep_alt.py` part vector 7, 2026-11-24): vectors of 7 and 8, {5}, a variable |
| `multiply_bignum_word` | `22:B8 x y z` (r_r_r, `inst_tab.kl1`:247; X, Y in, Z out, `blt.kl1`) | `multiply_bignum_by_word(BigX, Y, ^BigZ)`: "The result of multiplying BigX by Y seen as a 32-bit unsigned integer"; a bignum a 32-bit string read unsigned, "The MSB is the zeroth element and is zero suppressed" (manual `e-builtin.tex` 703-741). The edges as VPIM's (`klb_body_blt_bignum.psl.c` `kblt_b_multiply_bignum_by_word`, `f_reduce_bignum.psl.c`, `str_bignum.psl.c` `s_Multiply_BIGNUM_By_Word`): the empty X is the answer itself, Y = 0 the empty string, the product one word longer only when the last carry is not 0. A leading zero word, X not a 32-bit string or Y not an integer: the exception, refused. Bluespec: two passes from the least significant word, the word step in the multiply box (`PimmMBox` `multiplyAdd`, unsigned a*b+c), the words written into a new string of zeros (OURS, the order the reference follows) | checked at its stub (`lockstep_bignum.py`, 2026-11-24): with and without a last carry, a carry between words, Y unsigned, the empty X, Y = 0, X waited for |
| `add_bignum` | `22:B6 x y z` (r_r_r, `inst_tab.kl1`:245; X, Y in, Z out, `blt.kl1`:718-719) | `add_bignum(BigX, BigY, ^BigZ)`: "Adds BigX and BigY and unifies the result with BigZ" (manual `e-builtin.tex` 710-717). The edges as VPIM's (`klb_body_blt_bignum.psl.c` `kblt_b_add_bignum`, `f_reduce_bignum.psl.c` `f_Add_BIGNUM_Sub`, `str_bignum.psl.c` `s_Add_BIGNUM`): X empty gives Y itself, Y empty X itself, else the sum, as long as the longer, one word longer when the last carry is 1. A leading zero word in either, or either not a 32-bit string: the exception, refused. Bluespec (rules `ba1`..`ba9`): two passes from the least significant word of the longer, the first finding the last carry (so the length), the second writing each word into a new string of zeros, the carry word last (OURS, the order the reference follows) | checked at its stub (`lockstep_bignum.py`, 2026-11-25): 5+3, a carry out, a carry between words, Y the longer, equal lengths with a carry out, the empty operands, Y waited for; met in the shell's `ts` |
| `subtract_bignum` | `22:B7 x y z`, the fourth operand the next cell's top byte (r4, `inst_tab.kl1`:246; X, Y in, Borrow, Z out, `blt.kl1`) | `subtract_bignum(BigX, BigY, ^Borrow, ^BigZ)`: "The difference between BigX and BigY is calculated and the absolute value of that result is unified with BigZ. If the result was non-negative 0, otherwise 1, is unified with Borrow" (manual `e-builtin.tex` 720-727). The edges as VPIM's (`klb_body_blt_bignum.psl.c` `kblt_b_subtract_bignum`, `f_reduce_bignum.psl.c` `f_Subtract_BIGNUM_Sub`, `str_bignum.psl.c` `s_Subtract_BIGNUM`): Y empty gives X itself and 0, X empty gives Y itself and 1, equal gives the empty string and 0, else the larger less the smaller with its leading zero words dropped. A leading zero word in either, or either not a 32-bit string: the exception, refused. Bluespec: the larger found (lengths, then words from the most significant), then two passes from the least significant word, the borrow in a 33-bit subtract, the kept words written into a new string of zeros (OURS, the order the reference follows) | checked at its stub (`lockstep_bignum.py`, 2026-11-24): either larger, a borrow, words dropped, Y the longer, the empty operands, equal, Y waited for |
| `search_character` | `22:D9 x y z`, the fourth to sixth operands the next cell's top three bytes (r6, `inst_tab.kl1`:321; String, Start, End, Code in, Position, NewString out, `blt.kl1`:663-664) | `search_character(String, Start, End, Code, ^Position, ^NewString)` (manual `e-builtin.tex` 928-942; VPIM `kblt_b_search_character` the same): the elements from Start to End, both included, searched for Code, from the rear when End < Start; Position the first found, -1 when none; NewString the string. A range outside the string or a code wider than its elements is the exception: refused. Bluespec: the string box, one element per read | checked at its stub (`lockstep_alt.py` part search, 2026-11-24): 8- and 16-bit strings, both directions, a miss, Start waited for |
| `unbound` | `22:EF x y` (r_r, `inst_tab.kl1`:348) | `unbound(X, ^Result)`: "If X is an undefined variable ... a vector {Id, Address, NewX} is unified with Result ... If X has been instantiated, a vector composed of only one element {NewX}"; never suspends (manual `e-builtin.tex` 102-109). As VPIM (`klb_body_blt_cont.psl.c` `kblt_b_unbound`): {the cluster, the variable's address as an integer, the reference}; the cluster 0 (OURS, one) | checked at its stub (`lockstep_login.py` part unbound) |
| `add_extended`, `subtract_extended`, `multiply_extended`, `divide_extended` | `22:B2`..`22:B5 x y z`, the fourth (and fifth) operand the next cell's top byte(s) (`inst_tab.kl1`:241-244; `blt.kl1`:706-717) | the operands read as 32-bit unsigned: the carry and the low word of X + Y; the borrow and X - Y modulo 2^32; the high and low words of X * Y; Xh:Xl / Y, the quotient and the remainder (manual `e-builtin.tex` 615-660, `devide_extended`). Y = 0 or Xh >= Y (the quotient wider than 32 bits, VPIM's test) and a non-integer are the exception: refused. Bluespec: a 33-bit add, the multiply box, the divide box's 64-by-32 unsigned divide (`divideWide`) | checked at their stubs (`lockstep_login.py` part extended): carries, a borrow, wide products, a 64-bit dividend, X waited for |
| `module` (guard) | `23:FB x y` (r_r, `inst_tab.kl1`:214) | `module(X, ^Size)`: "Unifies the size of the module X with Size. Suspend: X uninstantiated. Fail: X anything other than a module" (manual `e-builtin.tex` 86-92). Size is the count in the module's descriptor (the loader's `06000000h \/ (size - 1)`; the unloader reads that many elements, `library/unloader/encoder.kl1`); VPIM reads its own header's size word | checked (`lockstep_login.py` part module, on code of the bench): `scsi_fep_util`'s 174 (`asm/kbndis.py`'s table), 5 fails, X waited for |
| `extended_floating_point` (guard) | `23:6E 8 y z` (function 8 of 23:6E, f_r_r, `inst_tab.kl1`:104; `blt.kl1` In [X], Out [NewX], Pre [wait]) | the type test: an extended floating point has its own tag, 3Fh (`library/kbn/kbnheap.kl1`); anything else fails, an unbound X is noted. An extended float is refused (none can be made here, NewX undocumented) | checked (`lockstep_login.py` part extended float, on code of the bench): an integer and an atom fail, X waited for |
| `extended_floating_point_less_than`, `_not_less_than` (guards) | `23:6E 2 y z`, `23:6E 3 y z` (`inst_tab.kl1`:98-99; `blt.kl1`:417-424, both inputs waited for) | the compiler's `$$<` and `$$>=` (`macro/pimos/pimos/pimos.smac`:390-405). In neither the manual nor VPIM nor PDSS. Arguments that are not both extended floats (tag 3Fh) fail the guard, as the held sorter needs (`utility/sorter/sorter.kl1`:51-71: its comparator tries each kind in turn); two extended floats are refused (none can be made here). R7L, 2026-11-25, met in the Listener | checked (`lockstep_sord.py` part xf, on code of the bench): integers and atoms fail, for both functions |
| `string_less_than`, `string_not_less_than` (guards) | `23:FE x y`, `23:FF x y` (`inst_tab.kl1`:227, 229; `blt.kl1`:392-397, both waited for) | the manual's order (`e-builtin.tex`:813-837): wider elements larger; otherwise element by element from the first, a longer string larger; Suspend if either is unbound, Fail if either is not a string. As VPIM computes it (`s_WhichIsLessString`, `structures/str_string.psl.c`; `f_reduce_string_ope.psl.c`:251): element sizes, then the words from the first as unsigned, then the word counts, then the element counts (`pimm.py` `string_order`, `PimmSBox.bsv` `compare`). R7L, 2026-11-25, met in the Listener | checked (`lockstep_sord.py`: by width, unsigned words, a word more, an element more, a goal suspended and woken); the word-count step is not separable from the element count (no pair orders differently by the two) |
| `bignum_less_than`, `bignum_not_less_than` (guards) | `23:B6`, `23:B7 x y` (r_r, `inst_tab.kl1`:171-172; both waited for, `blt.kl1`:399-404) | "32-bit strings ... handled as though they represented unsigned integer values. The MSB is the zeroth element and is zero suppressed"; B1 < B2 (B1 >= B2) succeeds; anything other than such a bignum fails (manual `e-builtin.tex` 665-697). As VPIM (`str_bignum.psl.c` `s_IfBignumLessThan`, `s_CompareBIGNUM`): an element size other than 32 or a leading zero word fails either; the longer is the larger, equal lengths compared word by word from element 0, unsigned. Bluespec: the string box, one word per read | checked (`lockstep_login.py` part bignum, on code of the bench): eleven pairs on both guards, B1 waited for |
| `switch_on_non_integer` | `23:28 x c16` | if `r[x]` is bound to an integer, fall through; otherwise go to the label. An unbound `r[x]` also records the variable as one the goal is waiting on | integer and atom cases checked; the unbound case by its consequence (the goal suspends) |
| `hash_on_constant` | `23:2D x c16`, then a word, then a table | `c16` is a mask. The next cell holds the miss label, relative to itself (`its address + 2 + value`). Then `mask + 1` slots, indexed by `r[x] AND mask`: `{atom, 0}` is empty; `{integer, count << 16 \| offset}` points, `offset` cells from the slot, at `count` pairs `{key, offset}`; a matching pair's target is `offset cell + 1 + offset` | checked (three of the five injections are here) |
| `switch_on_constant` | `23:2C x c16`, then `c16` pairs | Each pair is `{key, {integer, else << 16 \| offset}}`; both 16-bit fields are labels relative to the pair's second cell (`its address + 2 + value`). The pairs are compared in order with `r[x]` dereferenced (tag and value); a match goes to its `offset` label, no match to the last pair's `else` label. Every pair carries the same else label. An unbound `r[x]` is noted and takes the else label (the first pair's), as `hash_on_constant` takes its miss label: this last point is our reading by analogy, not from a source | encoding from `library/assembler/klb_opr.kl1` (`r_c16_c16_16s_sw`, `make_label`), checked against the image's `replace_position/3`; run in `lockstep_rpos.py` |
| `put_integer` | `23:31 x c16` | `r[x]` := integer `c16` | checked |
| `not_less_than` | `23:F1 x y` | guard: `r[x] >= r[y]`, else fail to the next clause | checked; unbound operands not exercised |
| `b_subtract` | `22:C1 x y z` | `r[z]` := `r[x] - r[y]` | checked |
| `b_add` | `22:C0 x y z` | `r[z]` := `r[x] + r[y]` | checked |
| `equal` | `23:F2 x y` | guard: `r[x] = r[y]`, integers | checked |
| `and` | `23:EA x y z` | guard arithmetic: `r[z]` := `r[x]` and `r[y]` | checked |
| `get_atom` | `23:C0+r`, atom in the low 24 bits | unify `r[r]` with the atom | checked (`scsi_common:check_completion_code/4`) |
| `put_vector_N` | `23:38+N x` | `r[x]` := a new vector of N cells; the structure pointer is set to its first cell | checked for N = 2, 3, 4. The pointer's tag is written with the low bit set, as the image builder writes every pointer; what the machine does there (MRB) is not known. *2026-11-26: the held firmware gives MRB off (`VECT1o`, `VECT2o` stamped at `31f9`, `31fd`; `LISTo` for `put_list` at `31d0`), executed by `ref/pu/check_pu.py`; this model is not changed* |
| `write_atom` | `23:23`, atom in the low 24 bits | store the atom at the structure pointer and advance it | checked |
| `write_nil` | `23:22` | store `[]` (atom 0) at the structure pointer and advance it | checked (`lockstep_gca.py`) |
| `put_vector` (general) | `23:3F x`, size in the low 16 bits | `r[x]` := a new vector of that many cells in the long form (descriptor), the structure pointer at its first element; `load_module` builds `module/9`, ten cells, with size 10. Sizes below 7 are refused (the image has 7, 8 and 10 only) | checked for 10 (`lockstep_lmod.py`); the size's upper byte is NOT checked |
| `execute_external` | `23:62 n`, label | the same goal goes on at a predicate of another module. The label locates a four-cell predicate descriptor in the caller's GC area (TM-662 fig. 2: cache field, `{REFx}` to a cell holding `{REFo}` to the module, key `{atom, arity << 24 \| name + arity}`, module name). The called module's code area begins with its predicate entry table: `{INT, mask}`, `mask + 1` slots indexed by key AND mask, a slot `{INT, count << 16 \| offset}` to pairs `{key, {INT, off}}`, the code at the off cell + off. Read from the image: all 59 entries of its 20 modules follow it, and all 76 calls resolve. The cache field (filled on first call on Multi-PSI/V2) is NOT used or written: what the machine writes is not known; both models look up at every call and refuse a non-zero cache | checked: 49 of the 76 calls land where `asm/kbndis.py` finds the predicate by its head (`lockstep_ext.py`). A second pair in a slot and the caller's guard state are NOT checked |
| `wait_value` | `23:A4 x y` | the guard `X = Y` on two arguments (TR-246 p. 5); an unbound one is noted and the guard fails. Atomic values and strings: two strings are the same when their descriptors and every word are (PDSS `emulator/passive.c` `passive_unify`), a string and an atomic value are not. A list or a vector on either side (**2026-11-25**, VPIM's general passive unification, `functions/f_reduce_passive_unify.psl.c` `f_EqualStruct` 41-109 and `f_Equal_Sub` 166-312, `structures/str_passive_unify.psl.c` the unify stack; met compiling the primer's sample1, `pimos::keyed_bag` `if_empty/4` comparing the compiler's keys `{car, {arg, 1}}`): words of two types are not equal; depth first, with an explicit stack of frames (crp, size, X's and Y's first element), each pair of elements dereferenced: an unbound X is noted and the guard fails there, then an unbound Y; a module or a code is equal only to the same tag and value (MOD 27h and COD 26h differ in the bit other tags keep for the MRB); other types that differ are not equal; integers and atoms by value; strings by descriptor and words; the null vector is equal; a list (car, cdr), a short vector, or a long vector after its size, pushes the frame in hand, even one at its end (so a list's cdr takes a frame), and its elements come next. The stack holds 512 frames, VPIM's bound (`_LOCAL_MEM_UNIFY_STACK_AREA_SIZE` 0x800 words, `basics/bsc_mem_map.psl.c`:90, 4 words a frame), not PIM/m's, which is not held; a 513th push is refused (VPIM suspends there with a DEBUG warning and no variable to wake the goal). Neither a list, a vector nor a string, and not both atomic (**2026-11-27**, the IFS sweep's top first stop, `docs/ifs_apps.md` 4): VPIM's `klb_equal` (`interpreter/klb_compare.psl.c` 91-97) compares an atomic X with Y by tag and value, so an atomic X and a Y that is not are not equal; any other X goes to `f_EqualStruct` (45-105): types that differ are not equal, and a shoen's handle, a module or a code (SHREC, MOD, COD) is equal only to the same whole tag and value; any other type is VPIM's DEBUG `Illegal type`, refused (`wait_value on a XX word`). Both reference models (`pimm.py` `equal_other`, which `pimm_pe.py` takes); the Bluespec core still refuses these pairs (`PimmStages.bsv`, `E unimp`). Refused also: an element of a type not compared above. One variable twice (X and Y the same unbound variable, **2026-11-27**, the IFS sweep's ldlib, mssd, aya, H9-07) is waited on, as an unbound X always is: VPIM `klb_equal` "suspends even if both point to the same variable" (`interpreter/klb_compare.psl.c` 36-43), PDSS `passive_unify` the same; INFERENCE for PIM/m; both reference models (`ref_node_alert.py`), the core still refuses it (`PimmStages.bsv` 1016-1017). VPIM's dereference writes back into the structure: not carried over. Until 2026-11-25 both models took two vectors of 0..6 atomic elements only, after PDSS (`emulator/emulate.c` `KL1B_WAIT_VALUE`), refusing the rest; PDSS goes into nested structures to depth 100 (`emulator/config.h`:187-196) and fails past it. On the Bluespec the passive-unification box (`PimmPBox.bsv`, its own memory port, the data box for each dereference) | checked on integers (`lockstep_ext.py`), on strings equal and unequal (`lockstep_atab.py`: the pool's keys), and on vector keys of the IPL's pool (`lockstep_pvec.py`: 20 comparisons of two vectors, equal, an element differing, sizes differing; two empty vectors; an atom against the empty vector); nested vectors, lists, long vectors, strings, codes and a module as elements, differences after a pop, four goals waiting on an unbound element of X or Y, 512 frames and the 513th refused (`lockstep_pstruct.py`, OURS goal in heap cells); a string against an atomic value at the top is not run; at the top, on the reference models alone (one PE and several): modules, codes and shoen handles against each other, an atom, an integer, a string and a list, two goals waiting on X or Y, an extended float refused (`ref_wait_value.py`) |
| `wait_constant` | `23:A0 x`, then a cell | the guard `X = constant`, the constant the whole next cell; two cells. Atomic values only | checked for -2^31 (`lockstep_ext.py`) |
| `tag_and_value` (guard) | `23:76`, function 4: `y z`, third register in the next cell's top byte | `r[z]` := the tag, the third := the value of `r[y]`'s cell, as integers; an unbound one is noted and the guard fails; two cells. Sources: PDSS `emulator/blt_system.c`; `library/unloader/encoder.kl1` writes instruction cells with it and the `.sav` files hold their tags as the image has them. Whether a tag's MRB bit is returned is NOT established: the tag is returned as it stands | the value is checked (`lockstep_ptab.py`); the tag only as both models agree |
| `new_instruction` | `22:D5 x y z` | `r[z]` := the cell with tag `r[x]` and value `r[y]` (`decoder.kl1` `decode_atomic`, `encoder.kl1` `decode_pred_hash_key`). Both models refuse reference and pointer tags (4..1Fh) | checked for tag 2: the keys it makes are the image's (`lockstep_ptab.py`) |
| `b_vector_element` | `22:CC x y z`, fourth register in the next cell | `vector_element(V, I, ^E, ^V1)`: `r[z]` := element, the fourth := the vector (manual) | checked (`lockstep_ptab.py`) |
| `add` (guard) | `23:F4 x y z` | `r[z]` := `r[x]` + `r[y]`; an overflow fails the guard (manual) | the sum is checked; the overflow is NOT run |
| `multiply` (guard) | `23:F6 x y z` | `r[z]` := `r[x]` * `r[y]`; a non-integer or an overflow fails the guard ("Fail, Exception", manual `e-builtin.tex`:268-283; directions `iio`, `blt.kl1`:29-30); an unbound operand is noted. On the Bluespec the multiply box of `b_multiply` (`PimmMBox.bsv`), its overflow flag failing the guard | checked at the four sites of `scsi_fep` in `pimm_patch_scsifep360E.sav` (`lockstep_gmul.py`): products ((L+3)/4)*4 for L from -2147483645 to 2147483640; the overflow, a non-integer and an unbound operand are NOT run (no site there reaches them) |
| `save`, `restore` | `23:19 x c16`, `23:1A x c16` | the KL1 compiler's register spill (`library/compiler/regass.kl1` `outputCode/6`): `save` puts `r[x]` in work slot `c16`, `restore` gives `r[x]` the slot's value (TM-1044's `save(Reg,POS)`/`restore(POS,Reg)` on "work memory", in each processor's local area, as listed in `docs/literature_gaps.md`). **The area is OURS**: 256 slots of their own, traced as `V` lines; a slot of 256 or more is refused | checked (`lockstep_gmul.py`, `scsi_fep:send_packet1/8`: slots 0, 32, 33 saved, slot 0 restored); a restore from another slot than 0 is NOT run |
| `diff` | `23:F9 x y` | the guard `X \= Y` (`blt.kl1`:239-244, both inputs): "Succeeds if it is assured that X is not equal to Y ... X or Y must be an atomic term"; an unbound one is noted and the guard fails (suspends); equal fails (manual `e-builtin.tex`:114-143). Equal = the same tag and value, so an integer is never an atom. One atomic and the other not (a structure, a string, the empty vector): never equal, diff succeeds (2026-11-24, met in `pim:go/4` at `task_handler`; KLIC `include/klic/gb.h` `gblt_diff`: "isatomic(y) \|\| isatomic(x) ? (x) == (y)"; PDSS `emulator/emulate.c` `KL1B_G_DIFF`, `passive_unify`). Neither atomic ("Illegal DIFF!!!" on the Multi-PSI's CSP, the same page; KLIC and PDSS differ there): refused by both models | checked at `file_request_device:driver_0/10` in `pimm_patch_mkdir360E.sav` (`lockstep_rdvc.py`): both diffs succeeding, each failing, an integer equal in value to the atom, an unbound operand waited for, a vector against the atoms |
| `wait_nil` | `23:A2 x` | guard: `r[x]` is `[]` | run (`lockstep_ptab.py`); another atom there is NOT run |
| `wait_list` | `23:A6 x` | guard: `r[x]` is a list; the structure pointer at its car | checked |
| `read_atom` | `23:B3`, atom in the low 24 bits | the element at the structure pointer must be that atom; an unbound one is noted and the guard fails | run; another atom there is NOT run |
| `switch_on_non_atom` | `23:29 x`, label | next if `r[x]` is an atom, else the label; an unbound one is noted | checked (`lockstep_ext.py`) |
| `write_marked_value`, `set_marked_value` | `23:27 x`, `23:16 n y` | as `write_value`, `set_value`, with the MRB of the source register and of the copy set (see "The MRB") | checked: both writes are traced |
| `set_integer` | `23:11 n`, c16 | goal argument n := the signed 16-bit integer | checked for non-negative operands |
| `put_structured_constant` | `23:37 x`, label | `r[x]` := the cell at the label, a place in the GC area holding the pointer to a constant built outside the module (TM-662). A `{REFx}` there is `module#M`: a reference to the image's module-table cell, or in a loaded module to the variable the linker binds to the module object; the register gets the cell as it stands and its users dereference it (`ipl:boot/0` passes `module#ipl` to `predicate_to_code`). Run on the reference model alone by `pim:go/4` after the whole link (`longrun_ipl.py --reference --go`); NOT yet in a lockstep test: its image sites lead into shoen | checked: three error clauses return their string (`lockstep_ptab.py`) |
| `collect_list`, `collect_vector` | `23:1E x`, `23:1F x n` | MRB reclamation of a list cell or vector: nothing here, as `collect_value` (no reference counts) | run |
| `enqueue_goal` with more than 11 arguments | `23:63 n`, label | a goal has 11 argument slots: the compiler packs the arguments from the 11th on into a vector passed as the 11th (`library/compiler/pack.kl1`, `max_goal_slots`). The called predicate reads `r10`, `r11`, ... with no code to unpack, so the firmware spreads the vector; where is not known. Both models spread it as the goal is made and keep every argument in their own record. A vector of 7 or more (more than 16 arguments, 2026-11-24, met after the login) is spread the same way from its descriptor's first element (`pimm.py` `vsize`, `vbase`; Bluespec: its size from the vector box first). Refused: no vector, a size other than the arguments left over | checked for 12 (`lockstep_pack.py`), 13 (`lockstep_file.py`) and 17 (`lockstep_login.py` part enqueue 17); the refusals are NOT run |
| unification of two lists or two vectors (any instruction that unifies) | — | not done on the spot: a ready goal of the stub `unify_step` (`22:01`, OURS, `asm/pimm_stubs.py`) with arguments X, Y, 0 unifies the elements one pair each time the step is taken, an element taken with its MRB on if its structure's is. From PDSS (`emulator/unify.c` `make_unify_vector_vector_goal_and_enqueue`, `dc_unify_vector_vector2`); PIM/m's own way is not known. Two vectors of seven or more (2026-11-24) make the same goal; their sizes are in memory, so the step compares them each time it is taken and fails on a difference (OURS; PDSS `active_unify_with_vector` compares the lengths before it makes the goal: a failure either way), and the elements are found from the descriptors | `lockstep_unif.py`; the MRB rule is not caught by it; vectors of seven or more: `lockstep_alt.py` part long unify (equal sizes, an element unequal, sizes 8 and 9) |
| `scsi_where` | `22:A0 x` | `r[x]` := `[{0, 0, 0, 6}]`: one SCSI port, cluster 0, processor 0, port 0, own unit 6. The grammar and the single-FEP value are the PIMOS source's stand-in for the built-in (`bios/boot/scsi_conf.kl1`); what the firmware read is not known | checked (`lockstep_where.py`, a bench-made code) |
| `predicate_to_code` | `22:F3 x y z`, a fourth register in the next cell | `r[w]` := the code of predicate `r[y]`/`r[z]` in the module object `r[x]`, or the vector `{Module, Name, Arity}` if the module has none (PIMOS manual `e-builtin.tex`; PDSS differs). A code is `{COD, first instruction}`: the target is assumed (`lockstep_p2c.py` header) | checked on the image's 349 predicates (`lockstep_p2c.py`) |
| `apply` | `22:F1 x y` | `apply(Code, Args)`: a new ready goal of the code `r[x]` with the elements of the vector `r[y]` as its arguments; waits for either (PIMOS manual `e-builtin.tex`). The goal is made as PDSS makes it (`emulator/blt_system.c` `blt_b_apply`): each element taken with its MRB on if the vector's is. The manual's exceptions (not a code, not a vector, the count differs from the predicate's) are refused, as is a vector of more than 16 (OURS, the limit). A vector of 7 to 16 (2026-11-24, met after the login) gives its elements from its descriptor's first. The empty vector makes a goal of no argument | checked, with the IPL's own `apply` site (`lockstep_apply.py`; the empty vector on a predicate of the bench, 2026-11-24; a vector of 7, `lockstep_login.py` part apply long) |
| `create_shoen` | `22:E0 x y z`, four more registers in the next cell | `create_shoen(MinPrio, MaxPrio, ExcepMask, Code, Argv, ^Report, ^Shoen)`, format `r7`. **PIM/m-sourced**: the encoding and the directions (`assembler/inst_tab.kl1`:332-362, `klb_opr.kl1`:144-154, `compiler/blt.kl1`:567-569), and that the outputs may be the input registers (the image's `shoen:execute/4`, cell 15553, is `22:e0040506 / 00:00010001`: Code and Report both `r0`, Argv and Shoen both `r1`), so every input is read before an output is written. The manual does not document it. **What it does is not PIM/m-sourced** ("Shoen" below): the three first operands are waited for, must be integers and are dropped; a shoen record, a fresh Report variable, the handle `{SHREC, record}`, and one parked goal `apply(Code, Argv)` of the new shoen. Code and Argv are not waited for. The distributed form (2026-11-24, met after the login): `shoen:execute1/7`, what `execute/9` calls, passes `{MinPrio, MaxPrio}` and `{MinNode, NumNode}` in place of the first two (`kernel/builtin/shoen.kl1`); two 2-vectors there are accepted and dropped, their elements not read (OURS: one node, no priorities). Refused: a mask that is not an integer, any other priority operands | checked (`lockstep_shoen.py`, through the image's `execute/4` and through its stub; the distributed form through the image's `execute1/7`, `lockstep_shoen3.py` part execute1); the refusal is not in the suite (observed by hand on both models, the test's header) |
| `start_shoen` | `22:E1 x y` | `start_shoen(Shoen, ^NewShoen)` (encoding and directions **PIM/m-sourced**, `inst_tab.kl1`, `blt.kl1`:537-601; the image's `control/2`, cell 15755). A dormant shoen: 8 is reported first, then it is started and its parked goal goes on the ready queue (the order is VPIM's, **carried over**); `r[y]` := the same handle (**ours**). Stage 3: a STOPPED shoen likewise, 8, started, and every goal parked on it back on the queue (PDSS `shoen.c`, **carried over**). Refused: a shoen that is neither dormant nor stopped, anything but a handle | checked (`lockstep_shoen.py`; start after stop `lockstep_shoen3.py`); a second start is refused on both models, observed by hand (the test's header), not in the suite |
| `shoen_statistics` | `22:E6 x y` | `shoen_statistics(Shoen, ^NewShoen)` (encoding and directions **PIM/m-sourced**, `inst_tab.kl1`, `blt.kl1`:537-601; the image's `control/2` for `statistics`). 10 on the report stream, then `{9, H, L}`: twice the shoen's reductions, its descendants' included, as 64 bits (the value **PIM/m-sourced**, manual `e-shoen.tex`:234; 10 then 9 at once is VPIM's, **carried over**; what a reduction is and where the count lives, "Shoen" below). `r[y]` := the same handle (**ours**). On a running shoen the count as it stands (**ours**). Refused: anything but a handle | checked (`lockstep_shoen2.py`: through the image's `control/2` and three monitors, H, L from the trace's own count of reductions) |
| `remove_shoen` | `22:E4 x` | `remove_shoen(Shoen)` (encoding and direction **PIM/m-sourced**; the image's `control/2` for `[]`). A terminated shoen: `{14, H, L}` (`return_resource`, H:L the resource left, 0 if none; R7L, until which it was 0, 0), then the report stream closed with `[]`, status removed; one not yet terminated is marked and removed at its termination (VPIM's, **carried over**). Refused: a shoen removed already, anything but a handle | checked (`lockstep_shoen2.py`, both cases); the refusal not in the suite |
| `stop_shoen` | `22:E2 x y` | `stop_shoen(Shoen, ^NewShoen)` (encoding and directions **PIM/m-sourced**, `inst_tab.kl1`, `blt.kl1`:537-552; the image's `control/2` for `stop`). 11 `stopped` on the report stream, then a started shoen is stopped (11 first: VPIM's, **carried over**); its goals and its descendants' are parked when taken from the queue (PDSS's, **carried over**; "Shoen" below). `r[y]` := the same handle (**ours**). Refused: anything but a handle | checked (`lockstep_shoen3.py`: through the image's `control/2`, a woken goal parked, then released by `start`) |
| `allow_shoen_resource_report` | `22:E7 x y` (r_r, `inst_tab.kl1`:339; Shoen in, NewShoen out, `blt.kl1`:595) | the shoen's `allow_resource_report` (`shoen.kl1`:131-133): "Allows a report to be sent as the amount of consumed resource has nearly reached its upper bound", acknowledged by `resource_report_allowed` (manual `e-shoen.tex`:174-180, 254-262), 7 (`pimos.vmac`). VPIM (`f_shoen_control.psl.c` `f_AllowShoenResourceReport_Sub`) reports it, then clears the shoen's report-disallowed flag (R7L, 2026-11-25: kept, `SH_RSC_FLAGS`, "Shoen" below); NewShoen is the handle. Refused: anything but a handle, a closed report stream | `lockstep_shoen3.py` part allow_resource_report: the Report `[started, resource_report_allowed, resource_low, resource_added \| _]`; parts `resource: silent` and `resource: reported again`: a second `resource_low` only after the flag is cleared |
| `add_shoen_resource` | `22:E5 x y z`, the fourth operand the next cell's top byte (r4, `inst_tab.kl1`:337; Shoen, High, Low in, NewShoen out, `blt.kl1` `active_builtin(add_shoen_resource(X1,X2,X3,X4))`) | the shoen's `add_resource(H, L)` (the image's `shoen:control/2`, `kernel/builtin/shoen.kl1`:127-130): "A value of which the upper 32 bits are expressed in Amount_h and the lower 32 bits ... in Amount_l is added to the upper bound value of the resource consumption amount", acknowledged by `resource_added` (manual `e-shoen.tex`:166-172, 254-262), 5 (`pimos.vmac`). VPIM (`f_shoen_control.psl.c` `f_AddShoenResource_Sub`) reports 5 first, then adds, reporting `return_resource` only when the bound passes 2^63; NewShoen is the handle. R7L (2026-11-25): H:L is added to the resource left (refused at 2^63 or past), and a STARTED shoen with some left has its parked goals put back on the queue (the manual: "If the upper bound value is increased when execution is suspended due to trespassing the upper bound, shoen execution resumes", `e-shoen.tex`:31). Refused: anything but a handle, High or Low not an integer, a closed report stream | `lockstep_shoen3.py` part add_resource (2026-11-24): the image's control/2 with `[start, add_resource(0, 1000) \| _]`, the Report `[started, resource_added \| _]` |
| `abort_shoen` | `22:E3 x y` | `abort_shoen(Shoen, ^NewShoen)` (encoding and directions **PIM/m-sourced**; the image's `control/2` for `abort`). 1 `aborted` on the report stream, then the shoen terminates at once (12, its reductions and one off its parent's count: **ours**; the manual has `terminated` follow `aborted`); its goals and its descendants' are discarded when taken from the queue (PDSS's, **carried over**). A terminated shoen: 1 only (VPIM's). Refused: the current goal's own shoen or one above it, anything but a handle | checked (`lockstep_shoen3.py`: an inner shoen by its control stream, an outer one by `top_level_monitor/4`) |
| `raise` | `22:F2 x y z` | `raise(Tag, Info, Data)` (encoding and directions **PIM/m-sourced**, `blt.kl1`; the image's `shoen:raise/3`). Waits for Tag only (VPIM's, **carried over**); the exception 16 `raised`, Info `{0, Info, Data}` (the firmware's format **PIM/m-sourced**, `excpt_tbl.kl1`; Pe 0 **ours**) reported to the innermost shoen whose mask AND Tag is not 0 ("Shoen" below), and the goal `apply(NewCode, NewArgv)` in the current shoen. Refused: a Tag that is not an integer, a tag no shoen accepts | checked (`lockstep_shoen3.py`: the image's `raise/3`, and `control/2`'s raise for an illegal message) |
| `current_processor` | `22:EB x y z` | `current_processor(^Processor, ^X, ^Y)` (encoding **PIM/m-sourced**, `inst_tab.kl1`); no input, never waits. **One processor here**: 0, 1, 1, PDSS's values (`blt_system.c`) | checked inside `exception_table:translate/4` (`lockstep_shoen3.py`; `lockstep_ext.py` enters `translate/2` and `/4`) |
| `code` (guard) | `23:FA x y z`, a fourth register in the next cell | succeeds if `r[x]` is a code (whole tag 26h), with `r[y]` := arity, `r[z]` := its module, the fourth := its offset from the module's descriptor cell; anything else fails (PIMOS manual) | checked, outputs from the trace (`lockstep_p2c.py`) |
| `list` (guard) | `23:E3 x` | "Succeeds if X is a list. Suspend: If X is uninstantiated. Fail: If X is anything other than a list" (PIMOS manual `e-builtin.tex` 62-68, PRINTED; `inst_tab.kl1` 190); a list cell only, `[]` (the atom 0) is not one, as in PDSS (`emulate.c` 685 `KL1B_LIST`) and VPIM (`klb_index.psl.c` 117-127 `klb_is_list`). Reference models only, 2026-11-27 (the IFS sweep's mmi); the Bluespec core lacks it | `ref_prio_list.py`: a list, `[]`, an atom, an integer, a vector, a string, an unbound X waited on, both models |
| `atom` (guard) | `23:E1 x` | "If X is an atom, this predicate succeeds, otherwise it fails" (PDSS manual); an unbound X is noted | run succeeding only (`lockstep_link.py`: the IPL's link table); a non-atom is not run |
| `floating_point` (guard) | `23:E6 x` | "If X is a floating point, this predicate succeeds, otherwise it fails" (PDSS manual); an unbound X is noted. The type test only | failing: `lockstep_run.py`; succeeding on a float: APPS `float_klic` (`docs/float.md`) |
| `divide` (guard) | `23:F7 x y z` | `r[z]` := `r[x] / r[y]`; a non-integer, a zero divisor or the overflow (the least integer by -1) fails the guard (manual: "failure or exception"). Truncated towards zero as PDSS's C `/`, not established for PIM/m | run on 3 / 2 (`lockstep_run.py`); a negative operand, zero and the overflow are not run |
| `shift_left` (guard) | `23:E8 x y z` | `r[z]` := `r[x] << r[y]`, 32 bits; a count outside 0..31 fails the guard (manual), as `shift_right` | checked (`lockstep_run.py`, against the module's source); the count limit is not run |
| `put_marked_variable` | `23:35 x y` | as `put_variable`, both references with the MRB on (PDSS `emulate.c` `KL1B_PUT_MARKED_VARIABLE`) | checked: both register writes are traced |
| `read_variable_without_deref` | `23:A7 x` | as `read_variable`. The compiler writes it for `read_variable` when the clause collects the structure and not the element (`library/compiler/regass.kl1` `convertIfNotCollected`); the machine's `read_variable` dereferences what it takes at once and this does not, and here neither does (the instruction that uses the register dereferences) | checked (`lockstep_run.py`: the list hashed) |
| `display_console` | `23:7F x` | `display_console(X)`: "displays the current value of X on the console window, even if this variable is unbound" (PDSS manual): it does not wait and cannot fail. Here the console is the trace: a `C` line with the dereferenced value and, for a string, an `S` line for its descriptor and each word. Displayed when the instruction is executed, so a clause tried again displays again. How PIM/m's console SHOWED a value (an integer's digits, where a line ends) is not known and not modelled | checked on 8-bit strings (`lockstep_cons.py`: a real file's comment and a file's name, through the IPL's `display_console/1` and `jis_to_ascii`); a non-string or unbound value is not run |
| `new_atom` | `22:D2 x` | `new_atom(^Atom)`: `r[x]` := an atom no other holds, without a name ("creates a new atom ... The atom has no printing name", PDSS manual). The number is OURS: a counter up from 10000h, clear of the image's 486 atoms. PDSS counts down from the top of its table; PIM/m gave each processor a range (`supply_atom_number`, the server in `pimos::top`) whose first value is not known | checked (`lockstep_atab.py`): one atom per name, none of the image's |
| `hash` | `22:F6 x y z` | `hash(X, ^Value, ^NewX)`: "unifies Value with a hash code computed according to X, and also unifies NewX with X" (PDSS manual); waits for X. The code is PDSS's (`emulator/blt_system.c` `blt_b_hash`): an atom's or integer's value, -1 for a list, a vector's size, a string's word count plus a mix of its first and last words. PIM/m's function is lost with the firmware: any function gives a correct table, so WHERE an entry lies in a hashed table is not the machine's. Long vectors and other types are refused | run on strings (the IPL's atom table); a constant function in both models passes the test, as it must |
| `floating_point_equal`, `_not_equal`, `_less_than`, `_not_less_than` (guards) | `23:FC`, functions 0-3: `y z` | numeric IEEE single comparison of two FLT words (so +0.0 equals -0.0); an unbound input is noted, a non-float fails ("Fail, Exception", the KL1 manual). `docs/float.md` | `lockstep_float.py` (cmp0-3) |
| `floating_point_to_integer`, `integer_to_floating_point` (guards) | `23:FC`, functions 4, 5: `y z`, the result in r[z] | truncation toward zero, failing outside [-2^31, 2^31) or on inf/NaN; integer to single, round to nearest even (INFERENCE: no source states the mode). `docs/float.md` | `lockstep_float.py` (toint, toflt) |
| `floating_point_add`, `_subtract`, `_multiply`, `_divide` (guards) | `23:FD`, functions 0-3: `y z`, two cells, the result register the second cell's top byte | IEEE single, round to nearest even; overflow gives the infinity, x/0 the infinity of the signs; inf-inf, 0*inf, 0/0, inf/inf fail. `docs/float.md` | `lockstep_float.py` (arith0-3) |
| the body forms of the above | `22:CE` functions 0-1, `22:CF` functions 0-3 | as the guards; an unbound input or an exception is refused loudly (no stub; not modelled) | `lockstep_float.py` (body0-3, btoint, btoflt) |
| `set_constant` | `23:10 x`, two cells (`c8_c40`) | goal argument x becomes the whole next cell (a float: PDSS `compiler/outp.kl1`:432) | `lockstep_shell.py` APPS `float_klic` |
| `new_module` | `22:D6 x y` | `new_module(Vector, ^Module)`: `r[y]` := `{MOD, a}` -> `{CDESC, 06 << 24 \| n}` and the vector's other n elements as they are, the shape of the image's 20 modules. `library/loader/loader.kl1`: "First Element is for CDESC created by new_module"; its caller puts `06000000h \/ (size - 1)` in element 0. A copy on both models (whether the machine converts in place is not known). A reference to a variable is kept (the loader leaves one where another module will be). Refused: an element 0 that is not that integer, an unbound cell in the vector itself | checked (`lockstep_newm.py`); the refusals are NOT run |
| `set_atom` N | `23:00`..`0F`, atom in the low 24 bits | goal argument N := the atom (`assembler/inst_tab.kl1`) | checked (`lockstep_file.py`) |
| `calculate_priority_from_minimum` | `22:ED x y` | `r[y]` := the logical priority for the relative priority `r[x]`, 0..4096, in the shoen's range (manual). No shoen here: the range is taken as 0..4096, so the result is the operand. **The range is ours** | both models agree; nothing reads the value |
| `calculate_priority_from_current` | `22:EC x y` | `r[y]` := the logical priority for the self-relative priority `r[x]`, -4096..4096, "calculated from the logical priority of this predicate" (manual, `e-builtin.tex`); waits for X. The manual gives no formula: **PDSS's** (`emulator/blt_system.c` `blt_b_rltv`: for X >= 0 the current priority plus X/4096 of the way to the shoen's maximum, for X < 0 minus -X/4096 of the way to its minimum), with the range 0..4096 as for `_from_minimum` and the current priority at its top, 4096 (**both ours**; PDSS starts a shoen's goals at its maximum, `emulator/shoen.c`:100,166). So `r[y]` = 4096 + X for X < 0, 4096 for X >= 0, and `shoen:execute/7`'s `C - 4096` gives C back. Outside -4096..4096 (the manual's exception) is refused | checked (`lockstep_prio.py`): at its stub on the ends and middle of the range, one input bound late, and at `shoen:execute/7`, where both its uses wait for their input; nothing reads the value there (`create_shoen` drops it), so it is checked in the trace |
| `system_timer` | `23:78 x y` | `system_timer(^X1, ^X2)`, a guard with no input (`blt.kl1`:287-288): "The upper 16 bits of the time (in 1/16 msec units) that has passed since the processor ... was booted is unified with X1, and the lower 32 bits ... with X2. Suspend, Exception: None" (manual, `e-builtin.tex`:1537-1549); VPIM gives X1 = 0 (`klb_pimos.psl.c` `kblt_system_timer`). **The clock (2026-11-24; it stood at 0 before)**: one tick every 423 instructions executed, counted before the instruction (`pimm.py` `INSTRUCTIONS_PER_TICK`): 615 KLIPS on `append` (`M92` p. 425) at this image's 11 instructions an `append/3` reduction; equal cost per instruction is OURS. `r[x]` := its upper 16 bits, then `r[y]` := its lower 32 | checked on code of the bench (`lockstep_timer.py`, the clock at 0 and at 2 after 1,204 instructions); the real sites (`bios/boot/sysTman.kl1` `create/3`, the stop of `pim:go/4`; `sysTdvc.kl1`) are in the bios file and go on into modules it does not hold: NOT run |
| `set_timer` | `22:FF x y` | `set_timer(Time, ^Wakeup)`, body, Time the input (`blt.kl1`:702-704); VPIM's comment before `kblt_system_timer`: a time already come wakes at once with the timer's value, "T2 is after T1 :- T2 &- T1 < 2^(W-1)". With the clock (`system_timer`'s): (now - Time) mod 2^32 < 2^31 gives Wakeup = now, the clock's lower 32 bits; waits for an unbound Time (its stub). A time still to come (R7L, 2026-11-25) arms the processor's one alarm, as VPIM's `kblt_b_set_timer` (`klb_pimos.psl.c`, ~560-625): an alarm already armed is cancelled first, its Wakeup bound to `[]`; Wakeup is a fresh variable, bound to the timer's low 32 bits when the time comes (`f_WakeupGoalByAlarmClock`, `f_event_external_int.psl.c` ~150-180). When the alarm is checked is OURS: at each goal switch, before the next goal is taken (`pimm.py` `run`, `PimmCore.bsv` `pick_or_fire`, the box `PimmTBox.bsv`); a machine with nothing to run and an alarm armed has its clock moved on to it (the driver's ALARM, `tick_skip`). Not a FEP service: the timer device stays local (`fep_services.md` §3, the start, item 3). 22:FF is ALSO `modname_to_module` in `library/assembler/inst_tab.kl1`:371,373: both models take it as `set_timer`, the site's source (`sysTman.kl1` `create/3`) | checked at its stub (`lockstep_timer.py`: four times reached, one waited for, one reached when the clock is 2; an alarm armed, re-armed (the first Wakeup `[]`), fired by ALARM with the time asked, its waiting goal woken then); in `ts` (APPS, `kernel/task/int_hdl.kl1` `on_after(10000)`) |
| `set_heap_alert` | `22:FD x y` | `set_heap_alert(Size, ^Alarm)`, body, Size the input (`inst_tab.kl1`:367, `blt.kl1`:669-670). VPIM (`interpreter/klb_pimos.psl.c` 163-181, `kblt_b_set_heap_alert` 209-351): when the heap's use (get_heap_size's Used) is past Size, Alarm = the use at once; else the alert is armed with a fresh variable as Alarm, bound to the use at the first goal switch after the use passes Size, after the collection (VPIM tests at each growth of the heap top and binds in the event handler, `f_event_self_int.psl.c` 67-116: the goal switch is INFERENCE); a request while one is armed binds the earlier Alarm to `[]`; Size at or above get_heap_size's Size (`range_overflow`) or not an integer (`illegal_input`) is refused; an unbound Size waits (its stub); the armed Alarm is a root of the collector (VPIM `structures/str_gc_pre_post.psl.c` 2.11). One alert per machine (`heap_alert_var`, `heap_alert_size`), as VPIM's one per PE. **2026-11-27**, the IFS sweep's h907_nseq | reference models alone, one PE and several (`ref_node_alert.py`: at once, armed at Used = Size, cancelled with `[]`, fired one past, waiting on Size, through a collection, the two refusals); not on the core |
| `current_node` | `22:EE x y` | `current_node(^NodeNumber, ^TotalNode)`: "The node number will be a value between 0 and (TotalNode - 1) inclusive" (manual, `e-builtin.tex`); no input (`compiler/blt.kl1`:655), so it never waits and has no stub. **One node here (ours)**: `r[x]` := 0, then `r[y]` := 1, PDSS's values (`emulator/blt_system.c` `blt_b_current_node`) | checked on code of the bench (`lockstep_prio.py`) and at `top:go1/4` (`lockstep_atom.py`: TotalNode 1 throws one atom-number client); `exception_table:translate/2,4` go on to `current_processor` (shoen stage 3) |
| `supply_atom_number` | `22:B9 x y z` | `supply_atom_number(X, Y, ^Done)`: encoding `r_r_r` and directions (in, in, out) **PIM/m-sourced** (`assembler/inst_tab.kl1`:249, `compiler/blt.kl1`:747-750; the debugger's `excpt_tbl.kl1`:639 names `2B9`). **No manual entry; nothing in PDSS, VPIM, the PIMOS source or these docs says what it does** (searched 2026-11-23: PDSS has no such built-in; VPIM's `new_atom` takes a counter initialized to atom 0 and puts the cluster number in the top byte, `interpreter/klb_body_blt_cont.psl.c` `kblt_b_new_atom`, `init_vpim.psl.c`, and nothing supplies it a range). What its callers force (`top:throw_atom_number_client/7`, `atom_number_client/5`, decompiled in `lockstep_atom.py`): X and Y are integers, a block of atom numbers from the server in `pimos::top` (first call `(512, 15872)`; the server answers `(Next + 8192, 8192)` from Next = 16384 to the limit 2^24); Done is waited for, and each binding makes the client ask for another block, so the machine binds it LATER, not at once (at once, the client would ask to the limit). NOT forced: whether X is a block's first number or its end (the first call fits the one, the server's answers the other, its near-limit answer neither), so which numbers a processor hands out is not inferred. **OURS, the narrowest**: the inputs are waited for, must be integers and are dropped; Done is a fresh variable no model binds, consistent with `new_atom` (ours, a counter from 10000h that draws on no block). So `top:go1/4`'s clients never start unless something binds Done | checked (`lockstep_atom.py`: `top:go1/4`, the bench binding Done twice in the machine's place; three calls with the values above); a non-integer is refused, NOT run |
| `enqueue_goal_with_priority` | `23:64 x`, label; arity in the next cell's top byte | as `enqueue_goal`, two cells (`assembler/klb_opr.kl1` `p(r_c16_c8_exe)`; the image's five sites agree with their `set_*` count). `r[x]` must be an integer and is **dropped**: one ready queue here, a goal stack per priority on the machine, so the order goals run in is not the machine's. More than 11 arguments: on the reference models since **2026-11-27** (the IFS sweep's H9-07, a goal of 12 with `@priority(3000)`) the vector of those from the 11th on is spread as `enqueue_goal` spreads it: the compiler packs a goal with a pragma as it packs a plain one (PIMOS `library/compiler/newnorm.kl1` 907-909, `pack_body_goal` before `normalize_with_pragma`; the arity is the unpacked goal's, 893-901). The Bluespec core still refuses more than 11 (`PimmStages.bsv`, `E unimp`): no lockstep reaches it | checked (`lockstep_file.py`); 12 arguments on both reference models (`ref_prio_list.py`) |
| `enqueue_goal_to_processor` | `23:65 x`, label; arity in the next cell's top byte | `Goal@processor(N)`: as `enqueue_goal_with_priority`'s operands (`assembler/klb_opr.kl1` `p(r_c16_c8_exe)`), `r[x]` the processor (TM-1044 `enqueue_to_processor(.., Rprocessor, ARITY)`, as listed in `literature_gaps.md`). **One processor here, number 0 (ours)**: for 0 the goal is made as `enqueue_goal` makes it. On the reference `pimm.py`, since **2026-11-27** (the IFS sweep's mgtp_n, mmi, H9-07, multialign), any integer makes the goal here, as the single-processor systems do (PDSS `compiler/outp.kl1` 360-363, `doc.e/pdss.tex` 71-72; KLIC on one node, `runtime/sched.c` 277-289): a DECLARED DIFFERENCE, OURS, from PIM/m's `range_overflow` (`e-shoen.tex` 491-514), which `pimm_pe.py` keeps (`ref_node_alert.py`); the core refuses any number but 0, a non-integer is refused on both. **An unbound number is waited for: carried over from VPIM, agreeing with KLIC; the PIM/m firmware's behaviour is not held** (VPIM `src/interpreter/klb_fork.psl.c` `klb_enqueue_to_processor`, 406-447: a D-code goal `dcode_enqueue_processor(Processor,Code,Argv) :- integer(Processor) \| dcode_apply(Code,Argv)@processor(Processor).` hooked on it; KLIC `runtime/sched.c` 267-330; PDSS drops the number at compile time, `compiler/outp.kl1`:360-363). OURS: the goal's arguments, then P, then the code address, in a suspended goal of the stub `to_processor N, N+1, N` (22:02, `asm/pimm_stubs.py` `TO_PROCESSOR`, N up to 11, as `enqueue_goal`'s; 9 until a goal of 10 arguments was met, 2026-11-24) hooked on P; it waits again while P is unbound, makes the goal ready at 0 | checked (`lockstep_body.py`, `scsi_fep_module:create/7`: the goal runs `$bar2/2` into `scsi:create/2`, which waits for its first argument and fails on a non-integer); the wait at the one site of `pimm_patch_scsifep360E.sav` (`lockstep_tproc.py`: P unbound, then 0; P bound to another variable, then 0); the refusal is NOT run |
| `read_eagerly` | `23:6B` | what the compiler writes for `alternatively.` (`compiler/indexornot.kl1` `compile_one_block`). The clauses after it are tried "not only when the first clause fails but also when it suspends" (TR-483 2.4.4); the instruction: "if external references are on the suspension stack, perform Eager Read on them", no branch (TM-1044 s3; both quotations from `literature_gaps.md`, the reports not reopened). One processor has no external references: **nothing is done**; the variables noted so far stay noted | checked (`lockstep_alt.py`): `scsi_fep_util:set_attention/1`, `close_attention/1`, `close_device/2`, and `scsi_fep_file:reply_with_attention/4`, where a goal reaches `suspend` past it with the variables the earlier clauses noted and suspends (an injection that forgets them is caught there) |
| `scsi_init` | `22:DF x y z` | `scsi_init(^Obj, ^TargetInterruptVector, ^Info)`, three outputs (`compiler/blt.kl1`). **The values are OURS**, those of the stand-in `bios/scsi/scsi_blt.kl1` (in the image at cell 13952): `1`, `{0,0,0}`, `{16000,8,4,0}`. `Info` element 0 is the largest transfer; `scsi_fep_module` makes its two packet buffers that long. The 16000 is the DEVICE's (`fep.py` `MAX_BUFFER`): it is asked (the trace's `B init`), and on the core comes over the port (`bsv/PimmScsiBox.bsv`). Order: `Obj` written, the device asked, then each vector's cells and its register. Refused without a device (`Machine.fep`; on the bench, no tape) | checked (`lockstep_scsi.py`, at its site `scsi:create/2`, the device's size 1000); `ref_scsi.py` on the reference |
| `scsi_command` | `22:DB`, seven registers (four in the next cell) | `scsi_command(Obj, {Unit, LUN, CDB, Length, Dir, Buffer, 0}, ^Data, ^TransferredLength, ^Id, ^Result, ^NewObj)` (`compiler/blt.kl1`). From its callers (`scsi:command_executer/2`, `scsi_processor`, `scsi_common`): Dir 0/1/2 = none/out/in, `Result` 0 = success, `Data` the whole buffer again (the caller's next buffer) with what was received written in. **OURS**: it waits for every element of the vector, as `string_operation` does (the stub's goal on the first unbound one); `Id` counts commands; `NewObj` = `Obj`; `Data` for bytes received is a NEW 8-bit string as long as the buffer (the bytes, then the rest of the buffer's, pad zero), for none the buffer itself; `TransferredLength` is the bytes received for Dir 2, else `Length`; a command the device cannot finish yet gives `Id` and `NewObj` at once and leaves the other three as new variables, unbound until the device has the reply; the waiting commands are held outside memory (Python's list; the core's box, at most four), given to the device again after any command that finishes (before its outputs are written) and when the machine has run dry (`Machine.scsi_poll`; the script's `POLL`), oldest first, a finished one's three variables unified in order. Every try is one `B` line (Trace). The device is `ref/pimm/fep.py`; on the core it is outside, on a port. Refused: a vector not of seven, a seventh element that is not 0, a length over the buffer, a CDB or buffer not of 8-bit elements | checked (`lockstep_scsi.py`: at its site `scsi:command_executer/2`, TEST UNIT READY, SEND, RECEIVE, a reply cut in two, a command that waits finished inside a SEND and one at a poll, an element waited for; the refusals NOT run). `ref_scsi.py`'s six IPL parts in lockstep too (`lockstep_scsi.py --part 1..6`: the IPL's own file service, the waiting path at 7 polls in "late"). Injections in both tests' headers |
| `b_string` | `22:CB x y z`, fourth register in the next cell | body `string(X, ^Size, ^ElementSize, ^NewString)`: "The size of string X is unified with Size, the element bit width is unified with ElementSize, and X is unified with NewString" (PIMOS manual, `e-builtin.tex` line 844; directions in `compiler/blt.kl1`) | checked at its stub (`lockstep_body.py`: 8-, 16- and 32-bit strings, the empty string, an unbound X) and at three of its five real sites (`lockstep_elw.py`, `scsi_fep_module:send_last_packet/9` and `copy_str8_elements/7`) |
| `b_divide`, `b_modulo` | `22:C3`, `22:C4 x y z` | `divide` and `modulo` in a body (manual, `e-builtin.tex` lines 285, 303: quotient, remainder), the guards' arithmetic (truncation towards zero, the dividend's sign: PDSS's, not established for PIM/m); a zero divisor is the built-in's exception, refused | checked (`lockstep_body.py`): `scsi_fep_module:str8_to_msg/3` on replies whose string is not last (a wrong quotient misplaces what follows), `str16_to_str8/2` on even and odd lengths, and eleven signed pairs at the stubs with the answers written out; the refusals are NOT run |
| `not_equal` | `23:F3 x y` | guard `not_equal(Integer1, Integer2)`, `X =\= Y`: "Succeeds if Integer1 is not equal to Integer2" (manual, `e-builtin.tex` line 206) | checked on integers, succeeding and failing (`lockstep_alt.py`, `scsi_fep_file:reply_with_attention/4`, its only site in the image); an unbound or non-integer operand is NOT run |
| `wait_vector_0` | `23:A8` | as `wait_vector_2`: `r[x]` is the empty vector `{}` (nothing is read after it) | checked on five cells of code the bench writes (`lockstep_alt.py` part vector 0: `{}`, a variable waited for, `{5}` failing); its real sites (`scsi_fep:receive_packet2_1/8`, `receive_packet3/8`, the stop of `pim:go/4`) go on into `builtin#substring`, a module the loaded file does not hold: NOT run |
| `wait_vector_1`, `_4`, `_6` | `23:A9`, `23:AC`, `23:AE` | as `wait_vector_2` | checked (`lockstep_alt.py`): 4 in `scsi:request_manager/3`, with the wrong size; 6 in `scsi:command_executer/2` up to its `scsi_command` (passing with an unbound first element, failing on the size); 1 has NO site in the IPL image and is run on six cells of code the bench writes into the heap |
| `merge` | `22:F0 x y` | `merge(In, ^Out)` "creates a built-in constant time merger" (manual); as compiled the first operand is the OUTPUT stream as given, the second receives the input (`compiler/blt.kl1`). **Not the machine's merger**: PIM/m's input is a cell of its own tag (`MGHOK`) pointing at a record {output}{number of inputs} (TR-466 3.3) and acts at unification; here the input is a variable with a goal waiting on it, whose code is the stub `merge_in` (`22:00`, ours, an opcode the firmware's decode table leaves empty; refused elsewhere), and the output appears after a goal switch. **The merger's list (decided 2026-11-24, both models)**: VPIM (`f_reduce_merger_unify.psl.c`, the `MGHOK` cell), KLIC (`runtime/gmerge.c`) and PDSS (`emulator/unify.c`, `active_unify_stream_list`) all pass a list bound to a merger input on to the output AT the unification, so messages reach the output in the order their inputs were bound, before anything the binding reduction spawned runs. Here a woken goal of `merge_in` goes on the merger's list instead of the ready queue; at each pickup the goals woken since the last one go to that list's front in the order they were woken, and the list is taken before the ready queue. Acting at the next goal switch rather than inside the unification is OURS (the binding reduction's own remaining instructions run first). The three sources split on a VECTOR bound to an input (VPIM connects unbound elements at once and sends bound ones through a goal, last to first; KLIC hooks elements 0..n-1 at once; PDSS makes a goal per element): left as it was, each element's goal goes on the ready queue (`record`, READY), as do parked goals (`start_shoen`, release). Until 2026-11-24 a woken `merge_in` went on the ready queue, newest first, so two inputs bound in one step passed on in the reverse order; with a typed `shutdown` that ordered two requests to the user table against the order they were sent and the run stopped in a wait cycle (`binary_reverse_engineering.md` 1.4, "A command typed"). The logic is the manual's. A vector on the input adds as many inputs as it has elements ("When a vector is unified to an MHV, as many input streams (MHVs) as the arity of the vector are added to the merger process and each element of the vector is unified to each new input stream", TR-466 3.3): the input that was bound ends, the count goes up by the size less one (the empty vector only ends the input), and each element gets a ready goal of `merge_in`, the last element's newest. Each goal is made through the argument registers (a1 the element, taken with its MRB on, a2 the record), as `enqueue_goal` makes one; **decided 2026-11-23** (until then the reference wrote these records straight from cells, which the core's goal box cannot, and the core refused the case): the reference changed, the goal box did not, and the merger box got `spread` beside `close`. A vector of seven or more (**2026-11-25**, met by the compiler on the primer's sample1, two vectors of 9): the same, its size and first element from its descriptor (`vsize`/`vbase`; the core's `vbox.info`, rule `mergeVecL`); no source bounds the arity (TR-466 3.3 "as many input streams as the arity"; KLIC `runtime/gmerge.c`:81-104 any size; VPIM `f_Unify_MGHOK_VECT_Sub` takes a long vector, with a WARNING at :1499-1500). Refused: an output that is not a variable, a non-stream | checked against a dictionary through `ipl_pool:keyed_set/2` (`lockstep_pool.py`); the order of two and three inputs bound in one step, through the same pool (`lockstep_merge.py`, which the rule before 2026-11-24 fails; its `seven senders` part a vector of seven, one element unbound and one `[]`); the vector at the image's `top:throw_atom_number_client/4` (`C = {E, F}` on `top:go1/4`'s merger, `lockstep_atom.py`: count, the two inputs, the server's input exactly the client's two requests and closed); also run by `ref_scsi.py` (`scsi_fep_general:request_device_io/5` binds two merger inputs to `{J, K}`, 39 vectors of two); the refusals are NOT run |
| `put_vector_0` | `23:38 x` | `r[x]` := the empty vector `{VECT0, 0}` | checked (`lockstep_pool.py`) |
| external call from a LOADED module | as above | the descriptor's module field is dereferenced to the module object `{MOD, descriptor cell}`: in the image through the module table, in a module the IPL loaded through the variable its linker bound (`ipl_link_table:unify_modules/1`). Checked on the image by `lockstep_ext.py`; on a loaded module by `lockstep_xmod.py` (both models): `pimm_patch_mkdir360E.sav` loaded by the IPL's `load/4`, whose link is abnormal, so the bench binds one module variable as `unify_modules/1` would (through a variable of its own: two references), and the `enqueue_goal_external` at cell 674183 reaches `filereq_filter`'s predicate where the file's index table puts it. No test has two loaded modules linked by the IPL itself: the smallest closed set of files is some 49 M cells |
| `set_nil`, `enqueue_goal_external` | `23:12 n`; `23:66 n`, label | goal argument n := `[]`; `enqueue_goal` with the predicate found as `execute_external` finds it (`klb_opr.kl1` `p(c8_c16_ext)`) | checked (`lockstep_load.py`) |
| `string_operation` | `22:B0 x y z`, fourth register in the next cell | `string_operation(Op, Vector, ^NewS1, ^NewS2)`, what the compiler makes of `binary_string_operation` with `Vector = {Pos1, Str1, Len, Pos2, Str2}` (`compiler/blt.kl1` `specialPredicate`): operation Op (0..15, the manual's table) on Len elements; NewS1 is a copy of Str1 with them replaced, NewS2 is Str2. An element of the vector that is not yet a value is waited for, as an operand is (the manual says the built-in waits; `builtin_utility:append_string/2` needs it): the goal of the stub waits on the first such element in order, and tries again when woken (checked, `lockstep_elw.py`: `scsi_fep_module:send_last_packet/9`, `append_string/2`, and the elements bound out of order at the stub). The vector of three is the unary form, `unary_string_operation(Op, Str1, Pos1, Len, NewS1)` as `{Pos1, Str1, Len}` with NewS2 a new variable of the compiler's (`compiler/blt.kl1`:937-939): VPIM's `f_UnaryStringOpe_Sub` (`functions/f_reduce_string_ope.psl.c`:1206-1229) is the binary operation with Str1 and Pos1 in place of the second string's, so each element becomes op(e, e); NewS2 gets Str1 (OURS; 2026-11-25, the compiler's `reg.kl1` register masks). Refused: the vector of four (shifting), the exceptions | checked for operation 3, the IPL's (`lockstep_load.py`); 7 and the unary 0, 10, 15 on 1-bit strings and 10 on an 8-bit one, and the unary form waiting on its Len (`lockstep_s1.py`); the others are NOT run |
| `change_element_size` | `22:DA x y z` | to 8, 16 or 32 bits, from 1, 8, 16 or 32 (a change to 1 bit refused): "the smallest index element occupies the highest order bits", widening pads with zeros (manual). The same words under another descriptor; 32-bit strings are type 5, no padding (`kbnheap.kl1` `string_cdesc`) | checked for 16 to 32 (`lockstep_load.py`) and 1 to 8 (`lockstep_s1.py`); narrowing and a padded result are NOT run |
| `string_element` (guard), `exclusive_or` (guard), `b_exclusive_or` | `23:EF x y z`, `23:EC x y z`, `22:C9 x y z` | element, or the guard fails outside the string; exclusive or | checked (`lockstep_load.py`): the IPL's checksum over a real file comes to 0, and to an error with one word altered |

| `write_integer` | `23:21`, integer in the low 24 bits | store the integer at the structure pointer and advance it. The 24 bits are SIGNED: the PIMOS assembler writes a constant in -2^23..2^23-1 in this c24 form masked to 24 bits, any other in the two-cell c40 form (`library/assembler/klb_opr.kl1` `p(c24, ..)` 50-54, `p(c40, ..)` 60-81) | checked for 35 (`lockstep_modc.py`) and for -1 at `scsi_fep:check_data_size1/6`, `L = [-1\|NL]` (`lockstep_wint.py`, a loaded patch file) |
| `write_marked_variable` | `23:26 x` | as `write_variable`; the variable is referenced more than once, so `r[x]` gets `REFx` | the write and the register are checked (`lockstep_modc.py`) |
| `b_multiply` | `22:C2 x y z` | `r[z]` := `r[x]` * `r[y]`; a non-integer or an overflow is the built-in's exception (manual, `multiply`), not modelled: both models stop. On the Bluespec a 32-step shift-and-add multiplier in `PimmMBox.bsv`; the count is ours | checked for N * 2, N at most 15 (`lockstep_modc.py`); large or negative operands and the overflow are NOT run |
| `put_atom` | `23:40`+r, atom in the low 24 bits | `r` := the atom; the register is the opcode's low five bits, as for `get_atom` | checked for register 0 only (`lockstep_gca.py`): a wrong register field is NOT caught |
| `write_value` | `23:25 x` | store `r[x]` at the structure pointer and advance it | checked |
| `write_variable` | `23:24 x` | the element at the structure pointer becomes a new unbound variable, `r[x]` a reference to it; advance | checked with `x` = 31 only (`analyze_standard_format/5`): the cell and the register are in the trace, nothing reads the register. That the variable is the element itself is our choice. *2026-11-26: the held firmware (`3195`-`3199`, executed by `ref/pu/check_pu.py`) takes a new cell from the one-cell free list, makes it `UNDF`, and writes `{REF, cell}` at the structure pointer and into `r[x]`: the same term after dereference; this model is not changed* |
| `switch_on_non_list` | `23:2A x`, label | guard: `r[x]` a list, the structure pointer is set to its car; otherwise go to the label (an unbound `r[x]` is noted first) | checked (`shoen:ground_term/2`). |
| `switch_on_non_vector` | `23:2B x y`, then a cell holding the label | a vector: `r[y]` := its number of elements (the compiler's `index.kl1` calls the register `Ari` and switches on it), the structure pointer at its first; otherwise go to the label (an unbound `r[x]` is noted first) | checked (`shoen:ground_term/2`) |
| `vector` | `23:E4 x y` | guard `vector(X, ^Size)`: `r[y]` := the number of elements | checked |
| `vector_element` | `23:EE x y z` | guard `vector_element(V, I, ^E)`: `r[z]` := element `r[y]`, a reference if it is an unbound variable; fails outside 0..size-1 | checked, except the index equal to the size |
| `mark_element` | `23:1C x y` | the MRB of element `r[y]` of the vector `r[x]` is set, in the vector (PDSS `KL1B_MARK_ELEMENT`); both registers are dereferenced; a cell that is itself an unbound variable is left. On a list cell (R9, 2026-11-26) `r[y]` = 0 is the car's cell and 1 the cdr's (HELD-SOURCE: PIMOS's compiler emits `put_constant(0/1, Rpos), mark_element(Rlist, Rpos)` for a car/cdr the body refers to, `library/compiler/body.kl1`:437-460; the list's two cells at its address, as a short vector's, is INFERENCE from the firmware routine `30a9` having no room for a tag dispatch; PDSS indexes vectors only, VPIM deleted the instruction); another position on a list is refused | checked (`lockstep_ptab.py`: the cell write); on lists, the MGTP rows of `lockstep_shell.py` APPS |
| `new_vector` | `22:D3 x y` | body `new_vector(Size, ^V)`: `r[y]` := a vector of `r[x]` cells of integer 0 (PIMOS manual) | checked for 1..6 |
| `set_vector_element` | `22:D0 x y z`, then `w4 w5` | body `set_vector_element(V, I, New, ^Old, ^V1)`: `r[w5]` := `r[x]` with element `r[y]` replaced by `r[z]`, `r[w4]` := the old element. Does not wait for `New` (manual: suspends on Vector or Position only). In place, `r[w5]` being `r[x]`, when the vector is reached with every MRB off; otherwise a copy (see "The MRB") | checked on vectors made by `new_vector`; both ways, by address and content, in `lockstep_mrb.py` |
| `put_nil` | `23:32 x` | `r[x]` := nil, the atom 0 (`library/kbn/kbnatom.kl1`: "The atom number of '[]' is fixed to zero") | checked |
| `wait_vector_N` | `23:A8+N x` | guard: `r[x]` is a vector of N cells; the structure pointer is set to its first | checked for N = 2, 3, 5 (`exception_table:replace_argument/3`), including the wrong size and an unbound `r[x]`; for 1, 4, 6 see the row `wait_vector_1`, `_4`, `_6` above |
| `read_variable` | `23:B4 x` | `r[x]` := the element at the structure pointer; advance. An element that is an unbound variable is taken as a reference to it | checked |
| `put_reused_structure` | `23:2F x y n` | `r[x]` := a structure of n cells to fill with `write_*`, under the tag of the structure in `r[y]` | checked for vectors of 2, 3, 5; a vector of seven or more gets a descriptor of its own (checked, `lockstep_reuse.py`: `scsi_fep_file:request_device_io/6` rebuilding `{201, ...}`, the image's one such site; fewer than seven cells under a long vector's tag is refused by both models, NOT run). The machine reuses `r[y]`'s cells when nothing else refers to them (MRB); the models keep no reference counts and always take new cells, which is what the machine does for a shared structure |
| `get_bound_value` | `23:BD x y` | unify `r[x]` with `r[y]` (as `get_value`; the name says `r[y]` is known to be bound) | checked for a vector against an unbound variable |
| `b_and`, `b_or` | `22:C7`, `22:C8 x y z` | `r[z]` := `r[x]` and / or `r[y]`, bitwise | checked (`scsi_common:get_4_bytes/4`) |
| `b_shift_left` | `22:C5 x y z` | `r[z]` := `r[x] << r[y]`, 32 bits | checked for a count of 8; a count outside 0..31 is an exception in PDSS (`blt_basic.c`) and stops the model |
| `b_shift_right` | `22:C6 x y z` | `r[z]` := `r[x] >> r[y]`, logical (manual, `shift_right`: "Logically shifts Integer to the right"), 32 bits | checked (`lockstep_dec0.py`), logical against arithmetic by the 8-bit strings of `lockstep_deca.py`; a count outside 0..31 is an exception, not modelled |
| `shift_right` (guard) | `23:E9 x y z` | `r[z]` := `r[x] >> r[y]`, logical; an unbound operand is noted and the guard fails; a non-integer or a count outside 0..31 fails the guard (manual: "Fail, Exception") | checked, logical against arithmetic included (`lockstep_rss.py`); the count limit is not run |
| `integer` (guard) | `23:E2 x` | succeeds if `r[x]` is an integer; unbound is noted and fails (manual: suspend), anything else fails | checked, except the unbound case (a `wait` always precedes it) |
| `modulo` (guard) | `23:F8 x y z` | `r[z]` := remainder of `r[x]` by `r[y]`; an unbound operand is noted and fails; a non-integer or a zero divisor fails the guard (manual: "Fail, Exception"). The remainder takes the dividend's sign, as PDSS's C `%` (`emulator/blt_basic.c`): for negative operands that is PDSS's behaviour, not established for PIM/m. On the Bluespec the divide box takes 32 steps; the count is ours | checked for a small positive length mod 2 only (`lockstep_deca.py`); negative operands and the zero divisor are NOT run |
| `put_vector_1`, `_5`, `_6` | `23:39`, `3D`, `3E` | as `put_vector_2..4` | `_5` checked; `_1`, `_6` not run |
| `put_list` | `23:2E x` | two new cells, car then cdr, filled by the two `write_*` that follow; `r[x]` := a list pointer to them | checked (`lockstep_dect.py`) |
| `put_constant` | `23:30 x`, then a cell | `r[x]` := the whole next cell (`klb_opr.kl1` `r_c40`); two cells | checked for an integer constant (`lockstep_deca.py`); the tag being carried is NOT checked |
| `get_nil` | `23:BA x` | unify `r[x]` with `[]` (the atom 0) | checked |
| `wait_atom` | `23:80+r`, atom in the low 24 bits | guard: `r` dereferenced must be that atom; unbound is noted and fails | checked |
| `get_value` | `23:BC x y` | unify `r[x]` with `r[y]` | checked for integer against unbound only |
| `get_integer` | `23:B9 x c16` | unify `r[x]` with integer `c16` | checked against unbound only |
| `otherwise` | `23:6A x c16` | clauses below apply only if none above can: if a guard above was waiting on a variable, the goal suspends; else continue | both cases checked. `x` is the arity and the label is the predicate's own first instruction; what the machine uses them for is inferred (re-entry after suspension) |
| `suspend` | `23:69 x c16` | end of the clauses: suspend if a guard was waiting, else the reduction fails. Same operands as `otherwise` | suspension checked; the failure case inferred |
| `collect_value` | `23:1D x` | reclaim what `r[x]` refers to (MRB) | not modelled: a no-op in the reference model |
| `proceed` | `23:60` | the goal is done; the machine takes the next ready goal | checked |
| `wait` | `23:E0 x` | guard: `r[x]` is bound; if not, note the variable and fail to the next clause | both cases checked |
| `wait_integer` | `23:A1 x c16` | guard: `r[x]` is the integer `c16` | checked (0 ends `convert_loop`; 16 selects 16-bit strings) |
| `less_than` | `23:F0 x y` | guard: `r[x] < r[y]` | weakly: the only use is `0 < N` after `N = 0` has been tried |
| `subtract` | `23:F5 x y z` | guard arithmetic: `r[z]` := `r[x] - r[y]` | the run cannot tell (the only use has `x = z`); the destination is from the compiler's table, `asm/bltdir.py`: `iio` |
| `string` | `23:E5 x y z` | guard `string(S, Length, Size)`: `r[x]` is a string; `r[y]` := its length, `r[z]` := its element size in bits | checked |
| `put_value` | `23:34 x y` | `r[x]` := `r[y]` | checked |
| `put_marked_value` | `23:36 x y` | `r[y]`'s MRB is set, then `r[x]` := `r[y]` (TR-248: "for reference duplication"; PDSS marks the source first) | checked: both register writes are traced |
| `put_variable` | `23:33 x y` | `r[x]` and `r[y]` := one fresh unbound variable | checked |
| `set_value` | `23:14 x y` | argument `x` (from 1) of the goal being built := `r[y]` | checked |
| `set_variable` | `23:13 x y` | argument `x` of the goal being built and `r[y]` := one fresh variable | inferred from `ipl:boot/0`; not yet executed |
| `set_marked_variable` | `23:15 x y` (c8_r, `inst_tab.kl1`:18) | as `set_variable`, a new variable for goal argument x and r[y], both references with the MRB on (PDSS `emulate.c` `KL1B_SET_MARKED_VARIABLE`: `SetAll(arg, REF, undef, MRBON)`, the register a copy), as `put_marked_variable` | checked on six cells of the bench (`lockstep_alt.py` part marked variable, 2026-11-24) |
| `enqueue_goal` | `23:63 x c16` | make a goal of the predicate at the label with the `x` built arguments and put it on the ready queue | checked. That the newest goal runs first is the model's choice, not established |
| `execute` | `23:61 x c16` | continue as a reduction of the predicate at the label, arguments already in `r[0..x)` | checked |
| `new_string` | `22:D4 x y z` | `r[z]` := a new string of `r[x]` elements of `r[y]` bits: 1, 8, 16 or 32 (the manual allows 1 to 32; VPIM takes 1, 8, 16 and 32, `klb_body_blt_struct.psl.c` `kblt_b_search_character`; others are refused). A 1-bit string is type 0 with a five-bit pad, (32 - Len mod 32) << 27 (`kbnheap.kl1` `string_cdesc`:168-169), element 0 the top bit of word 0 (2026-11-25) | checked (`lockstep_s32.py` for 32; `lockstep_s1.py` for 1: set, read, string/3, search, the operations, change to 8, lengths 0, 32 and 40) |
| `module_element` | `22:F7 x y z` (r_r_r, `inst_tab.kl1`:356) | `module_element(Module, Position, ^Element)`: `r[z]` := the cell Position + 1 after the module's descriptor, 0 <= Position < the descriptor's count (the unloader writes the descriptor, then element 0, the GC size, `kbn.kl1` `encode_module`:140-158; `modutil.kl1`:52-67 reads 1 as the name, 2 as the package). VPIM `klb_body_blt_cont.psl.c` `kblt_b_module_element`: Position out of range or Module not a module is the built-in's exception: refused. 2026-11-25, met compiling the primer's sample1 | checked (`lockstep_melem.py`: three image modules against `asm/kbndis.py`'s table, a `new_module`'s, a Position waited for, one past the end refused) |
| `b_string_element` | `22:CD x y z`, next cell `w << 24` | `r[z]` := element `r[y]` of string `r[x]`; `r[w]` := the string | checked |
| `set_string_element` | `22:D1 x y z`, next cell `w << 24` | `r[w]` := string `r[x]` with element `r[y]` set to `r[z]` | checked, including the case that matters: `r[z]` unbound when the instruction is reached |

**A body built-in whose input is unbound waits.** In `convert_loop/4`
the compiled order is `string_element`, `set_string_element`,
`enqueue_goal convert_loop`, `execute convert_element`: the element
that `set_string_element` stores is still unbound when it is reached.
The built-in becomes a waiting goal, its output register gets a fresh
variable, and it runs when `convert_element` binds the element. The
test counts one such wait per string element (201). How the machine
represents the waiting built-in is not known; PDSS's
`body_builtin_suspend` (`emulator/goal.c`) is the nearest description.

**Vectors and terms.** A vector of 1 to 6 elements is `{VECTn,
address}` pointing at its n element cells, with no header; the empty
vector is `{VECT0, 0}`; 7 or more have a descriptor (`{VECT, a}` ->
`{VDESC, a+3}`, `{INT, n}`, `{INT, n}`, elements). A list cell is
`{LIST, address}` -> car, cdr. This is `library/kbn/kbnheap.kl1`
`heap/10`, the code that lays out the image's constants. A compound
term `f(a, b)` is the vector `{f, a, b}`: `check_completion_code`
builds `abnormal(no_status(C, D))` as a 3-vector inside a 2-vector, and
the test reads it back by atom name. Vectors of up to 6 are built, read
and updated (`put_vector_N`, `wait_vector_N`, `read_variable`,
`new_vector`, `set_vector_element`; `bsv/PimmVBox.bsv`), and list cells
are read and rebuilt (`switch_on_non_list`, `put_reused_structure`);
the long form (7 or more) is made, read and updated by the same
built-ins since `lockstep_deca.py`. Its layout has that one source
(the image holds no long vector); why the length is there twice is not
known, and both models read the first and write both. The guard `vector` on a long vector is checked by `lockstep_gca.py`
(every module's information vector has 8 elements);
`switch_on_non_vector` on one is written but NOT run; unifying two long vectors is not modelled.

**Strings.** `{STRG, address}` points at `{CDESC, pad << 27 | type <<
24 | words}` and then `words` 32-bit cells, elements packed from the
top bit; type 3 is 8-bit elements, 4 is 16-bit (`kbnheap.kl1`
`string_cdesc`). The packing is checked against the image itself:
`test_jtoa.py` reads the IPL's message strings with it ("Illegal IPL
File", "Unable to Decode Constant").
The reference model copies on `set_string_element`; the machine may
update in place when the string is singly referenced.

## Trace

Both models can write the same trace, one line per event, and are
compared on it (`ref/pimm/lockstep_jtoa.py`, `bsv/run_pimm_lockstep.sh`):

    I pc cell      an instruction is taken (pc in cells from the load
                   address; cell = tag and value, ten hex digits)
    R n cell       register n is written
    A n cell       argument register n (of the goal being built) is written
    M addr cell    a memory cell is written
    E how          the reduction ends: done, fail, susp
    G addr         the goal record at addr is taken from the ready queue
    W addr         the suspended goal at addr is woken
    Q              the ready queue is empty
    C cell         display_console is given this value
    S cell         ... and, for a string, each of its cells: the
                   descriptor, then the words
    B init         scsi_init asks the SCSI device its buffer size
    B u l cdb d n [bytes]
                   a SCSI command is given to the device (each try:
                   a command that waits is given again by each poll):
                   unit u, LUN l, the CDB's bytes in hex, direction d
                   (0 none, 1 out, 2 in), length n, and for a SEND
                   (d = 1, n > 0) the n bytes sent, in hex
    K gc lo hp to top sum
                   a garbage collection (R7G, ref/pimm/pimm_gc.py,
                   INFERENCE/OURS) at a goal switch: the old heap
                   [lo, hp), the new [to, top), from the load address,
                   and an FNV-1 checksum of the new heap's cells (tag,
                   then value); its own writes are not traced.  Asked
                   by collect_garbage, or (stage 5) by an allocation
                   that takes hp - lo past the heap limit less 4096
                   (Machine.heap_limit, RESTORE 5; pimm_gc.py "When
                   memory runs out"); the request itself has no line

Every register and memory write is traced, whoever makes it: an
instruction, the scheduler taking a goal, a wake-up, or the bench
making a variable or a goal. In the Bluespec the `M` line is printed
where the write reaches the RAM, not where it is requested. The
Bluespec core can also end with `E unimp` (an instruction or case it
does not implement) or `E error`; the reference model raises an
exception there, so neither can appear in a matching trace. The trace
has no cycle numbers: the two models agree on what happens and in what
order, not on when.

The SCSI device is not in either model's trace: on the reference it is
`ref/pimm/fep.py`, and on the bench the answers it gave, recorded while
the reference played the same script (`Machine.scsi_tape`) and written
after the script as a tape (`ref/pimm/driver.py` "The device tape":
the buffer size, "not ready", or Result and the bytes received). The
Bluespec bench prints each `B` line from what the core put on its port,
the reference from what it gave its device, so the bus is compared and
only the answers are replayed. "Not ready" is the device's answer at a
try, so a command waits at the same point on both; the dry-machine
poll is the script's `POLL`, placed where the reference ran dry with a
command waiting.

## The MRB

The low tag bit of a reference or pointer (tags 04h to 1Fh; `REFo` 06,
`REFx` 07) is kept as the multiple reference bit by both models, since
2026-11-23. One thing is done on its strength: `set_vector_element`
updates in place when the vector is reached with every MRB off
(PDSS `blt_basic.c`: `if (Mrbof(vect) == MRBOFF)`), and copies
otherwise, the copy's elements marked. Nothing is reclaimed
(`collect_*` do nothing; strings and `put_reused_structure` still
copy). The rules are PDSS's
(`emulator/deref.c`, `emulate.c`, `blt_basic.c`, V2.52), the sibling
whose code we hold; PIM/m's own are described in `M92` pp. 429-430 and
TR-248 (`literature_gaps.md` section 3) and agree where they speak.

- **Dereference.** If any reference on the way has its MRB on, the
  result has (`deref.c`: `SetAll(reg, ..., MRBON)`). Otherwise the
  value is taken as its cell holds it.
- **Marked instructions.** `put_marked_value`, `set_marked_value`,
  `write_marked_value` set the MRB of the source register, then copy;
  `write_marked_variable` gives `REFx`.
- **Elements.** What is taken from a cell that goes on holding it has
  its MRB on: the guard and body `vector_element`, the merger's copy of
  a message, a packed goal's arguments, the copy `set_vector_element`
  makes. The body `vector_element` and `mark_element` also set it in
  the cell. `read_variable` after `wait_vector_N` takes the element as
  it is when the vector word's MRB is off (PDSS `read_element`: "if
  (Mrbof(ptr) == MRBON) SetMrbof(car, MRBON)").
- **Off:** the result of `new_vector`, the copy `set_vector_element`
  makes (in place the vector's word is given back as it was, which
  is off), and a new variable's two references.
- **On:** every other structure pointer, as before (`put_vector_N`,
  `put_list`, constants in a module), and whatever the test driver
  passes from a slot, which it keeps.

Ours, not the sources': integers and atoms are never marked (PDSS
marks them; nothing reads the bit); the guard `vector_element` marks
its result whatever the vector's MRB (PDSS only when it is on); list
cells are always treated as multiply referenced; the copy in
`set_vector_element` marks the new vector's elements but does not go
back and mark the old one's (PDSS does; the old vector is only reached
by marked pointers); an element cell that is itself an unbound
variable is taken as `REFx`, and is never overwritten in place: such
a vector is copied (the cell is the variable; PDSS, whose variables
are cells too, does the same by another route, not followed here).
A marked vector is copied whole, where the Multi-PSI had a
mutable-array scheme. All of these err towards "on", which
costs copies and never correctness.

What the in-place update rests on: that every way a second reference
to a vector can arise sets a bit. `lockstep_mrb.py` checks five ways
by address and content, and the module objects the loader builds are
checked cell by cell against their files (`lockstep_newm.py`,
`lockstep_load.py`); paths the scripts do not run are not checked.

Checked (when the MRB went in; the suite had 23 tests then and has 39
on 2026-11-23, `bsv/run_pimm_lockstep.sh`, all on both models): the 23 lockstep tests agree line for line, and for 22 of them
the reference model's trace before the change equals the trace after
it once the lines the marking adds are dropped and the bit masked
(`jtoa`, whose count did not move, was not compared). Twelve
injections into the Bluespec FAILed (dereference forgetting a marked
link, at the first or a later link; each half of a marked instruction;
`write_marked_variable`; `read_variable` never marking; `wait_vector`
always single; the vector box's elements; `mark_element`'s write;
`new_vector` and the copy coming back marked; the driver's slots).
**Not caught**: `read_variable` marking although the vector is single
(no test reads a vector whose word is unmarked: `put_vector_N` marks),
and the merger taking a message unmarked (every message so far is
already marked or an unbound cell).

## Runtime state

How the PIM/m firmware kept goals, the ready queue and suspended goals
is lost with it. What follows is **this project's design**, shaped
after PDSS (`emulator/record.h`, `goal.c`) and fixed in
`asm/pimm_layout.py`, which both models read. It will grow (priorities,
MRB) and is not a claim about the machine.

**What the literature says against it** (`docs/literature_gaps.md`
section 0, a search made 2026-11-20). PIM/m's KL1 system was converted
from the Multi-PSI/V2 microprogram (Taki, FGCS'92), so Multi-PSI/V2
reports carry over and VPIM (the other PIMs) is a design reference
only. Against those sources this design is wrong or unconfirmed in
these ways, none yet changed in the models:

- one ready list, where the machines have a goal stack per priority
  (newest-first within a priority is confirmed);
- `HOOK` -> suspension record always, where the documented siblings use
  `HOOK` -> the goal record itself for a single waiter and `MHOOK` ->
  suspension records sharing a flag record for several;
- a status word in the goal record, which no source shows;
- waking on variable-to-variable binding, where VPIM and PDSS merge the
  hook chains;
- a heap that only grows, where PIM/m has free pools, MRB reclamation
  and a copying collector.

A waiting built-in as a hooked goal, the low tag bit as the MRB, and
the string descriptor agree with the sources. PIM/m's own field-level
layouts were not found in print; the firmware binary we hold
(`psdpim`'s `pimm.MEkbn`) may hold them; its microprogram is not read.
The console's inspector for the multiple suspension record offers
`prev`, `next`, `goal`, `rival` (`pseudo_pimm_firmware.md`); whether
those are its fields is not established.

- **Heap.** A heap pointer register; cells are taken in order and never
  returned. Running out stops both models.
- **Goal record**, 4 + n cells: `{INT, next record in the ready queue
  or 0}`, `{INT, shoen << 2 | status}` (0 ready, 1 suspended, 2 taken;
  the shoen is the goal's shoen record as an address relative to the
  load address, 0 for the root, so a goal outside every shoen has the
  plain status: "Shoen" below), `{INT, code address}`, `{INT, n}`,
  then the n arguments. Addresses in cells are absolute.
- **Ready queue.** A register holding the newest ready record; a new or
  woken goal goes on the front and the front goal runs next (PDSS's
  default, `enqueue` to the head of its priority's queue). No
  priorities yet.
- **Unbound variable.** `{UNDF, 0}`, or `{HOOK, first suspension
  record}` when goals wait on it. Dereferencing stops at either.
- **Suspension record**, 2 cells, one per (goal, variable):
  `{INT, next suspension record on this variable or 0}`,
  `{INT, goal record}`.
- **Suspending.** `otherwise`/`suspend` write a new suspended record
  (entry = the instruction's label, arguments `r[0..arity)`) and hook it
  on each variable the guards met unbound, in the order met. A variable
  met twice is hooked twice; the status cell makes the goal wake once.
  The record the goal came from is not reused.
- **Binding** writes the value over the variable's cell, then walks its
  suspension list, newest first: each goal still suspended becomes
  ready and goes on the queue (so the oldest waiter runs first). A
  hooked variable bound to another unbound variable wakes its goals
  too; they run, find the second variable and suspend on it. PDSS
  merges the lists instead; this is simpler and costs reductions.
- **A waiting built-in is a goal.** A body built-in with an unbound
  input becomes a suspended goal whose code is a stub from a fixed
  table placed after the image (`asm/pimm_stubs.py`: the built-in on
  `r[0..n)`, a `get_value` per output, `proceed`), with the
  instruction's operands as arguments, a fresh variable for each
  output, hooked on the first unbound input. PDSS does the same with
  its `dc_*` pseudo-code (`body_builtin_suspend`). Because a stub is
  ordinary code, a test can also spawn one directly.

### Shoen (stages 1 to 3: create, start, terminate; statistics, remove; exceptions, stop, abort)

Three tiers, kept apart:

- **PIM/m-sourced** (the IPL image, PIMOS's compiler, assembler, macros
  and manual): the encodings and operand directions of `create_shoen`
  and `start_shoen` (rows above); the handle's tag, 38h `SHREC`
  (`debugger/inspector/tagtbl.kl1`); the report stream's integer
  codes, 8 `started` and 12 `terminated`, which the image's
  `shoen:report/2` (cell 15818) translates (`macro/pimos/pimos/
  pimos.vmac`:177-199 agrees); that a shoen is dormant until `start`
  and that `terminated` reports its end (manual, `e-shoen.tex`:
  117-262); the protocol of `shoen:execute/4`, `control/2`, `report/2`.
  Stage 2: the encodings and directions of `shoen_statistics` (22:E6,
  `r_r`) and `remove_shoen` (22:E4, `r`); the codes 10
  `statistics_started`, `{9, H, L}` `statistics(H, L)` and `{14, H, L}`
  `return_resource(H, L)` (the image's `report/2`, `pimos.vmac`);
  that `statistics_started` is the acknowledgement of `statistics`
  and `statistics(H, L)` follows it, H and L the high and low 32 bits
  of the shoen's resource consumption "including the descendent
  shoens", which "in the current specifications" is "twice of the
  number of reductions", exact once the shoen has terminated and never
  more than the truth before (manual, `e-shoen.tex`:42, 227-262); and
  what a reduction is: dequeues and executes less suspensions
  (`e-shoen.tex`:388-395, the profile's counts), i.e. one per
  `execute`/`execute_external` and one per `proceed`.
  Stage 3: the encodings and directions of `stop_shoen` (22:E2),
  `abort_shoen` (22:E3), `raise` (22:F2) and `current_processor`
  (22:EB) (`inst_tab.kl1`:334-351, `blt.kl1`:537-552); the report
  codes 1 `aborted`, 11 `stopped` and the message `{2, Kind, Info,
  NewCode, NewArgv}` (`pimos.vmac`:177-199, the image's `report/2`);
  Kind the firmware's exception number, 9 `reduction_failure`, 16
  `raised` (`pimos.vmac`:331-349), Info `{Pe, Code, ArgV}` for 9 and
  `{Pe, Info, Data}` for 16 (`kernel/builtin/excpt_tbl.kl1`, its
  "FIRMWARE FORMAT"; the image's own `exception_table:translate/4`,
  cell 1997, is a different text from that held source but reads Info's
  element 0 the same way, via `current_node`/`current_processor`); the
  tag of exception n, bit 16 + n (manual, `e-shoen.tex`, the tag table;
  `reduction_failure` 1 << 25); the mask rule, the report goes to the
  innermost shoen whose mask AND the tag is not 0 (`e-shoen.tex`:57;
  the `raise` entry at :776 says "is 0", taken as a slip); the failing
  goal (or `raise`) replaced by the goal NewCode(NewArgv), the shoen not
  ending before the handler binds them (`e-shoen.tex`:59-60, 773);
  start restarting a stopped shoen, abort final and `terminated`
  following `aborted` (`e-shoen.tex`:136-158, 212-218).
  2026-11-27, reference models only: a failed body unification inside
  a shoen is exception 10 `unification_failure`, Info `{Pe, DataX,
  DataY}` "without Caller" (`excpt_tbl.kl1` 56, 209-215; VPIM
  `f_reduce_exception_handler.psl.c` 79-96, tag bit 0x04000000), made
  by the same path, and the body goes on at the next instruction, as
  VPIM's active unification returns to the instruction stream after
  reporting (`interpreter/klb_unify_bound.psl.c` 263-269, 371-374); the
  pair is the one that would not unify. The one-cell `get_atom`,
  `get_integer`, `get_value`, `get_bound_value`, `get_nil` only
  (`pimm.py` `UNIFY_GOES_ON`); a failure in a structure's `unify_step`
  or a built-in's output is still refused (`a goal failed inside a
  shoen`), as every one was before. The Bluespec core has no such path
  (`ref_prio_list.py`).
- **Carried over from the siblings, not PIM/m-sourced**: counting a
  shoen's goals and its child shoen and ending it at zero (PDSS
  `emulator/emulate.c`:340, `shoen.c`:123-178 and 280-309); the first
  goal being an `apply` (PDSS `dc_apply`) and being parked until the
  shoen is started (PDSS `goal.c`:310-334); `started` reported before
  the state changes and `terminated` alone while the control stream
  is open (VPIM `functions/f_shoen_control.psl.c`:324-330,
  `f_shoen_with_fp.psl.c`:86). VPIM's own message numbers are not
  used. Stage 2: counting reductions where PDSS does (`emulate.c`:
  333-365, `KL1B_PROCEED`, `KL1B_EXECUTE`, `KL1B_EXECUTE_EXTERNAL`)
  and adding a child's total to its parent at the child's termination
  (`shoen.c`:293); `statistics_started` then `statistics(H, L)` at
  once for a terminated shoen (VPIM `f_shoen_control.psl.c`:691-727);
  `remove_shoen` of a terminated shoen reporting `return_resource`,
  then closing the report stream, and of one not yet terminated only
  marking it, the removal then happening at its termination
  (`terminated`, `return_resource`, the close: VPIM
  `f_shoen_control.psl.c`:547-575, `f_shoen_with_fp.psl.c`:69-71).
  Stage 3, from VPIM (`functions/f_reduce_exception_handler.psl.c`,
  `f_Failure_Sub`, `f_Raise_Sub`): NewCode and NewArgv made as two new
  variables first, the goal `apply(NewCode, NewArgv)` enqueued in the
  CURRENT shoen, then Info, then the report; `raise` waiting for Tag
  only (`klb_body_blt_shoen.psl.c`, `kblt_b_raise`); `stopped` and
  `aborted` reported before the status changes, stop and abort of a
  terminated shoen only reporting (`f_shoen_control.psl.c`:392-530).
  From PDSS (`goal.c`:302-335, `shoen.c`:185-267): a goal of an aborted
  shoen discarded, and one of a stopped shoen parked on the shoen,
  when taken from the ready queue; start releasing the parked goals;
  abort removing one from the parent's count; `current_processor` = 0,
  1, 1 (`blt_system.c`).
- **Ours**: everything below about records and cells; in stage 3 also
  Pe = 0, Code the failing predicate's entry (the label of its
  `suspend`), ArgV its argument registers r0..r(arity-1); a failure
  counted as one reduction (as a `proceed`); the check of every goal
  taken inside a shoen by a walk up its shoen's parents; an aborted
  shoen terminated at once (`terminated` at once after `aborted`, its
  reductions and one off its parent's count then; VPIM terminates it
  when its last goal is gone, PDSS never reports it); abort of the
  goal's own shoen or one above it refused; an exception no shoen
  accepts refused.

The design:

- **Shoen record**, 11 cells in the heap (`asm/pimm_layout.py`; 8
  until R7L, so a machine pickled before 2026-11-25 is not loadable):
  `{INT, count}` the shoen's live goals plus its live child shoen;
  `{INT, status}` 0 dormant, 1 started, 2 terminated, 3 removed;
  `{INT, the parent's record, or 0}` (the root has no record); a
  reference to the report stream's unbound tail; `{INT, the goal
  record of the first goal}`; (stage 2) `{INT, reductions}`, the
  shoen's and its terminated descendants', 32 bits (it wraps at 2^32
  reductions, not checked); `{INT, 1 if a remove is pending}`; (stage
  3) `{INT, mask}`, `create_shoen`'s Mask (-1 for `execute/4`). In
  stage 3 status 4 is stopped, and the first-goal cell is the head of
  the list of PARKED goals (linked through their records' link cells),
  0 once the shoen is started. (R7L) `{INT, high}`, `{INT, low}`, the
  resource left as a signed 64-bit number, 0 at create (VPIM
  `f_shoen_main.psl.c` `_INIT_SHOEN_RESOURCE`); `{INT, flags}`, bit 0
  reports of `resource_low` disallowed. The handle is `{SHREC, the
  record's address}`.
- **Resource** (R7L, 2026-11-25): at the end of each run of n > 0
  reductions 2n is taken from the current shoen and from each above it
  (twice the reductions: manual `e-shoen.tex`:42, 234, as
  `shoen_statistics` counts them); a goal of a shoen taken from the
  queue with a shoen at or above its own that is STOPPED or has none
  left parks there (the innermost); if that shoen is the exhausted one
  and its reports are allowed, the flag is set and `resource_low` (6)
  reported (`e-shoen.tex`:179, 218-224; VPIM
  `f_ReplicateSupplyResourceDestinations`, `f_shoen_with_fp.psl.c`:
  560-590). When it is reported is OURS: when none is left (VPIM: under
  one supply unit, 2^24, of the bound; the manual leaves it to the
  processing system, `e-shoen.tex`:224). PIMOS starts a task with
  none and answers its `resource_low` (`kernel/init/init.kl1`:84-89,
  `kernel/task/int_hdl.kl1`:191, 560-566; the Listener's task monitor
  waits for exactly that, `debugger/listener/task_mon.kl1`:13); a
  bench with no monitor gives the same amount
  (`driver.Script.fund_parked`).
- **A goal's shoen** is in its record's status cell (above). The
  machine has a register, the current shoen: that of the goal last
  taken from the ready queue, and the root's (0) once the queue is
  empty, so what a bench makes between runs is the root's. A goal
  record written during a reduction (a new goal, a suspension, a
  waiting built-in, the goal of a unification or of a merger input)
  belongs to the current shoen. Waking keeps a goal's shoen.
- **Counting.** Every goal record written while a shoen is current
  adds one to its count, after the record's last cell; the end of
  every reduction of a goal of that shoen (`proceed` or a suspension,
  not `execute`) takes one off. So a suspension nets nothing and a
  `proceed` is one less. The root is not counted: no memory traffic,
  and every trace made before the shoen existed is unchanged.
- **Reductions** (stage 2). The exec stage counts, for the goal in
  hand, one per `execute` and `execute_external` and one for its
  `proceed` (a suspension adds none); at the end of the goal's run
  that number is added to its shoen's reduction cell (one read and one
  write, before the count's), and at a shoen's termination its total
  is added to its parent's the same way. Writing the cell once per run
  is ours; so is that a stub's goal (`apply`, `unify_step`, a waiting
  built-in, a merger input) counts as an ordinary one (its proceed),
  where the manual's profile counts `unify_vector` per element.
- **`create_shoen`**: Code and Argv go to argument registers 1 and 2
  as they are; then the record (count 1, dormant, parent = the
  current shoen), a fresh Report variable, the first goal (code:
  `apply`'s stub of `asm/pimm_stubs.py`; suspended, on no queue and
  on no variable; it belongs to the new shoen and is the 1 of its
  count), reductions 0, no remove, and one more on the parent's count
  unless that is the root.
- **`start_shoen`**: 8 on the report stream, status started, then the
  first goal becomes ready and goes on the queue as a woken goal does
  (a `W` line).
- **Termination.** When a count reaches 0: status terminated, 12 on
  the report stream, the removal if a remove is pending (below), then
  the parent gets the shoen's reductions and one off its count, and so
  on up.
- **`shoen_statistics`** (stage 2): 10 on the report stream, then
  `{9, H, L}`, H:L = twice the reduction cell as 64 bits (high, low);
  `r[y]` := the same handle (ours). On a shoen not yet terminated the
  cell is reported as it stands (ours: VPIM asks its processors and
  answers later; the manual allows an undercount). Refused: anything
  but a handle; on a removed shoen the closed stream refuses it.
- **`remove_shoen`** (stage 2): a terminated shoen is removed: `{14,
  H, L}` (`return_resource`, H:L the resource left, 0 if it is
  negative; R7L, until which it was 0, 0), then the report stream's tail
  is unified with `[]`, then status removed. A dormant or started
  shoen gets its remove cell set and is removed at its termination
  (so 12, 14, `[]` come together). Refused: a shoen removed already,
  anything but a handle.
- **A message on the report stream**: two new cells `{INT, code}`
  `{UNDF}` (for `{9, H, L}` and `{14, H, L}`, first the vector's three
  cells, the list cell's car then being the vector); the record's
  tail, followed through references, is bound to the list cell with
  the ordinary wake of the goals waiting on it; the record's tail
  becomes the new cell. A tail someone has bound to a value is
  refused.
- **The exception path** (stage 3). A goal of a shoen with no clause
  that applies (its `suspend` with nothing noted), or `raise(Tag, Info,
  Data)` (Tag an integer; it waits on Tag only): from the current
  shoen up, the first whose mask AND the tag is not 0 is the target
  (none: refused). Two new variables NewCode, NewArgv; the goal
  `apply(NewCode, NewArgv)` in the CURRENT shoen (one on its count);
  ArgV (a failure: a vector of the arity's registers; 0 or more than 6
  arguments refused) and Info `{0, Code, ArgV}` (failure, Kind 9, tag
  1 << 25) or `{0, Info, Data}` (raise, Kind 16, tag Tag); then `{2,
  Kind, Info, NewCode, NewArgv}` on the target's report stream. The
  failing goal ends, counted as one reduction; `raise` proceeds. So the
  shoen ends only after its handler binds NewCode/NewArgv and the
  applied goal runs (the image's monitors answer their own `dummy/2`
  and `{{Kind, Info}, Shut}`). A UNIFICATION failure (`unify` of two
  values) is still refused: VPIM reports it as 10 and goes on with the
  reduction, which we do not model.
- **`stop_shoen(Shoen, ^NewShoen)`** (stage 3): 11 on the report
  stream, then a started shoen becomes stopped (any other status
  unchanged); NewShoen := Shoen. A goal taken from the ready queue
  whose shoen, or an ancestor, is stopped is parked on the innermost
  stopped one (`E park` on the trace) and counts as suspended.
  `start_shoen` of a stopped shoen: 8, started, every parked goal back
  on the queue (a `W` line each), the list emptied.
- **`abort_shoen(Shoen, ^NewShoen)`** (stage 3): 1 on the report
  stream; then, unless the shoen has terminated already, it terminates
  at once: 12, the removal if pending, its reductions to its parent
  and one off the parent's count (cascading). Its goals, and those of
  every shoen inside it, are discarded when taken from the queue (`E
  aborted`); goals still suspended stay so. Its inner shoen are not
  reported to (theirs stay `started`). Refused: abort of the current
  goal's own shoen or an ancestor, anything but a handle.
- **`current_processor(^P, ^X, ^Y)`** (stage 3): 0, 1, 1, never waits.
- **No resource model: 6 (`resource_low`) is never reported.** Ours,
  and probably not the machine's: VPIM reports it for a shoen with no
  limit left, and every caller of `execute/4` in the image grants
  resource only when it is told `resource_low`.
- **Refused, loudly** (the reference model raises `Unimplemented`,
  the Bluespec ends `E unimp`): `shoen_profile`,
  `create_profiling_shoen`, a unification failure inside a shoen, an
  exception no shoen's mask accepts. `add_shoen_resource` and
  `allow_shoen_resource_report` (2026-11-24) are acknowledged on the
  report stream and nothing else: what they change is not sourced: the allowance a
  new shoen starts with (PDSS starts every shoen exhausted, VPIM
  reports `resource_low` with no limit; the manual gives none), the
  `resource_low` threshold, and how a shoen is suspended on
  exhaustion and resumed by `add_shoen_resource` (VPIM's code for it
  is per-processor and asynchronous). Any model of them would be ours,
  and every caller of `execute/4` in the image grants resource only
  when it is told `resource_low`, which nothing here would make true.
- **Tested** (stage 3): `lockstep_shoen3.py`, through the image's
  `execute/4`, `execute/7`, `control/2`, `report/2`,
  `exception_table:translate/4`, `shoen:raise/3` and its three
  monitors. Not run: an inner shoen whose mask does NOT accept (it
  needs `execute/7` inside a shoen, an `apply` of a 7-element Argv,
  over the bench's 6), so innermost-first and not reading the mask at
  all are not discriminated; the manual's mask rule against VPIM's is
  (Tag 3 under mask 1; see the test's header).
- **What follows for the image's own `execute/4`** (observed,
  `lockstep_shoen.py`, `lockstep_shoen2.py`): its `control/2` and
  `report/2` belong to the shoen that called it, and end only through
  `remove_shoen` and the closing of the report stream. In stage 1 a
  shoen whose code is `execute/4` never terminated. With stage 2 the
  image's monitors (`ipl:ipl_monitor/3`, `top:bios_monitor/3`,
  `top:top_level_monitor/4`) answer `terminated` with `[statistics]`,
  `control/2` calls `shoen_statistics` and `remove_shoen`, the inner
  stream closes, `report/2` ends, and the OUTER shoen terminates: the
  last goal of the outer to end is the inner's `report/2` (observed
  in `lockstep_shoen2.py`, `nested`). A child's own termination is
  never what takes its parent to 0 with the image's code: `report/2`
  of the child is the parent's and outlives it (the close comes with
  or after the child's termination). That step of the cascade (a
  parent terminated inside its child's termination) is not run.

Things this predicate shows about the compiler, useful for reading the
rest: range guards compile to `put_integer` and a comparison per bound;
33 constant clauses compile to one `hash_on_constant`, placed after the
`switch_on_non_integer` and before the range clauses even though the
source has the ranges first (the clauses are mutually exclusive, so the
order does not show).
