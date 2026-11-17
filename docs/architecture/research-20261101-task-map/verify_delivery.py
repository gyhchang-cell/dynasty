#!/usr/bin/env python3
"""Bounded evidence verification only. No game, Java, network, or production edits."""
import ast
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SETTLEMENTS=OUT.parent/'research-20261101-settlements'


def main():
    mapping=json.loads((OUT/'architecture-task-map.json').read_text())
    lines={}
    for source in mapping['source_snapshots']:
        path=Path(source['path']);raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==source['sha256'],path
        lines[str(path)]=raw.decode('utf-8-sig').splitlines()
    assert not Path(mapping['cod5']['path']).exists()
    anchored=[]
    def check_anchors(value):
        if isinstance(value,dict):
            if 'exact_lines' in value:
                current=lines[value['file']]
                assert [r['line'] for r in value['exact_lines']]==list(range(value['start_line'],value['end_line']+1))
                for row in value['exact_lines']:assert current[row['line']-1]==row['text']
                anchored.append((value['file'],value['start_line'],value['end_line']))
            for v in value.values():check_anchors(v)
        elif isinstance(value,list):
            for v in value:check_anchors(v)
    check_anchors(mapping)
    assert len(mapping['canonical_dungeons'])==10
    assert len(mapping['cod1_artifact_source_spaces'])==25
    assert len(mapping['cod3_npc_location_rows'])==15
    assert len(mapping['cod3_secrets_deduplicated'])==29
    assert len(mapping['cod3_scenic_anchor_rows'])==7
    assert len(mapping['cod3_world_state_scene_rows'])==10
    assert len(mapping['conflicts'])==9

    sources=json.loads((SETTLEMENTS/'sources.json').read_text())
    manual=json.loads((SETTLEMENTS/'manual-review.json').read_text())
    assert len(sources['candidates'])==len(manual['cases'])==15
    archive_hashes={}
    for row in sources['candidates']:
        source=Path(row['source_archive'])
        if str(source) not in archive_hashes:
            archive_hashes[str(source)]=hashlib.sha256(source.read_bytes()).hexdigest()
        assert archive_hashes[str(source)]==row['source_sha256']
        with ZipFile(source) as z:
            assert hashlib.sha256(z.read(row['member'])).hexdigest()==row['nbt_sha256']
    viewed=[]
    fields={'layout','proportion','facade','roof','material','circulation','terrain'}
    for row in manual['cases']:
        assert set(row['seven_observations'])==fields
        assert all(row['seven_observations'].values())
        assert row['formal_credit']==0
        for name in row['actual_viewed_images']:
            assert (SETTLEMENTS/name).is_file();viewed.append(name)
    assert len(viewed)==len(set(viewed))==30
    generated=[p.name for p in SETTLEMENTS.glob('*.png')]
    unviewed=sorted(set(generated)-set(viewed))
    assert len(generated)==43 and len(unviewed)==13

    def state_map(ident):
        rows=json.loads((SETTLEMENTS/(ident+'-states.json')).read_text())
        return {tuple(v['position']):v['state'] for v in rows}
    def role(name):
        name=re.sub(r'minecraft:(oak|spruce|jungle|acacia)_','wood_',name)
        name=re.sub(r'minecraft:(red|blue|white|yellow)_wool','cloth',name)
        return 'wall_post' if name.endswith('_wall') else name
    dedup=[]
    for a,b in [('S02','S04'),('S14','S15')]:
        x,y=state_map(a),state_map(b)
        def shell(states):return {(p,role(s['Name'])) for p,s in states.items() if p[1]>=1 and ('wood_' in role(s['Name']) or role(s['Name'])=='cloth')}
        xs,ys=shell(x),shell(y)
        roofx={(p,role(s['Name'])) for p,s in x.items() if p[1]==4}
        roofy={(p,role(s['Name'])) for p,s in y.items() if p[1]==4}
        dedup.append(dict(pair=[a,b],wood_cloth_shell=dict(left=len(xs),right=len(ys),same=len(xs&ys),union=len(xs|ys)),
                          y4=dict(left=len(roofx),right=len(roofy),same=len(roofx&roofy),union=len(roofx|roofy)),
                          decision='仅为人工整体现看去重的辅助证据，不是按哈希自动认定建筑相同'))
    assert dedup[0]['y4']['same']==61
    assert dedup[1]['wood_cloth_shell']==dict(left=70,right=70,same=70,union=70)
    (SETTLEMENTS/'dedup-evidence.json').write_text(json.dumps(dedup,ensure_ascii=False,indent=2)+'\n')

    expanded=json.loads((OUT/'scope-expansion-manual-review.json').read_text())
    expanded_source=json.loads((OUT/'scope-expansion-sources.json').read_text())
    assert expanded['distinct_old_designs_reassessed']==3 and expanded['actual_image_views']==12
    for row in expanded['cases']:
        assert set(row['seven_observations'])==fields and row['formal_new_credit']==0
        assert all(Path(n).is_file() for n in row['actual_viewed_images'])
    for row in expanded_source['candidates']:
        path=Path(row['source_archive'])
        if str(path) not in archive_hashes:archive_hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        assert archive_hashes[str(path)]==row['source_archive_sha256']
        with ZipFile(path) as z:assert hashlib.sha256(z.read(row['source_member'])).hexdigest()==row['nbt_sha256']

    registry_path=ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'
    registry=json.loads(registry_path.read_text())
    assert len(registry['entries'])==148
    assert registry['scope_status'][0]['credited_verified_complete_buildings']==148
    assert registry['scope_status'][1]['credited_verified_complete_buildings']==0
    scripts=list(OUT.glob('*.py'))+list(SETTLEMENTS.glob('*.py'))
    for p in scripts:ast.parse(p.read_text(),filename=str(p))
    report=dict(check='本批新研究与映射证据的一致性检查，不是Java/编译/游戏/功能验收',passed=True,
        source_prompt_hashes_unchanged=5,exact_anchor_records_checked=len(anchored),unique_anchor_ranges=len(set(anchored)),
        cod5_absent=True,canonical_dungeons=10,artifact_source_spaces=25,npc_locations=15,secrets=29,scenic_rows=7,world_states=10,
        local_new_template_studies=15,local_viewed_images=30,generated_but_unviewed_settlement_images=unviewed,
        prior_designs_reassessed_for_new_scope=3,expanded_scope_image_views=12,
        source_archives_verified_unchanged=len(archive_hashes),source_nbt_members_checked=18,
        research_scripts_parsed=len(scripts),formal_registry_count=148,formal_gap=852,cod6_count=0,cod6_gap=1000,
        official_registry_sha256_observed=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        formal_new_credit=0,new_architecture_may_start=False,
        runtime_validation='未实机验证；未运行Java、Gradle、编译器、游戏、客户端或服务端',
        changed_scope='仅本两个独立研究目录；未写外部提示词、主清单、主登记、生产程序、模型、贴图或共享Jar')
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('generated_but_unviewed_settlement_images',)},ensure_ascii=False))


if __name__=='__main__':main()
