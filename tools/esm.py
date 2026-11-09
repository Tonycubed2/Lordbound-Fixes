import struct, zlib, mmap
class Rec:
    __slots__=('type','size','flags','fid','vc','ver','unk','off','path','_subs','_data','plugin')
    def __init__(s): s._subs=None; s._data=None
    def data(s):
        if s._data is None:
            raw=s.plugin.mm[s.off+24:s.off+24+s.size]
            if s.flags & 0x40000: raw=zlib.decompress(raw[4:])
            s._data=bytes(raw)
        return s._data
    def subs(s):
        if s._subs is None:
            d=s.data(); out=[]; i=0; ext=None
            while i<len(d):
                t=d[i:i+4].decode('latin1'); sz=struct.unpack_from('<H',d,i+4)[0]; i+=6
                if t=='XXXX': ext=struct.unpack_from('<I',d,i)[0]; i+=sz; continue
                if ext is not None: sz=ext; ext=None
                out.append((t,d[i:i+sz])); i+=sz
            s._subs=out
        return s._subs
    def get(s,t):
        for k,v in s.subs():
            if k==t: return v
    def getall(s,t): return [v for k,v in s.subs() if k==t]
    def edid(s):
        v=s.get('EDID'); return v.rstrip(b'\0').decode('latin1') if v else ''
    def raw(s): return bytes(s.plugin.mm[s.off:s.off+24+s.size])
class Plugin:
    def __init__(s,path):
        s.f=open(path,'rb'); s.mm=mmap.mmap(s.f.fileno(),0,access=mmap.ACCESS_READ)
        s.recs=[]; s.byfid={}; s.byedid={}
        s.header=s._rec(0,())
        s._walk(24+s.header.size,len(s.mm),())
        for r in s.recs: s.byfid[r.fid]=r
    def _rec(s,off,path):
        r=Rec(); r.plugin=s
        r.type,r.size,r.flags,r.fid,r.vc,r.ver,r.unk=struct.unpack_from('<4sIIIIHH',s.mm,off)
        r.type=r.type.decode('latin1'); r.off=off; r.path=path; return r
    def _walk(s,off,end,path):
        while off<end:
            if s.mm[off:off+4]==b'GRUP':
                gsz,label,gtype=struct.unpack_from('<I4sI',s.mm,off+4)
                s._walk(off+24,off+gsz,path+((gtype,label),)); off+=gsz
            else:
                r=s._rec(off,path); s.recs.append(r); off+=24+r.size
    def masters(s): return [v.rstrip(b'\0').decode('latin1') for v in s.header.getall('MAST')]
    def index_edid(s):
        for r in s.recs:
            e=r.edid()
            if e: s.byedid[e.lower()]=r
def lstr(b): return b.rstrip(b'\0').decode('latin1') if b else ''
def fid_of(b,o=0): return struct.unpack_from('<I',b,o)[0]
