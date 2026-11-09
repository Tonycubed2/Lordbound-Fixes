# Each fix: (id, description, function(out)) ; function applies overrides to out
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import *
import espw
FIXES=[]
LOG=[]
def fix(desc):
    def d(f): FIXES.append((desc,f)); return f
    return d
def replace_ctda(r,pred,newfn):
    subs=[]; n=0
    for t,v in r.subs():
        if t=='CTDA' and pred(v): v=newfn(v); n+=1
        subs.append((t,v))
    assert n>0,'no ctda matched in %08X'%r.fid
    return subs

@fix("Masters of Highreach: Lanelle had no reaction line if Fardris's quest (LBMQ05) was the master quest you finished first, so the talk ended and stage 2 was never set; her generic line now covers that case")
def f_lbmq01(out):
    r=P.byfid[0x0505C4CE]
    subs=[(t,v) for t,v in r.subs() if not (t=='CTDA' and 'GetQuestCompleted(DD_LBMQ05' in ctda(v))]
    assert len(subs)==len(r.subs())-1
    out.override(r,subs)

import pickle, vmadw
BASETYPES=('ACTI','NPC_','CONT','MGEF','BOOK','KEYM','MISC','WEAP','FLOR','ARMO','LIGH','DOOR','FURN')
SKIPNAMES={'teleportmarker'}
AUTOFILL_REPORT=[]
import pex as _pex
_RN={}
def realname(scr,pn):
    k=scr.lower()
    if k not in _RN:
        p=os.path.expanduser('~/mnt/Lordbound/scripts/%s.pex'%k)
        _RN[k]={pr['name'].lower():pr['name'] for pr in _pex.Pex(open(p,'rb').read()).objects[0]['props']}
    return _RN[k].get(pn.lower(),pn)
@fix("Fill script properties the authors declared and use but left empty in the CK (quests, scenes, triggers, NPCs); empty properties make stages, scenes and triggers silently do nothing")
def f_autofill(out):
    fills=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fills.pkl'),'rb'))
    byrec={}
    for (fid,ctx,scr),L in fills.items():
        o=P.byfid[fid]
        for pn,pt,c in L:
            if pn.lower() in SKIPNAMES: continue
            if o.type in BASETYPES and pt.lower() in ('objectreference','actor'): continue
            pn=realname(scr,pn)
            if c[0]=='form': entry=(pn,c[1],-1)
            else: entry=(pn,c[1],c[2])
            d=byrec.setdefault(fid,[{},{}])
            if ctx: d[1].setdefault(int(ctx[5:]),{}).setdefault(scr.lower(),[]).append(entry)
            else: d[0].setdefault(scr.lower(),[]).append(entry)
    for fid,(adds,aadds) in byrec.items():
        r=P.byfid[fid]
        prev=out.ov.get(fid)
        subs=list(prev[1]) if prev and prev[1] else list(r.subs())
        for i,(t,v) in enumerate(subs):
            if t=='VMAD':
                nv,n=vmadw.add_props(v,r.type,adds,aadds); subs[i]=('VMAD',nv)
                AUTOFILL_REPORT.append((r.type,r.edid() or '%08X'%fid,n,[e[0] for L in adds.values() for e in L]+[e[0] for d in aadds.values() for L in d.values() for e in L]))
        out.override(r,subs)

def subs_of(out,r):
    prev=out.ov.get(r.fid)
    return list(prev[1]) if prev and prev[1] else list(r.subs())
def set_cond(out,fid,match,newval=None,newop=None):
    r=P.byfid[fid]; subs=subs_of(out,r); n=0
    for i,(t,v) in enumerate(subs):
        if t=='CTDA' and match in ctda(v):
            if newop is not None: v=espw.set_ctda_op(v,newop)
            if newval is not None: v=espw.set_ctda_value(v,newval)
            subs[i]=(t,v); n+=1
    assert n==1,('set_cond',hex(fid),match,n)
    out.override(r,subs)

