"""AST facts for explicitly reviewed contexts, not keyword->credit conversion.
Records exact branch text, guards, reads/writes, catches and local consumers.
No whole-program binding/type resolution or runtime equivalence claims.
"""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
sys.path.insert(0,str(B/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
rows=[json.loads(s) for s in (O/'reviewed.jsonl').read_text().splitlines()]
items={e['candidate_id']:e for r in rows for e in r['evidence']}
cache={};results=[]
def walk(n):
    yield n
    for c in n.children:yield from walk(c)
for k,e in items.items():
    p=R/e['private_file']
    if p not in cache:
        raw=p.read_bytes();tree=parser.parse(raw);cache[p]=(raw,tree)
    raw,tree=cache[p]
    assert hashlib.sha256(raw).hexdigest()==e['file_sha256']
    def tx(n):return raw[n.start_byte:n.end_byte].decode(errors='replace') if n else None
    matches=[n for n in walk(tree.root_node) if n.type in ('method_declaration','constructor_declaration') and n.start_point.row+1==e['start_line'] and n.end_point.row+1==e['end_line']]
    assert len(matches)==1,(k,e['method'])
    method=matches[0];assert tx(method)==e['context']
    def guards(n):
        out=[];cur=n.parent
        while cur and cur!=method:
            if cur.type=='if_statement':
                con=cur.child_by_field_name('consequence');alt=cur.child_by_field_name('alternative')
                branch='then' if con and con.start_byte<=n.start_byte<con.end_byte else 'else' if alt and alt.start_byte<=n.start_byte<alt.end_byte else 'condition'
                out.append({'condition':tx(cur.child_by_field_name('condition')),'branch':branch})
            cur=cur.parent
        return out[::-1]
    calls=[];assign=[];branches=[];returns=[];catches=[]
    for n in walk(method):
        if n.type=='method_invocation':
            name=tx(n.child_by_field_name('name'));args=n.child_by_field_name('arguments')
            calls.append({'line':n.start_point.row+1,'receiver':tx(n.child_by_field_name('object')),'name':name,'arguments':tx(args),'guards':guards(n),'expression':tx(n)})
        elif n.type=='assignment_expression':assign.append({'line':n.start_point.row+1,'left':tx(n.child_by_field_name('left')),'right':tx(n.child_by_field_name('right')),'expression':tx(n),'guards':guards(n)})
        elif n.type in ('if_statement','ternary_expression'):
            branches.append({'line':n.start_point.row+1,'condition':tx(n.child_by_field_name('condition')),'then':tx(n.child_by_field_name('consequence')),'else':tx(n.child_by_field_name('alternative'))})
        elif n.type=='return_statement':returns.append({'line':n.start_point.row+1,'statement':tx(n),'guards':guards(n)})
        elif n.type=='catch_clause':catches.append({'line':n.start_point.row+1,'statement':tx(n)})
    constants=[];counterparts=[];local_callers=[]
    for n in walk(tree.root_node):
        if n.type=='field_declaration':
            decl=tx(n)
            names=[tx(z.child_by_field_name('name')) for z in n.children if z.type=='variable_declarator']
            if any(x and x in e['context'] for x in names):constants.append({'line':n.start_point.row+1,'declaration':decl})
        elif n.type=='method_declaration' and n!=method:
            name=tx(n.child_by_field_name('name'))
            if name and any(w in name.lower() for w in ['save','write','serial','load','read','clone','restore']):
                counterparts.append({'line':n.start_point.row+1,'method':name,'sha256':hashlib.sha256(tx(n).encode()).hexdigest()})
        elif n.type=='method_invocation' and tx(n.child_by_field_name('name'))==e['method'] and not (method.start_byte<=n.start_byte<method.end_byte):
            local_callers.append({'line':n.start_point.row+1,'expression':tx(n),'binding':'same-file syntactic call only, not resolved overload/owner'})
    results.append({'candidate_id':k,'file_sha256':e['file_sha256'],'method_sha256':e['method_sha256'],'full_context_in':'reviewed.jsonl evidence.context','calls':calls,'assignments':assign,'branches':branches,'returns':returns,'catches':catches,'referenced_field_declarations':constants,'same_file_persistence_methods':counterparts,'same_file_syntactic_callers':local_callers,'tool_limits':['AST textual guard/control evidence, not runtime path execution','receiver types, virtual calls, overloads, cross-file callers and lambda side effects require deeper review','same-file persistence method names are consumer candidates, not proof of ownership','no research credit granted by this extractor']})
(O/'review-context-facts.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in results))
summary={'reviewed_contexts_including_supporting':len(results),'source_files':len(cache),'full_context_hashes_verified':len(results),'credit_granted':0,'facts_sha256':hashlib.sha256((O/'review-context-facts.jsonl').read_bytes()).hexdigest()}
(O/'review-context-facts-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(summary)
