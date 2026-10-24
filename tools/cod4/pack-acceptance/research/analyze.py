"""AST-delimited implementation study. Candidates are not counted as reviewed references."""
from pathlib import Path
import sys,json,re,hashlib,collections
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'build/cod4-pack-20261022/python39'))
import tree_sitter,tree_sitter_java
PARSER=tree_sitter.Parser(tree_sitter.Language(tree_sitter_java.language()))
CACHE=ROOT/'build/cod4-pack-20261022/language-sources';OUT=ROOT/'docs/cod4/audit-20261022/pack-acceptance/language-study'
def walk(n):
 yield n
 for c in n.named_children:yield from walk(c)
def localwalk(n):
 yield n
 for c in n.named_children:
  if c.type not in ('method_declaration','constructor_declaration'):yield from localwalk(c)
LOC=re.compile(r'(?:translat(?:able|e|ion)|localiz(?:e|ed)|I18n\.(?:get|format)|getTranslatedName|getLocalizedName|Lang\.\w+|GuiText\.\w+\.(?:text|getLocal)|Tooltips\.\w+|GuiLang\.\w+|TextComponentHelper)',re.I)
UI=re.compile(r'(?:client|gui|screen|tooltip|category|widget|jei|rei|emi|display|hud|book|manual)',re.I)
CALLBACK=re.compile(r'(?:tooltip|hovertext|render|draw|description|displaytext|addwidgets|addinformation|setupdisplay|setrecipe|init|update|build|create|add.*text|add.*label)',re.I)
def analyze():
 rows=[];rejected=collections.Counter();seen={}
 for meta in sorted(CACHE.glob('*/source.json')):
  src=json.loads(meta.read_text());base=meta.parent
  for f in sorted(base.rglob('*.java')):
   path=f.relative_to(base).as_posix()
   if re.search(r'/(?:data|datagen|generated|test|tests|model|models)/|(?:DataGenerator|LangProvider|LanguageProvider|Test)\.java$',path,re.I):continue
   data=f.read_bytes();tree=PARSER.parse(data)
   for n in walk(tree.root_node):
    if n.type not in ('method_declaration','constructor_declaration'):continue
    body=n.child_by_field_name('body');name=n.child_by_field_name('name')
    if body is None or name is None:continue
    name=data[name.start_byte:name.end_byte].decode();text=data[n.start_byte:n.end_byte].decode();bodytext=data[body.start_byte:body.end_byte].decode()
    if not LOC.search(bodytext):continue
    nodes=list(localwalk(body));statements=[x for x in nodes if x.type.endswith('_statement') or x.type=='local_variable_declaration']
    controls=[x.type for x in nodes if x.type in ['if_statement','switch_expression','switch_statement','for_statement','enhanced_for_statement','while_statement','ternary_expression','lambda_expression']]
    calls=[data[x.start_byte:x.end_byte].decode() for x in nodes if x.type in ['method_invocation','object_creation_expression'] and LOC.search(data[x.start_byte:x.end_byte].decode())]
    # Retain smallest localization expressions, not their enclosing whole method-call tree.
    calls=[x for x in calls if not any(y!=x and y in x for y in calls)]
    if not (UI.search(path) or CALLBACK.search(name)):rejected['not_client_text_lifecycle']+=1;continue
    if len(statements)<2 or (not controls and len(statements)<3):rejected['trivial_static_accessor_or_single_text']+=1;continue
    if name.startswith(('getName','getTitle','getTranslationKey','getDescriptionId')) and len(statements)<5:rejected['static_accessor']+=1;continue
    category='dynamic-tooltip' if re.search(r'tooltip|hovertext|information',name,re.I) else 'recipe-text-layout' if re.search(r'jei|rei/|emi/|category',path,re.I) else 'localized-client-ui'
    if re.search(r'reload|cache|invalidat|language|splitLines|wrapLines',bodytext,re.I):category='text-lifecycle-or-cache'
    # Equal code differing only in literal keys/whitespace is not a distinct implementation.
    normalized=text
    for x in sorted((x for x in nodes if x.type in ['string_literal','line_comment','block_comment']),key=lambda x:x.start_byte,reverse=True):
     a=x.start_byte-n.start_byte;b=x.end_byte-n.start_byte;normalized=normalized[:a]+('"TEXT"' if x.type=='string_literal' else '')+normalized[b:]
    digest=hashlib.sha256(re.sub(r'\s+','',normalized).encode()).hexdigest()
    if digest in seen:rejected['same_body_except_literal_keys']+=1;continue
    seen[digest]=1
    ln=n.start_point.row+1;end=n.end_point.row+1
    rows.append({'repo':src['repo'],'commit':src['sha'],'path':path,'line':ln,'end_line':end,'method':name,'category':category,'source_url':f"https://github.com/{src['repo']}/blob/{src['sha']}/{path}#L{ln}-L{end}",'file_sha256':hashlib.sha256(data).hexdigest(),'dedup_sha256':digest,'source_cache':str(f.relative_to(ROOT)),'control_flow':dict(collections.Counter(controls)),'statements':len(statements),'localization_calls':calls,'body':text})
 rows.sort(key=lambda r:(r['repo'],r['path'],r['line']))
 for i,r in enumerate(rows,1):r['candidate']=i
 (OUT/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 summary={'candidate_count':len(rows),'counted_references':0,'by_project':dict(collections.Counter(r['repo'] for r in rows)),'by_category':dict(collections.Counter(r['category'] for r in rows)),'excluded':dict(rejected),'method':'AST method/constructor boundaries; excludes datagen/tests/models, static accessors, single text statements, exact/key-only clones. Candidate discovery is not completion.'}
 (OUT/'candidate-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':analyze()
