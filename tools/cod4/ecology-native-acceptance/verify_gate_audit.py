"""Synthetic QA verifier regression cases; no Minecraft or research credit."""
import copy,hashlib,json
from pathlib import Path
from audit_native_gates import audit

def fixture(opened=True,local=None):
    if local is None:local=[opened]
    common={'scope_id':1,'chunk':[1,2],'overworld_game_time':400}
    return [dict(common,kind='native_persistent_chunk_opportunity',parent_scope_id=0,dimension='minecraft:overworld',native_spawn_friendlies=True,native_persistent_phase=True,native_calculator_identity_observed=True),
        dict(common,kind='actual_native_creature_category_return',actual_category_return=opened,actual_identity_matched_local_returns=local,foreign_local_return_count=0,pairing_status='ONE_IDENTITY_MATCHED_LOCAL_RETURN' if local else 'LOCAL_RETURN_NOT_OBSERVED',local_evaluation_observed=bool(local)),
        dict(common,kind='native_chunk_loop_return',parent_scope_id=0,paired_return=True,creature_category_return_count=1,identity_matched_local_return_count=len(local),foreign_local_return_count=0)]

cases=[]
def check(name,rows,expected):
    result=audit(rows);assert result['accepted_complete_native_scopes']==expected,(name,result)
    assert result['natural_birth_credit_added']==0 and result['drop_pickup_credit_added']==0
    cases.append({'name':name,'accepted_scopes':expected,'pass':True})
check('actual_global_and_local_open',fixture(),1)
check('actual_local_closed',fixture(False),1)
check('global_closed_local_not_called',fixture(False,[]),1)
r=fixture();r[0]['native_calculator_identity_observed']=False;check('unknown_calculator_rejected',r,0)
r=fixture();r.append({'kind':'unclosed_native_scopes_at_tick_end','overworld_game_time':400,'scope_ids':[7]});check('whole_anomalous_tick_rejected',r,0)
r=fixture();r[0]['parent_scope_id']=9;r[-1]['parent_scope_id']=9;check('unknown_ancestor_rejected',r,0)
r=fixture();r.insert(2,copy.deepcopy(r[1]));check('multiple_category_returns_rejected',r,0)
r=fixture();r[1]['foreign_local_return_count']=1;check('foreign_local_return_rejected',r,0)
r=fixture();r[1]['actual_identity_matched_local_returns']=[];r[1]['pairing_status']='LOCAL_RETURN_NOT_OBSERVED';r[1]['local_evaluation_observed']=False;r[-1]['identity_matched_local_return_count']=0;check('no_local_open_inference',r,0)
r=fixture();r[1]['actual_category_return']=False;check('contradictory_true_local_false_category_rejected',r,0)
r=fixture();r[1]['overworld_game_time']=401;check('cross_tick_scope_rejected',r,0)
r=fixture();r.append({'kind':'actual_native_creature_category_return','scope_id':None});check('unattributable_row_invalidates_gate_count',r,0)
root=Path(__file__).resolve().parents[3];source=Path(__file__).with_name('audit_native_gates.py')
receipt={'status':'PASS_SYNTHETIC_VERIFIER_CASES_ONLY','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':cases,'game_or_java_started':False,'runtime_acceptance':False}
(root/'docs/cod4/audit-20261022/ecology-native-acceptance/preparation-20261028/gate-audit-regression.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(cases),'synthetic verifier cases; no gameplay credit')
