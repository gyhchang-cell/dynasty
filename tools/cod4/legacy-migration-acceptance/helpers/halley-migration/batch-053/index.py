"""Static AST inventory, not reviewed credit. Uses locally installed parser only."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent))
from extract import PARSER, walk, norm, sha, ROOT
def build():
    rows=[]; skipped=[]
    for source in json.loads((BASE/'source-manifest.json').read_text()):
        for file in source['files']:
            if not file['path'].endswith('.java'):continue
            raw=(ROOT/file['source']).read_bytes()
            try:raw.decode('utf-8')
            except UnicodeDecodeError:
                skipped.append(dict(file,reason='Source is not UTF-8; raw bytes preserved unchanged, not parsed/reviewed or credited'));continue
            tree=PARSER.parse(raw)
            for n in walk(tree.root_node):
                if n.type not in ('method_declaration','constructor_declaration') or not n.child_by_field_name('body'):continue
                name=n.child_by_field_name('name'); text=raw[n.start_byte:n.end_byte].decode()
                rows.append(dict(repo=source['repo'],commit=source['commit'],git_tree=source['git_tree'],path=file['path'],source=file['source'],sourceSha256=file['sourceSha256'],source_blob=file['source_blob'],start=n.start_point.row+1,end=n.end_point.row+1,name=raw[name.start_byte:name.end_byte].decode(),text=text,excerptSha256=sha(text.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((source['repo']+source['commit']+file['path']+str(n.start_byte)).encode())[:20],parse_has_error=n.has_error))
    (BASE/'unparsed-source-inventory-not-credit.json').write_text(json.dumps(skipped,indent=2)+'\n')
    (BASE/'method-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print('Unreviewed AST inventory',len(rows))
if __name__=='__main__':
    if len(sys.argv)==1:build()
    else:
        rows=json.loads((BASE/'method-index.json').read_text())
        for r in rows:
            if sys.argv[1] in r['path'] and (len(sys.argv)<3 or r['name'] in sys.argv[2:]):
                print('\n###',r['repo'],r['path'],r['name'],r['start'],r['end']);print(r['text'])
