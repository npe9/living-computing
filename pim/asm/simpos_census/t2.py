import sys; sys.path.insert(0, sys.argv[1]); import esplex
def show(t):
    k=t[0]
    if k in('var','atom','num'): return t[1]
    if k=='str': return '"%s"'%t[1]
    if k=='cmp': return '%s(%s)'%(t[1], ', '.join(show(a) for a in t[2]))
    if k=='list': return '[%s%s]'%(', '.join(show(a) for a in t[1]), ('|'+show(t[2])) if t[2] else '')
    if k=='brace': return '{%s}'%show(t[1])
text,_=esplex.decode(open(sys.argv[2],'rb').read())
toks=esplex.tokenize(text)
for t,err,line in esplex.read_all(toks):
    if line==int(sys.argv[3]): print(show(t)[:int(sys.argv[4])])
