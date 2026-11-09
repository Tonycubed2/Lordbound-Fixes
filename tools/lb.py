import sys,struct,os,re
W=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,W)
import esm,vmad
P=esm.Plugin(os.path.expanduser('~/mnt/Lordbound/Druadach.esm')); P.index_edid()
FN={0:'GetWantBlocking',1:'GetDistance',5:'GetLocked',14:'GetActorValue',35:'GetDisabled',36:'MenuMode',42:'SameFaction',45:'GetDetected',46:'GetDead',47:'GetItemCount',48:'GetGold',50:'GetTalkedToPC',53:'GetScriptVariable',56:'GetQuestRunning',58:'GetStage',59:'GetStageDone',67:'GetInCell',69:'GetIsRace',71:'GetInFaction',72:'GetIsID',73:'GetFactionRank',74:'GetGlobalValue',77:'GetRandomPercent',79:'GetQuestVariable',80:'GetLevel',110:'GetCurrentAIPackage',123:'IsGreetingPlayer',132:'GetPCInFaction',136:'GetIsReference',141:'IsTalking',159:'GetSitting',161:'GetIsCurrentPackage',182:'GetEquipped',214:'HasMagicEffect',248:'IsScenePlaying',249:'IsInDialogueWithPlayer',250:'GetLocationCleared',263:'IsWeaponOut',264:'HasSpell',277:'GetBaseActorValue',289:'IsInCombat',300:'IsInInterior',310:'GetInWorldspace',323:'GetCombatState',354:'IsEssential',359:'GetInCurrentLoc',360:'GetInCurrentLocAlias',362:'HasLinkedRef',372:'IsInList',414:'Exists',430:'GetHealthPercentage',448:'HasPerk',453:'GetPlayerTeammate',543:'GetQuestCompleted',550:'IsSceneActionComplete',560:'HasKeyword',561:'HasRefType',566:'GetIsAliasRef',576:'GetEventData',590:'IsInScene',598:'GetLocationAliasCleared',603:'IsInSameCurrentLocAsRef',604:'IsInSameCurrentLocAsRefAlias',629:'GetVMQuestVariable',630:'GetVMScriptVariable',639:'GetWithinDistance',650:'IsLinkedTo',726:'DoesNotExist'}
CT={0:'==',1:'!=',2:'>',3:'>=',4:'<',5:'<='}
def name(fid):
    r=P.byfid.get(fid)
    return '%s[%s %08X]'%(r.edid(),r.type,fid) if r else '%08X'%fid
def full(r): return esm.lstr(r.get('FULL'))
def ctda(b):
    op=b[0]; cmp=CT.get(op>>5,'?'); fl=op&0x1f
    val=struct.unpack_from('<f',b,4)[0] if not fl&4 else name(struct.unpack_from('<I',b,4)[0])
    fn=struct.unpack_from('<H',b,8)[0]; p1,p2=struct.unpack_from('<II',b,12); rt=struct.unpack_from('<I',b,20)[0]; ref=struct.unpack_from('<I',b,24)[0]
    run={0:'subj',1:'targ',2:'ref',3:'combtarg',4:'linked',5:'alias',6:'pkgdata',7:'evdata'}.get(rt,rt)
    return '%s(%s,%s) on %s%s %s %s%s'%(FN.get(fn,'fn%d'%fn),name(p1) if p1>0xffff else p1,name(p2) if p2>0xffff else p2,run,(' '+name(ref)) if ref else ('#%d'%ref if rt==5 else ''),cmp,val,' OR' if fl&1 else '')
def rec(x): return P.byedid[x.lower()] if isinstance(x,str) else P.byfid[x]
def qdump(e,conds=True):
    q=rec(e); print('QUEST',q.edid(),'%08X'%q.fid,repr(full(q)))
    d=q.get('DNAM'); print(' DNAM flags=%04X pri=%d'%(struct.unpack_from('<H',d,0)[0],d[2]))
    for t,v in q.subs():
        if t=='INDX': print(' STAGE',struct.unpack_from('<H',v,0)[0],'flags',v[2])
        elif t=='CNAM': print('    log:',esm.lstr(v)[:140])
        elif t=='QOBJ': print(' OBJ',struct.unpack_from('<H',v,0)[0])
        elif t=='NNAM': print('    objtext:',esm.lstr(v)[:110])
        elif t=='QSTA': print('    target alias',struct.unpack_from('<i',v,0)[0])
        elif t in ('ALST','ALLS'): print(' ALIAS',t,struct.unpack_from('<I',v,0)[0])
        elif t=='ALID': print('    name',esm.lstr(v))
        elif t=='ALFR': print('    forced',name(esm.fid_of(v)))
        elif t=='ALUA': print('    unique',name(esm.fid_of(v)))
        elif t=='ALFL': print('    flags %08X'%struct.unpack_from('<I',v,0)[0])
        elif t=='ALFA': print('    from alias',struct.unpack_from('<i',v,0))
        elif t=='ALCO': print('    create',name(esm.fid_of(v)))
        elif t=='PKID': print('    pkg',name(esm.fid_of(v)))
        elif t=='ALSP': print('    spell',name(esm.fid_of(v)))
        elif t=='CTDA' and conds: print('    cond',ctda(v))
    vm=q.get('VMAD')
    if vm:
        x=vmad.parse(vm,'QUST'); print(' scripts',[(s[0],s[1]) for s in x['scripts']]); print(' fragfile',x.get('fragfile'))
        for f in sorted(x.get('frags',[])): print('   frag stage',f[0],f[3])
    return q
