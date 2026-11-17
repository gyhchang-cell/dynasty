"""Check recent curated provenance against immutable tree blobs, never infer semantic credit."""
from ledger import B,O,R
import json,hashlib,datetime
rows=json.loads((O/'reviewed.json').read_text())[274:]
files={};trees={};n=0;archive_refs=0;tree_refs=0
for row in rows:
 for ref in row['source_refs']+row.get('auxiliary_refs',[]):
  repo=ref.get('repo',row['repo']);commit=ref.get('commit',row['commit'])
  root=B/'sources'/repo.replace('/','__')
  if repo not in trees:
   meta=json.loads((root/'source.json').read_text())
   if (root/'tree.json').exists():
    tree=json.loads((root/'tree.json').read_text());assert meta['commit']==tree['sha'] and not tree.get('truncated')
    trees[repo]=(meta['commit'],{x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'},None)
   else:
    assert meta.get('archive_sha256') and meta['archive_url'].endswith('/'+meta['commit'])
    trees[repo]=(meta['commit'],None,{x['path']:x['sha256'] for x in meta['files']})
  rev,blobs,archive_files=trees[repo];assert rev==commit
  path=R/ref['path'];assert path.resolve().is_relative_to(root.resolve())
  raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  assert sha==ref['file_sha256']
  if blobs is not None:
   assert blob==blobs[ref['source_path']];tree_refs+=1
  else:
   assert sha==archive_files[ref['source_path']];archive_refs+=1
  a,b=ref['lines'];assert 1<=a<=b<=len(raw.decode().splitlines())
  assert ref['url']==f'https://github.com/{repo}/blob/{commit}/{ref["source_path"]}#L{a}-L{b}'
  files[ref['path']]={'sha256':sha,'git_blob_sha1':blob if blobs is not None else None,'basis':'fixed_commit_tree_blob' if blobs is not None else 'fixed_commit_archive_cached_file_manifest','archive_bytes_rehashed_now':False};n+=1
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows_verified':len(rows),'tree_blob_reference_ranges_verified':tree_refs,'fixed_archive_manifest_reference_ranges_verified':archive_refs,'archive_boundary':'Archive-only source checks cached source SHA against manifest and fixed commit URL; no tree or current archive-byte verification claimed.','unique_files_verified':len(files),'reference_ranges_verified':n,'rows':[r['id'] for r in rows],'files':files,'semantic_independence_automatically_proven':False,'effective_credits_added_by_verifier':0,'game_started':False}
(O/'RECENT-PROVENANCE-20261027.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['files','rows']},ensure_ascii=False))
