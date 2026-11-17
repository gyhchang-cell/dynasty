from pathlib import Path
import subprocess,json,hashlib,datetime
B=Path(__file__).resolve().parent;out=B/'source-archives';out.mkdir(exist_ok=True);base='https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.1.0/forge-1.20.1-47.1.0-sources.jar';rows=[]
for suffix,name in [('.sha1','forge-47.1.0-sources.sha1'),('','forge-47.1.0-sources.zip')]:
 p=out/name;url=base+suffix;x=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','30',url,'-o',str(p)],capture_output=True,text=True);row=dict(url=url,local=str(p.relative_to(B)),exit_code=x.returncode,stderr=x.stderr)
 if x.returncode: rows.append(row);break
 row.update(sha1=hashlib.sha1(p.read_bytes()).hexdigest(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size);rows.append(row);print(name,row['bytes'])
if len(rows)==2 and not any(x['exit_code'] for x in rows):
 expected=(out/'forge-47.1.0-sources.sha1').read_text().strip().split()[0];assert rows[1]['sha1']==expected;rows[1]['maven_checksum_match']=True
(B/'forge-acquisition.json').write_text(json.dumps(dict(saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n')
