import sys,os,re,struct; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import *
import pex
SRC=os.path.expanduser('~/mnt/Lordbound/scripts')
PC={}
def load(n):
    n=n.lower()
    if n not in PC:
        p=os.path.join(SRC,n+'.pex')
        PC[n]=pex.Pex(open(p,'rb').read()) if os.path.exists(p) else None
    return PC[n]
def owner_quest(r):
    if r.type=='QUST': return r.fid
    if r.type=='INFO':
        d=info_dial(r); q=d.get('QNAM') if d else None; return esm.fid_of(q) if q else None
    if r.type=='SCEN':
        v=r.getall('PNAM'); return esm.fid_of(v[-1]) if v else None
    return None
sets={}   # quest fid -> set(stages) ; None in set => unknown stage
def add(q,s,src): sets.setdefault(q,{}).setdefault(s,[]).append(src)
unknown_targets=0
for r in P.recs:
    v=r.get('VMAD')
    if not v: continue
    try: x=vmad.parse(v,r.type)
    except: continue
    insts=[(s,p,None) for s,p in x['scripts']]+[(s,p,al) for al,ss in x.get('aliasscripts',[]) for s,p in ss]
    oq=owner_quest(r)
    for sname,props,al in insts:
        px=load(sname)
        if not px:
            qs=[int(v[1],16) for k,v in props.items() if isinstance(v,tuple) and v[0]=='obj' and P.byfid.get(int(v[1],16)) is not None and P.byfid[int(v[1],16)].type=='QUST']
            sts=[v for k,v in props.items() if isinstance(v,int) and 'stage' in k.lower()]
            for qq in qs:
                for sv in sts: add(qq,sv,'vanilla %s on %s'%(sname,r.edid() or '%08X'%r.fid))
            if qs and not sts and any('stage' in k.lower() for k in props): pass
            continue
        o=px.objects[0]
        autos={pr['auto'].lower():pr['name'] for pr in o['props'] if 'auto' in pr}
        pl={k.lower():val for k,val in props.items()}
        def propval(var):
            pn=autos.get(var.lower())
            return pl.get(pn.lower()) if pn else None
        isquest=(r.type=='QUST' and al is None)
        for stn,fs in o['states']:
            for fn,f in fs:
                tmp={}
                for nm,a in f['ins']:
                    if nm=='callmethod':
                        meth=a[0][1]; tgt=a[1]; dest=a[2]
                        if meth.lower()=='getowningquest' and dest[0]=='id': tmp[dest[1].lower()]=('q',oq if al is None else r.fid)
                        if meth.lower() in ('setstage','setcurrentstageid'):
                            # resolve quest
                            q=None
                            if tgt==('id','self') and isquest: q=r.fid
                            elif tgt[0]=='id':
                                t=tgt[1].lower()
                                if t in tmp and tmp[t][0]=='q': q=tmp[t][1]
                                else:
                                    pv=propval(t) or (tmp.get(t,(None,None))[1] if t in tmp and tmp[t][0]=='p' else None)
                                    if isinstance(pv,tuple) and pv[0]=='obj': q=int(pv[1],16)
                            st=a[3] if len(a)>3 else None
                            sv=None
                            if st and st[0]=='int': sv=st[1]
                            elif st and st[0]=='id':
                                pv=propval(st[1]); sv=pv if isinstance(pv,int) else None
                            if q is None: unknown_targets+=1; continue
                            add(q,sv,'%s %s:%s'%(r.type,r.edid() or '%08X'%r.fid,fn))
                    elif nm=='cast' and a[0][0]=='id' and a[1][0]=='id':
                        t=a[1][1].lower()
                        if t in tmp: tmp[a[0][1].lower()]=tmp[t]
                        else:
                            pv=propval(t)
                            if isinstance(pv,tuple): tmp[a[0][1].lower()]=('p',pv)
                    elif nm=='assign' and a[0][0]=='id' and a[1][0]=='id':
                        t=a[1][1].lower()
                        if t in tmp: tmp[a[0][1].lower()]=tmp[t]
# startup stages
for q in [r for r in P.recs if r.type=='QUST']:
    for t,v in q.subs():
        if t=='INDX' and v[2]&2: add(q.fid,struct.unpack_from('<H',v,0)[0],'startup')
# also SMQN can't set stage. Now conditions
issues=[]
for r in P.recs:
    if r.type not in ('INFO','SCEN','PACK','QUST','SMQN','DLBR','MESG','PERK','SPEL','MGEF'): continue
    for t,v in r.subs():
        if t!='CTDA': continue
        fn=struct.unpack_from('<H',v,8)[0]; op=v[0]>>5; fl=v[0]&0x1f
        if fl&4: continue
        val=struct.unpack_from('<f',v,4)[0]; p1,p2=struct.unpack_from('<II',v,12)
        q=p1; stage=None
        if fn==58 and op==0: stage=int(val)
        elif fn==59 and op==0 and val==1.0: stage=p2
        else: continue
        if stage==0: continue
        qs=sets.get(q,{})
        if None in qs: continue
        if stage not in qs:
            qr=P.byfid.get(q)
            if not qr: continue
            defined=any(tt=='INDX' and struct.unpack_from('<H',vv,0)[0]==stage for tt,vv in qr.subs())
            issues.append((qr.edid(),stage,defined,r.type,'%08X'%r.fid,r.edid()))
print('unknown setstage targets',unknown_targets)
from collections import defaultdict
g=defaultdict(list)
for i in issues: g[(i[0],i[1],i[2])].append(i[3:])
for k in sorted(g): print(k[0],'stage',k[1],'(defined)' if k[2] else '(NOT a stage)',len(g[k]),g[k][:3])
import pickle; pickle.dump(sets,open('stagesets.pkl','wb'))
