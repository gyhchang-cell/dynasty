"""Bounded metadata-only keep/Create comparison; not a whole-building reading."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))

def main():
    metadata_path=BASE/'research-20261101-dungeons-026/all-structure-metadata.json'
    metadata=get(metadata_path)
    members=['data/betterfortresses/structures/keep.nbt','data/betterfortresses/structures/mod_integration/keep_create.nbt']
    source=next(r for r in metadata['entries'] if r['member']==members[0])
    archive=source['source_archive'];rows=[];maps=[];socketmaps=[];resources={}
    with ZipFile(archive) as z:
        manifest=z.read('META-INF/mods.toml')
        for member in members:
            raw=z.read(member);d=read(raw);pal=d.get('palette') or d['palettes'][0]
            states={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
            cs={p:s for p,s in states.items() if s['Name'] not in AIR}
            sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
            for socket in sockets:
                pool=socket['data']['pool']
                if pool=='minecraft:empty':continue
                namespace,tail=pool.split(':',1)
                poolmember=f'data/{namespace}/worldgen/template_pool/{tail}.json'
                if poolmember in z.namelist():
                    content=z.read(poolmember);resources[poolmember]=dict(member=poolmember,sha256=sha(content),data=json.loads(content))
            rows.append(dict(source_archive=archive,member=member,nbt_sha256=sha(raw),size=d['size'],
                occupied_bounds=[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)],
                stored_positions=len(states),nonair_positions=len(cs),sockets=sockets,
                non_actor_non_empty_interfaces=[s for s in sockets if s['data']['pool'] not in ('betterfortresses:mobs','minecraft:empty')],
                actual_visual_reading=False,building_credit=0,complete_building_identity_confirmed=False))
            maps.append(states);socketmaps.append(sockets)
        assert socketmaps[0]==socketmaps[1]
    changes=[dict(position=list(p),before=maps[0].get(p),after=maps[1].get(p)) for p in sorted(set(maps[0])|set(maps[1])) if maps[0].get(p)!=maps[1].get(p)]
    absence_air=[r for r in changes if r['before'] is None and r['after']['Name'] in AIR]
    other=[r for r in changes if r not in absence_air]
    oldoccupied={p for p,s in maps[0].items() if s['Name'] not in AIR}
    newoccupied={p for p,s in maps[1].items() if s['Name'] not in AIR}
    comparison=dict(state_changes=len(changes),omitted_to_explicit_air=len(absence_air),other_state_changes=len(other),
        original_states_for_non_air_padding_changes=other,
        occupied_positions_added=[list(p) for p in sorted(newoccupied-oldoccupied)],
        occupied_positions_removed=[list(p) for p in sorted(oldoccupied-newoccupied)],
        all_jigsaw_positions_states_and_data_identical=True,
        interpretation='No two-design credit. Large diff includes omitted-to-explicit-air padding; machinery/stair changes and identical interfaces do not establish two independent complete layouts. No visual reading or assembly claimed.')
    dump('component-boundary-audit.json',dict(date='2026-11-03',batch=37,
        metadata=evidence(metadata_path),archive=dict(path=archive,sha256=sha(Path(archive).read_bytes())),
        manifest_sha256=sha(manifest),manifest_text=manifest.decode(),entries=rows,
        pool_resources=list(resources.values()),comparison=comparison,
        decision='HOLD_COMPLETE_DESIGN_BOUNDARY_NOT_TWO_WHOLE_BUILDINGS',
        reason='Both files carry external well, bridge, side and four tower-stair dependencies. Their complete whole-design boundary is not established by this central body. Need author-boundary study before any relevant whole-building admission.',
        actual_images_viewed=0,new_visually_studied_source_templates=0,new_valid_scoped_references=0,
        java_run=False,game_run=False,network_requests=0,components_assembled=False))
    prior_path=BASE/'research-20261103-dungeons-036/scoped-reference-update.json'
    scope=get(prior_path)
    scope.update(prior_update=evidence(prior_path),added_ids=[],added_credit=0,new_source_discoveries=0,
        previous_batch_scope_observations_retained=scope.pop('current_scope_observations'),current_scope_observations=[],
        current_batch_boundary_holds=[dict(member=n,source_archive=archive,credit=0,actual_visual_reading=False) for n in members],
        limits='37批只有两份主楼模板的接口/变体边界预审，没有新增实看或完整建筑。保持36批9/10/1及全部旧问题；不按文件数、差异数、Create换装和接口计数。')
    dump('scoped-reference-update.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=37,
        previous_receipt=evidence(BASE/'research-20261103-dungeons-036/RECEIPT.json'),
        status='METADATA_BOUNDARY_PRECHECK_PENDING_INTEGRITY_VERIFICATION',counts=[9,10,1],remaining=[991,990,999],
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        next='继续优先尚未实看的完整相关建筑；主楼两变体不进入1000参考，若要研究整堡先证明原作者完整边界。',
        production_allowed=False,java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    print(json.dumps(dict(templates_prechecked=2,actual_images_viewed=0,state_changes=len(changes),
        omitted_to_explicit_air=len(absence_air),other_state_changes=len(other),
        external_non_actor_non_empty_interfaces_per_template=[len(r['non_actor_non_empty_interfaces']) for r in rows],
        new_valid_scoped_references=0),ensure_ascii=False))

if __name__=='__main__':main()
