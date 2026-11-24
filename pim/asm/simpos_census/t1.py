import sys; sys.path.insert(0, sys.argv[1]); import esplex
src = open(sys.argv[2],'rb').read(); text, enc = esplex.decode(src)
toks = esplex.tokenize(text)
print(enc, len(toks))
for t, err, line in esplex.read_all(toks):
    if err: print('ERR', line, err)
    else: print(line, repr(t)[:600])
