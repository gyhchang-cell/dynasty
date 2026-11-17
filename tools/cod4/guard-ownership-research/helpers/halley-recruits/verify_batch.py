"""Final read-only schema/hash/AST verification; never runs upstream source."""
from pathlib import Path
import sys,json,hashlib,re
sys.dont_write_bytecode=True
from extract import parser,walk
ROOT=Path(__file__).resolve().parent
DOCS=ROOT.parents[4]/'docs/cod4/audit-20261022/guard-ownership-research/helpers/halley-recruits'
def sha(x):return hashlib.sha256(x).hexdigest()
required={'repo','commit','path','start','end','name','source','sourceSha256','text',
          'excerptSha256','normalizedSha256','url','observation','application','limits'}
rows=json.loads((DOCS/'batch-001.json').read_text())
support=json.loads((DOCS/'supporting-methods-001.json').read_text())
assert len(rows)==30
seen=set();norms=set();asts={}
for i,r in enumerate(rows+support):
    if i<len(rows):assert required <= r.keys()
    assert r['credit']==r['research_credit']==0 and r['accepted'] is False
    assert r['id'] not in seen;seen.add(r['id'])
    raw=Path(r['source']).read_bytes()
    assert sha(raw)==r['sourceSha256']
    assert sha(r['text'].encode())==r['excerptSha256']
    normalized=re.sub(r'/\*.*?\*/|//[^\n]*','',r['text'],flags=re.S)
    normalized=re.sub(r'\s+','',normalized)
    assert sha(normalized.encode())==r['normalizedSha256']
    if i<len(rows):
        assert r['normalizedSha256'] not in norms;norms.add(r['normalizedSha256'])
    if r['source'] not in asts:asts[r['source']]=list(walk(parser.parse(raw).root_node))
    hits=[n for n in asts[r['source']] if n.type in ['method_declaration','constructor_declaration']
          and n.start_point.row+1==r['start'] and n.end_point.row+1==r['end']]
    assert len(hits)==1 and not hits[0].has_error
    assert raw[hits[0].start_byte:hits[0].end_byte].decode()==r['text']
v=json.loads((DOCS/'source-verification-001.json').read_text())
for m in v['metadataFiles']:assert sha(Path(m['path']).read_bytes())==m['sha256']
for m in v['verifiedFiles']:
    raw=Path(m['source']).read_bytes()
    assert sha(raw)==m['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==m['git_blob_sha1']
print(f'PASS: {len(rows)} full-method suggestions; {len(support)} zero-credit auxiliary methods; '
      f'{len(v["verifiedFiles"])} pinned source files; all schema/text/AST/hash checks passed.')
