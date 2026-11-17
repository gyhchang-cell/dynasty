"""Remove only debug-name attributes in a derived analysis copy; retain bytecode bytes."""
from pathlib import Path
import struct,zipfile,hashlib,json,subprocess
U2=lambda n:struct.pack('>H',n)
U4=lambda n:struct.pack('>I',n)
def strip(data):
 pos=8;cp={};n=struct.unpack_from('>H',data,pos)[0];pos+=2;i=1
 while i<n:
  tag=data[pos];pos+=1
  if tag==1:
   ln=struct.unpack_from('>H',data,pos)[0];pos+=2;cp[i]=data[pos:pos+ln].decode('utf-8',errors='replace');pos+=ln
  elif tag in [3,4,9,10,11,12,17,18]:pos+=4
  elif tag in [5,6]:pos+=8;i+=1
  elif tag in [7,8,16,19,20]:pos+=2
  elif tag==15:pos+=3
  else:raise ValueError(tag)
  i+=1
 prefix=data[:pos];payload=data[pos:];codes=[]
 def attrs(buf,off):
  count=struct.unpack_from('>H',buf,off)[0];off+=2;out=[]
  for _ in range(count):
   idx,ln=struct.unpack_from('>HI',buf,off);off+=6;body=buf[off:off+ln];off+=ln;name=cp[idx]
   if name in ['LocalVariableTable','LocalVariableTypeTable','MethodParameters']:continue
   if name=='Code':
    length=struct.unpack_from('>I',body,4)[0];codes.append(hashlib.sha256(body[8:8+length]).hexdigest());k=8+length;ec=struct.unpack_from('>H',body,k)[0];k+=2+8*ec;tail,end=attrs(body,k);assert end==len(body);body=body[:k]+tail
   out.append(U2(idx)+U4(len(body))+body)
  return U2(len(out))+b''.join(out),off
 off=6;ni=struct.unpack_from('>H',payload,off)[0];off+=2+2*ni;out=payload[:off]
 for group in range(2):
  count=struct.unpack_from('>H',payload,off)[0];off+=2;out+=U2(count)
  for _ in range(count):
   out+=payload[off:off+6];off+=6;a,off=attrs(payload,off);out+=a
 a,off=attrs(payload,off);out+=a;assert off==len(payload)
 return prefix+out,codes
if __name__=='__main__':
 b=Path(__file__).resolve().parent;src=b/'source/old-complete-inner-input.jar';out=b/'source/old-debug-stripped-analysis.jar';records=[]
 with zipfile.ZipFile(src)as z,zipfile.ZipFile(out,'w')as dz:
  for n in z.namelist():
   raw=z.read(n);derived,codes=strip(raw);again,codes2=strip(derived);assert derived==again and codes==codes2;dz.writestr(n,derived);records.append({'entry':n,'raw_sha256':hashlib.sha256(raw).hexdigest(),'derived_sha256':hashlib.sha256(derived).hexdigest(),'unchanged_instruction_code_hashes':codes})
 dest=b/'derived-1.12-final';dest.mkdir(exist_ok=True);tool='/Users/a15356015027/.gradle/caches/minecraftforge/forgegradle/mavenizer/caches/maven/mcp-tools/org/vineflower/vineflower/1.10.1/vineflower-1.10.1.jar';cmd=['/usr/bin/java','-Djava.awt.headless=true','-Xmx256m','-jar',tool,'-log=WARN','-thr=1',str(out),str(dest)]
 with (b/'decompiler-final.log').open('w')as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=45)
 assert p.returncode==0
 assert all('☃'not in p.read_text()for p in dest.glob('*.java'))
 (b/'debug-strip-receipt.json').write_text(json.dumps({'records':records,'command':cmd,'reason':'Debug-name flags in cached tool left ambiguous snowman references; remove only debug name tables in derived analysis class copies','all_Code_instruction_bytes_preserved':True,'game_starts':0,'production_changes':0,'raw_client_or_cache_modified':False},indent=2)+'\n');print('readable',len(records))
