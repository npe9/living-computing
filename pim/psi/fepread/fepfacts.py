#!/usr/bin/env python3
"""What docs/fep_services.md §6 reports about pimfep.ptf, computed from
the cells.  OURS.

    python3 -I psi/fepread/fepfacts.py handlers   the 63-row table (markdown)
    python3 -I psi/fepread/fepfacts.py extra      handled or named on the PSI, never sent by PIMOS
    python3 -I psi/fepread/fepfacts.py strings    the login dialogue's strings (markdown)
    python3 -I psi/fepread/fepfacts.py facts      the per-unknown facts check.py pins

How a command reaches its handler (READ in ptfread listings; the
opcode readings are witness.py's):
  pimos_scsi_front_end local command_type/2 sorts a command number into
  `server` (103, 240, 70, 80, 901, 902), `device_create` (the ten keys
  of fep_device_class/2) or `device` (anything else).
  server:        refute_server_command/3, clauses on the message vector.
  device_create: `:refute(Class, Name, Args)` on the class
                 fep_device_class/2 gives, Name being the command's name
                 in fep_command_code_table: a CLASS method Name of arity
                 message length + 4.
  device:        the raw message is put on the device's stream; the
                 device process (as_pimos_device local refute/3; for a
                 window pimos_window kl1_message/2, on its editor) does
                 `:refute(Device, Name, MessageVector)`: an INSTANCE
                 method Name of arity message length + 1, i.e. PIMOS's
                 argument count + 3 (receiver, device id, command).
`refute/3` itself is not in pimfep.ptf (an ESP/SIMPOS method of every
object); that it calls the method named, with the vector's elements as
arguments, is INFERENCE from the arities, which fit in all 63 rows.
"""
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptfread as R      # noqa: E402

# (code, [(PIMOS device module of fep_services.md §2, argument counts or
#  'create' / 'server')]).  The 63 codes of §2.
CODES = [
    (60, [('every', (0,))]), (70, [('every', 'server')]), (80, [('link', 'server')]),
    (201, [('file', 'create')]), (202, [('file', 'create')]), (203, [('file', 'create')]),
    (240, [('file', 'server')]), (210, [('file', (1,)), ('socket', (1,))]),
    (220, [('file', (0,))]),
    (111, [('file', (1,)), ('window', (1,)), ('socket', (2,))]),
    (112, [('file', (0,)), ('window', (0,)), ('socket', (0,))]),
    (221, [('file', (0,)), ('directory', (0,))]), (222, [('file', (0,))]),
    (204, [('directory', 'create')]), (205, [('directory', 'create')]),
    (237, [('directory', (1,))]), (231, [('directory', (1,))]), (239, [('directory', (1,))]),
    (232, [('directory', (1,))]), (238, [('directory', (1,))]), (233, [('directory', (1,))]),
    (235, [('directory', (0,))]),
    (310, [('timer', 'create')]), (301, [('timer', (0,))]), (302, [('timer', (1,))]),
    (303, [('timer', (1,))]), (304, [('timer', (0,))]),
    (601, [('string_io', 'create')]), (620, [('string_io', (2,))]),
    (104, [('window', 'create')]), (102, [('window', 'create')]), (103, [('window', 'server')]),
    (110, [('window', (0,))]), (113, [('window', (0,))]), (114, [('window', (1,))]),
    (121, [('window', (2,))]), (120, [('window', (0,))]), (124, [('window', (2,))]),
    (123, [('window', (0,))]), (127, [('window', (4,))]), (126, [('window', (0,))]),
    (130, [('window', (1,))]), (132, [('window', (1,))]), (140, [('window', (1,))]),
    (146, [('window', (0,))]), (141, [('window', (0,))]), (142, [('window', (0,))]),
    (143, [('window', (0,))]), (144, [('window', (0,))]), (145, [('window', (0,))]),
    (122, [('window', (0,))]), (125, [('window', (0,))]), (131, [('window', (0,))]),
    (133, [('window', (0,))]),
    (801, [('socket', 'create')]), (802, [('socket', (1,))]), (803, [('socket', (1,))]),
    (804, [('socket', (1,))]), (805, [('socket', (1,))]), (812, [('socket', (2,))]),
    (806, [('socket', (1, 2, 3))]), (810, [('socket', (1,))]), (811, [('socket', (1,))]),
]
DEVICE_CLASS = {'file': 'pimos_file', 'directory': 'pimos_directory', 'timer': 'pimos_timer',
                'string_io': 'as_pimos_string_io_device', 'window': 'pimos_window_editor',
                'socket': 'pimos_tcpip_socket'}
