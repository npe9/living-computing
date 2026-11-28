#!/usr/bin/env python3
"""SIMPOS file-system methods the held PSI FEP (pimfep##pimos_directory,
pimfep##pimos_file) sends when PIMOS's file and directory requests are
served from the PSI's own tree (psi/mendels.py's bridge, the FEP store
step, 2026-11-28), as kl0 models (Python): stand-ins, NOT SIMPOS.  The
tree is psi/simpos_fs.py's (OURS); the classes are the stand-ins
psi/standin/directory.esp and binary_file.esp.

Every selector and its argument order is the held cells' (each model's
docstring names the call site, `python3 -I psi/fepread/ptfread.py pimfep
pimos_directory` / `pimos_file`); every body is OURS, its meaning
INTERPOLATED from TR-524 PDF p36 (folio 35) Table 3, "Directory Methods
(class directory) :retrieve/c, :make/c, :delete/i, :undelete/i,
:find/i, :expunge/i" (PRINTED, names only) and PDF p9 (folio 8) on
versions.  LABELS has each model's grade.

Representation (OURS): a directory's `entries` are {Name, Node}; a
deleted file is moved to the directory's `deleted` list (TR-524 Table 3
lists undelete beside delete, so a deleted file is kept until an
expunge), and expunge/1 empties that list.
"""

LABELS = {
    ('simpos##directory', 'instance', 'delete_with_wildcard', 3):
        'INTERPOLATED (selector and order HELD, pimos_directory delete/4 @e8-ef; body OURS)',
    ('simpos##directory', 'instance', 'expunge', 1):
        'INTERPOLATED (selector HELD, pimos_directory expunge/3 @13f-142; TR-524 Table 3 :expunge/i; body OURS)',
    ('simpos##directory', 'class', 'parent_directory', 5):
        'INTERPOLATED (selector HELD, pimos_file open_file/4 @360; DirPath HELD-SOURCE cil ds_bep.esp:3116; '
        'Dir and It INFERENCE from remove/2; body OURS)',
    ('simpos##binary_file', 'class', 'make_only', 3):
        'INTERPOLATED (selector HELD, pimos_file write_open/4 @3f9; kappa2 BCKFIF.ESP:1501; failing on a taken '
        'name INFERENCE; body OURS)',
    ('simpos##binary_file', 'instance', 'open', 3):
        'INTERPOLATED (selector HELD, pimos_file write_open/4 @3fe; body OURS)',
    ('simpos##binary_file', 'instance', 'accessor', 2):
        'INTERPOLATED (selector HELD, pimos_file open_file/4 @36a; TR-524 App. A PRINTED interface; the file its '
        'own accessor OURS)',
    ('simpos##binary_file', 'instance', 'request_data_size', 2):
        'INTERPOLATED (selector HELD, pimos_file putb/4 @288; body OURS)',
    ('simpos##binary_file', 'instance', 'write_data', 2):
        'INTERPOLATED (selector HELD, pimos_file putb/4 @28c; kappa2 SRVCNF.ESP:423; body OURS)',
    ('simpos##binary_file', 'instance', 'write_next', 1):
        'INTERPOLATED (selector HELD, pimos_file putb/4 @28f; kappa2 KFILMP.ESP:594; body OURS)',
    ('simpos##binary_file', 'instance', 'close', 1):
        'INTERPOLATED (selector HELD, pimos_file close/2 @232; kappa2 SRVCNF.ESP:409; body OURS)',
    ('simpos##binary_file', 'instance', 'owner_name', 2):
        'INTERPOLATED (selector HELD, pimos_file get_describe_info/2 @3ab; the user OURS)',
    ('simpos##binary_file', 'instance', 'update_user_name', 2):
        'INTERPOLATED (selector HELD, pimos_file get_describe_info/2 @3af; the user OURS)',
    ('simpos##binary_file', 'instance', 'creation_date', 2):
        'INTERPOLATED (selector HELD, pimos_file get_describe_info/2 @3b3; the date OURS)',
    ('simpos##binary_file', 'instance', 'modification_date', 2):
        'INTERPOLATED (selector HELD, pimos_file get_describe_info/2 @3bc; the date OURS)',
    ('simpos##date_time', 'instance', 'get_string', 3):
        'INTERPOLATED (selector HELD, pimos_file get_describe_info/2 @3b8; the form INFERENCE from PIMOS\'s '
        'reader, fileutil.kl1:31-58)',
    ('simpos##binary_file', 'instance', 'link_counter', 2):
        'INTERPOLATED (selector HELD, pimos_file get_describe_info/2 @3c5; the count OURS)',
    ('simpos##standard_input_file', 'instance', 'getb', 3):
        'INTERPOLATED (selector and order HELD, pimos_file getb/4 @25f; body OURS)',
    ('simpos##standard_input_file', 'instance', 'getl', 2):
        'INTERPOLATED (selector HELD-SOURCE MENDELS mdl_check.esp:100; the line without its newline INFERENCE; '
        'body OURS)',
    ('simpos##standard_input_file', 'instance', 'end_of_input', 1):
        'INTERPOLATED (selector HELD, pimos_file getb/4 @240; the term reading kl0 Machine.input_end; the two '
        'readings OURS)',
}


