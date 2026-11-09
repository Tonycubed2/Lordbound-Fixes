import struct
from vmad import R,_val
def ws(s): b=s.encode('latin1'); return struct.pack('<H',len(b))+b
def objprop(name,fid,alias=-1):
    return ws(name)+bytes([1,1])+struct.pack('<Hh I'.replace(' ',''),0,alias,fid)
def _skipval(r,t,fmt): _val(r,t,fmt)
def _scripts_raw(r,ver,fmt):
    """returns list of [name,status,[(pname,rawbytes)]]"""
    out=[]
    for _ in range(r.u16()):
        name=r.ws(); st=r.u8() if ver>=4 else 0; props=[]
        for _ in range(r.u16()):
            s=r.i; pn=r.ws(); pt=r.u8(); r.u8() if ver>=4 else 0; _skipval(r,pt,fmt); props.append((pn,r.b[s:r.i]))
        out.append([name,st,props])
    return out
def _scripts_bytes(sc):
    b=struct.pack('<H',len(sc))
    for name,st,props in sc:
        b+=ws(name)+bytes([st])+struct.pack('<H',len(props))+b''.join(p for _,p in props)
    return b
def add_props(vm,rtype,adds,alias_adds=None):
    """adds: {scriptname_lower: [(propname,fid,aliasid)]}; alias_adds: {aliasid:{scriptname_lower:[...]}}"""
    r=R(vm); ver=r.u16(); fmt=r.u16(); assert ver>=4 and fmt==2
    sc=_scripts_raw(r,ver,fmt)
    def apply(sc,adds):
        n=0
        for s in sc:
            for pn,fid,al in adds.get(s[0].lower(),[]):
                if any(x[0].lower()==pn.lower() for x in s[2]): continue
                s[2].append((pn,objprop(pn,fid,al))); n+=1
        return n
    n=apply(sc,adds or {})
    head=struct.pack('<HH',ver,fmt)+_scripts_bytes(sc)
    tail=vm[r.i:]
    if alias_adds and rtype=='QUST':
        t=R(vm); t.i=r.i
        t.u8(); nfr=t.u16(); t.ws()
        for _ in range(nfr): t.u16(); t.u16(); t.i32(); t.u8(); t.ws(); t.ws()
        fragpart=vm[r.i:t.i]
        na=t.u16(); als=[]
        for _ in range(na):
            s=t.i; t.u16(); al=struct.unpack_from('<h',t.b,t.i)[0]; t.i+=2; t.u32(); objb=vm[s:t.i]
            v2=t.u16(); f2=t.u16(); scs=_scripts_raw(t,v2,f2)
            n+=apply(scs,alias_adds.get(al,{}))
            als.append(objb+struct.pack('<HH',v2,f2)+_scripts_bytes(scs))
        assert t.i==len(vm),(t.i,len(vm))
        tail=fragpart+struct.pack('<H',na)+b''.join(als)
    return head+tail,n
