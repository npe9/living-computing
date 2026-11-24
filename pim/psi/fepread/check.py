#!/usr/bin/env python3
"""Self-check of psi/fepread: pins every fact docs/fep_services.md §6
reports about pimfep.ptf.  OURS.

    python3 -I psi/fepread/check.py          (under a second; pimfep and the
                                              paragraph witnesses only)

Shown to discriminate (2026-11-24, by patching the loaded data in
memory, nothing on disk): turning the `27 00 00 00` of fep_attributes/7
into `27 00 00 01` fails "240: Code 0 ..." and nothing else; dropping
the instance method reshape/7 from pimos_window_editor fails "handler
table: all 63 rows resolved", "window handlers" and nothing else; a
witness with one operand byte changed fails "witnesses".  Observed, not
predicted.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptfread as R      # noqa: E402
import fepfacts as F     # noqa: E402
import witness           # noqa: E402

TRUE = [
    '240: Code 0, Dir ">", FileVer ".", Comment ""',
    '240: OS is "SIMPOS " ++ :version(#simpos##version)',
    '240: Host is :get_my_node(#simpos##network_node_name)',
    '240: FepVer is the class attribute version',
    '240: reply is a 9-vector {Id, 1, the seven in order}',
    'login message: "PimosLoginHL1234" ++ RN ++ RP ++ UN ++ UP',
    'login message: RN, RP are :local_name and :user_password of the process user',
    'NI: Node of a local login is "local"',
    'NI: "IN" ++ lengths ++ Node ++ body, element 1 := length of Node',
    'NI: element 0 := the key grant_socket gives',
    'server io(0, _): From_fep ""',
    'replier io(0, _): From_fep ""',
    'replier io(1, _): From_fep "\\x00" if sent, else "\\x01"',
    'simpos_user_device Dir falls back to ">"',
    'simpos_user_device Dir from :remote_or_local(#simpos##pathname, ...)',
    'string io reply {Id, 1, From_fep}; abort gives {Id, 6}',
    '903 after close, dropped unless the link is a remote_fep',
    '900 only to a remote_fep',
    '70: abort/3 with pimos_abort, no reply assembled',
    'aborted timer request answers {Id, 6}',
    'timer alarm answers {Id, 1, 9}',
    '80 answers {Id, 11}',
]
EQUAL = {
    'class attributes': {'error_report_mode': 'off', 'comment': 'mkdir/rmdir, all_device_end',
                         'creation_date': '14-Jan-94', 'version': 'V0.45'},
    'server clauses (length, command)': [(6, 103), (3, 240), (2, 70), (2, 902), (2, 80),
                                         (2, 901)],
    'login message: elements 10-15 are set (H, L, four lengths)': [10, 11, 12, 13, 14, 15],
    'server_type: "local" local_login, "lia" lia, "tcpip" tcpip': ['"local"', '"lia"',
                                                                   '"tcpip"'],
    'window handlers': ['set_font/4', 'show/3', 'reshape/7'],
    'pimos_standard_io_window io/4 keys': ['104', '60', '130', '124', '121', '141', '142',
                                           '111', '110', '112', '145'],
    'fep types': ['nise_scsi', 'pimscsi', 'pseudo_scsi', 'remote_fep', 'sline'],
    '900-903 immediates': {
        900: ['pimfep_message_receiver refute_internal_command/4',
              'pimos_scsi_front_end $or$4/3', 'pimos_scsi_front_end create_device/4'],
        901: ['pimfep_message_receiver check_end/2',
              'pimfep_message_receiver refute_internal_command/4',
              'pimos_scsi_front_end check_fep_end/4', 'pimos_scsi_front_end command_type/2',
              'pimos_scsi_front_end refute_server_command/3'],
        902: ['pimfep_message_receiver receive_first_message/2',
              'pimos_scsi_front_end check_fep_end/4', 'pimos_scsi_front_end command_type/2',
              'pimos_scsi_front_end refute_server_command/3'],
        903: ['as_pimos_device close/3', 'fep_scsi_output put/4',
              'pimfep_message_receiver refute_internal_command/4']},
}
# (classes, classes whose pool fills cells 2..h2-1, class references,
#  class references naming a class id or self) for pimfep
POOL = (47, 47, 255, 255)
# (predicates, with a hash table, misses, misses among those with a table)
SPAN = (1046, 6, 0, 0)
LOGIN_TEXTS = [
    'Enter FEP node name--------->', 'Enter your PIMOS user name-->',
    'Enter your PIMOS password--->', 'Pimos remote login ', 'font:test_11.font',
    'me:pimos.feps', 'PIMOS FEPs', 'me:pimos.uids', 'PIMOS USERs', 'ABORT', 'close', 'exit',
    'local', 'Receive timeout.', 'Network error.', 'Network error', 'Illigal input.',
    'Unknown FEP node name.', 'PimosLoginHL1234', 'PimosLogin', 'Your request is accepted.',
    'IN', 'lia', 'tcpip']


def run():
    out = []

    def ok(name, cond, got=None):
        out.append((name, bool(cond), got))

    f = F.facts()
    for k in TRUE:
        ok(k, f.get(k) is True, f.get(k))
    for k, v in EQUAL.items():
        ok(k, f.get(k) == v, f.get(k))
    got = R.pool_check(['pimfep'])
    ok('pool: cells 2..h2-1, class references', got == POOL, got)
    got = R.span_check(['pimfep'])
    ok('hash tables span mask+1 + 2*keys + 2 cells', got == SPAN, got)
    rows = F.handlers()
    ok('handler table: 63 rows', len(rows) == 63 and len({r[0] for r in rows}) == 63, len(rows))
    bad = [(r[0], h) for r in rows for h in r[2] if not h[2]]
    ok('handler table: all 63 rows resolved', not bad, bad)
    got = F.extra()
    ok('handled on the PSI, never sent by PIMOS', got == ([901, 902], [
        (114, 'ungetb', 'pimos_file ungetb/4')]), got)
    ls = F.login_strings()
    texts = {x[2] for x in ls}
    ok('login strings', len(ls) == 52 and all(t in texts for t in LOGIN_TEXTS),
       (len(ls), [t for t in LOGIN_TEXTS if t not in texts]))
    minus = [x for x in ls if 0x215d in x[4]]
    ok('the prompts use JIS 215d (MINUS SIGN), not a hyphen',
       len(minus) == 3 and all('−' in x[3] for x in minus), len(minus))
    bad = witness.check()
    ok('witnesses', not bad, bad)
    return out


def main(argv):
    out = run()
    bad = [x for x in out if not x[1]]
    for name, _c, got in bad:
        print('fepread: FAIL %s: got %r' % (name, got))
    if not bad:
        print('fepread: PASS (%d checks: pimfep.ptf read for fep_services.md §6; '
              '%d opcode witnesses)' % (len(out), len(witness.W)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
