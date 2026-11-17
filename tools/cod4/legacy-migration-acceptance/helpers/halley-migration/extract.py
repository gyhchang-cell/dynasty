"""Local static analysis only. Never imports or executes upstream code."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, hashlib
ROOT = Path('/Users/a15356015027/Desktop/dynasty')
BASE = ROOT / 'tools/cod4/legacy-migration-acceptance/helpers/halley-migration'
DOC = ROOT / 'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
sys.path.insert(0, str(ROOT / 'tools/cod4/guard-ownership-research/.work/python39'))
import tree_sitter, tree_sitter_java
PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_java.language()))
def sha(data): return hashlib.sha256(data).hexdigest()
def walk(n):
    yield n
    for c in n.children: yield from walk(c)
def norm(n, raw):
    tokens=[]; ids={}
    for a in walk(n):
        if a.children or a.type in ('line_comment','block_comment'): continue
        t=raw[a.start_byte:a.end_byte].decode()
        if a.type=='identifier': t=ids.setdefault(t,'I'+str(len(ids)))
        elif 'literal' in a.type or a.type=='string_fragment': t=a.type
        tokens.append(t)
    return sha(' '.join(tokens).encode())
def index():
    rows=[]
    for source in json.loads((DOC/'SOURCE-RESERVATION.json').read_text())['repos']:
        cache=ROOT/source['source_cache']
        for file in sorted(cache.rglob('*.java')):
            raw=file.read_bytes(); root=PARSER.parse(raw).root_node
            rel=file.relative_to(cache).as_posix()
            for n in walk(root):
                if n.type not in ('method_declaration','constructor_declaration') or not n.child_by_field_name('body'): continue
                text=raw[n.start_byte:n.end_byte].decode(); name=n.child_by_field_name('name')
                rows.append(dict(repo=source['repo'],revision=source['commit'],path=rel,original_file=str(file.relative_to(ROOT)),start_line=n.start_point.row+1,end_line=n.end_point.row+1,method=raw[name.start_byte:name.end_byte].decode(),context=text,file_sha256=sha(raw),method_sha256=sha(text.encode()),structural_fingerprint=norm(n,raw),candidate_id=sha((source['repo']+source['commit']+rel+str(n.start_byte)).encode())[:20],parse_has_error=n.has_error))
    (BASE/'method-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print('Indexed static methods:',len(rows))
if __name__=='__main__': index()
