"""Rebuild the corrected 100-image selection, failing on cross-task duplicates.

Manual visual observations live in additional-observations.json. This script does
not mark unseen images as reviewed; the additional sheets were inspected first.
"""
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[3]
PREVIOUS = ['silverfall-v1','ancient-array-v1','crystal-canopy-v2','sun-crow-v2',
            'ice-bloom-v2','xuanwu-v2','azure-dragon-v2']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

previous_hashes=set();manifests=[]
for name in PREVIOUS:
    path=ROOT/f'docs/art/cod3-{name}/references.json'
    content=json.loads(path.read_text());rows=content if isinstance(content,list) else content['references']
    previous_hashes.update(r['sha256'] for r in rows)
    manifests.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'references':len(rows)})
old=json.loads((P/'selected-before-cross-task-dedup.json').read_text())
old_hashes={r['sha256'] for r in old}
removed=[r for r in old if r['sha256'] in previous_hashes]
kept=[r for r in old if r['sha256'] not in previous_hashes]
assert len(removed)==53 and len(kept)==47
notes=json.loads((P/'additional-observations.json').read_text())
candidates=json.loads((P/'candidates.json').read_text())
added=[]
for r in candidates:
    if str(r['number']) not in notes:continue
    assert r['number']>=161 and r['number']!=197
    assert r['sha256'] not in previous_hashes|old_hashes
    added.append(dict(r,review_level='viewed_contact_sheet_image',
        review_sheet=f"additional-{(r['number']-161)//15+1}.jpg",
        observation_zh=notes[str(r['number'])],
        used_as='environment/form comparison; not imported assets',
        new_vs_prior_fire_tree_selection=True))
assert len(added)==len(notes)==53
selected=sorted(kept+added,key=lambda r:r['number'])
for i,r in enumerate(selected,1):
    assert sha(P/r['file'])==r['sha256']
    r['reviewNumber']=i
    r['cross_task_overlap_count']=0
    r['cross_task_dedup_audit']='cross-task-dedup.json'
    r.setdefault('new_vs_prior_fire_tree_selection',False)
assert len({r['sha256'] for r in selected})==100
assert len({r['url'] for r in selected})==100
assert not previous_hashes&{r['sha256'] for r in selected}
projects=sorted({r['slug'] for r in selected})
audit={'status':'PASS','comparison':'image-file SHA-256; author gallery thumbnails',
    'prior_manifests':manifests,'prior_record_count':sum(r['references'] for r in manifests),
    'prior_unique_sha256_count':len(previous_hashes),'previous_fire_tree_selection':100,
    'original_cross_task_overlaps':53,'removed_ids':[r['number'] for r in removed],
    'removed_sha256':[r['sha256'] for r in removed],'retained':47,
    'newly_viewed_candidates_this_revision':74,'failed_or_unviewed_candidate_ids':[197],
    'newly_selected':53,'new_ids':[r['number'] for r in added],
    'new_sha256':[r['sha256'] for r in added],'new_vs_old_fire_tree_overlap':0,
    'final_selected':100,'final_unique_sha256':100,'final_cross_task_overlap':0,
    'project_count':len(projects),'projects':projects,
    'limits_zh':'100张作者环境图，不是100个独立项目或100个已核实世界坐标。SHA去重验证文件内容；另人工排除明显同景换角度候选。'}
dump(P/'cross-task-dedup.json',audit);dump(P/'selected-100.json',selected)
summary={'candidate_downloaded_initially':235,'candidate_images_viewed':234,
    'candidate_images_viewed_before_revision':160,'new_images_viewed_this_revision':74,
    'selected_images_viewed':100,'unique_projects':len(projects),
    'reading_level':'作者官方画廊缩略图；只统计实际看图，不将页面文字计作图像。',
    'page_text_only_counted_as_images':0,'not_viewed':[197],
    'replacement_count':53,'cross_task_overlap_count':0,'cross_task_audit':'cross-task-dedup.json',
    'selected_local_images_retained':100,'excluded_additional_ids':[n for n in range(161,236) if str(n) not in notes]}
dump(P/'review-status.json',summary)
lines=['# 火树环境参考：跨前七项去重后的100张图','',
       f'最终100张、{len(projects)}个项目；前七项700条记录SHA交集为0。本轮新看74张候选，替换53张重合项，保留47张。',
       '',audit['limits_zh'],'',
       '旧版漏做跨任务去重；旧名单仅保留在 selected-before-cross-task-dedup.json 作为修订历史，不计入当前100张。',
       '新增001批实际看图证据为 additional-1.jpg 至 additional-5.jpg；编号197获取失败且未查看。明显同景角度重复、无关或过暗候选未入选。',
       '所有图片只用于形式与环境研究，没有引入地图、模型或贴图；建筑NBT本轮保留。','']
for r in selected:
    lines += [f"{r['reviewNumber']:03}. 候选{r['number']:03} [{r['project']} / {r.get('title') or 'gallery image'}]({r['page']}) — [作者图]({r['url']})。{r['observation_zh']} 跨任务SHA重合：0。",'']
(P/'REFERENCES.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:audit[k] for k in ['retained','newly_selected','final_selected','final_cross_task_overlap','project_count']},ensure_ascii=False))
