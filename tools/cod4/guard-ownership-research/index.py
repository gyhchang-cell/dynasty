#!/usr/bin/env python3
"""Pinned candidate extraction only. Never marks semantic review accepted."""
import hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.work/python39'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
BASE=ROOT.parents[2]/'build/item-use-references'
OUT=ROOT/'.work'; OUT.mkdir(exist_ok=True)
def digest(b): return hashlib.sha256(b).hexdigest()
def walk(n):
    yield n
    for c in n.children: yield from walk(c)
rows=[]; sources={}; source_keys=set()
for repo in sorted(list(BASE.iterdir())+list((OUT/'sources').iterdir())):
    meta=repo/'source.json'
    if not meta.exists(): continue
    try: info=json.loads(meta.read_text())
    except Exception: continue
    if not info.get('sha') or not info.get('repo'):continue
    for f in sorted(repo.rglob('*.java')):
        rel=f.relative_to(repo).as_posix()
        if re.search(r'/(client|renderers?|models?|datagen|data|test|integration)/',rel,re.I):continue
        source_key=(info['repo'],info['sha'],rel)
        if source_key in source_keys:continue
        source_keys.add(source_key)
        b=f.read_bytes(); txt=b.decode('utf8',errors='replace')
        if not re.search(r'(Summon|Tame|Familiar|OwnerHurt|FollowOwner|Guard|Pet|Minion|Servant|isAlliedTo|wantsToAttack|getOwnerUUID)',txt):continue
        tree=parser.parse(b)
        for n in walk(tree.root_node):
            if n.type not in ('method_declaration','constructor_declaration'):continue
            parent=n.parent
            nested=False
            while parent is not None:
                if parent.type in ('method_declaration','constructor_declaration'): nested=True;break
                parent=parent.parent
            if nested:continue
            body=n.child_by_field_name('body')
            name=n.child_by_field_name('name')
            if body is None or name is None:continue
            text=b[n.start_byte:n.end_byte].decode('utf8')
            # Filter to behavior, not attributes, recipes, animation, or accessors.
            if not re.search(r'(target|owner|summon|tame|familiar|ally|allied|canAttack|hurt|attack|follow|servant|minion|guard|expire|lifespan)',text,re.I):continue
            if len(text)<110:continue
            norm=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
            norm=re.sub(r'\s+','',norm)
            key=f"{info['repo']}@{info['sha']}:{rel}:{n.start_point.row+1}:{n.end_point.row+1}"
            rows.append(dict(id=digest(key.encode())[:16],repo=info['repo'],commit=info['sha'],path=rel,start=n.start_point.row+1,end=n.end_point.row+1,name=b[name.start_byte:name.end_byte].decode(),source=str(f),sourceSha256=digest(b),excerptSha256=digest(text.encode()),normalizedSha256=digest(norm.encode()),url=f"https://github.com/{info['repo']}/blob/{info['sha']}/{rel}#L{n.start_point.row+1}-L{n.end_point.row+1}",text=text))
(OUT/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'candidateMethods':len(rows),'uniqueExactNormalized':len({r['normalizedSha256'] for r in rows}),'accepted':0,'repos':len({r['repo'] for r in rows})}))
