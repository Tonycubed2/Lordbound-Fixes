import sys,os,struct,re; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import *
def stage_conds(r):
    """returns {questfid: [(op,val)]} for GetStage on subject (run on any)"""
    out={}
    subs=r.subs(); i=0; conds=[v for t,v in subs if t=='CTDA']
    # skip if any OR flags involving GetStage (too complex)
    for v in conds:
        fn=struct.unpack_from('<H',v,8)[0]
        if fn==58 and not (v[0]&4):
            if v[0]&1: return None
            q=struct.unpack_from('<I',v,12)[0]; op=v[0]>>5; val=struct.unpack_from('<f',v,4)[0]
            out.setdefault(q,[]).append((op,val))
    return out
def ok(val,conds):
    for op,c in conds:
        if op==0 and not val==c: return False
        if op==1 and not val!=c: return False
        if op==2 and not val>c: return False
        if op==3 and not val>=c: return False
        if op==4 and not val<c: return False
        if op==5 and not val<=c: return False
    return True
def quest_stages(q):
    r=P.byfid.get(q)
    return sorted({struct.unpack_from('<H',v,0)[0] for t,v in r.subs() if t=='INDX'}) if r else []
def frag_sets(r):
    """stages this INFO's own fragments set on its owning quest (any fragment)"""
    out=set()
    for l in fragtext(r):
        m=re.search(r'(?i)setstage, ::temp\d+, ::temp\d+, (\d+)$',l)
        if m: out.add(int(m.group(1)))
    return out
IOD=iod()
res=[]
for d_fid,infos in IOD.items():
    for r in infos:
        ch=[esm.fid_of(v) for v in r.getall('TCLT')]
        if not ch: continue
        pc=stage_conds(r)
        if pc is None: continue
        d=P.byfid[d_fid]; qn=d.get('QNAM'); oq=esm.fid_of(qn) if qn else None
        for q,cs in pc.items():
            vals=set(s for s in quest_stages(q) if ok(s,cs))
            if q==oq: vals|=frag_sets(r)
            if not vals: continue
            for c in ch:
                cinfos=IOD.get(c,[])
                if not cinfos: res.append(('EMPTY TOPIC',r,c,q,vals)); continue
                anyok=False
                for ci in cinfos:
                    cc=stage_conds(ci)
                    if cc is None or q not in cc: anyok=True; break
                    if any(ok(v,cc[q]) for v in vals): anyok=True; break
                if not anyok: res.append(('DEAD',r,c,q,vals))
seen=set()
for kind,r,c,q,vals in res:
    k=(r.fid,c)
    if k in seen: continue
    seen.add(k)
    cd=P.byfid[c]
    print(kind,'%08X'%r.fid,'%s -> %s "%s"'%(info_dial(r).edid(),cd.edid(),esm.lstr(cd.get('FULL'))),'| %s parent allows %s'%(P.byfid[q].edid(),sorted(vals)), '| child needs',[ [ (CT[o],v) for o,v in (stage_conds(ci) or {}).get(q,[])] for ci in IOD.get(c,[])][:3])
print('total',len(seen))
