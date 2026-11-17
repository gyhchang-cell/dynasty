"""Read Git objects only; never checkout or execute upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
pins=[(48, 'Ladysnake/Cardinal-Components-API', 'tag:5.3.0', '56dbc9c01b98c67c27f981dff60b98a371646845'), (49, 'Ladysnake/PlayerAbilityLib', 'tag:1.9.0', '49d6bf142a8680b73f0d2014c88169ad9a475c94')]
def sha(b):return hashlib.sha256(b).hexdigest()
for number,repo,branch,commit in pins:
    base=BASE/('batch-%03d'%number);db=base/'upstream.git'
    def git(*args):return subprocess.check_output(['git','--git-dir='+str(db),*args])
    obj=git('cat-file','commit',commit)
    assert hashlib.sha1(b'commit '+str(len(obj)).encode()+b'\0'+obj).hexdigest()==commit
    tree=obj.splitlines()[0].decode().split()[1]
    meta=base/'provenance'/repo.replace('/','__');meta.mkdir(parents=True,exist_ok=True)
    (meta/'commit.raw').write_bytes(obj)
    commit_meta={'sha':commit,'tree':{'sha':tree},'provenance':'local verified Git commit object','raw_sha256':sha(obj)}
    entries=[];files=[]
    for item in git('ls-tree','-rz',commit).split(b'\0'):
        if not item:continue
        head,path=item.split(b'\t',1);mode,kind,blob=head.decode().split();path=path.decode()
        entries.append({'path':path,'mode':mode,'type':kind,'sha':blob})
        name=Path(path).name
        if kind!='blob' or not (path.endswith('.java') or name.lower().startswith(('readme','license')) or name in ('gradle.properties','mods.toml','neoforge.mods.toml','fabric.mod.json') or name.endswith('.mixins.json')):continue
        raw=git('cat-file','blob',blob)
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
        dest=base/'sources'/repo.replace('/','__')/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        files.append({'path':path,'source':str(dest.relative_to(ROOT)),'sourceSha256':sha(raw),'source_blob':blob})
    tree_raw=git('cat-file','tree',tree)
    assert hashlib.sha1(b'tree '+str(len(tree_raw)).encode()+b'\0'+tree_raw).hexdigest()==tree
    (meta/'tree.raw').write_bytes(tree_raw)
    tree_meta={'sha':tree,'truncated':False,'tree':entries,'provenance':'git ls-tree -rz exact verified commit; tree.raw is exact root tree object'}
    cb=(json.dumps(commit_meta,indent=2)+'\n').encode();tb=(json.dumps(tree_meta,indent=2)+'\n').encode()
    (meta/'commit.json').write_bytes(cb);(meta/'tree.json').write_bytes(tb)
    manifest={'repo':repo,'branch':branch,'commit':commit,'git_tree':tree,'commit_metadata_sha256':sha(cb),'tree_metadata_sha256':sha(tb),'acquisition':'bare Git object read; no checkout, hooks disabled, no upstream execution','files':files}
    (base/'source-manifest.json').write_text(json.dumps([manifest],indent=2)+'\n')
    (base/'index.py').write_text((BASE/'batch-042/index.py').read_text())
    print(number,repo,commit,tree,'static files not credit',len(files))
