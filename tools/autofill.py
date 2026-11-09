import sys,os,re,struct; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import *
TYPEMAP={'objectreference':('REFR','ACHR','PGRE','PHZD'),'actor':('ACHR',),'quest':('QUST',),'scene':('SCEN',),'globalvariable':('GLOB',),'actorbase':('NPC_',),'faction':('FACT',),'spell':('SPEL',),'message':('MESG',),'keyword':('KYWD',),'formlist':('FLST',),'package':('PACK',),'magiceffect':('MGEF',),'weapon':('WEAP',),'armor':('ARMO',),'miscobject':('MISC',),'key':('KEYM',),'book':('BOOK',),'sound':('SNDR',),'location':('LCTN',),'imagespacemodifier':('IMAD',),'effectshader':('EFSH',),'visualeffect':('RFCT',),'activator':('ACTI',),'idle':('IDLE',),'topic':('DIAL',),'topicinfo':('INFO',),'outfit':('OTFT',),'leveleditem':('LVLI',),'leveledactor':('LVLN',),'potion':('ALCH',),'explosion':('EXPL',),'hazard':('HAZD',),'weather':('WTHR',),'cell':('CELL',),'worldspace':('WRLD',),'locationreftype':('LCRT',),'static':('STAT',),'light':('LIGH',),'door':('DOOR',),'container':('CONT',),'race':('RACE',),'class':('CLAS',),'musictype':('MUSC',),'form':None,'shout':('SHOU',),'wordofpower':('WOOP',),'ingredient':('INGR',),'projectile':('PROJ',),'perk':('PERK',),'enchantment':('ENCH',),'sounddescriptor':('SNDR',),'furniture':('FURN',),'objectreference[]':None}
rows=[l.split('|') for l in open('unfilled.txt') if '|' in l]
fills={}; miss=[]
for a,b,c in rows:
    aa=a.split(); typ,fid=aa[0],int(aa[1],16); ed=aa[2] if len(aa)>2 else ''; bb=b.split(); ctx,scr=(bb if len(bb)==2 else ['',bb[0]]); ptype,pname=c.split()
    owner=P.byfid[fid]
    cand=None
    if ptype.lower() in ('referencealias','locationalias') and pname.lower().startswith('alias_') and owner.type=='QUST':
        an=pname[6:].lower(); aid=None
        cur=None
        for t,v in owner.subs():
            if t in ('ALST','ALLS'): cur=struct.unpack_from('<I',v,0)[0]
            elif t=='ALID' and esm.lstr(v).lower()==an: aid=cur
        if aid is not None: cand=('alias',owner.fid,aid)
    else:
        r=P.byedid.get(pname.lower())
        ok=TYPEMAP.get(ptype.lower(),'?')
        if r is not None and (ok is None or ok=='?' or r.type in ok): cand=('form',r.fid,r.type)
    if cand: fills.setdefault((fid,ctx,scr),[]).append((pname,ptype,cand))
    else: miss.append((typ,ed,ctx,scr,ptype,pname))
import pickle; pickle.dump(fills,open('fills.pkl','wb'))
print('fillable props',sum(len(v) for v in fills.values()),'records',len(fills),'unmatched',len(miss))
from collections import Counter
print(Counter(m[0] for m in miss))
for m in miss:
    if m[0] in ('QUST','SCEN','INFO'): print('MISS',m)
