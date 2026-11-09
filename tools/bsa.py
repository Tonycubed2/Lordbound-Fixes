import struct,zlib
def listbsa(path):
    f=open(path,'rb'); h=f.read(36)
    magic,ver,off,flags,nfold,nfile,lfold,lfile,fflags=struct.unpack('<4sIIIIIIII',h)
    assert magic==b'BSA\0'
    f.seek(off)
    folders=[]
    for _ in range(nfold):
        if ver==105: hsh,cnt,_,ofs=struct.unpack('<QIIQ',f.read(24))
        else: hsh,cnt,ofs=struct.unpack('<QII',f.read(16))
        folders.append(cnt)
    out=[]; recs=[]
    for cnt in folders:
        n=f.read(1)[0]; name=f.read(n)[:-1].decode('latin1')
        files=[]
        for _ in range(cnt):
            fh,size,fo=struct.unpack('<QII',f.read(16)); files.append((size,fo))
        recs.append((name,files))
    names=f.read(lfile).split(b'\0')
    i=0; res={}
    for folder,files in recs:
        for size,fo in files:
            res[(folder+'\\'+names[i].decode('latin1')).lower()]=(size,fo); i+=1
    return res,flags,ver
def extract(path,entry,flags,ver):
    size,fo=entry; f=open(path,'rb'); comp=bool(flags&4)
    if size&0x40000000: comp=not comp; size&=0x3FFFFFFF
    f.seek(fo)
    if flags&0x100:
        n=f.read(1)[0]; f.read(n); size-=n+1
    data=f.read(size)
    if comp:
        orig=struct.unpack('<I',data[:4])[0]
        if ver==105:
            import lz4.frame as l4; return l4.decompress(data[4:])
        return zlib.decompress(data[4:])
    return data