ALL_DEVICE_CLASSES = sorted(set(DEVICE_CLASS.values())) + ['as_pimos_device']
LOGIN_CLASSES = ['pimos_login_requester', 'as_pimos_login_requester',
                 'pimos_remote_login_server', 'pimos_remote_login_replier']
PRIMARY = 0x35

_cache = {}


def classes():
    if 'cl' not in _cache:
        _cache['cl'] = R.load('pimfep')
    return _cache['cl']


def cls(name):
    return R.find(classes(), name)


def pred(c, name, arity, kinds=None):
    for p in c.preds:
        if p.name == name and p.arity == arity and (kinds is None or p.kind in kinds):
            return p
    return None


def lines(cname, name, arity, kinds=None):
    """The listing lines of one predicate, cell numbers stripped."""
    c = cls(cname)
    p = pred(c, name, arity, kinds)
    return [x[8:] for x in R.listing(c, p)[1:]]


def names():
    """{code: name} of fep_command_code_table convert/2, in clause
    order: the first name of a code is kept (3 is control_c, then
    attention)."""
    c = cls('fep_command_code_table')
    p = pred(c, 'convert', 2, (0x11,))
    cs, _sp, _bad = R.cells_of(c, p)
    out = {}
    for a, b in zip(cs, cs[1:]):
        if a[1] == 0x20 and a[3] >> 24 == 0x27 and (a[3] >> 16) & 255 == 0 and b[1] == 0x60:
            out.setdefault(a[3] & 0xffff, c.sym(b[3]))
    return out


def command_types():
    """{key: 'server' | 'device_create'} from command_type/2: each key's
    clause is `get_integer r0, key; get_atom r1, type`."""
    c = cls('pimos_scsi_front_end')
    p = pred(c, 'command_type', 2)
    cs, _sp, _bad = R.cells_of(c, p)
    out = {}
    for a, b in zip(cs, cs[1:]):
        if a[1] == 0x20 and a[3] >> 24 == 0x27 and b[1] == 0x60 and b[2] == 1:
            out[a[3] & 0xffff] = c.sym(b[3])
    return out


def device_classes():
    """{key: class} from fep_device_class/2: `get_integer r0, key; cut;
    put pool class reference`."""
    c = cls('pimos_scsi_front_end')
    p = pred(c, 'fep_device_class', 2)
    cs, _sp, _bad = R.cells_of(c, p)
    out = {}
    for i, a in enumerate(cs[:-2]):
        b = cs[i + 2]
        if a[1] == 0x20 and a[3] >> 24 == 0x27 and b[1] == 0x20 and b[3] >> 24 == 0xa9:
            t = c.pool[b[0] + 2 + R.s16(b[3])]
            out[a[3] & 0xffff] = t[1].split('##')[-1]
    return out


def server_clauses():
    """[(vector length, command)] of refute_server_command/3: a
    get_vector (3N) and the unify_integer (47) within its elements."""
    c = cls('pimos_scsi_front_end')
    p = pred(c, 'refute_server_command', 3)
    cs, _sp, _bad = R.cells_of(c, p)
    out = []
    for i, a in enumerate(cs):
        if a[1] == 0x20 and 0x32 <= a[3] >> 24 <= 0x36:
            n = (a[3] >> 24) - 0x30
            for b in cs[i + 1:i + 1 + n]:
                if b[1] == 0x20 and b[3] >> 24 == 0x47:
                    out.append((n, b[3] & 0xffff))
    return out