def wildcard_match(pattern, name, version):
    """NAME (with VERSION) matches PATTERN: `*` any run of characters, a
    trailing `.N` a version (OURS: no held text gives SIMPOS's wildcard
    syntax; `*` is what PIMOS's own ls sends, docs/fep_services.md 2.3)."""
    import fnmatch
    parts = pattern.split('.')
    want = None
    if len(parts) >= 3 and parts[-1].isdigit():
        pattern, want = '.'.join(parts[:-1]), int(parts[-1])
    if want is not None and want != version:
        return False
    return fnmatch.fnmatchcase(name, pattern.replace('[', '[[]').replace('?', '[?]'))


def install(models, K):
    """Add the file-system models to kl0's SIMPOS_MODELS.  A send's
    arguments are in m.x[0..] after the receiver, the receiver last
    (OBSERVED: delete_with_wildcard/3's Wildcard in x[0], Dir in x[2])."""

    def directory(m, i):
        d = K.deref(m.x[i])
        if not isinstance(d, K.Instance) or d.cid != 'simpos##directory':
            raise K.Refusal('simpos', 'directory: receiver %r' % (d,))
        return d

    def string_arg(m, i, what):
        s = K.deref(m.x[i])
        if not isinstance(s, K.Str):
            raise K.Refusal('unbound argument' if isinstance(s, K.Var) else 'simpos',
                            'directory %s of %r' % (what, s))
        return s.text

    def items(t):
        out, t = [], K.deref(t)
        while isinstance(t, K.Cons):
            out.append(K.deref(t.args[0]))
            t = K.deref(t.args[1])
        return out

    def as_list(xs):
        out = K.NIL
        for x in reversed(xs):
            out = K.Cons(x, out)
        return out

    def delete_with_wildcard(m):
        """:delete_with_wildcard(Dir, Wildcard, Deleted).  HELD call site:
        pimos_directory delete/4 @e8-ef (PIMOS's 231, docs/fep_services.md
        2.3): Dir the device's directory_object, Wildcard the message's
        string, then `Deleted \\== []` (blt 65) before the reply {Id, 1}:
        a delete that matches nothing fails, and the device answers 5
        (as_pimos_device refute/3's second clause).  OURS: the files whose
        name matches (wildcard_match) are moved from the entries to the
        directory's deleted list, and Deleted is the list of them; a
        directory is not deleted (INFERENCE: TR-524 Table 3's delete is a
        file's)."""
        d = directory(m, 2)
        pat = string_arg(m, 0, 'delete_with_wildcard/3 wildcard')
        keep, gone = [], []
        for e in items(m.get_slot(d, 'entries')):
            node = K.deref(e.args[1])
            name = K.deref(e.args[0]).text
            if node.cid == 'simpos##binary_file' and wildcard_match(pat, name, m.get_slot(node, 'version')):
                gone.append(e)
            else:
                keep.append(e)
        if gone:
            m.set_slot(d, 'entries', as_list(keep))
            old = m.get_slot(d, 'deleted')
            m.set_slot(d, 'deleted', as_list(gone + (items(old) if isinstance(K.deref(old), K.Cons) else [])))
        return m.proceed() if m.unify(m.x[1], as_list([K.deref(e.args[1]) for e in gone])) else m.fail()

    def expunge(m):
        """:expunge(Dir).  HELD call site: pimos_directory expunge/3
        @13f-142 (PIMOS's 235), then the reply {Id, 1}.  OURS: the deleted
        list emptied (the files are gone for good)."""
        d = directory(m, 0)
        m.set_slot(d, 'deleted', K.NIL)
        return m.proceed()

    def root(m):
        r = m.get_slot(K.ClassRef('simpos##directory'), 'root')
        if not isinstance(r, K.Instance):
            raise K.Refusal('simpos', 'directory: no file system is mounted')
        return r

    def split(m, path, what):
        """An absolute PATH -> (its parent directory or None, the last name)."""
        if not path.startswith('>') or path == '>' or path.endswith('>'):
            raise K.Refusal('simpos', '%s of %r: not an absolute file pathname (OURS: no other '
                            'form is stood in)' % (what, path))
        d, base = path.rsplit('>', 1)
        return m.fs_walk(root(m), d[1:]), base

    def parent_directory(m):
        """:parent_directory(#directory, Path, Dir, It, DirPath).  HELD
        call sites: pimos_file open_file/4 @359-360 (a write or append
        open) and cil ds_bep.esp:3116 (HELD-SOURCE:
        `:parent_directory(#directory,Parent,_,_,Directory)`, then
        `:append(#string,[Directory,">",File_name],Pathname)`: DirPath is
        the directory's pathname).  The other two by their held uses,
        OBSERVED with this model (the FEP store step): It is what
        write_open/4 compares with the atom `root` (@3ed-3f0) and what its
        remove/2 gives :retrieve(#directory, X, It, Full) as the pathname
        (@1d9-1de), before is_directory/1 of X (a directory is not
        removed) and `:remove(Dir, It, _)` (@1e4-1ea, Dir the receiver:
        sent to anything else it refuses, OBSERVED); so Dir is the
        directory object holding the file and It the file's pathname
        (INFERENCE from those uses; the atom `root`, for a Path naming the
        root itself, is never given here, OURS).  A parent that does not
        exist fails (the open is answered 5)."""
        path = K.deref(m.x[0])
        if not isinstance(path, K.Str):
            raise K.Refusal('unbound argument' if isinstance(path, K.Var) else 'simpos',
                            'directory parent_directory/5 of %r' % (path,))
        d, base = split(m, path.text, 'directory parent_directory/5')
        if d is None or d.cid != 'simpos##directory':
            return m.fail()
        full = m.get_slot(d, 'full_name').text
        ok = (m.unify(m.x[1], d) and m.unify(m.x[2], K.Str(path.text))
              and m.unify(m.x[3], K.Str(full)))
        return m.proceed() if ok else m.fail()

    def entries_named(m, d, name):
        return [K.deref(e.args[1]) for e in items(m.get_slot(d, 'entries'))
                if K.deref(e.args[0]).text == name]

    def make_only(m):
        """:make_only(#binary_file, File, Path).  HELD call sites:
        pimos_file write_open/4 @3f5-3f9 and @407-40c (the second after
        remove/2 when the first fails), append_open/4; kappa2 BCKFIF.ESP
        :1501 (HELD-SOURCE, `:make_only(#binary_file,File,Path)`).
        INFERENCE from write_open/4's order (make_only, else remove the
        old file and make_only again): it makes a new, empty file and
        fails when the name is taken.  OURS: version 1, size 0, the
        contents an empty 16-bit string, entered in the parent
        directory."""
        path = K.deref(m.x[1])
        if not isinstance(path, K.Str):
            raise K.Refusal('unbound argument' if isinstance(path, K.Var) else 'simpos',
                            'binary_file make_only/3 of %r' % (path,))
        d, base = split(m, path.text, 'binary_file make_only/3')
        if d is None or d.cid != 'simpos##directory' or entries_named(m, d, base):
            return m.fail()
        f = K.new_instance(m.lib, 'simpos##binary_file', m)
        for k, v in (('name', K.Str(base)), ('version', 1), ('size', 0),
                     ('full_name', K.Str('%s>%s.1' % (m.get_slot(d, 'full_name').text, base))),
                     ('contents', K.Str('')), ('directory', d)):
            m.set_slot(f, k, v)
        m.set_slot(d, 'entries', K.Cons(K.Vec([K.Str(base), f]), m.get_slot(d, 'entries')))
        return m.proceed() if m.unify(m.x[0], f) else m.fail()

    def binary_file(m, i, what):
        f = K.deref(m.x[i])
        if not isinstance(f, K.Instance) or f.cid != 'simpos##binary_file':
            raise K.Refusal('simpos', 'binary_file %s: receiver %r' % (what, f))
        return f

    def file_open(m):
        """:open(File, Share, Mode).  HELD call site: pimos_file
        write_open/4 @3fb-3fe and @40e-411 (`shared`, `suppress`), after
        make_only/3.  OURS: the file marked open (`opened`); the modes are
        kept, not consulted."""
        f = binary_file(m, 2, 'open/3')
        m.set_slot(f, 'opened', K.Vec([K.deref(m.x[0]), K.deref(m.x[1])]))
        return m.proceed()

    def accessor(m):
        """:accessor(File, Accessor).  HELD call sites: pimos_file
        open_file/4 @36a (kept in the device's slot `accessor`) and putb/4
        @284, @29c.  TR-524 PDF p37 (folio 36) App. A, PRINTED: binary_file
        has the nature binary_file_accessor and the external method
        accessor/2.  OURS: the file is its own accessor."""
        f = binary_file(m, 1, 'accessor/2')
        return m.proceed() if m.unify(m.x[0], f) else m.fail()

    def request_data_size(m):
        """:request_data_size(Accessor, Bytes).  HELD call sites: pimos_file
        putb/4 @288 and putb_loop/5 @45d, @472 (3,968 bytes, 0xf80, for each
        whole piece of 1,984 characters, 0x7c0).  OURS: kept, the data
        written is what write_data/2 gives."""
        f = binary_file(m, 1, 'request_data_size/2')
        n = K.deref(m.x[0])
        if not isinstance(n, int):
            raise K.Refusal('simpos', 'binary_file request_data_size/2 of %r' % (n,))
        m.set_slot(f, 'request', n)
        return m.proceed()

    def write_data(m):
        """:write_data(Accessor, String).  HELD call sites: pimos_file
        putb/4 @28c, putb_loop/5 @461, @476; kappa2 SRVCNF.ESP:423
        (HELD-SOURCE, then close/1).  OURS: the string held for the next
        write_next/1."""
        f = binary_file(m, 1, 'write_data/2')
        s = K.deref(m.x[0])
        if not isinstance(s, K.Str):
            raise K.Refusal('unbound argument' if isinstance(s, K.Var) else 'simpos',
                            'binary_file write_data/2 of %r' % (s,))
        m.set_slot(f, 'pending', s)
        return m.proceed()

    def write_next(m):
        """:write_next(Accessor).  HELD call sites: pimos_file putb/4 @28f,
        putb_loop/5 @464, @479; kappa2 KFILMP.ESP:594 (HELD-SOURCE, after
        set_data_buffer/2).  OURS: the held string appended to the file's
        contents (16-bit codes, as psi/simpos_fs.py's text files), its
        size two bytes a code."""
        f = binary_file(m, 0, 'write_next/1')
        if K.deref(m.get_slot(f, 'opened')) == 0:
            raise K.Refusal('simpos', 'binary_file write_next/1: the file is not open')
        s = K.deref(m.get_slot(f, 'pending'))
        if not isinstance(s, K.Str):
            raise K.Refusal('simpos', 'binary_file write_next/1 with no write_data/2 before it')
        c = K.deref(m.get_slot(f, 'contents'))
        new = K.Str('')
        new.set_codes((c.codes() if isinstance(c, K.Str) else []) + s.codes())
        m.set_slot(f, 'contents', new)
        m.set_slot(f, 'size', 2 * len(new.codes()))
        m.set_slot(f, 'pending', 0)
        return m.proceed()

    def file_close(m):
        """:close(File).  HELD call site: pimos_file close/2 @232 (the
        after-demon of close/3, PIMOS's 60, for a binary_file); kappa2
        SRVCNF.ESP:409, :424 (HELD-SOURCE).  OURS: the file no longer
        open."""
        f = binary_file(m, 0, 'close/1')
        m.set_slot(f, 'opened', 0)
        return m.proceed()

    def input_stream(m, i, what):
        s = K.deref(m.x[i])
        if not isinstance(s, K.Instance) or s.cid != 'simpos##standard_input_file':
            raise K.Refusal('simpos', 'standard_input_file %s: receiver %r' % (what, s))
        f = m.get_slot(s, 'file')
        text = m.get_slot(f, 'contents') if isinstance(f, K.Instance) else None
        if not isinstance(text, K.Str):
            raise K.Refusal('simpos', 'standard_input_file %s: %r holds no contents here' % (what, f))
        return s, text.codes()

    def input_getb(m):
        """:getb(In, Buffer, N).  HELD call site: pimos_file local getb/4
        @259-25f (PIMOS's 210: Buffer a new 16-bit string of the message's
        Size, then the reply {Id, 1, substring(Buffer, 0, N)}; after
        end_of_input/1, which answers {Id, 2, ""}).  OURS: up to Size
        codes from the stream's character position (`chars`) put in
        Buffer, N how many."""
        s, codes = input_stream(m, 2, 'getb/3')
        buf = K.deref(m.x[0])
        if not isinstance(buf, K.Str):
            raise K.Refusal('simpos', 'standard_input_file getb/3 into %r' % (buf,))
        at = m.get_slot(s, 'chars')
        room = buf.codes()
        got = codes[at:at + len(room)]
        buf.set_codes(got + room[len(got):])
        m.set_slot(s, 'chars', at + len(got))
        return m.proceed() if m.unify(m.x[1], len(got)) else m.fail()

    def input_getl(m):
        """:getl(In, Line).  HELD-SOURCE call site: MENDELS mdl_check.esp
        :97-100 (`:end_of_input(File)` tested first, then `:getl(File,
        LineS)` on TEMP>compiler.msg, opened by med_utility open_file/5).
        INFERENCE: the next line without its newline (0x000a); OURS: fails
        at the end."""
        s, codes = input_stream(m, 1, 'getl/2')
        at = m.get_slot(s, 'chars')
        if at >= len(codes):
            return m.fail()
        end = codes.index(0x0a, at) if 0x0a in codes[at:] else len(codes)
        line = K.Str('')
        line.set_codes(codes[at:end])
        m.set_slot(s, 'chars', min(end + 1, len(codes)))
        return m.proceed() if m.unify(m.x[0], line) else m.fail()

    term_end = models[('simpos##standard_input_file', 'instance', 'end_of_input', 1)]

    def input_end(m):
        """:end_of_input(In), in two readings (OURS): a stream from which a
        term has been read (gett/2, `position` > 0) is at its end when
        every term has been read (kl0 Machine.input_end, unchanged); any
        other is at its end when every character has been read (`chars`,
        getb/3 and getl/2).  So a fresh stream is at its end only when
        its file is empty.  HELD call sites of the character reading:
        pimos_file local getb/4 @240 and end_of_file/4 @207 (PIMOS's 210
        and 220 on any file, an object file too), MENDELS mdl_check.esp:97
        (before getl/2)."""
        s = K.deref(m.x[0])
        if isinstance(s, K.Instance) and s.cid == 'simpos##standard_input_file' \
                and m.get_slot(s, 'position') > 0:
            return term_end(m)
        s, codes = input_stream(m, 0, 'end_of_input/1')
        return m.proceed() if m.get_slot(s, 'chars') >= len(codes) else m.fail()

    def file_user(m):
        """:owner_name(File, Name) and :update_user_name(File, Name).  HELD
        call sites: pimos_file get_describe_info/2 @3ab, @3af (PIMOS's
        222, the first two fields of the reply).  OURS: the PSI's one user,
        psi/simpos_fs.py USER (pmpsi), for every file: no held file
        records its owner."""
        import simpos_fs
        binary_file(m, 1, 'owner_name/2')
        return m.proceed() if m.unify(m.x[0], K.Str(simpos_fs.USER)) else m.fail()

    def file_date(m):
        """:creation_date(File, Date) and :modification_date(File, Date).
        HELD call sites: pimos_file get_describe_info/2 @3b3, @3bc, each
        then `:get_string(Date, DateString, TimeString)`.  OURS: a
        simpos##date_time made by its now/2 (psi/standin/date_time.esp:
        the class slots, 33742 and 0, the PSI's clock that does not run),
        the same for every file."""
        binary_file(m, 1, 'creation_date/2')
        C = K.ClassRef('simpos##date_time')
        d = K.new_instance(m.lib, 'simpos##date_time', m)
        m.set_slot(d, 'date', m.get_slot(C, 'date'))
        m.set_slot(d, 'time', m.get_slot(C, 'time'))
        return m.proceed() if m.unify(m.x[0], d) else m.fail()

    MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()

    def date_get_string(m):
        """:get_string(DateTime, DateString, TimeString).  HELD call sites:
        pimos_file get_describe_info/2 @3b8, @3c1 (the third to sixth
        fields of 222's reply).  The form is PIMOS's reader's, not SIMPOS's
        (INFERENCE): DD-Mon-YY and HH:MM:SS, what PIMOS's
        normalize_date_time takes apart (library/utility/fileutil.kl1:
        31-58, ref/pimm/fep.py attribute_string).  The date is the days
        from 01-Jan-1901 and the time the milliseconds from midnight
        (psi/standin/date_time.esp's head comment)."""
        import datetime
        d = K.deref(m.x[2])
        if not isinstance(d, K.Instance) or d.cid != 'simpos##date_time':
            raise K.Refusal('simpos', 'date_time get_string/3: receiver %r' % (d,))
        day = datetime.date(1901, 1, 1) + datetime.timedelta(m.get_slot(d, 'date'))
        ms = m.get_slot(d, 'time')
        ds = '%02d-%s-%02d' % (day.day, MONTHS[day.month - 1], day.year % 100)
        ts = '%02d:%02d:%02d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60)
        return m.proceed() if m.unify(m.x[0], K.Str(ds)) and m.unify(m.x[1], K.Str(ts)) else m.fail()

    def link_counter(m):
        """:link_counter(File, N).  HELD call site: pimos_file
        get_describe_info/2 @3c5 (222's seventh field).  OURS: 1, as
        ref/pimm/fep.py's home files answer."""
        binary_file(m, 1, 'link_counter/2')
        return m.proceed() if m.unify(m.x[0], 1) else m.fail()

    table = [
        (('simpos##binary_file', 'instance', 'owner_name', 2), file_user),
        (('simpos##binary_file', 'instance', 'update_user_name', 2), file_user),
        (('simpos##binary_file', 'instance', 'creation_date', 2), file_date),
        (('simpos##binary_file', 'instance', 'modification_date', 2), file_date),
        (('simpos##date_time', 'instance', 'get_string', 3), date_get_string),
        (('simpos##binary_file', 'instance', 'link_counter', 2), link_counter),
        (('simpos##standard_input_file', 'instance', 'getb', 3), input_getb),
        (('simpos##standard_input_file', 'instance', 'getl', 2), input_getl),
        (('simpos##standard_input_file', 'instance', 'end_of_input', 1), input_end),
        (('simpos##directory', 'instance', 'delete_with_wildcard', 3), delete_with_wildcard),
        (('simpos##directory', 'instance', 'expunge', 1), expunge),
        (('simpos##directory', 'class', 'parent_directory', 5), parent_directory),
        (('simpos##binary_file', 'class', 'make_only', 3), make_only),
        (('simpos##binary_file', 'instance', 'open', 3), file_open),
        (('simpos##binary_file', 'instance', 'accessor', 2), accessor),
        (('simpos##binary_file', 'instance', 'request_data_size', 2), request_data_size),
        (('simpos##binary_file', 'instance', 'write_data', 2), write_data),
        (('simpos##binary_file', 'instance', 'write_next', 1), write_next),
        (('simpos##binary_file', 'instance', 'close', 1), file_close),
    ]
    for key, f in table:
        f.__module__ = __name__
        models[key] = f
