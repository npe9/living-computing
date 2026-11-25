"""Generate the selector dictionary (appendix A) and per-class surface table (§2.x)
of pim/docs/simpos/subsystems/window.md from coverage_window.tsv + the notes TSVs.
Run: python3 -I gen.py  (reads notes/ coverage/ and ../required/; writes coverage/out/)."""
import csv,glob,collections,re
import os
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
os.makedirs(S+'coverage/out', exist_ok=True)
R=os.path.dirname(S.rstrip('/'))+'/required/'
cov=list(csv.DictReader(open(S+'coverage/coverage_window.tsv'),delimiter='\t'))
req={}
for r in csv.DictReader(open(R+'requirements.tsv'),delimiter='\t'):
    req[(r['class'],r['kind'],r['method'],r['arity'])]=r
part=[r['class'] for r in csv.DictReader(open(S+'coverage/partition_window.tsv'),delimiter='\t')]
other=set()
for p in ('librarian','shell','other'):
    for r in csv.DictReader(open(S+'coverage/partition_%s.tsv'%p),delimiter='\t'): other.add(r['class'])
# application classes of TM-115 etc. whose methods are NOT SIMPOS's
appcls={'font_inferior_window','font_superior_window','general_font','edited_font','font_executive','font_graphics_window','as_edit_pattern_window','parameters_display_menu'}
rank={'PRINTED':0,'PRINTED-INTERFACE':1,'PROSE':2,'SCREENSHOT':3,'USAGE':4,'INFERENCE':5,'COPY':4}
def gr(g):
    g=(g or '').upper()
    for k in sorted(rank,key=len,reverse=True):
        if g.startswith(k): return rank[k],k
    return 9,g
def shortv(v):
    v=v or ''
    m=re.search(r'compiled (\d{4})',v)
    if m: return 'ptf %s'%m.group(1)
    if 'held IFS' in v: return 'held 3.x-7.x'
    for pat,rep in ((r'SIMPOS 1\.00|1985 SIMPOS 1\.0|^1\.0 1985','1.0 (1985)'),(r'1984','1984 design'),(r'v2\.50|1986-09','2.50 (1986)'),(r'1986-04','2.0 (1986)'),(r'5\.x 1989','5.x (1989)'),(r'WINCS|1989-91','PSI-II (1989)'),(r'6\.1 patch','6.1 (1991)'),(r'^A00','A00 (video)')):
        if re.search(pat,v): return rep
    return re.sub(r'\s+',' ',v)[:24]
ev=collections.defaultdict(list)
for f in glob.glob(S+'notes/*.tsv'):
    src=f.split('/')[-1][:-4]
    for r in csv.DictReader(open(f),delimiter='\t'):
        if r['kind'] not in ('imethod','cmethod'): continue
        m,a=r['member'].strip(':'),(r['arity'] or '').strip()
        if '/' in m and not a: m,a=m.rsplit('/',1)
        if 'CESP' in (r['meaning'] or '')+(r['natures_or_slots'] or ''): continue
        c=r['class'].strip()
        if c in other or c in appcls: continue          # another subsystem's or an application's method
        if src=='video' and m=='size': continue          # :size(File,..) is a file method
        ev[(m,a)].append((gr(r['grade']),r,src))
def clip(s,n=150):
    s=re.sub(r'\s+',' ',(s or '')).replace('|','\\|')
    return s if len(s)<=n else s[:n-1]+'…'
def esc(s): return re.sub(r'\s+',' ',(s or '')).replace('|','\\|')
OVR={('create','2'):'class-method constructor without options (PRINTED-INTERFACE TM-125 p13); see §3.1 (window), §2.8 (standard_io_buffer)',
     ('create','3'):'class-method constructor (PRINTED-INTERFACE TM-125 p13-14); per-class argument order in §3.1 (windows: options list first; files/buffers/fonts differ)',
     ('create','4'):'pmacs_window (Opts,_,^W) and editor_text_buffer (^Buf,Name,Size) variants (USAGE kwic-esp src/inEditor1.esp:151-152 for pmacs_window, cal-esp/deb2.12/dmenu.esp:1214; disc/exshow.esp:23-25 sends pmacs_window create/3 and editor_text_buffer create/4, corrected 2026-11-24, re-read 2026-11-25); see §2.11, §3.1',
     ('close_input','1'):'close a standard_input_file opened with create/3 (USAGE: cal-esp/cal2.12/control.esp:193)',
     ('close_output','1'):'close (and write out) a standard_output_file (USAGE: cal-esp/cal2.12/control.esp:360)',
     ('get_slot','3'):'(INFERENCE) ESP object-level slot access by name, inherited by every class (not window-specific); see shell.md',
     ('set_slot','3'):'(INFERENCE) ESP object-level slot assignment by name (not window-specific); see shell.md',
     ('new','2'):'ESP allocator :new(Class,Obj) (not window-specific; TM-115 p12, TM-134 p67)',
     ('goal','1'):'font_editor program entry (as_program protocol; see shell.md)',
     ('beep','1'):'ring the bell once (USAGE; pimfep device command beep/3 is implemented by it, ptf.md W6; the login requester beeps twice, fep_services.md §6.9)',
     ('flash','1'):'make buffered output visible now (USAGE: after:putt/putf demons call it, cil/src/es_trc.esp:1401-1420; library_utility sets a flash flag iff the output object answers flash/1, ifs_libshell.md §4.1.1); INFERENCE on the exact effect',
     ('size','2'):'standard_io_buffer: :size(Buf,N) character count, used after :reread before :getb (USAGE cil/src/ds_bep.esp:1488-1491)',
     ('draw_rectangle','7'):'W,X,Y,Wd,Ht,Width,Style (USAGE call site fuzclust/fuzclust/src/window.net:102; §2.5)',
     ('draw_line','6'):'W,X1,Y1,X2,Y2,Width at gog-esp/KE_WINDOW.ESP:453 (USAGE call site); W,..,Op in paragraph (ptf); VARIANT, §2.5',
     ('draw_graph','2'):'W,[(X,Y),...] polyline (USAGE call site kwic-esp-002/kwic-esp/src/scrolls.esp:1135; §2.5)',
     ('reread','1'):'standard_io_buffer: rewind to read back what was written (USAGE call site cil/src/ds_bep.esp:1488; §2.8)',
     ('set_name','2'):'(W,String) window name, distinct from title (USAGE call site euod/RULED/ruled1.esp:623; meaning INFERENCE; §2.2)',
     ('kill','2'):'c:kill(#editor_text_buffer,BufferName) delete a pool buffer by name (USAGE call site cal-esp/cal2.12/file.esp:255; §2.11)',
     ('get_buffer_instance_list','2'):'c: list of pool buffers (USAGE call site cil/src/ms_mdm.esp:1646; §2.11)',
     ('set_current_buffer','2'):'(Editor,Buf) make Buf current (USAGE call site kappa2/kappa2/utility/mdu/ACCESS.ESP:653; §2.11)',
     ('find_file','2'):'(Editor,Path) visit a file in a buffer (USAGE call site cil/src/ds_edt.esp:915; §2.11)',
     ('getc','2'):'read one character code (USAGE: fdd_utility on screen, simpos.wmv esp@143; gog-esp/CGS_UTIL.ESP:393)',
    }
