"""Capture exact supporting methods/constants for reviewed ownership observations; credit zero."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';sys.path.insert(0,str(B/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()));sources=json.loads((O/'sources.json').read_text());records=[]
requests=[
 ('Polarice3/Goety-2','src/main/java/com/Polarice3/Goety/common/capabilities/soulenergy/SEImp.java',{'setCooldowns'}),
 ('Polarice3/Goety-2','src/main/java/com/Polarice3/Goety/common/capabilities/soulenergy/FocusCooldown.java',{'save','load','saveSpecifics','loadSpecifics'}),
 ('TeamTwilight/twilightforest','src/main/java/twilightforest/events/TravellersGearEvents.java',{'setup','keepAttachmentsOnDeath','copyAttachmentData'}),
 ('TeamTwilight/twilightforest','src/main/java/twilightforest/init/TFDataAttachments.java',set()),
 ('P3pp3rF1y/SophisticatedCore','src/main/java/net/p3pp3rf1y/sophisticatedcore/upgrades/tank/TankUpgradeWrapper.java',{'TankComponentItemHandler','migrateLegacyContents','hasValidFluidHandler','onContentsChanged'}),
 ('DaedalusGame/EmbersRekindled','src/main/java/teamroots/embers/power/DefaultEmberItemCapability.java',{'DefaultEmberItemCapability','migrateLegacy','getEmber','getEmberCapacity','setEmber','setEmberCapacity'})]
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
for repo,relative,names in requests:
 source=next(s for s in sources if s['repo']==repo);p=R/source['private_source']/relative;raw=p.read_bytes();tree=parser.parse(raw)
 assert not tree.root_node.has_error,(repo,relative)
 def tx(n):return raw[n.start_byte:n.end_byte].decode() if n else ''
 contexts=[]
 for n in walk(tree.root_node):
  nm=tx(n.child_by_field_name('name'))
  if n.type in ['method_declaration','constructor_declaration'] and nm in names:
   code=tx(n);contexts.append(dict(method=nm,start_line=n.start_point.row+1,end_line=n.end_point.row+1,code=code,method_sha256=hashlib.sha256(code.encode()).hexdigest()))
  elif n.type=='field_declaration' and (not names or 'ATTACHMENTS_TO_PRESERVE_ON_DEATH' in tx(n)):
   code=tx(n);contexts.append(dict(kind='field_declaration',start_line=n.start_point.row+1,end_line=n.end_point.row+1,code=code))
 assert contexts
 records.append(dict(repo=repo,revision=source['sha'],path=relative,file_sha256=hashlib.sha256(raw).hexdigest(),source_url=f'https://github.com/{repo}/blob/{source["sha"]}/{relative}',contexts=contexts,credit=0,role='additional complete supporting bodies/constants for accepted chain observations; not new independent implementation count'))
(O/'support-contexts-batch010.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('captured',sum(len(r['contexts']) for r in records),'support contexts, credit0')
