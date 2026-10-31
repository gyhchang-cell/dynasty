"""Authored static AST index. No source or upstream toolchain is executed."""
from pathlib import Path
import sys,json,hashlib,re
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[4]
sys.path.insert(0,str(PROJECT/'tools/cod4/guard-ownership-research/.work/python39'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
BASE=ROOT/'sources/talhanation__recruits'
def sha(x):return hashlib.sha256(x).hexdigest()
def walk(n):
    yield n
    for c in n.children:yield from walk(c)
def index():
    info=json.loads((BASE/'source.json').read_text());rows=[];warnings=[]
    for f in sorted(BASE.rglob('*.java')):
        b=f.read_bytes();tree=parser.parse(b)
        if tree.root_node.has_error:warnings.append(str(f))
        for n in walk(tree.root_node):
            if n.type not in ('method_declaration','constructor_declaration'):continue
            if n.has_error:continue
            body=n.child_by_field_name('body');name=n.child_by_field_name('name')
            if body is None or name is None:continue
            text=b[n.start_byte:n.end_byte].decode()
            norm=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S);norm=re.sub(r'\s+','',norm)
            path=f.relative_to(BASE).as_posix();a=n.start_point.row+1;z=n.end_point.row+1
            key=f"{info['repo']}@{info['sha']}:{path}:{a}:{z}"
            rows.append(dict(id=sha(key.encode())[:16],repo=info['repo'],commit=info['sha'],path=path,start=a,end=z,
                             name=b[name.start_byte:name.end_byte].decode(),source=str(f.resolve()),sourceSha256=sha(b),
                             text=text,excerptSha256=sha(text.encode()),normalizedSha256=sha(norm.encode()),
                             url=f"https://github.com/{info['repo']}/blob/{info['sha']}/{path}#L{a}-L{z}"))
    (ROOT/'parser-warnings.json').write_text(json.dumps(warnings,indent=2)+'\n')
    return rows
if __name__=='__main__':
    rows=index();(ROOT/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    if len(sys.argv)>1:
        for r in rows:
            if re.search(sys.argv[1],r['path']+':'+r['name']):print(r['path'].split('/')[-1],r['start'],r['end'],r['name'])
    else:print('Indexed candidates only:',len(rows))