def handlers():
    """[(code, name, [(device, handler text, ok)])]."""
    nm, ct, dc, sc = names(), command_types(), device_classes(), dict(
        (cmd, n) for n, cmd in server_clauses())
    rows = []
    for code, uses in CODES:
        name, hs = nm.get(code), []
        for dev, how in uses:
            if how == 'server':
                ok = ct.get(code) == 'server' and code in sc
                hs.append((dev, 'pimos_scsi_front_end refute_server_command/3, a %d-element '
                           'message' % sc.get(code, 0), ok))
            elif how == 'create':
                c = cls(dc[code]) if code in dc else None
                ps = [p for p in (c.preds if c else []) if p.name == name and p.kind == 0x25]
                ok = ct.get(code) == 'device_create' and len(ps) == 1
                hs.append((dev, 'class %s %s' % (dc.get(code), '/'.join(
                    [name, str(ps[0].arity)]) if ps else '?'), ok))
            else:
                where = DEVICE_CLASS.get(dev, 'as_pimos_device')
                found = []
                for n in how:
                    for cn in (where, 'as_pimos_device'):
                        if pred(cls(cn), name, n + 3, (PRIMARY,)):
                            found.append('%s %s/%d' % (cn, name, n + 3))
                            break
                ok = len(found) == len(how) and code not in ct
                hs.append((dev, ', '.join(found) or '?', ok))
        rows.append((code, name, hs))
    return rows


def extra():
    """(server keys PIMOS never sends, [(code, name, class method)] of
    names PIMOS never sends to that device kind)."""
    nm, ct = names(), command_types()
    sent = {}
    for code, uses in CODES:
        for dev, how in uses:
            sent.setdefault(code, set()).add(DEVICE_CLASS.get(dev, dev))
    keys = sorted(k for k in ct if k not in sent)
    more = []
    for code, name in sorted(nm.items()):
        for cn in ALL_DEVICE_CLASSES:
            for p in cls(cn).preds:
                if p.name == name and p.kind == PRIMARY and p.arity >= 3:
                    if 'every' in sent.get(code, ()):
                        continue
                    if cn not in sent.get(code, ()):
                        more.append((code, name, '%s %s/%d' % (cn, p.name, p.arity)))
    return keys, more


def login_strings():
    """[(class, predicates using it, ptfdump's ASCII reading, the JIS
    codec's text, JIS words)] for the login classes; empty strings are
    left out.  Raises if a word does not decode."""
    out = []
    for cn in LOGIN_CLASSES:
        c = cls(cn)
        users = R.pool_users(c)
        for k, text, words in R.strings(c):
            if not text or words is None:
                continue
            uni, bad = R.jis_unicode(words)
            if bad:
                raise ValueError('%s pool[%x]: undecoded %r' % (cn, k, bad))
            who = sorted({'%s/%d' % (p.name, p.arity) for p, _n, _o in users.get(k, [])})
            out.append((cn, who, text, uni, words))
    return out


def has(cname, name, arity, seq, kinds=None):
    """True if the lines SEQ occur adjacent and in order in a predicate
    (a line matches if it starts with the given text)."""
    ls = lines(cname, name, arity, kinds)
    for i in range(len(ls) - len(seq) + 1):
        if all(ls[i + j].startswith(s) for j, s in enumerate(seq)):
            return True
    return False


