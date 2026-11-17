from pathlib import Path
import json,hashlib,zipfile,runpy,sys
runpy.run_path('/tmp/armor-verify-v2.py',run_name='__main__')
b=Path(sys.argv[1]);H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=json.loads((b/'consumer-provenance.json').read_text());assert H(Path(p['archive']))==p['archive_sha256'];z=zipfile.ZipFile(p['archive'])
for e in p['files']:assert hashlib.sha256(z.read(e['entry'])).hexdigest()==H(b/e['local'])==e['sha256']
assert len(json.loads((b/'seven-dimension-mc-review.json').read_text())['dimensions'])==7
c=json.loads((b/'native-four-slot-factory-chains.json').read_text());assert len(c)==4 and len({x['item'] for x in c})==4
assert all(x['nonzero']==0 for x in json.loads((b/'native-hat-source-rectangles.json').read_text())['rectangles'])
print('PASS extra consumer archive members, four distinct native slots, seven review dimensions, empty default hat source rectangles')
