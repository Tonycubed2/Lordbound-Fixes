import os,pickle,sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import *
import niftex
DST=os.path.expanduser('~/mnt/Lordbound Fixes'); FX='F:\\SkyrimSEMOModfolder\\Lordbound Fixes'; DATA=os.path.expanduser('~/mnt/Data')
real=pickle.load(open('realmiss.pkl','rb')); mm=pickle.load(open('missmesh.pkl','rb')); vb=pickle.load(open('vanillabsa.pkl','rb'))
log=pickle.load(open('dllog.pkl','rb')); tl=pickle.load(open('copylog.pkl','rb')); ml=pickle.load(open('meshlog.pkl','rb'))
def have(t):
    t=t[5:] if t.startswith('data\\') else t
    return t in niftex.ALL or t in vb or os.path.exists(os.path.join(DST,*t.split('\\'))) or os.path.exists(os.path.join(DATA,*t.split('\\')))
# textures needed by meshes we copied in
for x in log+ml:
    k=x.split('  <=  ')[0].strip()
    if k.endswith('.nif'):
        for t in niftex.textures_in(open(os.path.join(DST,*k.split('\\')),'rb').read()):
            tt=t[5:] if t.startswith('data\\') else t
            if not have(tt): real.setdefault(tt,[]).append(k[7:])
still={k:v for k,v in real.items() if not os.path.exists(os.path.join(DST,*k.split('\\')))}
used={}
for r in P.recs:
    if r.type in ('REFR','ACHR','NAVM','LAND','INFO','DIAL','CELL'): continue
    for t,v in r.subs():
        if t in ('MODL','MOD2','MOD3','MOD4','MOD5'):
            m=esm.lstr(v).lower().replace('/','\\')
            if m.startswith('meshes\\'): m=m[7:]
            used.setdefault(m,[]).append(r)
after=set()
for tex,meshes in still.items():
    for m in meshes:
        for r in used.get(m.lower().replace('/','\\'),[]):
            base=tex.rsplit('.',1)[0]; kind='map only' if base[-2:] in ('_n','_m','_g','_e','_p','_s') or base.endswith(('_em','_sk')) else 'PURPLE'
            after.add((kind,r.type,r.edid(),full(r),tex))
mstill=[m for m in mm if not os.path.exists(os.path.join(DST,'meshes',*m.split('\\')))]
L=['Textures that Lordbound meshes ask for but that are in neither Lordbound, the base game/DLC, your MO2 mods, nor your Downloads.','Only objects Lordbound actually uses are listed. A missing main texture shows purple; a missing _n/_m/_g/_e map only makes it look flatter.','']
for k in sorted(after): L.append('%-8s %s %s "%s"  missing: %s'%k)
L+=['','Models still missing everywhere (%d):'%len(mstill)]+['   meshes\\'+m for m in sorted(mstill)]
L+=['','Copied into Lordbound Fixes from your MO2 mods (%d files):'%(len(tl)+len(ml))]+sorted(tl+ml)
L+=['','Copied into Lordbound Fixes from C:\\Users\\tony.TONYCUBED\\Downloads, the base game or Lordbound itself (%d files):'%len(log)]+sorted(log)
p=os.path.join(DST,'Lordbound Fixes - missing textures.txt'); open(p+'.new','w').write('\r\n'.join(L)+'\r\n'); os.replace(p+'.new',p)
p=os.path.join(DST,'Lordbound Fixes - detailed changes.txt'); s=open(p,'rb').read().decode('utf-8')
i=s.find('\r\n6. FILES COPIED FROM'); assert i>0; s=s[:i]
add=['','6. FILES COPIED FROM C:\\Users\\tony.TONYCUBED\\Downloads (OR THE BASE GAME / LORDBOUND ITSELF) INTO '+FX,'-'*72]
for x in sorted(log):
    a,b=x.split('  <=  ',1); add.append('   %s\\%s   <- from "%s"'%(FX,a,b))
s=s+'\r\n'+'\r\n'.join(add)+'\r\n'; open(p+'.new','wb').write(s.encode('utf-8')); os.replace(p+'.new',p)
from collections import Counter
print('== PURPLE')
for t in sorted({x[4] for x in after if x[0]=='PURPLE'}): print('  ',t,'|',', '.join(sorted({(x[3] or x[2]) for x in after if x[4]==t})))
c=Counter(x[4] for x in after if x[0]!='PURPLE'); print('== MAP',len(c))
for t,n in sorted(c.items(),key=lambda kv:(-kv[1],kv[0])): print('  ',n,t)
print('== MESHES',len(mstill)); [print('   meshes\\'+m) for m in sorted(mstill)]
