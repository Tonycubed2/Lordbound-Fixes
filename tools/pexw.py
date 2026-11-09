import struct
from pex import Pex, OPS, VARARG
OPNUM={v[0]:k for k,v in OPS.items()}
class W:
    def __init__(s,p): s.p=p; s.idx={x:i for i,x in enumerate(p.strings)}; s.b=bytearray()
    def S(s,x):
        if x not in s.idx: s.idx[x]=len(s.p.strings); s.p.strings.append(x)
        return s.idx[x]
def serialize(p):
    # first pass to collect strings: ensure all strings exist in table
    w=W(p)
    body=bytearray()
    def u8(v): body.extend(struct.pack('>B',v))
    def u16(v): body.extend(struct.pack('>H',v))
    def u32(v): body.extend(struct.pack('>I',v))
    def S(x): u16(w.S(x))
    def var(v):
        t,x=v
        if t=='none': u8(0)
        elif t=='id': u8(1); S(x)
        elif t=='str': u8(2); S(x)
        elif t=='int': u8(3); body.extend(struct.pack('>i',x))
        elif t=='flt': u8(4); body.extend(struct.pack('>f',x))
        elif t=='bool': u8(5); u8(x)
    def func(f):
        S(f['ret']); S(f['doc']); u32(f['uf']); u8(f['fl'])
        u16(len(f['params'])); [ (S(n),S(t)) for n,t in f['params'] ]
        u16(len(f['locals'])); [ (S(n),S(t)) for n,t in f['locals'] ]
        u16(len(f['ins']))
        for nm,a in f['ins']:
            op=OPNUM[nm]; u8(op); n=OPS[op][1]
            for x in a[:n]: var(x)
            if op in VARARG:
                var(('int',len(a)-n)); [var(x) for x in a[n:]]
    # debug
    u8(1 if p.debug else 0)
    if p.debug:
        body.extend(struct.pack('>Q',p.dbgtime)); u16(len(p.debug))
        for o,st,fn,ft,lines in p.debug:
            S(o); S(st); S(fn); u8(ft); u16(len(lines)); [u16(l) for l in lines]
    u16(len(p.uflags)); [ (S(n),u8(i)) for n,i in p.uflags ]
    u16(len(p.objects))
    for o in p.objects:
        S(o['name']); sizepos=len(body); u32(0); objstart=len(body)
        S(o['parent']); S(o['doc']); u32(o['flags']); S(o['auto'])
        u16(len(o['vars']))
        for n,t,uf,v in o['vars']: S(n); S(t); u32(uf); var(v)
        u16(len(o['props']))
        for pr in o['props']:
            S(pr['name']); S(pr['type']); S(pr['doc']); u32(pr['uf']); u8(pr['fl'])
            if pr['fl']&4: S(pr['auto'])
            else:
                if pr['fl']&1: func(pr['read'])
                if pr['fl']&2: func(pr['write'])
        u16(len(o['states']))
        for sn,fs in o['states']:
            S(sn); u16(len(fs))
            for fn,f in fs: S(fn); func(f)
        struct.pack_into('>I',body,sizepos,len(body)-objstart+4)
    head=bytearray()
    def h16(v): head.extend(struct.pack('>H',v))
    def hws(x): b=x.encode('latin1'); h16(len(b)); head.extend(b)
    head.extend(struct.pack('>IBBHQ',0xFA57C0DE,p.major,p.minor,p.game,p.time))
    hws(p.src); hws(p.user); hws(p.machine)
    h16(len(p.strings)); [hws(x) for x in p.strings]
    return bytes(head+body)
def getfunc(p,fname,state=''):
    for sn,fs in p.objects[0]['states']:
        if sn==state:
            for fn,f in fs:
                if fn.lower()==fname.lower(): return f
def add_debug_lines(p,fname,n,state=''):
    for i,(o,st,fn,ft,lines) in enumerate(p.debug):
        if fn.lower()==fname.lower() and st==state and ft==0:
            last=lines[-1] if lines else 0
            p.debug[i]=(o,st,fn,ft,lines+[last]*n); return True
    return False

def ID(x): return ('id',x)
def I(x): return ('int',x)
def F(x): return ('flt',float(x))
def B(x): return ('bool',1 if x else 0)
def STR(x): return ('str',x)
NONE=('none',None)
def ensure_local(f,name,typ):
    if not any(n==name for n,t in f['locals']): f['locals'].append((name,typ))
