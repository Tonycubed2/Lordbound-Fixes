import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import pex,pexw
from pexw import ID,I,F,B,STR,NONE,insert,ensure_local,add_var,getfunc
SRC=os.path.expanduser('~/mnt/Lordbound/scripts')
DST=os.path.expanduser('~/mnt/Lordbound Fixes/scripts')
SFIX=[]
def sfix(script,desc):
    def d(f): SFIX.append((script,desc,f)); return f
    return d
def load(n): return pex.Pex(open(os.path.join(SRC,n.lower()+'.pex'),'rb').read())

@sfix('DD_LBMQ09QuestScript',"Sins of the Father: remember the player's SpeedMult when you become Lanrick and restore any amount lost when you change back")
def s_lbmq09q(p):
    add_var(p,'::LBFixSpeed_var','Float',F(0))
    f=getfunc(p,'LanrickTransform')
    for n,t in (('::lbfA','Actor'),('::lbfF','Float')): ensure_local(f,n,t)
    insert(p,'LanrickTransform',0,[
        ('callstatic',[ID('Game'),ID('GetPlayer'),ID('::lbfA')]),
        ('callmethod',[ID('GetActorValue'),ID('::lbfA'),ID('::lbfF'),STR('SpeedMult')]),
        ('assign',[ID('::LBFixSpeed_var'),ID('::lbfF')]),
    ])
    f=getfunc(p,'LanrickRevert')
    for n,t in (('::lbfA','Actor'),('::lbfF','Float'),('::lbfD','Float'),('::lbfB','Bool'),('::NoneVar','None')): ensure_local(f,n,t)
    insert(p,'LanrickRevert',None,[
        ('callstatic',[ID('Utility'),ID('Wait'),ID('::NoneVar'),F(1.0)]),
        ('callstatic',[ID('Game'),ID('GetPlayer'),ID('::lbfA')]),
        ('callmethod',[ID('GetActorValue'),ID('::lbfA'),ID('::lbfF'),STR('SpeedMult')]),
        ('fsub',[ID('::lbfD'),ID('::LBFixSpeed_var'),ID('::lbfF')]),
        ('cmp_gt',[ID('::lbfB'),ID('::lbfD'),F(0.5)]),
        ('jmpf',[ID('::lbfB'),I(4)]),
        ('callmethod',[ID('ModActorValue'),ID('::lbfA'),ID('::NoneVar'),STR('SpeedMult'),ID('::lbfD')]),
        ('callmethod',[ID('ModActorValue'),ID('::lbfA'),ID('::NoneVar'),STR('CarryWeight'),F(0.1)]),
        ('callmethod',[ID('ModActorValue'),ID('::lbfA'),ID('::NoneVar'),STR('CarryWeight'),F(-0.1)]),
    ])

@sfix('DD__QF_DD_LBMQ09_0105BC20',"Sins of the Father: stage 260 also removes both flashback speed debuffs before you change back (in case stage 253 was skipped)")
def s_lbmq09f(p):
    f=getfunc(p,'Fragment_26')
    ensure_local(f,'::lbfA','Actor'); ensure_local(f,'::lbfB','Bool')
    insert(p,'Fragment_26',0,[
        ('callstatic',[ID('Game'),ID('GetPlayer'),ID('::lbfA')]),
        ('callmethod',[ID('RemoveSpell'),ID('::lbfA'),ID('::lbfB'),ID('::DD_LBMQ09FlashbackSpeedDebuff_var')]),
        ('callmethod',[ID('RemoveSpell'),ID('::lbfA'),ID('::lbfB'),ID('::DD_LBMQ09FlashbackSpeedDebuff02_var')]),
    ])

@sfix('DD__QF_DD_ImpMQ09A_010407D4',"The Sacking of Garshakur: Faaram Marvani is flagged essential on his base record, so 'Defeat Faaram Marvani' (stage 190) could never be completed; the stage now makes him mortal")
def s_impmq09a(p):
    f=getfunc(p,'Fragment_19'); ensure_local(f,'::lbfAB','ActorBase'); ensure_local(f,'::temp1','Actor'); ensure_local(f,'::NoneVar','None')
    insert(p,'Fragment_19',0,[
        ('callmethod',[ID('GetActorRef'),ID('::Alias_Mercenary03Alias_var'),ID('::temp1')]),
        ('callmethod',[ID('GetActorBase'),ID('::temp1'),ID('::lbfAB')]),
        ('callmethod',[ID('SetEssential'),ID('::lbfAB'),ID('::NoneVar'),B(False)]),
    ])

@sfix('DD__SF_DD_LBMQ02FulazWyrmsban_0105C5D1',"Grave of the First: barrier fragment now runs at the start of the casting phase, waits 6 s for Fulaz's spell, removes the barrier, then ends the scene if it is still stuck 4 s later")
def s_lbmq02(p):
    f=getfunc(p,'Fragment_2'); ensure_local(f,'::lbfB','Bool'); ensure_local(f,'::NoneVar','None')
    insert(p,'Fragment_2',0,[('callstatic',[ID('Utility'),ID('Wait'),ID('::NoneVar'),F(6.0)])])
    insert(p,'Fragment_2',None,[
        ('callstatic',[ID('Utility'),ID('Wait'),ID('::NoneVar'),F(4.0)]),
        ('callmethod',[ID('IsPlaying'),ID('self'),ID('::lbfB')]),
        ('jmpf',[ID('::lbfB'),I(2)]),
        ('callmethod',[ID('Stop'),ID('self'),ID('::NoneVar')]),
    ])

@sfix('DD__QF_DD_OrcNQ01_0107FCD1',"Marks of a Fighter: stage 40 takes 1 drink and 12 skulls from the new lists (any Stonebark drink or Ale; vanilla or Lordbound skull) instead of only the vanilla items")
def s_orcnq01(p):
    import pexw as W
    W.add_prop(p,'LBFixDrinks','FormList'); W.add_prop(p,'LBFixSkulls','FormList')
    f=getfunc(p,'Fragment_4')
    for n,t in W.LIST_LOCALS: ensure_local(f,n,t)
    old=f['ins']
    assert old[1]==('cast',[ID('::temp2'),ID('::pAle_var')]) and old[7]==('cast',[ID('::temp2'),ID('::pBoneHumanSkullFull_var')]), old[:9]
    keep=old[3:6]   # mammoth snout removal stays as it was
    new=W.assemble([('callstatic',[ID('Game'),ID('GetPlayer'),ID('::lbfA')])]+W.remove_from_list('::LBFixDrinks_var',1)+W.remove_from_list('::LBFixSkulls_var',12))
    f['ins']=new+keep+old[9:]
    for i,d in enumerate(p.debug):
        if d[2]=='Fragment_4' and d[4]: p.debug[i]=(d[0],d[1],d[2],d[3],[d[4][0]]*len(f['ins']))

def build():
    os.makedirs(DST,exist_ok=True); done=[]
    for script,desc,f in SFIX:
        p=load(script); f(p); data=pexw.serialize(p)
        q=pex.Pex(data)  # re-parse check
        open(os.path.join(DST,script.lower()+'.pex'),'wb').write(data); done.append((script,desc))
    return done
if __name__=='__main__':
    for s,d in build(): print('wrote',s)
