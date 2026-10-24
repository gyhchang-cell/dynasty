"""Extract pinned full-method candidates. This index grants no research credit."""
from pathlib import Path
import sys, json, re, hashlib, collections
B=Path(__file__).resolve().parent; R=B.parents[2]
O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
assert sys.version_info[:2]==(3,12), 'Use bundled Python 3.12; the Python 3.14 AST extension crashed during extraction.'
sys.path.insert(0,str(R/'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language, Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
sha=lambda b:hashlib.sha256(b).hexdigest()
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
def structural(n,raw):
 out=[]; ids={}
 for z in walk(n):
  if z.type in ('line_comment','block_comment'):continue
  if not z.children:
   t=raw[z.start_byte:z.end_byte].decode(errors='replace')
   if z.type=='identifier':t=ids.setdefault(t,'I'+str(len(ids)))
   if 'literal' in z.type or z.type=='string_fragment':t=z.type
   out.append(t)
 return sha(' '.join(out).encode())
groups={
 'deferred_queue':re.compile(r'enqueueWork|queueTask|queueServer|enqueueTask|addScheduledTask|scheduleTask|scheduleTick|TickTask|delayedTask|delayedAction|[Pp]ending[A-Z]|[Qq]ueue\b|[Dd]eferred'),
 'tick_phase':re.compile(r'TickEvent\.(?:Phase|ServerTick|WorldTick|LevelTick)|ServerTickEvents|END_SERVER_TICK|END_WORLD_TICK|TickPhase'),
 'expiry_window':re.compile(r'expir|timeToLive|TTL\b|last[A-Z]\w*(?:Tick|Time)|(?:getGameTime|getTotalWorldTime|getTickCount)\s*\('),
 'identity_receipt':re.compile(r'acknowledge|sequenceId|lastSequence|[Rr]eceipt|alreadyProcessed|processedEntities|hitEntities|alreadyHit|seenEntities|[Pp]ending[A-Z]'),
 'source_dimension':re.compile(r'(?:getSender|sender\s*\(|getPlayer\(\)).*(?:\n|.)*?(?:getEntity|dimension\(|getDimension|isRemoved|isAlive)|(?:dimension\(|getDimension\().*(?:\n|.)*?(?:packet|Packet|sendTo|task|Task)')
}
damage=re.compile(r'\.(?:hurt|attackEntityFrom|damage)\s*\(')
feedback=re.compile(r'playSound|sendParticles|broadcastEntityEvent|sendTo|sendTracking|sendToAll|PacketDistributor|spawnParticle|addParticle|triggerAnim|playAnimation')
sources=[]
for base in [B/'.work/research-sources',R/'tools/cod4/armor-acceptance/.work/research-sources',R/'build/item-use-references',R/'build/creature-reference-1000']:
 for p in sorted(base.glob('*/source.json')):
  d=json.loads(p.read_text())
  if d.get('repo') and d.get('sha'):sources.append(dict(repo=d['repo'],sha=d['sha'],root=str(p.parent.relative_to(R)),metadata=str(p.relative_to(R))))
for d in json.loads((R/'docs/cod4/audit-20261022/legacy-migration-acceptance/sources.json').read_text()):
 if not d['repo'].startswith('Minecraft+'):
  sources.append(dict(repo=d['repo'],sha=d['sha'],root=d['private_source'],metadata='docs/cod4/audit-20261022/legacy-migration-acceptance/sources.json'))
seenfiles=set(); rows=[]; errors=[]; visited=0
for source in sources:
 root=R/source['root']
 for p in sorted(root.rglob('*.java')):
  rel=str(p.relative_to(root));key=(source['repo'],source['sha'],rel)
  if key in seenfiles:continue
  seenfiles.add(key);raw=p.read_bytes();text=raw.decode(errors='replace');visited+=1
  scheduler_context=bool(re.search(r'EventQueue|TaskHandler|TaskScheduler|DelayedSpell|Scheduler|DeduplicatingRunner|EventLoop|TimerQueue',rel))
  damage_context=bool(damage.search(text) and feedback.search(text))
  if not scheduler_context and not damage_context and not any(pt.search(text) for pt in groups.values()):continue
  tree=parser.parse(raw)
  if tree.root_node.has_error:errors.append(str(p.relative_to(R)))
  for n in walk(tree.root_node):
   if n.type!='method_declaration':continue
   body=n.child_by_field_name('body');name=n.child_by_field_name('name')
   if body is None or name is None:continue
   code=raw[n.start_byte:n.end_byte].decode(errors='replace')
   tags=[k for k,pt in groups.items() if pt.search(code)]
   if scheduler_context:tags.append('scheduler_class_context')
   if damage.search(code) and feedback.search(code):tags.append('damage_feedback_candidate')
   if not tags:continue
   method=raw[name.start_byte:name.end_byte].decode()
   calls=[];guards=[]
   for z in walk(body):
    if z.type=='method_invocation':
     nn=z.child_by_field_name('name');calls.append(raw[nn.start_byte:nn.end_byte].decode() if nn else '?')
    if z.type in ('if_statement','ternary_expression','while_statement'):
     c=z.child_by_field_name('condition')
     if c:guards.append(raw[c.start_byte:c.end_byte].decode(errors='replace'))
   if not calls or len(code.splitlines())<4:continue
   ident=sha((source['repo']+source['sha']+rel+str(n.start_byte)).encode())[:20]
   rows.append(dict(candidate_id=ident,repo=source['repo'],revision=source['sha'],path=rel,method=method,
    source_local=str(p.relative_to(R)),source_metadata=source['metadata'],source_root=source['root'],
    line=n.start_point.row+1,end_line=n.end_point.row+1,source_sha256=sha(raw),snippet_sha256=sha(code.encode()),
    structural_fingerprint=structural(n,raw),url=f"https://github.com/{source['repo']}/blob/{source['sha']}/{rel}#L{n.start_point.row+1}-L{n.end_point.row+1}",
    discovery_tags=tags,ast_calls=calls,ast_guards=guards,parse_error=n.has_error,excerpt=code,status='unreviewed'))
rows.sort(key=lambda c:(0 if 'deferred_queue' in c['discovery_tags'] and ('tick_phase' in c['discovery_tags'] or 'expiry_window' in c['discovery_tags']) else 1 if 'tick_phase' in c['discovery_tags'] else 2,len(c['excerpt'].splitlines()),c['repo'],c['path'],c['line']))
oldpath=O/'candidates.jsonl'
if oldpath.exists():
 old=[json.loads(x) for x in oldpath.read_text().splitlines()];oldids={x['candidate_id'] for x in old};rows=old+[x for x in rows if x['candidate_id'] not in oldids]
(O/'candidates.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in rows))
summary=dict(source_file_identities_scanned=visited,source_roots=len(sources),candidates=len(rows),structural_families=len({c['structural_fingerprint'] for c in rows}),accepted_credit=0,parse_error_files=errors,tags=dict(collections.Counter(t for c in rows for t in c['discovery_tags'])))
(O/'discovery.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in summary.items() if k!='parse_error_files'})