def insert(p,fname,pos,ins,state=''):
    f=getfunc(p,fname,state); assert f,fname
    if pos is None or pos<0: pos=len(f['ins'])
    # fix relative jumps that cross the insertion point
    n=len(ins)
    for k,(nm,a) in enumerate(f['ins']):
        if nm in ('jmp','jmpt','jmpf'):
            off=a[-1][1]; tgt=k+off
            if k<pos<=tgt or tgt<pos<=k:
                if k<pos<=tgt or (tgt==pos and k>=pos): pass
            # recompute properly below
    old=f['ins']; new=old[:pos]+ins+old[pos:]
    def newidx(i): return i if i<pos else i+n
    fixed=[]
    for k,(nm,a) in enumerate(old):
        if nm in ('jmp','jmpt','jmpf'):
            tgt=k+a[-1][1]
            if tgt>=pos and not (tgt==pos and False): ntgt=newidx(tgt) if tgt!=pos else pos  # jumping to pos lands on inserted code start
            else: ntgt=tgt
            a=a[:-1]+[('int',ntgt-newidx(k))]
        fixed.append((nm,a))
    f['ins']=fixed[:pos]+ins+fixed[pos:]
    for i,(o,st,fn,ft,lines) in enumerate(p.debug):
        if fn.lower()==fname.lower() and st==state and ft==0:
            if not lines: continue  # line table stripped in original: keep it empty
            l=lines[min(pos,len(lines))-1] if pos>0 else lines[0]
            p.debug[i]=(o,st,fn,ft,lines[:pos]+[l]*n+lines[pos:])
    return f
def add_var(p,name,typ,init=NONE):
    o=p.objects[0]
    if not any(v[0]==name for v in o['vars']): o['vars'].append((name,typ,0,init))

def add_prop(p,name,typ):
    o=p.objects[0]; var='::%s_var'%name
    if not any(v[0]==var for v in o['vars']): o['vars'].append((var,typ,0,NONE))
    if not any(pr['name']==name for pr in o['props']):
        o['props'].append({'name':name,'type':typ,'doc':'','uf':0,'fl':7,'auto':var})
    return var
def assemble(code):
    """code: list of ('label',name) or (op,args) where a jump arg may be ('label',name)"""
    pos={}; k=0
    for c in code:
        if c[0]=='label': pos[c[1]]=k
        else: k+=1
    out=[]; k=0
    for c in code:
        if c[0]=='label': continue
        op,args=c
        args=[('int',pos[a[1]]-k) if isinstance(a,tuple) and a[0]=='label' else a for a in args]
        out.append((op,args)); k+=1
    return out
_lc=[0]
def remove_from_list(listvar,count,actor='::lbfA'):
    """Remove `count` items total from `actor`, taking from each form in the FormList in order."""
    _lc[0]+=1; L='L%d'%_lc[0]
    return [
        ('assign',[ID('::lbfN'),I(count)]),
        ('callmethod',[ID('GetSize'),ID(listvar),ID('::lbfSz')]),
        ('assign',[ID('::lbfI'),I(0)]),
        ('label',L+'loop'),
        ('cmp_lt',[ID('::lbfB'),ID('::lbfI'),ID('::lbfSz')]),
        ('jmpf',[ID('::lbfB'),('label',L+'end')]),
        ('callmethod',[ID('GetAt'),ID(listvar),ID('::lbfF'),ID('::lbfI')]),
        ('callmethod',[ID('GetItemCount'),ID(actor),ID('::lbfC'),ID('::lbfF')]),
        ('cmp_gt',[ID('::lbfB'),ID('::lbfC'),I(0)]),
        ('jmpf',[ID('::lbfB'),('label',L+'next')]),
        ('cmp_lt',[ID('::lbfB'),ID('::lbfC'),ID('::lbfN')]),
        ('jmpf',[ID('::lbfB'),('label',L+'useN')]),
        ('assign',[ID('::lbfT'),ID('::lbfC')]),
        ('jmp',[('label',L+'rm')]),
        ('label',L+'useN'),
        ('assign',[ID('::lbfT'),ID('::lbfN')]),
        ('label',L+'rm'),
        ('callmethod',[ID('RemoveItem'),ID(actor),ID('::NoneVar'),ID('::lbfF'),ID('::lbfT'),B(False),NONE]),
        ('isub',[ID('::lbfN'),ID('::lbfN'),ID('::lbfT')]),
        ('cmp_le',[ID('::lbfB'),ID('::lbfN'),I(0)]),
        ('jmpt',[ID('::lbfB'),('label',L+'end')]),
        ('label',L+'next'),
        ('iadd',[ID('::lbfI'),ID('::lbfI'),I(1)]),
        ('jmp',[('label',L+'loop')]),
        ('label',L+'end'),
    ]
LIST_LOCALS=[('::lbfA','Actor'),('::lbfN','Int'),('::lbfSz','Int'),('::lbfI','Int'),('::lbfB','Bool'),('::lbfF','Form'),('::lbfC','Int'),('::lbfT','Int'),('::NoneVar','None')]
