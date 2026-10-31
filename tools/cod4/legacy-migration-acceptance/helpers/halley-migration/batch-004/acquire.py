"""Download source bytes and official Git objects for static inspection only."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, io, json, ssl, urllib.request, zipfile
ROOT = Path('/Users/a15356015027/Desktop/dynasty')
BASE = Path(__file__).resolve().parent
DOC = ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
CTX = ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def get(url):
    request = urllib.request.Request(url, headers={'User-Agent':'Halley-static-source-audit'})
    with urllib.request.urlopen(request, context=CTX, timeout=60) as response:
        return response.read()
def sha(b): return hashlib.sha256(b).hexdigest()
def run():
    results=json.loads((BASE/'source-manifest.json').read_text()) if (BASE/'source-manifest.json').exists() else []
    for source in json.loads((DOC/'SOURCE-RESERVATION-20261028-004.json').read_text())['repos']:
        if any(r['repo']==source['repo'] and r['commit']==source['commit'] for r in results):continue
        repo=source['repo']; commit=source['commit']; key=repo.replace('/','__')
        meta=BASE/'provenance'/key; meta.mkdir(parents=True, exist_ok=True)
        commit_raw=get('https://api.github.com/repos/'+repo+'/git/commits/'+commit)
        commit_obj=json.loads(commit_raw); assert commit_obj['sha']==commit
        tree=commit_obj['tree']['sha']
        tree_raw=get('https://api.github.com/repos/'+repo+'/git/trees/'+tree+'?recursive=1')
        tree_obj=json.loads(tree_raw); assert tree_obj['sha']==tree and not tree_obj.get('truncated')
        (meta/'commit.json').write_bytes(commit_raw); (meta/'tree.json').write_bytes(tree_raw)
        blobs={x['path']:x['sha'] for x in tree_obj['tree'] if x['type']=='blob'}
        archive=get('https://codeload.github.com/'+repo+'/zip/'+commit)
        root=BASE/'sources'/key; root.mkdir(parents=True,exist_ok=True)
        files=[]
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            for member in z.infolist():
                if member.is_dir(): continue
                rel='/'.join(member.filename.split('/')[1:])
                if not (rel.endswith('.java') or rel.lower().startswith('license') or rel.lower().startswith('readme')): continue
                assert '..' not in Path(rel).parts and not Path(rel).is_absolute()
                raw=z.read(member)
                blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                assert blob==blobs[rel], rel
                target=root/rel; target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                files.append({'path':rel,'source':str(target.relative_to(ROOT)),'sourceSha256':sha(raw),'source_blob':blob})
        row=dict(source,git_tree=tree,commit_metadata_sha256=sha(commit_raw),tree_metadata_sha256=sha(tree_raw),archive_sha256=sha(archive),files=files)
        results.append(row)
        print(repo,commit,'verified source files',len(files),flush=True)
    (BASE/'source-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__': run()
