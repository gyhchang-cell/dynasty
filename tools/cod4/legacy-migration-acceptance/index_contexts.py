"""AST candidate extraction ONLY. Never converts candidates into reviewed evidence."""
from pathlib import Path
import sys,json,re,hashlib,collections
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
sys.path.insert(0,str(B/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
language=Language(tree_sitter_java.language());parser=Parser(language)
meta=json.loads((O/'sources.json').read_text());rows=[];errors=[]
pattern=re.compile(r'MissingMappings|FMLMissingMappings|\bDataFix(?:er|es)?\b|backward.?compat|backwards.?compat|\blegacy\b|fromLegacy|readLegacy|parseLegacy|\bmigrat\w*|old.?format|old.?version|data.?version|convertFrom|upgradeFrom|PlayerEvent\.Clone|onPlayerClone|PlayerPersisted|PERSISTED_NBT_TAG|reviveCaps|isWasDeath|copyFrom\s*\([^)]*[Pp]layer',re.I)
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
def structural(n,raw):
 out=[];ids={}
 for x in walk(n):
  if x.type in ('line_comment','block_comment'):continue
  if not x.children:
   token=raw[x.start_byte:x.end_byte].decode(errors='replace')
   if x.type=='identifier':token=ids.setdefault(token,'I'+str(len(ids)))
   if 'literal' in x.type or x.type=='string_fragment':token=x.type
   out.append(token)
 return hashlib.sha256(' '.join(out).encode()).hexdigest()
for source in meta:
 root=R/source['private_source']
 for p in sorted(root.rglob('*.java')):
  raw=p.read_bytes();text=raw.decode(errors='replace')
  explicit=bool(pattern.search(text)) or 'legacy' in p.name.lower() or (source['repo']=='PaperMC/DataConverter' and '/minecraft/versions/' in str(p))
  durable=bool(re.search(r'CompoundTag|CompoundNBT|NBTTagCompound|ValueInput|Json5Object',text)) and bool(re.search(r'/quest/|/player/|/storage/|/capabilit|/nbt/|/internal_caps/|inventor|/item|block.?entit|/entit|/attachment|/datafix|/saveddata|/network/|/data/|/save/|/team/|/skill/|/stage/|/research/|/ability/',str(p)))
  fallback=('ItemStack' in text or re.search('quest|advancement|progress',str(p),re.I)) and re.search(r'contains\(|hasKey\(|orElse\(|getOrDefault\(',text)
  if not explicit and not fallback and not durable:continue
  tree=parser.parse(raw)
  if tree.root_node.has_error:errors.append(str(p.relative_to(root)))
  for n in walk(tree.root_node):
   if n.type not in ('method_declaration','constructor_declaration'):continue
   body=n.child_by_field_name('body')
   if body is None:continue
   code=raw[n.start_byte:n.end_byte].decode(errors='replace')
   nm=n.child_by_field_name('name');method=raw[nm.start_byte:nm.end_byte].decode() if nm else '?'
   durable_method=durable and bool(re.search(r'load|read|deserial|restore|clone|copyFrom|getPersistentData|fromTag|fromNBT',method,re.I))
   if not explicit and not durable_method and not re.search(r'contains\(|hasKey\(|orElse\(|getOrDefault\(',code):continue
   calls=[];guards=[]
   for z in walk(body):
    if z.type=='method_invocation':
     nn=z.child_by_field_name('name');calls.append(raw[nn.start_byte:nn.end_byte].decode() if nn else '?')
    elif z.type in ('if_statement','ternary_expression'):
     c=z.child_by_field_name('condition')
     if c:guards.append(raw[c.start_byte:c.end_byte].decode(errors='replace'))
   rel=str(p.relative_to(root));ref=f'https://github.com/{source["repo"]}/blob/{source["sha"]}/{rel}#L{n.start_point.row+1}-L{n.end_point.row+1}' if '/' in source['repo'] and not source['repo'].startswith('Minecraft+') else source.get('maven')
   rows.append({'candidate_id':hashlib.sha256((source['repo']+source['sha']+rel+str(n.start_byte)).encode()).hexdigest()[:20],'status':'candidate_not_reviewed','repo':source['repo'],'revision':source['sha'],'path':rel,'private_file':str(p.relative_to(R)),'method':method,'start_line':n.start_point.row+1,'end_line':n.end_point.row+1,'file_sha256':hashlib.sha256(raw).hexdigest(),'method_sha256':hashlib.sha256(code.encode()).hexdigest(),'structural_fingerprint':structural(n,raw),'source_url_or_coordinate':ref,'ast_calls':calls,'ast_guards':guards,'context':code,'class_has_migration_marker':explicit,'parse_has_error':tree.root_node.has_error})
(O/'candidates.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n')
summary={'source_roots':len(meta),'candidate_methods':len(rows),'structurally_distinct_candidates':len(set(x['structural_fingerprint'] for x in rows)),'research_credit_granted_by_indexer':0,'parse_error_files':errors,'warning':'Candidate count is NOT reviewed count. See reviewed ledger for effective count. This script never grants research credit.'}
(O/'candidate-index-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print({k:v for k,v in summary.items() if k!='parse_error_files'})
