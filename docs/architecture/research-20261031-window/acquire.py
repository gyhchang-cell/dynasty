"""Bounded normal-TLS reference acquisition; does not credit or register buildings."""
import subprocess,json,re,html,hashlib,pathlib,urllib.parse,datetime
ROOT=pathlib.Path(__file__).resolve().parent

def stamp():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
def encoded(url):
 u=urllib.parse.urlsplit(url);return urllib.parse.urlunsplit((u.scheme,u.netloc,urllib.parse.quote(urllib.parse.unquote(u.path),safe='/:@'),urllib.parse.quote(urllib.parse.unquote(u.query),safe='=&/:?@'),u.fragment))
def get(folder,name,url):
 p=ROOT/folder;p.mkdir(parents=True,exist_ok=True);f=p/name
 if f.exists():raise RuntimeError('Refuse silent overwrite '+str(f))
 r=subprocess.run(['curl','--fail','--location','--max-time','25','--silent','--show-error','--output',str(f),'--write-out','%{http_code}',encoded(url)],capture_output=True,text=True)
 row={'file':name,'url':url,'request_url':encoded(url),'returncode':r.returncode,'http_code':r.stdout.strip(),'stderr':r.stderr,'bytes':f.stat().st_size if f.exists() else 0,'at':stamp(),'actually_viewed':False}
 if r.returncode==0:row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 elif f.exists():f.rename(f.with_suffix(f.suffix+'.failed'))
 receipt=p/(name+'.download.json');receipt.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
 if row['http_code']=='429' or '429' in row['stderr'] or 'usage limit' in row['stderr'].lower():raise RuntimeError('Provider limit recorded; STOP acquisition')
 return row

def meta(folder,key,url):
 row=get(folder,key+'.html',url)
 if row['returncode']:return row,None
 s=(ROOT/folder/(key+'.html')).read_text();t=html.unescape(s)
 m=re.search(r'<div class="fullImageLink".*?<a href="([^"]+)"',s,re.S)
 def field(name):
  z=re.search('id="fileinfotpl_'+name+'".*?</td>\\s*<td[^>]*>(.*?)</td>',t,re.S)
  return re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',z.group(1))).strip() if z else None
 licenses=[]
 for z in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
  try:
   d=json.loads(z);licenses.append(d.get('license'))
  except (json.JSONDecodeError,AttributeError):pass
 d={'source_url':url,'original_url':html.unescape(m.group(1)) if m else None,'author':field('aut'),'date':field('date'),'licenses':licenses,'metadata_saved_at':stamp(),'photo_actually_viewed':False,'not_whole_building_credit':True}
 (ROOT/folder/(key+'-meta.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return row,d
