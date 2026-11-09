import struct
class R:
    def __init__(s,b): s.b=b; s.i=0
    def u8(s): v=s.b[s.i]; s.i+=1; return v
    def u16(s): v=struct.unpack_from('<H',s.b,s.i)[0]; s.i+=2; return v
    def i32(s): v=struct.unpack_from('<i',s.b,s.i)[0]; s.i+=4; return v
    def u32(s): v=struct.unpack_from('<I',s.b,s.i)[0]; s.i+=4; return v
    def f32(s): v=struct.unpack_from('<f',s.b,s.i)[0]; s.i+=4; return v
    def ws(s): n=s.u16(); v=s.b[s.i:s.i+n].decode('latin1'); s.i+=n; return v
def _obj(r,fmt):
    if fmt==2:
        r.u16(); al=struct.unpack_from('<h',r.b,r.i)[0]; r.i+=2; fid=r.u32(); return ('obj',hex(fid),al)
    fid=r.u32(); al=struct.unpack_from('<h',r.b,r.i)[0]; r.i+=4; return ('obj',hex(fid),al)
def _val(r,t,fmt):
    if t==1: return _obj(r,fmt)
    if t==2: return r.ws()
    if t==3: return r.i32()
    if t==4: return r.f32()
    if t==5: return bool(r.u8())
    if t in (11,12,13,14,15):
        n=r.u32(); return [_val(r,t-10,fmt) for _ in range(n)]
    raise ValueError('ptype %d'%t)
def scripts(r,ver,fmt):
    out=[]
    for _ in range(r.u16()):
        name=r.ws(); st=r.u8() if ver>=4 else 0; props={}
        for _ in range(r.u16()):
            pn=r.ws(); pt=r.u8(); ps=r.u8() if ver>=4 else 0
            props[pn]=_val(r,pt,fmt)
        out.append((name,props))
    return out
def parse(b,rtype):
    r=R(b); ver=r.u16(); fmt=r.u16()
    res={'scripts':scripts(r,ver,fmt)}
    if r.i>=len(b): return res
    if rtype=='QUST':
        r.u8(); nfr=r.u16(); res['fragfile']=r.ws(); fr=[]
        for _ in range(nfr):
            stage=r.u16(); r.u16(); le=r.i32(); r.u8(); sn=r.ws(); fn=r.ws(); fr.append((stage,le,sn,fn))
        res['frags']=fr; al=[]
        for _ in range(r.u16()):
            o=_obj(r,fmt); v2=r.u16(); f2=r.u16(); al.append((o[2],scripts(r,v2,f2)))
        res['aliasscripts']=al
    elif rtype=='INFO':
        r.u8(); fl=r.u8(); fn=r.ws(); res['fragfile']=fn; fr=[]
        for bit in (1,2):
            if fl&bit: r.u8(); sn=r.ws(); f=r.ws(); fr.append(('begin' if bit==1 else 'end',sn,f))
        res['frags']=fr
    elif rtype=='SCEN':
        r.u8(); fl=r.u8(); fn=r.ws(); res['fragfile']=fn; fr=[]
        for bit in (1,2):
            if fl&bit: r.u8(); fr.append(('begin' if bit==1 else 'end',r.ws(),r.ws()))
        ph=[]
        for _ in range(r.u16()):
            pf=r.u8(); idx=r.u32(); r.u8(); ph.append((idx,r.ws(),r.ws(),'start' if pf&1 else 'end'))
        res['frags']=fr; res['phasefrags']=ph
    elif rtype=='PACK':
        r.u8(); fl=r.u8(); fn=r.ws(); fr=[]
        for bit,nm in ((1,'begin'),(2,'end'),(4,'change')):
            if fl&bit: r.u8(); fr.append((nm,r.ws(),r.ws()))
        res['fragfile']=fn; res['frags']=fr
    return res