@fix("Just Deserts: 'I had to kill him' / 'war criminal' replies required stage below 100, but killing Sergus sets stage 100, so options 2 and 3 dead-ended; now allowed up to stage 109")
def f_impsq01(out):
    for fid in (0x05096C91,0x05096C92,0x05096C8C):
        set_cond(out,fid,'GetStage(DD_ImpSQ01[QUST 05096CB8],0) on subj < 100.0',newval=110.0)

def drop_cond(out,fid,match):
    r=P.byfid[fid]; subs=subs_of(out,r)
    new=[(t,v) for t,v in subs if not (t=='CTDA' and match in ctda(v))]
    assert len(new)==len(subs)-1,('drop_cond',hex(fid),match)
    out.override(r,new)

@fix("The Lost Children: Lanelle's 'follow player to Garza' package only ran while she was inside Highreach, so she stopped following the moment you left town and the Garza scene trigger (needs both of you) never fired")
def f_orcmq05_lanelle(out):
    drop_cond(out,rec('DD_OrcMQ05LanelleFollowPlayerToGarza').fid,'GetInCurrentLoc(DDHighreachLocation')

def add_choices(out,fid,topic_fids):
    r=P.byfid[fid]; subs=subs_of(out,r)
    i=next(k for k,(t,v) in enumerate(subs) if t=='TRDT')
    new=subs[:i]+[('TCLT',struct.pack('<I',x)) for x in topic_fids]+subs[i:]
    out.override(r,new)

@fix("Wrath: Garom's two optional answers at the end had no links back to the remaining choices, so you were dropped into a '...' loop; they now offer the other questions and 'You can count on me'")
def f_orcmq09_garom(out):
    but,what,count=0x0506D37F,0x0506D380,0x0506D381
    add_choices(out,0x0506D392,[what,count])
    add_choices(out,0x0506D382,[but,count])

@fix("Kinslayer: after you spare Azgoth and pass Borgog's speech check, his reward line required stage 70 (the 'killed him' stage), so the quest never finished; the reward now also accepts the 'spared' stage 60")
def f_orcnq02(out):
    set_cond(out,0x0507FC73,'GetStage(DD_OrcNQ02[QUST 0507FCD3],0) on subj == 70.0',newval=60.0,newop=3)

@fix("Fill two more empty properties whose target records have slightly different names: Masters of Highreach 'LBMQ02' (Fulaz-Ahl's quest, used to tick his objective) and Tour of Duty's tracking spell (so M'zaad's tracking spell is removed afterwards)")
def f_manualfill(out):
    for edid,adds in (('DD_LBMQ01',{'dd__qf_dd_lbmq01_010173e2':[('LBMQ02',0x050173E1,-1)]}),
                      ('DD_ImpMQ01',{'dd_impmq01questscript':[('DD_ImpMQ01InterrogatorTrackerSpell',0x05018869,-1)]})):
        r=rec(edid); subs=subs_of(out,r)
        for i,(t,v) in enumerate(subs):
            if t=='VMAD':
                nv,n=vmadw.add_props(v,'QUST',adds); assert n==1,(edid,n); subs[i]=('VMAD',nv)
        out.override(r,subs)

import math
def set_xtel(out,doorfid,fwd,drot_deg):
    """Place the landing spot of door `doorfid` `fwd` units in front of the destination door (negative = behind), facing door heading + drot."""
    r=P.byfid[doorfid]; subs=subs_of(out,r); x=xtel(r); d=P.byfid[x['door']]; p=refpos(d); th=p[5]
    nx=p[0]+fwd*math.sin(th); ny=p[1]+fwd*math.cos(th); nz=p[2]
    nrot=th+math.radians(drot_deg)
    v=bytearray(x['raw']); struct.pack_into('<6f',v,4,nx,ny,nz,x['rot'][0],x['rot'][1],nrot)
    for i,(t,vv) in enumerate(subs):
        if t=='XTEL': subs[i]=('XTEL',bytes(v))
    out.override(r,subs)

