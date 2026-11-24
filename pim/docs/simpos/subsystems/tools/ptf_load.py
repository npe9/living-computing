import sys, os, glob, re
"""Loader for the ptf reader's kl0 runs (2026-11-24 dive). Set PTF_HELD to a directory made by
`python3 -I psi/held.py extract DIR`, and PAPYRUS_PAK to the directory holding papyrus's
`*.pak.1` (from its inner source.tar, demo/PACKAGE). Read-only use of asm/ptfdump.py and psi/."""
PIM=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..'))
sys.path[:0]=[PIM+'/asm',PIM+'/psi']
import ptfdump as P, held, librarian as LB
W=os.environ.get('PTF_HELD','')
PAP=os.environ.get('PAPYRUS_PAK','')
PAPFILES=sorted(glob.glob(PAP+'/*.pak.1'))
def lib():
    L=LB.Librarian()
    L.load_held(root=W)
    for f in PAPFILES:
        L.load_ptf(open(f,'rb').read(), 'papyrus:'+os.path.basename(f))
    return L
def records():
    out={}
    for p in held.PTF:
        n,a,recs=P.parse_bytes(open(held.ptf_path(W,p),'rb').read())
        for r in recs: out[r['id']]=r
    for f in PAPFILES:
        n,a,recs=P.parse_bytes(open(f,'rb').read())
        for r in recs: out[r['id']]=r
    return out
JIS=re.compile(r'<([0-9a-f]{4})>')
def dejis(s):
    def f(m):
        w=int(m.group(1),16)
        try: return bytes((w>>8|0x80,(w&255)|0x80)).decode('euc_jp')
        except Exception: return m.group(0)
    return JIS.sub(f,s)
