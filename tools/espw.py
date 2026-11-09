import struct
def sub(t,b):
    if len(b)>0xFFFF: return b'XXXX'+struct.pack('<HI',4,len(b))+t.encode()+struct.pack('<H',0)+b
    return t.encode()+struct.pack('<H',len(b))+b
def pack_subs(subs): return b''.join(sub(t,v) for t,v in subs)
class Out:
    """Overrides keyed by fid -> (rec, newsubs or None)."""
    def __init__(s,P): s.P=P; s.ov={}; s.newrecs=[]
    def override(s,r,subs=None,flags=None):
        s.ov[r.fid]=(r,subs,flags)
    def new(s,rtype,fid,subs):
        class NR: pass
        nr=NR(); nr.type=rtype; nr.fid=fid; nr.flags=0; nr.vc=0; nr.ver=44; nr.unk=0; nr.off=10**11+len(s.newrecs); nr.path=((0,rtype.encode()),); nr._newsubs=subs
        s.newrecs.append(nr); return nr
    def recbytes(s,r,subs=None,flags=None):
        if subs is None and flags is None: return r.raw()
        if subs is None: subs=r.subs()
        data=pack_subs(subs); fl=(r.flags if flags is None else flags)&~0x40000
        return struct.pack('<4sIIIIHH',r.type.encode(),len(data),fl,r.fid,r.vc,r.ver,r.unk)+data
    def build(s,path,masters,author='Tony Torres',desc='',esl=True):
        tree={}  # nested dict: key (gtype,label) -> {'_recs':[...]} 
        def node(path):
            n=tree
            for g in path: n=n.setdefault(g,{})
            return n
        need={}
        for fid,(r,subs,fl) in s.ov.items(): need[fid]=(r,subs,fl)
        # add owners of groups
        for fid,(r,subs,fl) in list(need.items()):
            for gt,lab in r.path:
                if gt in (1,6,7,8,9,10):
                    of=struct.unpack('<I',lab)[0]
                    if of not in need: o=s.P.byfid[of]; need[of]=(o,None,None)
        for fid,(r,subs,fl) in need.items():
            n=node(r.path); n.setdefault('_recs',[]).append((r,subs,fl))
        for nr in s.newrecs:
            n=node(((0,nr.type.encode()),)); n.setdefault('_recs',[]).append((nr,nr._newsubs,None))
        count=[0]
        def emit(n,top=False):
            out=b''
            # records first (sorted by original offset), then each record's child groups right after owner
            recs=sorted(n.get('_recs',[]),key=lambda x:x[0].off)
            groups=[(k,v) for k,v in n.items() if k!='_recs']
            used=set()
            for r,subs,fl in recs:
                out+=s.recbytes(r,subs,fl); count[0]+=1
                for k,v in groups:
                    gt,lab=k
                    if gt in (1,6,7) and struct.unpack('<I',lab)[0]==r.fid:
                        out+=grp(k,v); used.add(k)
                        if gt==6: pass
            for k,v in sorted(groups,key=lambda kv:min_off(kv[1])):
                if k in used: continue
                if k[0]==10 or k[0]==8 or k[0]==9:
                    pass
                out+=grp(k,v)
            return out
        def min_off(n):
            m=10**12
            for k,v in n.items():
                if k=='_recs': m=min([m]+[r.off for r,_,_ in v])
                else: m=min(m,min_off(v))
            return m
        def grp(k,v):
            gt,lab=k
            body=emit(v)
            # cell children groups (6) contain 8/9/10 groups; topics 7 contain INFOs
            if gt==6:
                inner=b''
                for kk in sorted([x for x in v if x!='_recs'],key=lambda x:x[0]):
                    pass
            return b'GRUP'+struct.pack('<I4sIHHHH',24+len(body),lab,gt,0,0,0,0)+body
        body=b''
        for k,v in sorted(tree.items(),key=lambda kv:min_off(kv[1])):
            body+=grp(k,v)
        hedr=struct.pack('<fII',1.71,count[0],0x800+len(s.newrecs))
        hs=[('HEDR',hedr),('CNAM',author.encode()+b'\0')]
        if desc: hs.append(('SNAM',desc.encode()+b'\0'))
        for m in masters: hs+=[('MAST',m.encode()+b'\0'),('DATA',b'\0'*8)]
        hd=pack_subs(hs)
        flags=0x200 if esl else 0
        head=struct.pack('<4sIIIIHH',b'TES4',len(hd),flags,0,0,44,0)+hd
        open(path,'wb').write(head+body)
        return count[0]
def set_ctda_value(b,val):
    return b[:4]+struct.pack('<f',val)+b[8:]
def set_ctda_op(b,opcode):
    return bytes([ (b[0]&0x1f) | (opcode<<5) ])+b[1:]
