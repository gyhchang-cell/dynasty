"""Append new candidates from runtime helpers/events/modules. Never automatically accept."""
from pathlib import Path
import re,json,hashlib,collections
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
MASK=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
METHOD=re.compile(r'(?m)^[ \t]*(?:(?:public|protected|private|static|final|synchronized|default)\s+)+(?:[\w<>?,.\[\]@]+\s+)+(?P<name>\w+)\s*\([^;{}]*?\)\s*(?:throws[^{;]+)?\{')
paths=[R/'build/item-use-references',R/'build/creature-reference-1000',B/'.work/research-sources']
round_file=E/'discovery-rounds.json'; rounds=json.loads(round_file.read_text()) if round_file.exists() else []; current_round=len(rounds)+2
old=json.loads((E/'armor-reference-candidates.json').read_text());seen={c['snippet_sha256'] for c in old};new=[];files=0
act=re.compile(r'(?:[a-zA-Z]*[Cc]ooldown\w*|(?:add|remove|set|clear|apply|reset|grant|revoke)\w*(?:Effect|Modifier|Attribute|Flying|Flight|Ability|Abilities|Active|Ticks|Timer|Duration|Charge|Owner|Target|Counter|Shield|State|Mode|Buff)\w*)\s*\(|(?:[Cc]ooldown|[Cc]harge|[Tt]imer|[Dd]uration|[Aa]ctive|[Ff]lying)\w*\s*(?:=|\+\+|--|\+=|-=)')
context=re.compile(r'(?i)armor|armour|curio|bauble|trinket|equipment|enchant|modifier|spell|cooldown|accessor|accessories|capabilit|accessory|module|relic|itemstack|equip|helditem|handitem')
for corpus in paths:
 for meta in sorted(corpus.glob('*/source.json')):
  d=json.loads(meta.read_text());repo=d.get('repo');rev=d.get('sha')
  if not repo or not rev:continue
  for p in sorted(meta.parent.rglob('*.java')):
   if any(x.lower() in {'client','render','renderer','renderers','model','models','datagen','generated','test','tests'} for x in p.parts):continue
   raw=p.read_text(errors='replace');code=MASK.sub(lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]),raw);files+=1
   ends={};stack=[]
   for n,ch in enumerate(code):
    if ch=='{':stack.append(n)
    elif ch=='}' and stack:ends[stack.pop()]=n+1
   for m in METHOD.finditer(code):
    end=ends.get(m.end()-1)
    if end is None or re.search(r'\b(?:record|class|interface)\b',m[0]):continue
    body=raw[m.start():end];masked=code[m.start():end];name=m['name']
    if name.startswith(('register','append','addInformation','getTooltip')):continue
    if not act.search(masked):continue
    if not context.search(str(p.relative_to(meta.parent))+' '+masked):continue
    if not re.search(r'\b(?:if|switch|for|while)\s*\(|\b(?:onUnequip|onEquip|onRemoved|onAdded|deserializeNBT|serializeNBT|load|save)\b',masked):continue
    digest=hashlib.sha256(re.sub(r'\s+','',MASK.sub('',body)).encode()).hexdigest()
    if digest in seen:continue
    seen.add(digest);startline=raw.count('\n',0,m.start())+1;last=raw.count('\n',0,end)+1;rel=p.relative_to(meta.parent).as_posix()
    new.append({'repo':repo,'revision':rev,'path':rel,'line':startline,'end_line':last,'method':name,'source_local':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'snippet_sha256':digest,'url':f'https://github.com/{repo}/blob/{rev}/{rel}#L{startline}-L{last}','item_scoped':False,'actions':act.findall(masked),'excerpt':body,'discovery_round':current_round})
new.sort(key=lambda c:(0 if re.search(r'(?i)armor|armour|curio|bauble|trinket|equipment|modifier|cooldown',c['path']) else 1,c['end_line']-c['line'],c['repo'],c['path'],c['line']))
(E/'armor-reference-candidates.json').write_text(json.dumps(old+new,ensure_ascii=False,indent=2)+'\n')
p=E/'discovery-rounds.json';rounds=json.loads(p.read_text()) if p.exists() else []
rounds.append({'round':len(rounds)+2,'roots':[str(p.relative_to(R)) for p in paths],'source_files_scanned':files,'existing_candidates':len(old),'appended_candidates':len(new),'total_candidates':len(old)+len(new),'counts_as_accepted':False});p.write_text(json.dumps(rounds,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rounds[-1],ensure_ascii=False));print(collections.Counter(c['repo'] for c in new))