@fix("Door landing spots that were left sitting on top of the destination door: Garshakur Tailor exit (you appeared between the door and the wall) and the Putrid Cove Retreat entrance (you appeared facing the wall)")
def f_doors(out):
    set_xtel(out,0x050AEA57,80,0)     # tailor -> exterior: this door model lands in front, same heading
    set_xtel(out,0x050146C7,-90,180)  # exterior -> Putrid Cove Retreat: room is behind this door, turn around


@fix("Grave of the First: Fulaz-Ahl's barrier-breaking scene only removed the barrier when his 'cast Thunderbolt at the barrier marker' package finished; if it never finished he stood there 'busy' forever. The barrier is now removed when that part of the scene starts (patched scene script waits a few seconds and ends the scene if it is still hung)")
def f_lbmq02_barrier(out):
    r=P.byfid[0x0505C5D1]; subs=subs_of(out,r)
    for i,(t,v) in enumerate(subs):
        if t=='VMAD':
            name=b'DD__SF_DD_LBMQ02FulazWyrmsban_0105C5D1'
            pat=bytes([2])+struct.pack('<I',2)+b'\x01'+struct.pack('<H',len(name))+name
            assert v.count(pat)==1
            subs[i]=('VMAD',v.replace(pat,bytes([1])+pat[1:]))
    out.override(r,subs)

FL_DRINKS=0x06000800; FL_SKULLS=0x06000801
def set_cond_param1(out,fid,oldp1,newp1):
    r=P.byfid[fid]; subs=subs_of(out,r); n=0
    for i,(t,v) in enumerate(subs):
        if t=='CTDA' and struct.unpack_from('<I',v,12)[0]==oldp1:
            subs[i]=(t,v[:12]+struct.pack('<I',newp1)+v[16:]); n+=1
    assert n==1,(hex(fid),hex(oldp1),n); out.override(r,subs)

@fix("Marks of a Fighter: Luzgrath asks for 'Stonebark Ale' and skulls, but only counted the vanilla Ale (rare in the valley) and the vanilla skull, not Lordbound's Stonebark ales or its own skull item; now any Stonebark drink or Ale, and either skull, count (and get taken)")
def f_orcnq01(out):
    drinks=[0x00034C5E]+[r.fid for r in P.recs if r.type=='ALCH' and 'stonebark' in r.edid().lower() and 'template' not in r.edid().lower() and 'custom' not in r.edid().lower()]
    skulls=[0x000AF5FD,0x0503FE57]
    out.new('FLST',FL_DRINKS,[('EDID',b'LBFix_OrcNQ01Drinks\0')]+[('LNAM',struct.pack('<I',f)) for f in drinks])
    out.new('FLST',FL_SKULLS,[('EDID',b'LBFix_OrcNQ01Skulls\0')]+[('LNAM',struct.pack('<I',f)) for f in skulls])
    for info in (0x0507FC92,0x0507FC9B,0x0507FC9A):
        set_cond_param1(out,info,0x00034C5E,FL_DRINKS)
        set_cond_param1(out,info,0x000AF5FD,FL_SKULLS)
    r=rec('DD_OrcNQ01'); subs=subs_of(out,r)
    for i,(t,v) in enumerate(subs):
        if t=='VMAD':
            nv,n=vmadw.add_props(v,'QUST',{'dd__qf_dd_orcnq01_0107fcd1':[('LBFixDrinks',FL_DRINKS,-1),('LBFixSkulls',FL_SKULLS,-1)]}); assert n==2; subs[i]=('VMAD',nv)
    out.override(r,subs)

