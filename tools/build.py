import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import fixes, espw
from lb import P
out=espw.Out(P)
ok=[]
for desc,f in fixes.FIXES:
    f(out); ok.append(desc)
dst=os.path.expanduser('~/mnt/Lordbound Fixes/Lordbound Fixes.esp')
n=out.build(dst,P.masters()+['Druadach.esm'],desc='Fixes for Lordbound 0.8.1 bugs (personal use)')
print('records',n,'fixes',len(ok))
