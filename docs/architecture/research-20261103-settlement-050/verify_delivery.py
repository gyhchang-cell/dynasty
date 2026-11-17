"""Evidence consistency against original sources; no Java/game or register edits."""
import hashlib,json,sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(name):return json.loads((OUT/name).read_text())
def ref(p):return dict(path=str(p.resolve()),sha256=sha(p))
def dump(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def bound(r):assert sha(Path(r['path']))==r['sha256'],r['path']
def main():
    assert not (OUT/'RECEIPT.json').exists(),'Sealed delivery: do not rewrite; independently inspect receipt instead.'
    prior=OUT.parent/'research-20261103-lodging-049'
    prior_receipt=json.loads((prior/'RECEIPT.json').read_text())
    for item in prior_receipt['files']:
        p=prior/item['path'];assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],str(p)
    scope=get('scope-status.json');bound(scope['prior_receipt']);bound(scope['prior_scope_status'])
    source=get('sources.json');c=source['candidates'][0]
    assert len(source['candidates'])==1 and source['automatic_credit']==0
    jar=Path(c['source_archive']);assert sha(jar)==c['source_archive_sha256']
    inventory=json.loads((OUT.parent/'research-20261101-dungeons-024/fixed-source-screen.json').read_text())
    assert any(x['path']==str(jar) and x['sha256']==sha(jar) for x in inventory['archives'])
    a=get('author-context.json');m=get('mob-support-boundary.json')
    with ZipFile(jar) as z:
        raw=z.read(c['member']);assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
        n=read(raw);pal=n['palette'];ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']}
        assert len(ss)==len(n['blocks'])==25024 and n['size']==[53,49,54]
        assert all(0<=v<limit for p in ss for v,limit in zip(p,n['size']))
        solid={p:s for p,s in ss.items() if s['Name'] not in AIR}
        assert len(solid)==25024 and a['explicit_air']==0 and a['omitted_positions']==115214
        assert dict(Counter(s['Name'] for s in solid.values()))==c['materials']
        for i,axis in enumerate('xyz'):assert a['nonair_bounds'][axis]==[min(p[i] for p in solid),max(p[i] for p in solid)]
        assert a['nonair_bounds']==dict(x=[0,52],y=[0,48],z=[0,53])
        resources={r['member']:r for r in a['resources']};assert len(resources)==6
        for member,r in resources.items():
            data=z.read(member);assert hashlib.sha256(data).hexdigest()==r['sha256']
            assert (data.decode()==r['text']) if 'text' in r else (json.loads(data)==r['data'])
        root=resources['data/trek/worldgen/structure/overworld/rare/villager_island.json']['data']
        assert root['start_pool']=='trek:overworld/rare/villager_island' and root['size']==2
        assert root['start_height']=={'absolute':-11} and root['terrain_adaptation']=='none'
        assert root['project_start_to_heightmap']=='WORLD_SURFACE_WG'
        pool=resources['data/trek/worldgen/template_pool/overworld/rare/villager_island.json']['data']
        assert len(pool['elements'])==1 and pool['elements'][0]['weight']==1
        e=pool['elements'][0]['element'];assert e['location']=='trek:overworld/rare/villager_island'
        assert e['projection']=='rigid' and e['processors']=='minecraft:empty'
        sockets=[b for b in n['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
        assert len(sockets)==13 and all(b['nbt']['pool']=='trek:mobs/villagers/plains/unemployed' for b in sockets)
        rawpool=z.read(m['pool_member']);assert hashlib.sha256(rawpool).hexdigest()==m['pool_sha256']
        assert json.loads(rawpool)==m['pool_data'] and len(m['support_templates'])==3
        assert sorted(r['weight'] for r in m['support_templates'])==[1,1,8]
        support_ids=[]
        for r,e in zip(m['support_templates'],m['pool_data']['elements']):
            data=z.read(r['archive_member']);assert hashlib.sha256(data).hexdigest()==r['sha256']
            d=read(data);assert d['size']==r['size']==[1,3,1]
            assert d['blocks']==r['blocks'] and d['palette']==r['palette'] and d['entities']==r['entities']
            assert len(d['blocks'])==3 and len(d['entities'])==1
            assert d['entities'][0]['nbt']['id']=='minecraft:villager'
            js=[b for b in d['blocks'] if d['palette'][b['state']]['Name']=='minecraft:jigsaw']
            assert len(js)==1 and js[0]['nbt']['pool']=='minecraft:empty'
            assert set(r['materials'])=={'minecraft:air','minecraft:jigsaw'}
            assert r['archive_member'].endswith(e['element']['location'].split(':',1)[1]+'.nbt')
            support_ids.append(d['entities'][0]['nbt']['VillagerData']['profession'])
        assert sorted(support_ids)==['minecraft:nitwit','minecraft:none','minecraft:none']
        assert m['transformed_or_assembled'] is False and m['native_spawn_verified'] is False
        beds={p:s for p,s in ss.items() if s['Name'].endswith('_bed')};assert len(beds)==8
        vectors=dict(north=(0,-1),south=(0,1),east=(1,0),west=(-1,0));pairs=[]
        for p,s in beds.items():
            pr=s['Properties']
            if pr['part']!='foot':continue
            dx,dz=vectors[pr['facing']];head=(p[0]+dx,p[1],p[2]+dz)
            assert head in beds and beds[head]['Name']==s['Name']
            assert beds[head]['Properties']['part']=='head' and beds[head]['Properties']['facing']==pr['facing']
            pairs.append([list(p),list(head)])
        assert len(pairs)==4 and {p[0][1] for p in pairs}=={24,25}
        doors={p:s for p,s in ss.items() if s['Name'].endswith('_door') and s['Properties']['half']=='lower'}
        assert len(doors)==18
        assert {str(k):v for k,v in Counter(p[1] for p in doors).items()}==a['lower_door_layers']
        assert a['lower_door_layers']=={'13':1,'19':2,'20':1,'23':1,'24':10,'29':1,'34':2}
        assert sum(s['Name'].endswith('_stairs') for s in ss.values())==614
        assert sum(s['Name']=='minecraft:ladder' for s in ss.values())==55
        for y in range(23,34):
            s=ss[(41,y,8)];assert s['Name']=='minecraft:ladder' and s['Properties']['facing']=='east'
        assert (41,34,6) in doors and (41,34,10) in doors
        signs=[b for b in n['blocks'] if b.get('nbt',{}).get('id')=='minecraft:sign'];assert len(signs)==7
        for b in signs:
            for i in range(1,5):assert json.loads(b['nbt'][f'Text{i}'])['text']==''
        for r in a['loot_tables']:
            assert (r['member'] in z.namelist())==r['present_in_source_archive']
            if r['present_in_source_archive']:
                data=z.read(r['member']);assert hashlib.sha256(data).hexdigest()==r['sha256'] and json.loads(data)==r['data']
        assert [r['id'] for r in a['loot_tables'] if not r['present_in_source_archive']]==['minecraft:chests/village/village_taiga_house']
    task=get('task-use-boundary.json');bound(task['original_prompt']);bound(task['original_lodging_scope'])
    lines=Path(task['original_prompt']['path']).read_text().splitlines()
    assert all(lines[r['line']-1]==r['text'] for r in task['excerpts'])
    assert not task['new_scope_definition'] and not task['new_ledger_created']
    review=get('manual-review.json');r=review['entries'][0]
    assert len(review['entries'])==1 and r['member']==c['member'] and r['nbt_sha256']==c['nbt_sha256']
    assert r['actual_new_images_viewed']==len(r['evidence_actually_viewed'])==7
    assert r['actual_old_images_viewed']==len(r['old_comparison_images_actually_viewed'])==2
    for img in r['evidence_actually_viewed']+r['old_comparison_images_actually_viewed']:
        bound(img);assert img['actual_visual_reading'] is True
        with Image.open(img['path']) as im:im.verify()
    for key in ['layout','proportion','facade','roof','material','circulation','terrain_connection']:
        assert len(r[key+'_observation'])>70
    assert r['same_agent_semantic_reading'] and not r['independent_review'] and not r['human_acceptance']
    assert r['actual_design_credit_proposed']==r['formal_credit_added']==review['formal_credit_added']==0
    dd=get('dedup-evidence.json');assert dd['formal_identity_records_checked']==151
    assert dd['historical_unique_local_archive_member_pairs']==250
    assert not dd['entries'][0]['historical_exact_matches']
    for key in ['funerary','lodging']:
        bound(scope[key]['baseline']);assert scope[key]['current_batch_added']==0 and scope[key]['scope_definition_unchanged']
    bound(scope['funerary']['coordinator_048_authority']);bound(scope['guard']['prior_hold_authority'])
    assert len(json.loads(Path(scope['funerary']['baseline']['path']).read_text())['entries'])==151
    ld=json.loads(Path(scope['lodging']['baseline']['path']).read_text())
    assert ld['accepted_references']==2 and ld['scope_definition']==scope['lodging']['scope_definition']==task['lodging_scope_definition']
    assert not scope['production_allowed'] and not scope['source_exhaustion_claimed']
    session=get('session.json')
    for key in ['java_run','game_run','audio_or_brightness_changed','wake_unlock_focus_or_process_queries','shared_coordinator_session_written']:assert session[key] is False
    for key in ['formal_credit_added','new_proposals','network_requests','production_changes','checklist_deletions','duration_hours_claimed']:assert session[key]==0
    status='PASS_ORIGINAL_COMPLETE_SETTLEMENT_READ_ONLY_SCOPE_RETAINED'
    verification=dict(status=status,date='2026-11-03',batch=50,actual_complete_designs_visually_studied=1,
      actual_new_images_viewed=7,actual_old_images_viewed=2,original_primary_nbts=4,
      parent_settlement_templates=1,mob_support_templates=3,mob_only_parent_sockets=13,
      complete_bed_pairs=pairs,continuous_original_ladder_states=11,
      native_route_or_generation_verified=False,old_scope_unchanged=True,new_scope_created=False,
      new_first_scope_proposals=0,formal_credit_added=0,funerary_formal_count=151,funerary_remaining=849,
      lodging_formal_count=2,lodging_remaining=998,cod6_credit_added=0,
      previous049_receipted_files_unchanged=True,
      earlier_integrity_bound_not_reexecuted=ref(prior/'verification.json'),
      source_exhaustion_claimed=False,production_allowed=False,
      java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',verification)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=50,
      session=ref(OUT/'session.json'),verification=ref(OUT/'verification.json'),
      scope=ref(OUT/'scope-status.json'),review=ref(OUT/'manual-review.json'),
      shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,
      duration_hours_claimed=0,no_automation=True))
    files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='RECEIPT.json']
    dump('RECEIPT.json',dict(status=status,files=files))
    print(json.dumps(verification,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
