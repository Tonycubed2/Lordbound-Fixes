import os,pickle,re,sys,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import libarchive,bsa
from unrar.cffi import rarfile
D=os.path.expanduser('~/mnt/Downloads'); DST=os.path.expanduser('~/mnt/Lordbound Fixes'); TMP=os.path.expanduser('~/tmp/bsa'); os.makedirs(TMP,exist_ok=True)
mins=float(sys.argv[1]) if len(sys.argv)>1 else 20
real=pickle.load(open('realmiss.pkl','rb')); mm=pickle.load(open('missmesh.pkl','rb'))
targets={k for k in real if not os.path.exists(os.path.join(DST,*k.split('\\')))}
targets|={'meshes\\'+m for m in mm if not os.path.exists(os.path.join(DST,'meshes',*m.split('\\')))}
targets|={k for k in ('textures\\insanity\\weapons\\third era\\cyrodiil\\steel\\scabbard.dds','textures\\insanity\\weapons\\third era\\cyrodiil\\steel\\scabbard_m.dds','textures\\insanity\\weapons\\third era\\cyrodiil\\steel\\scabbard_n.dds') if not os.path.exists(os.path.join(DST,*k.split('\\')))}
bases={}
for k in targets: bases.setdefault(os.path.basename(k),[]).append(k)
def norm(n):
    n=n.replace('/','\\').lower(); m=re.search(r'(?:^|\\)((?:textures|meshes)\\.*)$',n); return m.group(1) if m else None
log=pickle.load(open('dllog.pkl','rb')); found=[]; namehits=[]
def take(k,data,src):
    out=os.path.join(DST,*k.split('\\')); os.makedirs(os.path.dirname(out),exist_ok=True); open(out,'wb').write(data)
    log.append('%s  <=  %s'%(k,src)); found.append(k); targets.discard(k)
def check(name,getdata,src):
    k=norm(name)
    if name.lower().endswith('.bsa'):
        tp=os.path.join(TMP,'s.bsa'); open(tp,'wb').write(getdata())
        try:
            r,fl,v=bsa.listbsa(tp)
            for kk,ent in r.items():
                if kk in targets: take(kk,bsa.extract(tp,ent,fl,v),'%s (%s)'%(src,os.path.basename(name)))
                elif os.path.basename(kk) in bases: namehits.append((src,'BSA:'+kk))
        except Exception as ex: print('bsa err',src,name,ex)
        os.remove(tp)
    elif k in targets: take(k,getdata(),src)
    elif os.path.basename(name.replace('\\','/')).lower() in bases: namehits.append((src,name))
cut=time.time()-mins*60
for f in sorted(os.listdir(D)):
    p=os.path.join(D,f)
    if os.path.getmtime(p)<cut: continue
    try:
        if os.path.isdir(p):
            for dp,dn,fn in os.walk(p):
                for x in fn:
                    fp=os.path.join(dp,x); check(os.path.relpath(fp,p),lambda fp=fp:open(fp,'rb').read(),f)
        elif f.lower().endswith('.rar'):
            rf=rarfile.RarFile(p)
            for n in rf.namelist(): check(n,lambda n=n:rf.read(n),f)
        elif f.lower().endswith(('.7z','.zip')):
            with libarchive.file_reader(p) as a:
                for e in a:
                    if e.isfile:
                        data=None
                        n=e.pathname; k=norm(n)
                        if n.lower().endswith('.bsa') or k in targets:
                            data=b''.join(e.get_blocks()); check(n,lambda d=data:d,f)
                        elif os.path.basename(n).lower() in bases: namehits.append((f,n))
    except Exception as ex: print('err',f,str(ex)[:100])
    print(f,'done; found',len(found),flush=True)
pickle.dump(log,open('dllog.pkl','wb'))
print('FOUND:',found); print('SAME NAME ELSEWHERE:',namehits[:30])
