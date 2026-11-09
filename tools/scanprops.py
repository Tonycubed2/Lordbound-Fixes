import sys,os,re; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import *
import pex
SRC=os.path.expanduser('~/mnt/Lordbound/scripts')
cache={}
def script_info(n):
    n=n.lower()
    if n in cache: return cache[n]
    p=os.path.join(SRC,n+'.pex'); info=None
    if os.path.exists(p):
        x=pex.Pex(open(p,'rb').read()); o=x.objects[0]
        props={pr['name'].lower():(pr['type'],pr.get('auto')) for pr in o['props']}
        used=set()
        for sn,fs in o['states']:
            for fn,f in fs:
                for nm,a in f['ins']:
                    for t,v in a:
                        if t=='id': used.add(v.lower())
        info=(props,used,o['parent'])
    cache[n]=info; return info
res=[]
def check(owner,scr,filled,ctx):
    si=script_info(scr)
    if not si: return
    props,used,parent=si
    for pn,(pt,auto) in props.items():
        if pn in filled: continue
        if auto and auto.lower() in used:
            res.append((owner,ctx,scr,pt,pn))
for r in P.recs:
    v=r.get('VMAD')
    if not v: continue
    try: x=vmad.parse(v,r.type)
    except Exception as e: print('vmad err',r.type,'%08X'%r.fid,e); continue
    for scr,props in x['scripts']:
        check(r,scr,{k.lower() for k in props},'')
    for aid,scrs in x.get('aliasscripts',[]):
        for scr,props in scrs: check(r,scr,{k.lower() for k in props},'alias%d'%aid)
# fragment scripts: their properties are in the record's main 'scripts' too (fragfile appears as a script). covered.
for owner,ctx,scr,pt,pn in res:
    print('%s %08X %s | %s %s | %s %s'%(owner.type,owner.fid,owner.edid(),ctx,scr,pt,pn))
print('TOTAL',len(res))
