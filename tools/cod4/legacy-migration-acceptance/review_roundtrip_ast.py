"""Conservative tool-assisted review of real persistence read/write implementations.
Not a keyword counter: requires AST input provenance, actual saved-value branch,
explicit fallback, restored member state and a matching persistence writer.
Every admitted implementation carries full code, exact branch and counterpart code.
Output is separate for inspection; does NOT modify accepted ledger/gate.
"""
from pathlib import Path
import sys,json,re,hashlib,collections
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
sys.path.insert(0,str(B/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
index=[json.loads(s) for s in (O/'candidates.jsonl').read_text().splitlines()]
byfile=collections.defaultdict(list)
for c in index:
    # Pure fixes/codecs/Clone chains are handled separately; this rule is for saved state loaders.
    if re.search(r'^(read|load|deserial|restore|fromNBT|fromTag)',c['method'],re.I) and re.search(r'CompoundTag|CompoundNBT|NBTTagCompound|ValueInput|SNBTCompoundTag',c['context']):
        if not re.search(r'/client/|/render|/config|/test/|/datagen/|/data/generator|/worldgen/',c['path'],re.I):byfile[c['private_file']].append(c)
seen=set();rows=[];rejects=collections.Counter()
def walk(n):
    yield n
    for c in n.children:yield from walk(c)
for file,candidates in byfile.items():
    raw=(R/file).read_bytes();tree=parser.parse(raw)
    def tx(n):return raw[n.start_byte:n.end_byte].decode(errors='replace') if n else ''
    if tree.root_node.has_error:rejects['parse_error']+=len(candidates);continue
    methods=[n for n in walk(tree.root_node) if n.type=='method_declaration']
    lookup={(n.start_point.row+1,n.end_point.row+1):n for n in methods}
    for c in candidates:
        method=lookup.get((c['start_line'],c['end_line']))
        if method is None:rejects['missing_exact_method']+=1;continue
        owner=method.parent
        while owner and owner.type not in ('class_declaration','record_declaration','enum_declaration'):owner=owner.parent
        if not owner:rejects['no_owner']+=1;continue
        ownername=tx(owner.child_by_field_name('name'));params=method.child_by_field_name('parameters')
        roots={tx(n.child_by_field_name('name')) for n in params.named_children if re.search(r'CompoundTag|CompoundNBT|NBTTagCompound|ValueInput|SNBTCompoundTag',tx(n))}
        if not roots:rejects['no_nbt_parameter']+=1;continue
        fields={}
        body=owner.child_by_field_name('body')
        for z in body.named_children:
            if z.type=='field_declaration':
                for d in z.named_children:
                    if d.type=='variable_declarator':fields[tx(d.child_by_field_name('name'))]=tx(z)
        alias=set(roots);nodes=list(walk(method))
        locals={tx(z.child_by_field_name('name')) for z in nodes if z.type=='variable_declarator'}
        locals.update(tx(z.child_by_field_name('name')) for z in params.named_children)
        def refers(expr,names):return any(re.search(r'(?<![\w$])'+re.escape(k)+r'(?![\w$])',expr) for k in names if k)
        for _ in range(4):
            for z in nodes:
                if z.type=='variable_declarator':
                    v=tx(z.child_by_field_name('value'));nm=tx(z.child_by_field_name('name'))
                    if refers(v,alias):alias.add(nm)
        calls=[];reads=[];writes=[];branches=[];fallbacks=[];restored=[]
        for z in nodes:
            if z.type=='method_invocation':
                nm=tx(z.child_by_field_name('name'));obj=tx(z.child_by_field_name('object'));args=tx(z.child_by_field_name('arguments'))
                call={'line':z.start_point.row+1,'receiver':obj,'method':nm,'arguments':args,'expression':tx(z)};calls.append(call)
                if refers(obj,alias) and re.match(r'^(get|read|contains|has|as)',nm):reads.append(call)
                if nm in ('orElse','orElseGet','getOrDefault','resultOrPartial') and refers(tx(z),alias):fallbacks.append({'kind':nm,'line':z.start_point.row+1,'code':tx(z)})
                if nm in ('deserializeNBT','readFromNBT','load','read','readFromTag') and refers(args,alias):
                    member=obj[5:] if obj.startswith('this.') else obj
                    if member in fields and (obj.startswith('this.') or member not in locals):restored.append({'kind':'member_restoration_call','member':member,'line':z.start_point.row+1,'code':tx(z)})
            elif z.type=='assignment_expression':
                lhs=tx(z.child_by_field_name('left'));rhs=tx(z.child_by_field_name('right'));member=lhs[5:] if lhs.startswith('this.') else lhs
                if member in fields and (lhs.startswith('this.') or member not in locals) and refers(rhs,alias):restored.append({'kind':'member_assignment','member':member,'line':z.start_point.row+1,'code':tx(z)})
            elif z.type=='if_statement':
                cond=tx(z.child_by_field_name('condition'));yes=tx(z.child_by_field_name('consequence'));no=tx(z.child_by_field_name('alternative'))
                if refers(cond,alias):
                    branches.append({'line':z.start_point.row+1,'condition':cond,'then':yes,'else':no})
                    if no:fallbacks.append({'kind':'explicit_else','line':z.start_point.row+1,'condition':cond,'fallback_code':no})
            elif z.type=='ternary_expression':
                cond=tx(z.child_by_field_name('condition'))
                if refers(cond,alias):fallbacks.append({'kind':'ternary','line':z.start_point.row+1,'code':tx(z)})
            elif z.type=='catch_clause':
                if refers(tx(z.parent),alias):fallbacks.append({'kind':'catch','line':z.start_point.row+1,'code':tx(z)})
        if not reads:rejects['no_ast_parameter_read']+=1;continue
        if not fallbacks:rejects['no_explicit_compatible_fallback']+=1;continue
        if not restored:rejects['no_proven_member_restoration']+=1;continue
        # A matching writer in the SAME owner must consume restored members.
        counterpart=[];restored_names={a['member'] for a in restored}
        for z in body.named_children:
            if z.type!='method_declaration' or z==method:continue
            name=tx(z.child_by_field_name('name'))
            if not re.search(r'^(save|write|serial)',name,re.I):continue
            code=tx(z);members=[k for k in restored_names if refers(code,{k})]
            if not members:continue
            outcalls=[]
            for nn in walk(z):
                if nn.type=='method_invocation':
                    nm=tx(nn.child_by_field_name('name'))
                    if re.match(r'^(put|write|serial|save)',nm):outcalls.append(tx(nn))
            if outcalls:counterpart.append({'method':name,'line':z.start_point.row+1,'restored_members_used':members,'write_calls':outcalls,'context':code,'method_sha256':hashlib.sha256(code.encode()).hexdigest()})
        if not counterpart:rejects['no_matching_same_object_persistence_writer']+=1;continue
        # Scope: item/inventory/player/quest objects or actual stack/inventory payload in loader.
        relevant=bool(re.search(r'item|inventor|quest|player|progress|capabilit|storage|equipment|curios',c['path'],re.I)) or bool(re.search(r'ItemStack|ItemHandler|Inventory|[Ii]nventory|[Ii]tems|[Ii]nventor',c['context']))
        if not relevant:rejects['no_item_or_progress_object_scope']+=1;continue
        if c['structural_fingerprint'] in seen:rejects['structural_clone']+=1;continue
        seen.add(c['structural_fingerprint'])
        rows.append({'candidate_id':c['candidate_id'],'decision':'ast_roundtrip_context_review','scope':'item_or_progress_saved_state_explicit_fallback','owner':ownername,'input_parameters':sorted(roots),'input_aliases':sorted(alias),'saved_reads':reads,'version_or_field_branches':branches,'explicit_fallbacks':fallbacks,'restored_members':restored,'matching_persistence_writers':counterpart,'field_declarations':{k:fields[k] for k in restored_names},'evidence':c,'limits':['Static AST tool-assisted review; no per-case manual gameplay','Alias propagation is textual after AST declaration extraction; not whole-program dataflow or resolved types','Writer same-owner member intersection proves stored-state connection, not atomicity or total payload retention','Literal/alpha-normalized clones excluded; no credit per key/registration/loop item','Branch expressions and fallback output recorded verbatim; no universal claim all fallbacks are lossless'],'accepted_ledger_credit':0})
(O/'roundtrip-ast-review.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
summary={'ast_contexts_reviewed':sum(map(len,byfile.values())),'passed_strict_roundtrip_rule':len(rows),'reject_reasons':dict(rejects),'accepted_ledger_credit':0,'gate_not_changed':True,'by_repo':dict(collections.Counter(x['evidence']['repo'] for x in rows))}
(O/'roundtrip-ast-review-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
