#!/usr/bin/env python3
"""Register a manually authored, actually viewed reference batch (never create assets).

Candidate enumeration alone earns no credit. Review notes and exclusion decisions
remain separately inspectable; repeat runs replace only this batch's entries.
"""
import hashlib
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'docs/architecture/continuation-20261022/references'
BATCH = 'whole-candidates/review-batch-001.json'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--review', default=BATCH)
    args=ap.parse_args()
    batch=args.review
    folder=Path(batch).parent
    review=json.loads((REF/batch).read_text())
    candidates=json.loads((REF/folder/'candidates.json').read_text())['candidates']
    by_id={v['id']:v for v in candidates}
    accepted=review['accepted']; rejected=review['not_credited']
    if set(accepted) & set(rejected) or set(accepted)|set(rejected) != set(by_id):
        raise ValueError('Every candidate must have exactly one manual review decision')
    register=REF/'full-buildings.json'
    data=json.loads(register.read_text())
    entries=[e for e in data['entries'] if e.get('manual_review_file')!=batch]
    keys=['complete_boundary_and_relevance','layout_observation','proportion_observation',
          'facade_observation','roof_observation','material_observation',
          'circulation_observation','terrain_connection_observation']
    for ident,notes in accepted.items():
        if len(notes)!=len(keys) or any(not s.strip() for s in notes):
            raise ValueError(('Missing specific observations',ident))
        r=by_id[ident]
        if 'viewed_evidence' in review:
            evidence=[str(folder/f) for f in review['viewed_evidence'][ident]]
        else:
            contact=f'plans-{(int(ident[1:])-1)//4+1:02}.png'
            evidence=[str(folder/r['image']), str(folder/contact)]
        evidence_hashes={f:hashlib.sha256((REF/f).read_bytes()).hexdigest() for f in evidence}
        entries.append({
            'id':review.get('id_prefix','COD4-R001-')+ident,
            'status':'REVIEWED_COMPLETE_DESIGN_REFERENCE_ONLY',
            'credited_scopes':['COD4-1/11/13 architecture'],
            'target':review['target'],
            'verifiable_source':{'official_url':r['source_url'],'local_jar':r['source_jar'],
                                 'jar_sha256':r['source_jar_sha256'],'member':r['member'],'nbt_sha256':r['nbt_sha256']},
            'complete_building_identity':r['member'],
            'evidence_actually_viewed':evidence,
            'evidence_sha256':evidence_hashes,
            'manual_review_file':batch,
            'deduplication_basis':{
                'material_independent_rotation_normalized_geometry_sha256':r['material_independent_geometry_sha256'],
                'manual_design_family_exclusions':(
                    [k for k,v in review['manual_families'].items() if v==ident]
                    if 'manual_families' in review else
                    {'W005':['W008','W010'],'W012':['W019','W021']}.get(ident,[])),
                'count_unit':'One complete building/design; no per-view, per-floor or per-grave credit'},
            'relevance_to_current_task':notes[0],
            'template_size':r['size'],
            'doors_from_nbt':r['doors'],
            'pool_references':r['pool_references'],
            'native_collision_or_generation_validated':False,
            **dict(zip(keys,notes))})
    identities=[(e['verifiable_source']['official_url'],e['complete_building_identity']) for e in entries]
    if len(identities)!=len(set(identities)): raise ValueError('Repeated complete-building identity')
    data['entries']=entries
    batches=[b for b in data.get('reviewed_batches',[]) if b['file']!=batch]
    data['reviewed_batches']=batches+[{'file':batch,'candidates_actually_viewed':len(candidates),
                             'accepted_complete_designs':len(accepted),'excluded_or_deferred':len(rejected),
                             'native_game_acceptance':False}]
    for scope in data['scope_status']:
        count=sum(scope['scope'] in e.get('credited_scopes',[]) for e in entries)
        scope['credited_verified_complete_buildings']=count
        scope['remaining']=max(0,data['minimum_related_complete_buildings']-count)
        scope['new_architecture_may_start']=count>=data['minimum_related_complete_buildings']
        if scope['scope'].startswith('COD4'):
            scope['credited_target_zh']=review['target']
            scope['other_architecture_targets_require_separate_relevance_review']=True
    register.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'credited_this_batch':len(accepted),'excluded_or_deferred':len(rejected),
                      'scope_counts':data['scope_status']},ensure_ascii=False))


if __name__=='__main__': main()
