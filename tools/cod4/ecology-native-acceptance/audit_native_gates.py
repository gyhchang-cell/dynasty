"""Conservative audit of native gate rows; never awards species or loot credit."""
from collections import defaultdict
import argparse
import json
from pathlib import Path


def audit(rows):
    scopes=defaultdict(lambda: {'begin':[], 'category':[], 'end':[]})
    anomalous_ticks=set(); unclosed=set(); issues=[]
    kinds={'native_persistent_chunk_opportunity':'begin',
           'actual_native_creature_category_return':'category',
           'native_chunk_loop_return':'end'}
    for index,row in enumerate(rows):
        if row.get('kind')=='unclosed_native_scopes_at_tick_end':
            anomalous_ticks.add(row.get('overworld_game_time'))
            unclosed.update(row.get('scope_ids',[]))
        if row.get('kind') in kinds:
            sid=row.get('scope_id')
            if type(sid) is not int or sid<=0:
                issues.append({'row':index,'reason':'invalid_scope_id'});continue
            scopes[sid][kinds[row['kind']]].append((index,row))
    rejected={}; parents={}; accepted={}
    for sid,s in scopes.items():
        errors=[]
        if any(len(s[k])!=1 for k in ['begin','category','end']):
            rejected[sid]=['requires_exactly_one_begin_category_return_and_end'];continue
        bi,b=s['begin'][0];ci,c=s['category'][0];ei,e=s['end'][0]
        parents[sid]=b.get('parent_scope_id')
        if not bi<ci<ei:errors.append('callback_order')
        if any(type(r.get('overworld_game_time')) is not int for r in [b,c,e]) or len({r.get('overworld_game_time') for r in [b,c,e]})!=1:errors.append('missing_or_cross_tick_scope')
        if b.get('dimension')!='minecraft:overworld' or b.get('native_spawn_friendlies') is not True or b.get('native_persistent_phase') is not True:errors.append('not_actual_overworld_persistent_friendly_branch')
        if b.get('native_calculator_identity_observed') is not True:errors.append('unknown_calculator_identity')
        if b.get('chunk')!=c.get('chunk') or b.get('chunk')!=e.get('chunk'):errors.append('chunk_mismatch')
        if b.get('parent_scope_id')!=e.get('parent_scope_id'):errors.append('parent_mismatch')
        if e.get('paired_return') is not True or e.get('creature_category_return_count')!=1:errors.append('unexpected_combined_return_count')
        if any(r.get('overworld_game_time') in anomalous_ticks for r in [b,c,e]):errors.append('whole_tick_has_unclosed_native_scope')
        if sid in unclosed:errors.append('scope_unclosed')
        local=c.get('actual_identity_matched_local_returns',[])
        if not isinstance(local,list) or len(local)>1 or any(type(v) is not bool for v in local):errors.append('foreign_or_multiple_local_returns');local=[]
        if c.get('foreign_local_return_count')!=0 or e.get('foreign_local_return_count')!=0:errors.append('foreign_local_returns')
        if e.get('identity_matched_local_return_count')!=len(local):errors.append('local_count_mismatch')
        expected='ONE_IDENTITY_MATCHED_LOCAL_RETURN' if len(local)==1 else 'LOCAL_RETURN_NOT_OBSERVED'
        if c.get('pairing_status')!=expected:errors.append('pairing_status_anomaly')
        if c.get('local_evaluation_observed') is not bool(local):errors.append('local_observation_flag_mismatch')
        actual=c.get('actual_category_return')
        if type(actual) is not bool:errors.append('category_return_not_boolean')
        if actual is True and local!=[True]:errors.append('open_category_without_exact_actual_open_local_return')
        if actual is False and local==[True]:errors.append('contradictory_native_category_and_local_returns')
        if errors:rejected[sid]=errors
        else:accepted[sid]={'category_open':actual,'actual_local_return':local[0] if local else None,
                            'game_time':c.get('overworld_game_time'),'chunk':c.get('chunk')}
    # An inner callback can return after an outer exception popped the wrong frame.
    # Require every ancestor to exist, be accepted, and properly enclose this scope.
    for sid in list(accepted):
        child=sid;visited={sid};parent=parents.get(child)
        while parent!=0:
            if parent in visited or parent not in accepted:
                rejected[sid]=['unknown_rejected_or_cyclic_ancestor'];break
            visited.add(parent)
            pb=scopes[parent]['begin'][0][0];pe=scopes[parent]['end'][0][0]
            cb=scopes[child]['begin'][0][0];ce=scopes[child]['end'][0][0]
            if not pb<cb<ce<pe:
                rejected[sid]=['ancestor_does_not_enclose_child'];break
            child=parent;parent=parents.get(child)
    # Propagate rejections until no accepted child relies on a rejected ancestor.
    changed=True
    while changed:
        changed=False
        for sid in accepted:
            if sid not in rejected and parents.get(sid) in rejected:
                rejected[sid]=['rejected_ancestor'];changed=True
    if issues:
        for sid in accepted:rejected.setdefault(sid,[]).append('unattributable_native_row_invalidates_session_gate_count')
    accepted={sid:v for sid,v in accepted.items() if sid not in rejected}
    return {'status':'SCOPED_GATE_ROWS_AUDITED_NOT_GAMEPLAY_ACCEPTANCE',
            'accepted_complete_native_scopes':len(accepted),
            'actual_category_open_scopes':sum(v['category_open'] for v in accepted.values()),
            'actual_category_closed_scopes':sum(not v['category_open'] for v in accepted.values()),
            'accepted_scopes':accepted,'rejected_scopes':rejected,'global_row_issues':issues,
            'anomalous_ticks':sorted(x for x in anomalous_ticks if x is not None),
            'species_selected_inferred':False,'natural_birth_credit_added':0,'drop_pickup_credit_added':0,
            'does_not_bind_source_runtime_or_world_without_separate_receipt':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('jsonl',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    # Malformed/truncated JSON is an error; never silently discard adverse rows.
    rows=[json.loads(line) for line in args.jsonl.read_text().splitlines() if line.strip()]
    result=audit(rows)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
