import struct,sys,os
OPS={0:('nop',0),1:('iadd',3),2:('fadd',3),3:('isub',3),4:('fsub',3),5:('imul',3),6:('fmul',3),7:('idiv',3),8:('fdiv',3),9:('imod',3),10:('not',2),11:('ineg',2),12:('fneg',2),13:('assign',2),14:('cast',2),15:('cmp_eq',3),16:('cmp_lt',3),17:('cmp_le',3),18:('cmp_gt',3),19:('cmp_ge',3),20:('jmp',1),21:('jmpt',2),22:('jmpf',2),23:('callmethod',3),24:('callparent',2),25:('callstatic',3),26:('return',1),27:('strcat',3),28:('propget',3),29:('propset',3),30:('array_create',2),31:('array_length',2),32:('array_getelement',3),33:('array_setelement',3),34:('array_findelement',4),35:('array_rfindelement',4)}
VARARG={23,24,25}
class Pex:
    def __init__(s,data):
        s.d=data; s.i=0
        assert s.u32()==0xFA57C0DE
        s.major=s.u8(); s.minor=s.u8(); s.game=s.u16(); s.time=s.u64()
        s.src=s.rws(); s.user=s.rws(); s.machine=s.rws()
        s.strings=[s.rws() for _ in range(s.u16())]
        s.debug=[]
        if s.u8():
            s.dbgtime=s.u64()
            for _ in range(s.u16()):
                o,st,fn,ft=s.u16(),s.u16(),s.u16(),s.u8(); n=s.u16(); lines=[s.u16() for _ in range(n)]
                s.debug.append((s.strings[o],s.strings[st],s.strings[fn],ft,lines))
        s.uflags=[(s.S(),s.u8()) for _ in range(s.u16())]
        s.objects=[]
        for _ in range(s.u16()):
            o={}; o['name']=s.S(); o['size']=s.u32(); o['parent']=s.S(); o['doc']=s.S(); o['flags']=s.u32(); o['auto']=s.S()
            o['vars']=[(s.S(),s.S(),s.u32(),s.var()) for _ in range(s.u16())]
            props=[]
            for _ in range(s.u16()):
                p={'name':s.S(),'type':s.S(),'doc':s.S(),'uf':s.u32(),'fl':s.u8()}
                if p['fl']&4: p['auto']=s.S()
                else:
                    if p['fl']&1: p['read']=s.func()
                    if p['fl']&2: p['write']=s.func()
                props.append(p)
            o['props']=props; states=[]
            for _ in range(s.u16()):
                sn=s.S(); fs=[]
                for _ in range(s.u16()): fn=s.S(); fs.append((fn,s.func()))
                states.append((sn,fs))
            o['states']=states; s.objects.append(o)
    def u8(s): v=s.d[s.i]; s.i+=1; return v
    def u16(s): v=struct.unpack_from('>H',s.d,s.i)[0]; s.i+=2; return v
    def u32(s): v=struct.unpack_from('>I',s.d,s.i)[0]; s.i+=4; return v
    def u64(s): v=struct.unpack_from('>Q',s.d,s.i)[0]; s.i+=8; return v
    def rws(s): n=s.u16(); v=s.d[s.i:s.i+n].decode('latin1'); s.i+=n; return v
    def S(s): return s.strings[s.u16()]
    def var(s):
        t=s.u8()
        if t==0: return ('none',None)
        if t==1: return ('id',s.S())
        if t==2: return ('str',s.S())
        if t==3: v=struct.unpack_from('>i',s.d,s.i)[0]; s.i+=4; return ('int',v)
        if t==4: v=struct.unpack_from('>f',s.d,s.i)[0]; s.i+=4; return ('flt',v)
        if t==5: return ('bool',s.u8())
        raise ValueError(t)
    def func(s):
        f={'ret':s.S(),'doc':s.S(),'uf':s.u32(),'fl':s.u8()}
        f['params']=[(s.S(),s.S()) for _ in range(s.u16())]
        f['locals']=[(s.S(),s.S()) for _ in range(s.u16())]
        ins=[]
        for _ in range(s.u16()):
            op=s.u8(); nm,n=OPS[op]; a=[s.var() for _ in range(n)]
            if op in VARARG:
                c=s.var(); a+= [s.var() for _ in range(c[1])]
            ins.append((nm,a))
        f['ins']=ins; return f
def fmt(v):
    t,x=v
    if t=='none': return 'None'
    if t=='str': return repr(x)
    if t=='bool': return 'true' if x else 'false'
    return str(x)
def dis(p,only=None):
    out=[]
    for o in p.objects:
        out.append('ScriptName %s extends %s'%(o['name'],o['parent']))
        for v in o['vars']: out.append('  var %s %s = %s'%(v[1],v[0],fmt(v[3])))
        for pr in o['props']: out.append('  prop %s %s%s'%(pr['type'],pr['name'],(' auto->'+pr['auto']) if 'auto' in pr else ''))
        for sn,fs in o['states']:
            for fn,f in fs:
                if only and fn.lower()!=only.lower(): continue
                out.append('FUNC [%s] %s(%s) -> %s'%(sn,fn,', '.join('%s %s'%(t,n) for n,t in f['params']),f['ret']))
                for n,t in f['locals']: out.append('    local %s %s'%(t,n))
                for k,(nm,a) in enumerate(f['ins']):
                    out.append('  %3d %s %s'%(k,nm,', '.join(fmt(x) for x in a)))
    return '\n'.join(out)
if __name__=='__main__':
    p=Pex(open(sys.argv[1],'rb').read()); print(dis(p, sys.argv[2] if len(sys.argv)>2 else None))
