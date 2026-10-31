"""Fetch exact pinned primary files/dependencies; never counts reviews."""
import hashlib,json,pathlib,ssl,sys,urllib.request
R=pathlib.Path(__file__).resolve().parent;B=R.parents[2]/'build/item-use-references'
name,*suffixes=sys.argv[1:];source=B/name;dest=R/'.work/sources'/name
meta=json.loads((source/'source.json').read_text());tree=json.loads((source/'tree.json').read_text())
dest.mkdir(parents=True,exist_ok=True);(dest/'source.json').write_text(json.dumps(meta,indent=2)+'\n')
receipt=dest/'targeted-fetch-receipt.json';rows=json.loads(receipt.read_text())['files'] if receipt.exists() else []
for suffix in suffixes:
 matches=[x['path'] for x in tree['tree'] if x['path'].endswith(suffix)]
 if len(matches)!=1:raise ValueError((suffix,matches))
 path=matches[0];out=dest/path;out.parent.mkdir(parents=True,exist_ok=True)
 if not out.exists():
  if (source/path).exists():out.write_bytes((source/path).read_bytes())
  else:
   with urllib.request.urlopen(f"https://raw.githubusercontent.com/{meta['repo']}/{meta['sha']}/{path}",context=ssl.create_default_context(cafile='/etc/ssl/cert.pem'),timeout=30) as res:out.write_bytes(res.read())
 rows=[r for r in rows if r['path']!=path]+[dict(path=path,sha256=hashlib.sha256(out.read_bytes()).hexdigest())]
receipt.write_text(json.dumps(dict(repo=meta['repo'],commit=meta['sha'],files=rows,accepted=0),indent=2)+'\n');print('Pinned files',len(rows),'accepted 0')
