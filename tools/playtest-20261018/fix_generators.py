from pathlib import Path
import ast,json
R=Path(__file__).resolve().parents[2];f=R/'docs/playtest-20261018/recipe-fixes.json';records=json.loads(f.read_text())
for row in records:
 if row['file'].endswith('/bear_paw.json'):
  row['after']['ingredients'][-1]={'item':'minecraft:leather'};(R/row['file']).write_text(json.dumps(row['after'],indent=2)+'\n')
f.write_text(json.dumps(records,ensure_ascii=False,indent=2))
changes=[]
for p in (R/'tools/art').glob('gen_*.py'):
 s=p.read_text();lines=s.splitlines(keepends=True);offset=[0]
 for l in lines:offset.append(offset[-1]+len(l))
 try:tree=ast.parse(s)
 except SyntaxError:continue
 edits=[]
 for row in records:
  if 'ingredients' not in row['before']:continue
  key=Path(row['file']).stem;before=[x['item'] for x in row['before']['ingredients']];after=[x['item'] for x in row['after']['ingredients']]
  for node in ast.walk(tree):
   if not isinstance(node,ast.Dict):continue
   for k,v in zip(node.keys,node.values):
    if not isinstance(k,ast.Constant) or k.value!=key:continue
    for part in ast.walk(v):
     if isinstance(part,ast.List):
      try:value=ast.literal_eval(part)
      except:continue
      if value==before:
       # AST columns are UTF8 byte positions, translate them back to character indexes.
       a=offset[part.lineno-1]+len(lines[part.lineno-1].encode()[:part.col_offset].decode());b=offset[part.end_lineno-1]+len(lines[part.end_lineno-1].encode()[:part.end_col_offset].decode());edits.append((a,b,repr(after)));changes.append([str(p.relative_to(R)),key])
 for a,b,v in sorted(set(edits),reverse=True):s=s[:a]+v+s[b:]
 if edits:p.write_text(s)
p=R/'tools/art/gen_school_branches.py';s=p.read_text().replace("base='zhuxing_bow',material='refined_steel'","base='zhuxing_bow',material='sky_feather'");p.write_text(s)
(R/'docs/playtest-20261018/generator-fixes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2));print('Generator entries updated',len(changes))
