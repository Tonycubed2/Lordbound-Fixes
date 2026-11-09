import re,os,pickle
MESH=os.path.expanduser('~/mnt/Lordbound/meshes')
ALL=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'bsafiles.pkl'),'rb'))
def loose_mesh(p):
    p=p.lower().replace('/','\\')
    if p.startswith('meshes\\'): p=p[7:]
    fp=os.path.join(MESH,*p.split('\\'))
    if os.path.exists(fp): return fp
    # case-insensitive
    cur=MESH
    for part in p.split('\\'):
        try: m=[x for x in os.listdir(cur) if x.lower()==part]
        except: return None
        if not m: return None
        cur=os.path.join(cur,m[0])
    return cur
def textures_in(data):
    return sorted(set(m.decode('latin1').lower().replace('/','\\') for m in re.findall(rb'(?i)(?:data\\)?textures[\\/][\x20-\x7e]{3,200}?\.dds',data)))
def has_tex(t):
    t=t.lower().replace('/','\\')
    if t.startswith('data\\'): t=t[5:]
    return t in ALL