@fix("The Lost Legion added at the end of Lordbound: the faction-epilogue quest picks a journal entry for stage 100, and the Imperial entry's only condition (The Lost Legion at stage 270) was flagged OR with nothing after it, which leaves that entry's test open-ended; the stray OR flag is removed")
def f_epilogue_or(out):
    r=rec('DD_FactionEpilogue'); subs=subs_of(out,r); n=0
    for i,(t,v) in enumerate(subs):
        if t=='CTDA' and 'GetStage(DD_ImpMQ10[QUST 0504A175],0) on subj == 270.0 OR' in ctda(v):
            subs[i]=(t,bytes([v[0]&~1])+v[1:]); n+=1
    assert n==1; out.override(r,subs)

@fix("Chasing Dreams: the 'Find 3 Brainrot Mushrooms (x/3)' and 'Find 3 Nightshade (x/3)' objectives showed '[...]/3' because their counter globals were never added to the quest's Text Display Globals list")
def f_lbmq05_qtgl(out):
    r=rec('DD_LBMQ05'); subs=subs_of(out,r)
    i=next(k for k,(t,v) in enumerate(subs) if t=='DNAM')+1
    subs=subs[:i]+[('QTGL',struct.pack('<I',0x050AC965)),('QTGL',struct.pack('<I',0x050AC966))]+subs[i:]
    out.override(r,subs)

def set_model(out,edid,tag,path):
    r=rec(edid); subs=subs_of(out,r); n=0
    for i,(t,v) in enumerate(subs):
        if t==tag: subs[i]=(t,path.encode('latin1')+b'\0'); n+=1; break
    assert n==1,(edid,tag); out.override(r,subs)

@fix("Models that point at files Lordbound never shipped (red '!' in game), repointed to an existing model: Ashlorn rib-cap pieces (4 placed), a blue crystal in Ysgramor's Folly (typo'd path), a Highrock Stop roof, Aedron's armor spaulders on women, and the Liquor of Rooting bottle")
def f_models(out):
    set_model(out,'DrV_wrintdragonroomribcap01','MODL',r'Architecture\Whiterun\WRInteriors\WRCastle\WRIntDragonRoomRibCap01.nif')
    set_model(out,'DRV_BlueStaticCrystal','MODL',r'Clutter\SoulGem\SoulGemGreater01.nif')
    set_model(out,'DrV_FFHouse02RoofSnow','MODL',r'Architecture\DrV_Frostford\BehindtheInnHouseSnowHeavy.nif')
    set_model(out,'DrV_EbonySpauldersAA','MOD3',r'armor\ebony\m\Lautasantenni_Spaulders2_1.nif')
    set_model(out,'DRVC_RootingLiquorBrew','MODL',r'clutter\DrV_StoneBark\Brews\DrV_StonebarkCOBR.nif')

@fix("Enigmatic Origins: the Jagged Crown on the skeleton atop the throne in the Revenant's version of Highreach was a real, lootable crown placed as loose loot; it is now a static decoration with the same model")
def f_jagged_crown(out):
    STATFID=0x06000802
    out.new('STAT',STATFID,[('EDID',b'LBFix_JaggedCrownStatic\0'),('OBND',bytes.fromhex('f7fff6fff5ff09000a000b00')),('MODL',b'Armor\\BoneCrown\\BoneCrownGO.nif\0'),('DNAM',struct.pack('<fI',90.0,0))])
    r=P.byfid[0x05032ED1]; subs=subs_of(out,r)
    subs=[(t,struct.pack('<I',STATFID) if t=='NAME' else v) for t,v in subs]
    out.override(r,subs)

@fix("Removed the three spell tomes (Golden Sparks, Disintegrate the Undead, Fierce Flames) from the developers' 'Core Team Armoury' test room: those spells' effects use textures Lordbound never shipped (purple effects); the tome references are now initially disabled")
def f_remove_tomes(out):
    for fid in (0x050902C9,0x0508DCD7,0x050960C0):
        r=P.byfid[fid]; prev=out.ov.get(fid)
        out.override(r,prev[1] if prev else None,flags=r.flags|0x800)
