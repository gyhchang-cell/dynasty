"""Reconcile metadata queue without treating file reads as building studies."""
from collections import Counter,defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR

def sha(b):
    return hashlib.sha256(b).hexdigest()

def get(p):
    return json.loads(p.read_text())

def dump(n,v):
    (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def evidence(p):
    return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))

def locations(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k=='location' and isinstance(x,str):yield x
            else:yield from locations(x)
    elif isinstance(v,list):
        for x in v:yield from locations(x)

def main():
    queue_path=BASE/'research-20261101-dungeons-026/remaining-size-review-queue.json'
    meta_path=BASE/'research-20261101-dungeons-026/all-structure-metadata.json'
    metadata=get(meta_path)
    fixed=get(Path(metadata['fixed_archive_inventory']['path']))
    archives={a['path']:a for a in fixed['archives']}
    meta={(e['source_archive'],e['member']):e for e in metadata['entries']}
    spec=importlib.util.spec_from_file_location('historical_reader',BASE/'research-20261101-dungeons-002/check_dedup.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    indices=[BASE/'continuation-20261022/references/full-buildings.json',*sorted(BASE.glob('continuation-20261022/references/whole-candidates*/candidates.json'))]
    for folder in sorted(BASE.glob('research-*')):
        if folder==OUT:continue
        indices.extend(folder/n for n in ('sources.json','scope-expansion-sources.json','manual-review.json') if (folder/n).is_file())
    historical={}
    for p in indices:m.find_records(get(p),str(p),historical)
    groups=defaultdict(list)
    for row in get(queue_path)['entries']:groups[row['source_archive']].append(row)
    rows=[]; resources=[];source_archives=[]
    for archive,group in sorted(groups.items()):
        assert sha(Path(archive).read_bytes())==archives[archive]['sha256']
        source_archives.append(dict(path=archive,sha256=archives[archive]['sha256']))
        with ZipFile(archive) as z:
            pools=defaultdict(list)
            for member in z.namelist():
                if '/worldgen/template_pool/' not in member or not member.endswith('.json'):continue
                raw=z.read(member)
                try:data=json.loads(raw)
                except (UnicodeDecodeError,json.JSONDecodeError):continue
                for identifier in set(locations(data)):
                    pools[identifier].append(dict(member=member,sha256=sha(raw)))
            for q in group:
                key=(archive,q['member']);original=meta[key]
                raw=z.read(q['member']);assert sha(raw)==original['nbt_sha256']
                d=read(raw);assert d['size']==q['size']
                pal=d.get('palette') or d['palettes'][0]
                cs={tuple(b['pos']):pal[b['state']] for b in d['blocks'] if pal[b['state']]['Name'] not in AIR}
                bounds=[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
                assert bounds==q['occupied_bounds']
                prefix,tail=q['member'].split('/structures/',1)
                identifier=prefix.split('/')[-1]+':'+tail[:-4]
                matches=pools.get(identifier,[])
                for r in matches:resources.append(dict(archive=archive,**r))
                sockets=[dict(position=b['pos'],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
                actual_height=bounds[1][1]-bounds[1][0]+1
                flags=[]
                if d['size'][1]-actual_height>=5:flags.append('STORED_HEIGHT_PADDING_REQUIRES_ROOM_CHECK')
                if re.search(r'/(rooms?|pieces?|streets?|terminators?|decoration[^/]*)/|(?:_|/)(part|base|base_plate|feature_plate|layer|crossing|bridge|corridor|skeleton|rear|bottom|top|middle|roof|room|chamber|bookcase|stairs|towers)(?:_|\d|/|\.)',q['member']):
                    flags.append('NAME_SUGGESTS_COMPONENT_NOT_PROOF')
                if re.search(r'/village/|/houses?/|/(?:alchemist|cartographer|librarian|fletcher|farm|fountain|house|loom|mason|weaponsmith)',q['member']):
                    flags.append('NAME_SUGGESTS_VILLAGE_OR_OCCUPATION_USE_NOT_PROOF')
                if sockets:flags.append('HAS_JIGSAW_INTERFACES_ROLE_REQUIRES_REVIEW')
                if actual_height<17:flags.append('LOW_OCCUPIED_HEIGHT_REQUIRES_SCOPE_CHECK')
                if key in historical:route='ALREADY_IN_STUDY_INDEX_REUSE_EXISTING_DECISION'
                elif 'NAME_SUGGESTS_COMPONENT_NOT_PROOF' in flags:route='ASSEMBLY_BOUNDARY_REVIEW'
                elif 'STORED_HEIGHT_PADDING_REQUIRES_ROOM_CHECK' in flags:route='OCCUPIED_HEIGHT_AND_ROOM_REVIEW'
                elif 'LOW_OCCUPIED_HEIGHT_REQUIRES_SCOPE_CHECK' in flags:route='LOW_HEIGHT_SCOPE_REVIEW'
                elif 'NAME_SUGGESTS_VILLAGE_OR_OCCUPATION_USE_NOT_PROOF' in flags:route='PURPOSE_REVIEW'
                else:route='WHOLE_BODY_AND_PURPOSE_REVIEW'
                rows.append(dict(source_archive=archive,member=q['member'],nbt_sha256=sha(raw),size=d['size'],
                    occupied_bounds=bounds,occupied_height=actual_height,stored_height_padding=d['size'][1]-actual_height,
                    historical_indices=sorted(set(historical.get(key,{}).get('prior_indices',[]))),
                    direct_exact_location_pool_mentions=matches,jigsaw_interfaces=sockets,
                    routing_flags=flags,next_review_route=route,actual_visual_reading_in_this_batch=False,
                    complete_building_identity_confirmed=False,building_credit=0))
    resource_map={(r['archive'],r['member']):r for r in resources}
    summary=dict(queue_rows=len(rows),historical_distinct_source_pairs=len(historical),
        historical_queue_rows=sum(bool(r['historical_indices']) for r in rows),
        unmatched_queue_rows=sum(not r['historical_indices'] for r in rows),
        routes=dict(Counter(r['next_review_route'] for r in rows)),
        archives_rechecked=len(source_archives),source_nbt_bytes_rechecked=len(rows),
        actual_visual_readings=0,new_visually_studied_sources=0,new_valid_scoped_references=0)
    dump('queue-reconciliation.json',dict(summary=summary,entries=rows,
        limits='Routing hints only. Names, padding, pools and metadata do not establish semantic exclusion, completeness, family independence or building credit. No queue-exhaustion claim. The unresolved room-height convention remains unresolved.'))
    dump('input-evidence.json',dict(queue=evidence(queue_path),metadata=evidence(meta_path),
        fixed_inventory=metadata['fixed_archive_inventory'],historical_indices=[evidence(p) for p in indices],
        archives=source_archives,template_pool_resources=list(resource_map.values())))
    prior_path=BASE/'research-20261102-dungeons-034/scoped-reference-update.json'
    prior=get(prior_path);scope=dict(prior)
    scope.update(prior_update=evidence(prior_path),added_ids=[],added_credit=0,new_source_discoveries=0,
      current_batch_exclusions=[],prior_034_exclusions_retained=prior['current_batch_exclusions'],
      limits='35批只读复核元数据队列，不增加已实看来源、完整相关建筑或排除判定；保持34批8/10/1与全部旧待查。')
    dump('scoped-reference-update.json',scope)
    dump('discovery-boundary.json',dict(local_only=True,network_requests=0,java_run=False,game_run=False,
        production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0,
        actual_images_viewed=0,new_source_templates_visually_studied=0,building_credit_added=0))
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    main()