PSC=os.path.join(W,'dis')
def psc(name): 
    p=os.path.join(PSC,name.lower()+'.txt'); return open(p).read() if os.path.exists(p) else None
def frag(name,fn):
    t=psc(name); m=re.search(r'FUNC \[[^\]]*\] %s\(.*?(?=\nFUNC |\Z)'%fn,t,re.S); return m.group(0) if m else None
def qfrags(e):
    q=rec(e); x=vmad.parse(q.get('VMAD'),'QUST')
    for st,le,sn,fn in sorted(x.get('frags',[])):
        print('=== stage',st); print(frag(x['fragfile'],fn))
def info_dial(r):
    for gt,lab in reversed(r.path):
        if gt==7: return P.byfid.get(struct.unpack('<I',lab)[0])
_IOD=None
def iod():
    global _IOD
    if _IOD is None:
        _IOD={}
        for r in P.recs:
            if r.type=='INFO':
                d=info_dial(r)
                if d: _IOD.setdefault(d.fid,[]).append(r)
    return _IOD
INT=re.compile(r'setstage|setobjective|\.start\(|\.stop\(|forceref|enable|disable|moveto|scene|evaluatepackage|playercontrols|completequest|setav|modav|setactorvalue|modactorvalue|addspell|removespell|dispel|setessential|setprotected',re.I)
def fragtext(r):
    vm=r.get('VMAD')
    if not vm: return []
    x=vmad.parse(vm,r.type); f=x.get('fragfile')
    if not f: return []
    t=psc(f)
    if t is None: return ['(missing psc %s)'%f]
    want=set(fn for *_,fn in x.get('frags',[]) )
    out=[]
    for fn in want:
        b=frag(f,fn) or ''
        out+=[l.strip() for l in b.splitlines() if re.search(r'callmethod|callstatic|propset',l) and not re.search(r'GetActorRef|GetReference|GetOwningQuest|GetActorReference',l)]
    return out
def idump(r,pre=''):
    d=info_dial(r)
    print(pre+'INFO %08X topic=%s'%(r.fid,d.edid() if d else '?'), esm.lstr(r.get('RNAM'))[:60])
    e=r.get('ENAM')
    if e: print(pre+'   flags %04X'%struct.unpack_from('<H',e,0)[0])
    for v in r.getall('NAM1')[:2]: print(pre+'   says:',esm.lstr(v)[:110])
    for v in r.getall('CTDA'): print(pre+'   if',ctda(v))
    for l in fragtext(r): print(pre+'   frag>',l[:150])
    for v in r.getall('TCLT'): print(pre+'   ->',name(esm.fid_of(v)))
def walk(topic,depth=0,seen=None,maxd=6):
    seen=seen if seen is not None else set()
    d=rec(topic)
    if d.fid in seen or depth>maxd: return
    seen.add(d.fid); pre='  '*depth
    q=d.get('QNAM')
    print(pre+'TOPIC',d.edid(),'"%s"'%esm.lstr(d.get('FULL')), name(esm.fid_of(q)) if q else '')
    for r in iod().get(d.fid,[]):
        idump(r,pre+' ')
        for v in r.getall('TCLT'): walk(esm.fid_of(v),depth+1,seen,maxd)
def quest_infos(e):
    q=rec(e); out=[]
    for dfid,infos in iod().items():
        d=P.byfid[dfid]; qn=d.get('QNAM')
        if qn and esm.fid_of(qn)==q.fid: out+= [(d,r) for r in infos]
    return out
def grep(pat,files='*'):
    import glob
    for p in sorted(glob.glob(os.path.join(PSC,files+'.txt'))):
        for i,l in enumerate(open(p)):
            if re.search(pat,l,re.I): print(os.path.basename(p),i+1,l.rstrip()[:160])
def cell_of(r):
    for gt,lab in reversed(r.path):
        if gt in (6,8,9,10): return P.byfid.get(struct.unpack('<I',lab)[0])
def cellname(r):
    c=cell_of(r)
    if not c: return '?'
    return '%s "%s"'%(c.edid(),full(c))
def xtel(r):
    v=r.get('XTEL')
    if not v: return None
    d=struct.unpack_from('<I6fI',v,0); return {'door':d[0],'pos':d[1:4],'rot':d[4:7],'flags':d[7],'raw':v}
def refpos(r):
    v=r.get('DATA'); return struct.unpack_from('<6f',v,0) if v else None