sel=collections.OrderedDict()
for r in cov:
    key=(r['method'],r['arity'])
    d=sel.setdefault(key,{'uses':0,'classes':[],'kinds':set(),'status':collections.Counter()})
    d['uses']+=int(r['uses']); d['classes'].append(r['class']); d['kinds'].add(r['kind']); d['status'][r['status']]+=1
wp=set(part)|{'window',''}
def wish(e):
    c=e[1]['class'].strip('{}')
    return 0 if (c in wp or 'window' in c or 'menu' in c or c.startswith('{') or 'editor' in c or 'buffer' in c) else 1
out=['| selector | c/i | uses | meaning | grade | citation (notes) | version |','|---|---|---|---|---|---|---|']
unspec=[]
for (m,a),d in sorted(sel.items(),key=lambda x:(x[0][0],int(x[0][1] or 0))):
    kinds=''.join(sorted('c' if k=='class' else 'i' for k in d['kinds']))
    if (m,a) in OVR:
        gm=re.search(r'PRINTED-INTERFACE|PRINTED|PROSE|USAGE|INFERENCE',OVR[(m,a)])
        out.append('| `%s/%s` | %s | %d | %s | %s | (in meaning) | — |'%(m,a,kinds,d['uses'],OVR[(m,a)],gm.group(0) if gm else 'INFERENCE')); continue
    E=sorted(ev.get((m,a),[]),key=lambda x:(x[0][0]>3,wish(x),x[0][0]))
    doc=[e for e in E if e[0][0]<=3]
    use=[e for e in E if e[0][0]>=4]
    rowsout=([doc[0]] if doc else [])+([use[0]] if use else [])
    if not rowsout:
        ex=''
        for c in d['classes']:
            for kk in ('instance','class'):
                rr=req.get((c,kk,m,a))
                if rr and not ex: ex=rr['example_site']
        unspec.append((m,a,d['uses'],ex,d['classes']))
        out.append('| `%s/%s` | %s | %d | **UNSPECIFIED** | — | first use %s | — |'%(m,a,kinds,d['uses'],ex)); continue
    first=True
    for (rk,g),r,src in rowsout:
        cls=r['class']
        mean=clip(('[%s] '%cls if cls else '')+r['meaning'])
        out.append('| %s | %s | %s | %s | %s | %s (%s) | %s |'%(('`%s/%s`'%(m,a)) if first else '″',kinds if first else '',d['uses'] if first else '',mean,g,esc(r['citation']),src,shortv(r['version_or_year'])))
        first=False
open(S+'coverage/out/selectors.md','w').write('\n'.join(out)+'\n')
open(S+'coverage/out/unspec.tsv','w').write('\n'.join('%s/%s\t%d\t%s\t%s'%(m,a,u,ex,','.join(cs)) for m,a,u,ex,cs in sorted(unspec,key=lambda x:-x[2]))+'\n')
o2=['| class | progs | tier | methods sent to it (`c:` class method; number = uses; status D DOC-class, d DOC-unowned, U USAGE, u USAGE-unowned, N NONE) |','|---|---|---|---|']
pt={r['class']:r for r in csv.DictReader(open(S+'coverage/partition_window.tsv'),delimiter='\t')}
st={'DOC-class':'D','DOC-unowned':'d','USAGE':'U','USAGE-unowned':'u','NONE':'N'}
bycls=collections.defaultdict(list)
for r in cov: bycls[r['class']].append(r)
for c in part:
    L=bycls.get(c,[])
    s=', '.join('%s`%s/%s` %s%s'%('c:' if r['kind']=='class' else '',r['method'],r['arity'],r['uses'],st[r['status']]) for r in sorted(L,key=lambda r:(r['kind']!='class',-int(r['uses']))))
    o2.append('| `%s` | %s | %s | %s |'%(c,pt[c]['n_programs'],pt[c]['tier'].split(':')[0],s or '(nature or reference only)'))
open(S+'coverage/out/perclass.md','w').write('\n'.join(o2)+'\n')
print(len(out),len(o2),len(unspec))
