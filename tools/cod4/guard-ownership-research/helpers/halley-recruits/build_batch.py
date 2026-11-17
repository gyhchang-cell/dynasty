"""Assemble authored method reviews and verify pinned text. No upstream execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[4]
DOCS=PROJECT/'docs/cod4/audit-20261022/guard-ownership-research/helpers/halley-recruits'
MASTER=DOCS.parents[1]
BASE=ROOT/'sources/talhanation__recruits'
def digest(b):return hashlib.sha256(b).hexdigest()
def jsonread(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
meta=jsonread(BASE/'source.json');commit=jsonread(BASE/'commit.json');tree=jsonread(BASE/'tree.json')
assert meta['repo']=='talhanation/recruits' and meta['sha']==commit['sha']
assert commit['commit']['tree']['sha']==tree['sha']==meta['tree_sha']
assert not tree['truncated'] and meta['tls_verified']
# Reconstruct every Git tree object, not merely compare API path labels.
children=defaultdict(list)
for x in tree['tree']:
    parent,_,name=x['path'].rpartition('/')
    children[parent].append((name,x))
tree_hashes={}
for parent in sorted(children,key=lambda p:len(p.split('/')) if p else 0,reverse=True):
    entries=sorted(children[parent],key=lambda item:(item[0]+('/' if item[1]['type']=='tree' else '')).encode())
    raw=b''
    for name,x in entries:
        if x['type']=='tree':assert tree_hashes[x['path']]==x['sha']
        mode=format(int(x['mode'],8),'o')
        raw+=f'{mode} {name}'.encode()+b'\0'+bytes.fromhex(x['sha'])
    actual=hashlib.sha1(b'tree '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    tree_hashes[parent]=actual
assert tree_hashes['']==meta['tree_sha']
verified=[]
for item in meta['files']:
    p=BASE/item['path'];b=p.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert digest(b)==item['sha256'] and blob==item['git_blob_sha1']
    assert next(x['sha'] for x in tree['tree'] if x['path']==item['path'])==blob
    verified.append(dict(**item,source=str(p.resolve()),size=len(b)))

allrows=jsonread(ROOT/'candidates.json')
annotations=jsonread(ROOT/'annotations.json')
master_bytes=(MASTER/'references.json').read_bytes()
master=json.loads(master_bytes)
master_norms=defaultdict(list)
for row in master:master_norms[row['normalizedSha256']].append(row['id'])
rows=[];keys=set();norms=set()
def select(file,start,name=None):
    hits=[x for x in allrows if Path(x['path']).name==file and x['start']==start and (name is None or x['name']==name)]
    assert len(hits)==1,(file,start,name,len(hits))
    return hits[0]
def check_text(r):
    raw=Path(r['source']).read_bytes()
    assert digest(raw)==r['sourceSha256']
    assert digest(r['text'].encode())==r['excerptSha256']
    norm=re.sub(r'/\*.*?\*/|//[^\n]*','',r['text'],flags=re.S);norm=re.sub(r'\s+','',norm)
    assert digest(norm.encode())==r['normalizedSha256']
    # AST includes annotations and starts at the declaration token, not indentation.
    lines=raw.decode().splitlines(keepends=True)
    expected=''.join(lines[r['start']-1:r['end']]).strip()
    assert expected==r['text'],(r['path'],r['start'])
for a in annotations:
    r=dict(select(a['file'],a['start'],a['name']));check_text(r)
    assert r['id'] not in keys and r['normalizedSha256'] not in norms
    keys.add(r['id']);norms.add(r['normalizedSha256'])
    for key in ['observation','application','limits']:
        assert len(a[key])>=40,(a['file'],key)
        r[key]=a[key]
    r.update(credit=0,research_credit=0,accepted=False,status='helper_full_method_review_pending_coordinator_semantic_dedup',
             semanticFamily=a['family'],independentContribution=a['independence'],
             exactMasterMatches=master_norms.get(r['normalizedSha256'],[]),
             duplicateRisk='本批每完整方法仅一条；相关helper/平台/取值器未另计。主账跨仓库模板及语义重合仍由Herschel最终去重。',
             reviewMode='Complete method body plus caller/callee context read; static research only; no gameplay/runtime claim.',
             runtimeVerified=False)
    assert not r['exactMasterMatches'],('Exact master duplicate',r['id'])
    rows.append(r)
assert len(rows)==30

# Caller/callee bodies that were read to support the 30 sites; never independent credits.
support_specs={
 'Main.java':[59,92],
 'AbstractRecruitEntity.java':[161,229,313,321,399,486,562,688,866,1194,2051,2071,2079,2085,2089,2285,2378],
 'RecruitEvents.java':[369,474,490,511,586,594,602],
 'FactionEvents.java':[51,761,787],
 'RecruitOwnerHurtByTargetGoal.java':[22,37],
 'RecruitOwnerHurtTargetGoal.java':[22,37],
 'RecruitProtectHurtByTargetGoal.java':[22,40],
 'RecruitHurtByTargetGoal.java':[25,41],
 'RecruitMeleeAttackGoal.java':[35,78,85],
 'RecruitProtectEntityGoal.java':[27,32,36,44,87,99],
 'RecruitDefendVillageFromPlayerGoal.java':[48],
 'RecruitRangedCrossbowAttackGoal.java':[33,42,77,84,92,262,266,287,296,304],
 'RecruitRangedBowAttackGoal.java':[45,81,85,90,94,103,112,165,185,195,203],
 'AttackUtil.java':[24,40,52,64,83],
 'BowmanEntity.java':[85],
 'CrossBowmanEntity.java':[92],
 'MessageAttack.java':[29,33],
 'MessageAssignRecruitToPlayer.java':[37],
 'MessageProtectEntity.java':[35],
 'CommandEvents.java':[392,697,703],
 'NetworkSecurity.java':[58,105],
 'GovernorManager.java':[160],
 'RecruitsDiplomacyManager.java':[47,64],
 'RecruitsTreatyManager.java':[33,39],
 'CrossbowWeapon.java':[57,80,135],
 'IWeapon.java':[30],
 'RecruitsPlayerUnitManager.java':[45,50,71]
}
support=[]
for file,starts in support_specs.items():
    for start in starts:
        r=dict(select(file,start));check_text(r)
        assert r['id'] not in keys
        r.update(credit=0,research_credit=0,accepted=False,status='auxiliary_same_chain_not_counted')
        support.append(r)

DOCS.mkdir(parents=True,exist_ok=True)
dump(DOCS/'batch-001.json',rows)
dump(DOCS/'supporting-methods-001.json',support)
provenance=dict(repo=meta['repo'],commit=meta['sha'],treeSha=meta['tree_sha'],
                officialUrl='https://github.com/talhanation/recruits',
                githubCommitUrl=f"https://github.com/{meta['repo']}/commit/{meta['sha']}",
                verifiedGitTreeObjectCount=len(tree_hashes),verifiedGitTreeRoot=True,
                verifiedFiles=verified,allFileSha256AndGitBlobMatch=True,
                tls='ssl.create_default_context(cafile=/etc/ssl/cert.pem); certificate validation enabled',
                fetchNote='Raw AbstractRecruitEntity request failed with TLS EOF; exactly one alternate GitHub blob API acquisition succeeded and matched pinned blob. No insecure TLS or retry loop.',
                metadataFiles=[dict(path=str((BASE/f).resolve()),sha256=digest((BASE/f).read_bytes()))
                               for f in ['repository.json','commit.json','tree.json','source.json']],
                declaredMinecraft='1.20.1',declaredForge='47.4.10',
                versionCaveat='gradle.properties mod_version=1.10.7 while mods.toml version=1.15.2; use the immutable commit, do not invent a matching release version.',
                execution='Only authored Python download/text/AST verification scripts and existing parser libraries executed. No recruits Java, Gradle, server or game executed.',
                parserWarnings=jsonread(ROOT/'parser-warnings.json'),
                parserWarningScope='Type-use annotated varargs declaration in RecruitHurtByTargetGoal is not handled by this parser build. All selected/supporting AST method nodes are error-free; setAlertOthers was read as source context but is not an indexed or credited method.',
                createdUtc=datetime.now(timezone.utc).isoformat())
dump(DOCS/'source-verification-001.json',provenance)
summary=dict(repo=meta['repo'],commit=meta['sha'],requestedMethodTarget=30,fullMethodSuggestions=len(rows),
             supportingMethods=len(support),credit=0,research_credit=0,acceptedByHelper=0,
             masterReferencesReadCount=len(master),masterReferencesSha256=digest(master_bytes),
             exactNormalizedDuplicatesWithinBatch=0,exactNormalizedMatchesWithMaster=0,
             semanticDedupOwner='Herschel',candidateInventoryCount=len(allrows),
             countPolicy='30 authored full-method observations; candidates/downloads/auxiliaries/getters/protocol wrappers never automatic credits.',
             excludes='Owner getter/UUID setters, AI constructor and registration-only wrappers, attack timing/angle math, packet encode/decode, direct delegate ports and generic network security stay auxiliary or unreviewed.',
             allRequiredFieldsPresent=True,fullTextSourceAndExcerptHashesVerified=True,
             runtimeVerified=False,productionModified=False,masterModifiedByHelper=False,
             externalFallbackSucceeded=True)
dump(DOCS/'batch-verification-001.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
