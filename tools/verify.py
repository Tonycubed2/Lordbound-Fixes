import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lb import P,esm,vmad
q=esm.Plugin(os.path.expanduser('~/mnt/Lordbound Fixes/Lordbound Fixes.esp'))
bad=0
for r in q.recs:
    o=P.byfid.get(r.fid)
    if o is None:
        if r.fid>>24==6 and 0x800<=(r.fid&0xFFFFFF)<=0xFFF: print('new',r.type,hex(r.fid),r.edid(),len(r.getall('LNAM')),'entries'); continue
        print('NEW?',r.type,hex(r.fid)); bad+=1; continue
    if o.type!=r.type: print('TYPE MISMATCH',hex(r.fid)); bad+=1
    if [(g,l) for g,l in o.path]!=[(g,l) for g,l in r.path]: print('PATH MISMATCH',r.type,hex(r.fid),o.path,r.path); bad+=1
    try: r.subs()
    except Exception as e: print('SUBS ERR',hex(r.fid),e); bad+=1
    v=r.get('VMAD')
    if v:
        try: vmad.parse(v,r.type)
        except Exception as e: print('VMAD ERR',hex(r.fid),e); bad+=1
# group sizes sanity: re-walk already done by Plugin; check record count vs HEDR
import struct
print('records',len(q.recs),'HEDR count',struct.unpack_from('<fII',q.header.get('HEDR'))[1],'problems',bad)
