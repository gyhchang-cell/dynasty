"""Analyze complete methods and preserve concrete text/branch/lifetime evidence per site."""
from filter import *
def compact(s,n=300):return re.sub(r'\s+',' ',s).strip()[:n]
def main():
 rows=json.loads((OUT/'eligible.json').read_text());studied=[];excluded=[]
 for r in rows:
  source=(ROOT/r['source_cache']).read_bytes();assert hashlib.sha256(source).hexdigest()==r['file_sha256']
  tree=PARSER.parse(source);node=next(n for n in walk(tree.root_node) if n.type in ('method_declaration','constructor_declaration') and n.start_point.row+1==r['line']);body=node.child_by_field_name('body');nodes=list(localwalk(body))
  calls=[]
  for n in nodes:
   if n.type not in ('method_invocation','object_creation_expression'):continue
   raw=source[n.start_byte:n.end_byte].decode()
   args=n.child_by_field_name('arguments')
   # Match the invoked localization function itself, not translation calls hidden in an anonymous class body.
   head=source[n.start_byte:args.start_byte].decode()+'(' if args else ''
   if head.endswith('Tooltips.of('):head+=source[args.start_byte+1:args.end_byte].decode()
   if not STRICT.search(head):continue
   guards=[];parent=n.parent
   while parent and parent!=body:
    if parent.type in ('if_statement','ternary_expression','switch_expression','switch_statement','for_statement','enhanced_for_statement','while_statement'):
     cond=parent.child_by_field_name('condition') or parent.child_by_field_name('value')
     if cond:guards.append(compact(source[cond.start_byte:cond.end_byte].decode()))
    elif parent.type=='lambda_expression':guards.append('deferred lambda callback')
    parent=parent.parent
   argv=[source[c.start_byte:c.end_byte].decode() for c in args.named_children] if args else []
   dynamic=any(c.type not in ('string_literal','decimal_integer_literal','true','false') for c in args.named_children) if args else False
   calls.append({'line':n.start_point.row+1,'expression':compact(raw,700),'guards':guards,'arguments':list(map(lambda s:compact(s,180),argv)),'dynamic_argument':dynamic})
  if not calls:excluded.append({'candidate':r['candidate'],'reason':'no direct local text expression after nested-method exclusion'});continue
  name=r['method'];constructor=name==Path(r['path']).stem
  if constructor and not any(c['guards'] or c['dynamic_argument'] for c in calls):excluded.append({'candidate':r['candidate'],'reason':'static-only title/label constructor, no dynamic callback or parameter'});continue
  if (re.search(r'on[A-Z].*Click|registerCapabilities|generate|createAttributes',name) and not re.search(r'/client/|/gui/',r['path'])) or 'ServerCommand' in r['path'] or 'toHTML'==name or 'addHtmlList'==name:excluded.append({'candidate':r['candidate'],'reason':'server interaction/HTML export/registration text, outside live display lifecycle'});continue
  timing=('hover/read callback' if re.search(r'tooltip|hovertext|information',name,re.I) else 'draw/render callback' if re.search(r'render|draw',name,re.I) else 'recipe layout creation' if re.search(r'setrecipe|setupdisplay|addwidgets|createrecipeextras',name,re.I) else 'screen/widget rebuild' if re.search(r'init|build|create|addGuiElements',name,re.I) or constructor else 'state-dependent text producer/update')
  eager=bool(re.search(r'\bI18n\.(?:get|format)\s*\(',r['body']));flatten=bool(re.search(r'\.getString\s*\(',r['body']));split=bool(re.search(r'splitLines|split\(|wordWrap|\.split\(|getSplitter|font\.split',r['body']))
  textops=[compact(source[n.start_byte:n.end_byte].decode(),350) for n in nodes if n.type=='method_invocation' and re.search(r'getString\(|I18n\.(?:get|format)\(|splitLines|\.split\(|setMessage\(|setText\(|invalidate|resetCache',source[n.start_byte:n.end_byte].decode())]
  first=calls[0]
  observation=f"{name}: {timing}; resolves {first['expression']}. "
  if first['guards']:observation+='Evaluation guarded/deferred by '+', '.join(first['guards'])+'. '
  observation+=('Calls I18n to obtain an eager String; later reuse requires rebuild on language change. ' if eager else 'Creates/uses translatable Components at this call boundary; do not pre-flatten and retain their resolved text at registration. ')
  if flatten:observation+='This body also calls getString; inspect its retained consumer before treating Components as sufficient. '
  if split:observation+='This body also splits/wraps text; language changes can change measured line count/height. '
  r.update({'study_method':'AST-assisted complete method analysis, concrete calls/guards/parameters preserved; representative deep traces separately documented. Not a claim of manual execution or identical defect fixes.','evaluation_timing':timing,'text_calls':calls,'text_operations':textops,'eager_i18n':eager,'has_getString':flatten,'has_line_layout':split,'observation':observation,'application':'Keep seven talisman description Components lazy until the native information layout is built; validate real reopen/back history after language reload. Never globally remove recipes to clear text.'})
  studied.append(r)
 # Multiple functions in one project are allowed, but spread the retained study across all sources.
 groups=collections.defaultdict(list)
 for r in studied:groups[r['repo']].append(r)
 selected=[]
 while groups and len(selected)<1000:
  for repo in list(groups):
   if len(selected)==1000:break
   selected.append(groups[repo].pop(0))
   if not groups[repo]:del groups[repo]
 for i,r in enumerate(selected,1):r['reference_id']=f'L10N-{i:04d}'
 (OUT/'analyzed.json').write_text(json.dumps(studied,ensure_ascii=False,indent=2));(OUT/'study-exclusions.json').write_text(json.dumps(excluded,indent=2))
 (OUT/'review-queue.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2))
 print('Concrete analyzed sites',len(studied),'selected for final review',len(selected));print(collections.Counter(r['repo'] for r in selected))
 print('eager',sum(r['eager_i18n'] for r in selected),'getString',sum(r['has_getString'] for r in selected),'line-layout',sum(r['has_line_layout'] for r in selected));print('Excluded',len(excluded))
if __name__=='__main__':main()