def facts():
    """{name: value} the facts §6 states, read from the cells."""
    f = {}
    c = cls('pimos_scsi_front_end')
    attrs = c.pool[7][1]
    f['class attributes'] = {attrs[i][1]: attrs[i + 2][1] for i in range(0, len(attrs), 3)}
    # U1
    f['240: Code 0, Dir ">", FileVer ".", Comment ""'] = has(
        'pimos_scsi_front_end', 'fep_attributes', 7,
        ['pmi 27  00 00 00', 'pmi 29  04 f8 8a   pool[2f] = ">"',
         'pmi 29  05 f8 8a   pool[30] = "."', 'pmi 29  06 f8 8a   pool[31] = ""'])
    f['240: OS is "SIMPOS " ++ :version(#simpos##version)'] = has(
        'pimos_scsi_front_end', 'fep_attributes', 7,
        ['pmi a9  00 f8 8a   pool[32] = #simpos##version', 'blt 25', 'pmi a0  00 03 00',
         'pmi 73  01 02 00', 'selector version/2', 'pmi a9  00 f8 86   pool[33] = #simpos##string',
         'blt 25', 'pmi a2  01 00 00', 'pmi a9  04 f8 84   pool[34] = "SIMPOS "',
         'pmi aa  00 00 00', 'pmi 43  04 00 00', 'pmi 4a  00 00 00', 'pmi 44  03 00 00',
         'pmi-atom get r76, []', 'pmi 73  02 03 00', 'selector append/3'])
    f['240: Host is :get_my_node(#simpos##network_node_name)'] = has(
        'pimos_scsi_front_end', 'fep_attributes', 7,
        ['pmi a9  00 f8 7d   pool[35] = #simpos##network_node_name', 'blt 25',
         'pmi a2  00 01 00', 'pmi 73  01 02 00', 'selector get_my_node/2'])
    f['240: FepVer is the class attribute version'] = has(
        'pimos_scsi_front_end', 'fep_attributes', 7,
        ['pmi a9  00 f8 54   pool[11] = #pimfep##pimos_scsi_front_end', 'blt 25',
         'pmi a1  02 02 00', 'pmi a1  01 01 00', 'pmi a2  00 02 00', 'pmi 75  03 04 00',
         'selector pimfep_version/4']) and has(
        'pimos_scsi_front_end', 'pimfep_version', 4,
        ['pmi dc  04 00 00', 'pmi-atom put r4, version', 'blt 27  03 04 04', 'pmi 23  04 00 00'])
    f['240: reply is a 9-vector {Id, 1, the seven in order}'] = has(
        'pimos_scsi_front_end', '$or$3', 4,
        ['pmi a0  06 02 00', 'pmi a0  05 03 00', 'pmi a0  04 04 00', 'pmi a0  03 05 00',
         'pmi a0  02 06 00', 'pmi a0  01 07 00', 'pmi a0  00 08 00', 'pmi 60', 'pmi b7  02 00 09',
         'pmi 44  00 00 00', 'pmi 47  00 00 01', 'pmi 44  08 00 00', 'pmi 44  07 00 00',
         'pmi 44  06 00 00', 'pmi 44  05 00 00', 'pmi 44  04 00 00', 'pmi 44  03 00 00',
         'pmi 44  02 00 00'])
    f['server clauses (length, command)'] = server_clauses()
    # U2
    f['login message: "PimosLoginHL1234" ++ RN ++ RP ++ UN ++ UP'] = has(
        'as_pimos_login_requester', 'create_message', 3,
        ['pmi a9  04 fb f9   pool[20] = "PimosLoginHL1234"', 'pmi aa  00 00 00',
         'pmi 43  04 00 00', 'pmi 4a  00 00 00', 'pmi 44  07 00 00', 'pmi 4a  00 00 00',
         'pmi 44  08 00 00', 'pmi 4a  00 00 00', 'pmi 44  00 00 00', 'pmi 4a  00 00 00',
         'pmi 44  01 00 00'])
    f['login message: RN, RP are :local_name and :user_password of the process user'] = has(
        'as_pimos_login_requester', 'create_message', 3,
        ['selector self/2', 'pmi a4  01 05 00', 'pmi a0  00 06 00', 'pmi 73  01 02 00',
         'selector user/2', 'pmi a4  01 06 00', 'pmi a0  00 07 00', 'pmi 73  01 02 00',
         'selector local_name/2', 'pmi a4  01 06 00', 'pmi a0  00 08 00', 'pmi 73  01 02 00',
         'selector user_password/2'])
    f['login message: elements 10-15 are set (H, L, four lengths)'] = [
        int(x.split()[2] + x.split()[3] + x.split()[4], 16) & 0xffff
        for x in lines('as_pimos_login_requester', 'create_message', 3)[0x43:0x51]
        if x.startswith('pmi a7  0') and x.split()[3] == '00' and x.split()[4][0] == '0'
        and int(x.split()[4], 16) >= 10]
    f['NI: Node of a local login is "local"'] = has(
        'pimos_remote_login_server', 'remote_node_name', 5,
        ['pmi-atom get r0, local_login', 'pmi 29  04 f9 7c   pool[25] = "local"'])
    f['NI: "IN" ++ lengths ++ Node ++ body, element 1 := length of Node'] = has(
        'pimos_remote_login_server', 'reassemble_message', 3,
        ['pmi a9  06 f7 a9   pool[2c] = "IN"', 'pmi aa  00 00 00', 'pmi 43  06 00 00',
         'pmi 4a  00 00 00', 'pmi 43  04 00 00', 'pmi 4a  00 00 00', 'pmi 44  01 00 00',
         'pmi 4a  00 00 00', 'pmi 43  05 00 00', 'pmi-atom get r76, []', 'pmi 73  02 03 00',
         'selector append/3', 'pmi a2  02 02 00', 'pmi a7  00 00 01', 'pmi a2  01 07 00',
         'blt 2b  02 00 01'])
    f['NI: element 0 := the key grant_socket gives'] = has(
        'pimos_remote_login_server', 'receive_message', 5,
        ['pmi 60  00 03 1f   -> grant_socket/4', 'pmi d3  06 00 00', 'pmi a2  04 04 00',
         'pmi a7  00 00 00', 'pmi a4  01 05 00', 'blt 2b  04 00 01'])
    # U3
    f['server io(0, _): From_fep ""'] = has(
        'pimos_remote_login_server', 'io', 4,
        ['pmi 27  00 00 00', 'pmi 29  02 ff 84   pool[10] = ""'])
    f['replier io(0, _): From_fep ""'] = has(
        'pimos_remote_login_replier', 'io', 4,
        ['pmi 27  00 00 00', 'pmi 29  02 ff 73   pool[11] = ""'])
    f['replier io(1, _): From_fep "\\x00" if sent, else "\\x01"'] = has(
        'pimos_remote_login_replier', 'check_status', 3,
        ['pmi-atom get r0, normal', 'pmi 29  02 fe 9e   pool[16] = "\\x00"'])
    f['server_type: "local" local_login, "lia" lia, "tcpip" tcpip'] = [
        x.split('= ')[1] for x in lines('pimos_remote_login_server', 'server_type', 2, (0x11,))
        if 'pool[' in x]
    f['simpos_user_device Dir falls back to ">"'] = has(
        'simpos_user_device', '$or$3', 2, ['pmi 29  00 ff 38   pool[14] = ">"'])
    f['simpos_user_device Dir from :remote_or_local(#simpos##pathname, ...)'] = has(
        'simpos_user_device', '$or$3', 2,
        ['selector root_path/3', 'pmi a9  00 ff 43   pool[13] = #simpos##pathname'])
    f['string io reply {Id, 1, From_fep}; abort gives {Id, 6}'] = has(
        'as_pimos_string_io_device', 'do_io', 6,
        ['pmi b3  00 00 00', 'pmi 44  00 00 00', 'pmi 47  00 00 01', 'pmi 44  03 00 00']) and has(
        'as_pimos_string_io_device', 'abort_string_io', 2,
        ['pmi b2  00 00 00', 'pmi 45  03 00 00', 'pmi 47  00 00 06'])
    # U4
    f['window handlers'] = [
        '%s/%d' % (p.name, p.arity) for p in cls('pimos_window_editor').preds
        if p.kind == PRIMARY and p.name in ('reshape', 'set_font', 'show')]
    f['pimos_standard_io_window io/4 keys'] = R.hash_keys(
        cls('pimos_standard_io_window'), pred(cls('pimos_standard_io_window'), 'io', 4))[0]
    # U5
    imm = {}
    for c2 in classes():
        for p in c2.preds:
            for _n, op, v in R.immediates(c2, p):
                # the two tables only name the codes; remote_pimfep_executor's
                # 900/901 number its own console texts ("900: Wel...")
                if 900 <= v <= 903 and op is not None and c2.name not in (
                        'fep_command_code_table', 'scsi_fep_macro', 'remote_pimfep_executor'):
                    imm.setdefault(v, set()).add('%s %s/%d' % (c2.name, p.name, p.arity))
    f['900-903 immediates'] = {k: sorted(v) for k, v in sorted(imm.items())}
    f['903 after close, dropped unless the link is a remote_fep'] = has(
        'as_pimos_device', 'close', 3,
        ['pmi b2  00 00 00', 'pmi 42  00 00 00', 'pmi 47  00 03 87']) and has(
        'fep_scsi_output', 'put', 4,
        ['pmi-atom put r0, remote_fep', 'blt 65  01 00 00']) and has(
        'fep_scsi_output', 'put', 4,
        ['pmi a7  01 03 87', 'blt 62  00 01 00', 'pmi d3  02 00 00',
         'pmi a9  00 ff 31   pool[11] = #pimfep##pimfep_message_log', 'blt 25',
         'pmi a2  00 00 00', 'pmi 75  01 02 00', 'selector log/2'])
    f['900 only to a remote_fep'] = has(
        'pimos_scsi_front_end', '$or$4', 3,
        ['pmi-atom put r0, remote_fep', 'pmi 73  01 02 00', 'selector fep_type/2',
         'pmi d3  03 00 00'])
    f['fep types'] = sorted({
        x.split(', ')[1] for cn in ('pimscsi_fep', 'pseudo_scsi_fep', 'nise_scsi_fep',
                                    'sline_fep', 'remote_pimfep_invoker')
        for i, x in enumerate(lines(cn, 'goal', 1))
        if x.startswith('pmi-atom put r0, ')
        and lines(cn, 'goal', 1)[i + 2].startswith('selector create/6')})
    # U6
    f['70: abort/3 with pimos_abort, no reply assembled'] = has(
        'pimos_scsi_front_end', 'abort_device', 4,
        ['selector abort_handler/2', 'pmi a4  02 01 00', 'pmi-atom put r1, pimos_abort',
         'pmi a2  00 00 00', 'pmi 75  02 03 00', 'selector abort/3']) and not any(
        'assemble' in x for x in lines('pimos_scsi_front_end', 'abort_device', 4))
    f['aborted timer request answers {Id, 6}'] = has(
        'pimos_timer', 'abort_timer', 3,
        ['pmi b2  00 00 00', 'pmi 45  04 00 00', 'pmi 47  00 00 06'])
    f['timer alarm answers {Id, 1, 9}'] = has(
        'pimos_timer', 'on_after', 4,
        ['pmi b3  00 00 00', 'pmi 44  01 00 00', 'pmi 47  00 00 01', 'pmi 47  00 00 09'],
        (0x11,))
    f['80 answers {Id, 11}'] = has(
        'pimos_scsi_front_end', 'refute_server_command', 3,
        ['pmi b2  00 00 00', 'pmi 43  04 00 00', 'pmi 47  00 00 0b'])
    return f


def main(argv):
    what = argv[0] if argv else ''
    if what == 'handlers':
        print('| Code | Name | PIMOS device (§2) | PSI handler |')
        print('|---|---|---|---|')
        for code, name, hs in handlers():
            print('| %d | %s | %s | %s |' % (
                code, name, '; '.join(h[0] for h in hs),
                '; '.join(('`%s`' % h[1]) + ('' if h[2] else ' **?**') for h in hs)))
        return 0
    if what == 'extra':
        keys, more = extra()
        print('server keys never sent by PIMOS: %r' % keys)
        for code, name, m in more:
            print('%4d %-18s %s' % (code, name, m))
        return 0
    if what == 'strings':
        print('| Class | Used in | Text | JIS words not in the alphanumeric row |')
        print('|---|---|---|---|')
        for cn, who, text, uni, words in login_strings():
            odd = sorted({'%04x %s' % (w, unicodedata.name(u, '?'))
                          for w, u in zip(words, uni) if w >> 8 != 0x23 and w != 0x2121})
            print('| `%s` | %s | `%s` | %s |' % (cn, ', '.join(who), text, '; '.join(odd)))
        return 0
    if what == 'facts':
        for k, v in facts().items():
            print('%s: %r' % (k, v))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
