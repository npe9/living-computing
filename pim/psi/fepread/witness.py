#!/usr/bin/env python3
"""The KL0 opcode readings that docs/fep_services.md §6 leans on, each
with its witness.  OURS.

    python3 -I psi/fepread/witness.py            the table
    python3 -I psi/fepread/witness.py --check    verify every witness

No held document prints KL0 opcode numbers (docs/simpos/layers/KL0.md
§3), so a reading is only as good as its witness.  Two kinds are used:

  SOURCE     compiled code of paragraph.ptf beside the held ESP source
             of the same clause (pimos.tar.Z src_util/paragraph).  The
             check finds the listed cells, in order and adjacent, in the
             named predicate, and the quoted text in the named file.
  CROSS-END  compiled code of pimfep.ptf beside the PIMOS source for the
             other end of the same message (cited in fep_services.md
             §2-§3).  Weaker: it shows the reading is consistent with
             what PIMOS sends or expects, not what the compiler was
             given.

Operand order.  In a method the receiver (the first argument in the
source) is in the LAST argument register and the other arguments are in
r0..; in a local predicate the registers are in source order.  Witness:
`:count(Obj,Obj!count):-!;` reads the slot from r1 and unifies with r0.

Opcodes used in §6 with no witness of either kind are listed in
UNWITNESSED with what is assumed of them; a result that needs one of
them is graded INFERENCE there.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptfread as R      # noqa: E402
import held              # noqa: E402

P = 'paragraph'
LIB = ('list_index_buffer', 'p_buf.esp')
# (opcode, reading, kind, package, class, predicate/arity, cells, file, text)
W = [
    ('0:5f n', 'allocate an environment', 'SOURCE', P, LIB[0], 'put_contents_with_key/2',
     ['pmi 5f  04 00 00', 'pmi 20  00 00 00', 'pmi 20  01 01 00'], LIB[1],
     ':put_contents_with_key(Obj,L):- :clear(Obj),'),
    ('0:20 A Y', 'get_variable: Y := rA (permanent)', 'SOURCE', P, LIB[0],
     'put_contents_with_key/2', ['pmi 20  00 00 00', 'pmi 20  01 01 00', 'pmi a3  00 01 00'],
     LIB[1], ':put_contents_with_key(Obj,L):- :clear(Obj),'),
    ('0:73 r n + selector', 'method call; receiver in r(n-1), the last argument register',
     'SOURCE', P, LIB[0], 'put_contents_with_key/2',
     ['pmi a3  00 01 00', 'pmi 73  00 01 00', 'selector clear/1'], LIB[1], ':clear(Obj),'),
    ('0:a0 A Y', 'put_variable: rA := a new Y', 'SOURCE', P, LIB[0], 'put_contents_with_key/2',
     ['pmi a0  02 02 00', 'pmi a2  00 00 00', 'pmi 60  00 00 fb'], LIB[1],
     'set_all(L,Obj!root,Tail),'),
    ('0:a2 A Y', 'put_value: rA := Y', 'SOURCE', P, LIB[0], 'put_contents_with_key/2',
     ['pmi a2  01 01 00', 'pmi-atom put r0, root', 'blt 27  01 00 01'], LIB[1],
     'set_all(L,Obj!root,Tail),'),
    ('0:a4 A Y', 'put_value of a Y at its last use', 'SOURCE', P, LIB[0],
     'put_contents_with_key/2', ['pmi-atom put r0, count', 'pmi a4  02 03 00',
                                 'blt 2f  01 00 02'], LIB[1], 'Obj!count:=N,'),
    ('0:60 / 61', 'local call / local execute (last call)', 'SOURCE', P, LIB[0], 'search/3',
     ['pmi a3  00 04 00', 'pmi 61  00 00 8c'], LIB[1], 'search(Obj!root,Obj!tail,Key,X);'),
    ('0:a3 A X', 'put_value: rA := rX (temporary)', 'SOURCE', P, LIB[0], 'search_num/4',
     ['pmi a3  05 02 00', 'pmi a7  04 00 01', 'pmi a3  03 01 00'], LIB[1],
     'search(Obj!root,Obj!tail,Key,X,1,N);'),
    ('0:a7 A int16', 'put_integer', 'SOURCE', P, LIB[0], 'search_num/4',
     ['pmi a7  04 00 01'], LIB[1], 'search(Obj!root,Obj!tail,Key,X,1,N);'),
    ('0:dc n, f0', 'neck cut of an arity-n method; proceed', 'SOURCE', P, LIB[0], 'count/2',
     ['pmi dc  02 00 00', 'pmi-atom put r2, count', 'blt 27  01 02 01', 'pmi 23  01 00 00',
      'pmi f0  00 00 00'], LIB[1], ':count(Obj,Obj!count):-!;'),
    ('0:23 A X', 'get_value: unify rA with rX', 'SOURCE', P, LIB[0], 'count/2',
     ['blt 27  01 02 01', 'pmi 23  01 00 00'], LIB[1], ':count(Obj,Obj!count):-!;'),
    ('0:21 A X', 'get_variable: rX := rA (temporary)', 'SOURCE', P, LIB[0], 'search/5',
     ['pmi 21  00 05 00', 'pmi 23  01 05 00', 'pmi d5  00 00 00'], LIB[1],
     'search(T,T,_,_,_):-!,fail;'),
    ('0:e4 / e2 / e0', 'try_me_else / retry_me_else / trust_me', 'SOURCE', P, LIB[0], 'skip/3',
     ['pmi e4  03 00 02', 'pmi 21  00 03 00', 'pmi 27  01 00 00', 'pmi 23  02 03 00',
      'pmi d2  00 00 00', 'pmi e0  00 00 00'], LIB[1], 'skip(H,0,H):-!;'),
    ('0:27 A int16', 'get_integer', 'SOURCE', P, LIB[0], 'skip/3', ['pmi 27  01 00 00'],
     LIB[1], 'skip(H,0,H):-!;'),
    ('0:d2 / d5 / d0', 'cut and proceed / cut and fail / cut', 'SOURCE', P, LIB[0], 'search/4',
     ['pmi 23  05 04 00', 'pmi d0  00 00 00', 'pmi a7  01 00 02'], LIB[1],
     'search(H,T,X,Y):-first(H,X),!,vector_element(H,2,Y);'),
    ('0:26 A', 'get_nil', 'SOURCE', P, LIB[0], 'all/3', ['pmi 26  02 00 00', 'pmi d2  00 00 00'],
     LIB[1], 'all(T,T,[]):-!;'),
    ('0:2b A H T', 'get_list with head and tail variables', 'SOURCE', P, LIB[0], 'all/3',
     ['pmi 2b  02 03 02'], LIB[1], 'all(H,T,[F|L]):-'),
    ('0:2a A, 4b n, 41 X', 'get_list; unify_void n; unify_variable', 'SOURCE', P, LIB[0],
     'count/2#local', ['pmi 2a  00 00 00', 'pmi 4b  00 00 01', 'pmi 41  00 00 00'], LIB[1],
     'count([_|L],N):-'),
    ('0:22 A Y', 'get_value: unify rA with Y', 'SOURCE', P, LIB[0], 'count/2#local',
     ['blt 45  00 01 00', 'pmi 22  00 00 00'], LIB[1], 'N=N1+1;'),
    ('0:3N A (N<7), 37 A _ N', 'get_vector of N elements, unify instructions follow',
     'SOURCE', P, LIB[0], 'set_all/3', ['pmi 2b  00 03 00', 'pmi 32  03 00 00',
                                        'pmi 41  03 00 00', 'pmi 41  04 00 00'], LIB[1],
     'set_all([{X,Key}|L],H,T):-'),
    ('0:47 int16', 'unify_integer', 'SOURCE', P, 'what_manipulator', 'convert/7',
     ['pmi 37  0f 00 0c', 'pmi 41  0f 00 00', 'pmi 47  00 00 00', 'pmi 47  00 00 01',
      'pmi 43  0c 00 00'], 'p_what.esp',
     'convert([{P,M,Pr,A,R,S,Id}|L],[{St,0,1,R,S,P,M,Pr,A,W,Id,St0}|L1],Len,C,N,Sum,Total):-!,'),
    ('0:43 X', 'unify_value (temporary)', 'SOURCE', P, 'what_manipulator', 'convert/7',
     ['pmi 47  00 00 01', 'pmi 43  0c 00 00', 'pmi 43  0d 00 00'], 'p_what.esp',
     'convert([{P,M,Pr,A,R,S,Id}|L],[{St,0,1,R,S,P,M,Pr,A,W,Id,St0}|L1],Len,C,N,Sum,Total):-!,'),
    ('0:a9 A rel', 'put a pool constant (string, list, class reference)', 'SOURCE', P,
     'wshell_tester', 'font/1', ['pmi a9  01 ff f7', 'blt 25  01 02 00', 'pmi a3  01 00 00',
                                 'pmi a9  00 ff f5', 'pmi 74  02 03 00', 'selector create/3'],
     'p_wtest.esp', 'attribute font:= F :- :create(#font,"font:test_11.font",F);'),
    ('1:25 A D', 'class object of a class reference (#class)', 'SOURCE', P, 'profiler_ux_patch',
     'get_parameter/2', ['pmi a9  00 ff f7', 'blt 25  00 01 00', 'pmi a0  00 01 00',
                         'pmi 73  01 02 00', 'selector get_plane_count/2'], 'p_ux_patch.esp',
     ':get_plane_count(#bitmap,N),'),
    ('0:74 r n + selector', 'method execute (last call)', 'SOURCE', P, 'wshell_tester', 'font/1',
     ['pmi 74  02 03 00', 'selector create/3'], 'p_wtest.esp',
     'attribute font:= F :- :create(#font,"font:test_11.font",F);'),
    ('0:aa A, 44 Y, 43 X, 4a, 60 4c atom', 'put_list; unify_value Y / X; the tail is a list; '
     'unify_atom', 'SOURCE', P, 'what_manipulator', 'make_string/7',
     ['pmi aa  00 00 00', 'pmi 44  06 00 00', 'pmi 4a  00 00 00', 'pmi 43  04 00 00',
      'pmi 4a  00 00 00', 'pmi 44  07 00 00'], 'p_what.esp',
     ':append(#string,[S1,"::",S2,":",S3,"/",S4],S0),'),
    ('1:0b S L T', 'string(S, Length, ElementType)', 'SOURCE', P, 'what_manipulator',
     'make_string/7', ['pmi a2  06 05 00', 'blt 0b  06 01 00'], 'p_what.esp',
     'string(S0,Len0,_),'),
    ('1:2b S I V', 'set_string_element', 'SOURCE', P, 'what_manipulator', 'sp/3',
     ['pmi a7  03 21 21', 'blt 2b  00 01 03', 'blt 45  01 01 01', 'blt 46  02 01 02'],
     'p_what.esp', 'set_string_element(S,C,#" "),'),
    ('1:45 A imm D / 46 A imm D', 'add / subtract an immediate', 'SOURCE', P, 'what_manipulator',
     'sp/3', ['blt 45  01 01 01', 'blt 46  02 01 02', 'pmi 61  00 ff f6'], 'p_what.esp',
     'sp(S,C+1,N-1);'),
    ('1:32 S F L + cell', 'substring(S, From, Length, Result); the cell after names the result '
     'register in its top byte', 'SOURCE', P, 'bar2_h', '$or$22/12',
     ['pmi a7  00 00 00', 'pmi a7  01 00 01', 'blt 32  0a 00 01', 'integer 0 (0)',
      'pmi 24  00 08 00'], 'bar2_h.esp', 'substring(XM_String,0,1,XM1),'),
    ('0:24 A Y', 'get_variable Y := rA after a built-in', 'SOURCE', P, 'bar2_h', '$or$22/12',
     ['integer 0 (0)', 'pmi 24  00 08 00', 'pmi a3  00 01 00', 'pmi a7  01 00 02'],
     'bar2_h.esp', 'substring(XM_String,1,2,XM2),'),
    ('1:27 O N D / 2f O N V', 'slot read Obj!name / slot write Obj!name := V', 'SOURCE', P,
     LIB[0], 'clear/1', ['pmi-atom put r1, count', 'pmi a7  02 00 00', 'blt 2f  00 01 02'],
     LIB[1], 'Obj!count:=0,'),
    ('1:62 A B', '== (in a guard)', 'SOURCE', P, 'array_index_buffer', 'member/2',
     ['pmi 41  02 00 00', 'pmi 4b  00 00 01', 'blt 62  00 02 00', 'pmi d2  00 00 00'],
     'p_buf4.esp', 'member(F,[F1|_]):-F==F1,!;'),
    ('1:64 A B', '== (the last alternative of a disjunction)', 'SOURCE', P, 'profiler_ux_patch',
     '$or$0/2', ['pmi a7  02 00 08', 'blt 64  01 02 00', 'pmi d0  00 00 00',
                 'pmi 27  00 1f ff'], 'p_ux_patch.esp', 'N==8,!,Dev=16#"1FFF");'),
    ('0:f1 n / 62 n rel', 'deallocate and proceed / deallocate and local execute', 'SOURCE', P,
     'profiler_ux_patch', 'get_parameter/2', ['pmi a5  01 01 00', 'pmi a2  00 00 00',
                                              'pmi 62  0a 00 03'], 'p_ux_patch.esp',
     '(N==1,!,Dev=16#"07FF";'),
    # cross-end
    ('1:23 S I D', 'string_element(S, I, D)', 'CROSS-END', 'pimfep', 'simpos_user_device',
     'melt/4', ['pmi a7  01 00 00', 'blt 23  00 01 01', 'pmi a7  04 00 01', 'blt 23  00 04 04',
                'pmi a7  05 00 02', 'blt 32  00 05 01'],
     'server/fep/fep/confirm.kl1:301-323', 'io(0, [len(Name), len(Pass)] ++ Name ++ Pass)'),
    ('0:bN A (N<7), b7 A _ N', 'put_vector of N elements', 'CROSS-END', 'pimfep',
     'pimos_scsi_front_end', '$or$3/4', ['pmi b7  02 00 09', 'pmi 44  00 00 00',
                                         'pmi 47  00 00 01', 'pmi 44  08 00 00'],
     'bios/fep_module/file_dvc.kl1:51-52', '{Id, 1, Code, OS, Host, FepVer, Dir, FileVer, '
     'Comment}: nine elements, status 1'),
    ('0:b3 A + 47', 'put_vector 3 with integers', 'CROSS-END', 'pimfep', 'pimos_timer',
     'on_after/4#local', ['pmi b3  00 00 00', 'pmi 44  01 00 00', 'pmi 47  00 00 01',
                          'pmi 47  00 00 09'],
     'server/fep/timer/time_dvc.kl1:254-257', 'the alarm is {Id, 1, 9}'),
    ('0:29 A rel', 'get a pool constant: unify rA with it', 'CROSS-END', 'pimfep',
     'pimos_scsi_front_end', 'fep_attributes/7', ['pmi 27  00 00 00', 'pmi 29  04 f8 8a'],
     'server/fep/file/fileRdvc.kl1:125, 326-359', 'element 4 of the reply is the path '
     'delimiter Deli, appended between directory and name; SIMPOS writes ">"'),
]

UNWITNESSED = [
    ('0:42 Y / 45 X / 46 Y', 'further unify_value forms inside a put_vector or put_list '
     '(42 a Y at its last use, 45 an X, 46 a new Y): the element is the variable named'),
    ('0:a1 / a5', 'further put forms (a5 a Y at its last use before a deallocating call)'),
    ('0:c4 / c2 / c0', 'try / retry / trust of the alternatives of a `;` or of clauses with '
     'an environment; d1 / d3 / d4 / dd / de the cuts that go with them; 6e deallocate; '
     '75 method execute with deallocate'),
    ('0:c7 + cc pairs, ca, c9, hash tables', 'switch on the first argument; read only for '
     'their keys'),
    ('0:fe / ff', 'fail (the end of a clause chain / the default of a switch)'),
    ('1:40 41 42 43 / 48 49', 'add, subtract, multiply, divide of two registers / multiply, '
     'divide by an immediate.  Assumed from hex_string/5 and create_message/3, where '
     'they rebuild a 16-bit character from two bytes and a length from two characters'),
    ('1:65 / 67 / 68', '\\== / an ordering test / string equality.  Assumed from use'),
    ('1:35, 30, 1a, 06, 0d, 01, e6, f5, f0, f2', 'not read; no result depends on them'),
]


def norm(s):
    return re.sub(r'\s+', '', s)


def _pred(c, spec):
    name, _, rest = spec.partition('/')
    arity, _, where = rest.partition('#')
    for p in c.preds:
        if p.name == name and p.arity == int(arity) and (
                not where or (where == 'local') == (p.kind in (0x11, 0x12))):
            if where or True:
                yield p


def has_cells(pkg_classes, cls, spec, cells):
    c = R.find(pkg_classes, cls)
    for p in _pred(c, spec):
        lines = [x[8:].split('   ')[0].strip() for x in R.listing(c, p)[1:]]
        for i in range(len(lines) - len(cells) + 1):
            if lines[i:i + len(cells)] == cells:
                return True
    return False


def check():
    bad, pk, src = [], {}, None
    for op, reading, kind, pkg, cls, spec, cells, fname, text in W:
        if pkg not in pk:
            pk[pkg] = R.load(pkg)
        if not has_cells(pk[pkg], cls, spec, cells):
            bad.append('%s: cells not found in %s %s' % (op, cls, spec))
        if kind == 'SOURCE':
            if src is None:
                src = {k: norm(v.decode('euc_jp', 'replace'))
                       for k, v in held.src_files('paragraph').items()}
            if norm(text) not in src.get(fname, ''):
                bad.append('%s: text not found in %s' % (op, fname))
    return bad


def main(argv):
    if '--check' in argv:
        bad = check()
        for b in bad:
            print('witness: FAIL ' + b)
        if not bad:
            print('witness: PASS (%d witnesses: %d against ESP source, %d cross-end)'
                  % (len(W), sum(w[2] == 'SOURCE' for w in W),
                     sum(w[2] == 'CROSS-END' for w in W)))
        return 1 if bad else 0
    for op, reading, kind, pkg, cls, spec, cells, fname, text in W:
        print('%-22s %s\n    %s: %s %s %s\n    %s: %s\n    cells: %s'
              % (op, reading, kind, pkg, cls, spec.split('#')[0], fname, text, ' | '.join(cells)))
    print('\nUNWITNESSED')
    for op, what in UNWITNESSED:
        print('%-22s %s' % (op, what))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
