"""Record small-temple relevance hold, author selection and same-shell variant."""
from collections import Counter
import hashlib
import importlib.util
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
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def fields(v,target,p='$'):
    if isinstance(v,dict):
        for k,x in v.items():yield from fields(x,target,p+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):yield from fields(x,target,p+f'[{i}]')
    elif v==target:yield p
def main():
    src=get(OUT/'sources.json');resources=[];roles=[];cache={}
    with ZipFile(src['source_archives'][0]['path']) as z:
        for c in src['candidates']:
            target=c['member'].split('/')[1]+':'+c['member'].split('/structures/')[1][:-4]
            direct=[]
            for r in c['pool_references']:
                hits=list(fields(r['data'],target));selects=any(x.endswith('.location') for x in hits)
                roles.append(dict(candidate=c['id'],member=r['member'],sha256=sha(z.read(r['member'])),matching_fields=hits,directly_selects_template=selects))
                if selects:direct.append(r)
            c['pool_references']=direct
            d=read(z.read(c['member']));pal=d.get('palette') or d['palettes'][0]
            cache[c['id']]={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
        for name in ['mossy_temple','frostbitten_temple']:
            for kind in ['worldgen/structure/','worldgen/template_pool/','tags/worldgen/biome/has_structure/']:
                n='data/legendary_monsters/'+kind+name+('_biomes' if kind.startswith('tags/') else '')+'.json'
                raw=z.read(n);resources.append(dict(member=n,sha256=sha(raw),data=json.loads(raw)))
        manifest=z.read('META-INF/mods.toml')
    src.update(new_source_templates=3,previous_source_template_rereads=0);dump('sources.json',src)
    a,b=cache['F02'],cache['F03'];changes=[dict(position=list(p),left=a.get(p),right=b.get(p)) for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
    preserved_names={'minecraft:smooth_quartz_stairs','minecraft:smooth_quartz_slab','minecraft:diorite_wall','minecraft:lantern'}
    shell_a={p:s for p,s in a.items() if s['Name'] in preserved_names};shell_b={p:s for p,s in b.items() if s['Name'] in preserved_names}
    dump('author-and-family-evidence.json',dict(author_resources=resources,selection_roles=roles,
        manifest_sha256=sha(manifest),manifest_text=manifest.decode(),publisher_url_not_present_in_manifest=True,
        pair=['041-F02','041-F03'],changed_raw_states=len(changes),changes=changes,
        preserved_shell_names=sorted(preserved_names),preserved_shell_cells=len(shell_a),shell_states_identical=shell_a==shell_b,
        semantic_family_decision='One low central hall with four corner wall/column groups and stepped ice/snow roof; ice patches and floor/snow changes do not form a second building.',
        no_exact_json_selector_for_F03_claims_only_archive_search=True,native_placement_verified=False))
    observations=[dict(
      layout='完整低矮近方形主体，中心大室、四向外凸门廊及周边厚墙/突出支撑；单模板包含地面、四周围护和顶盖，不缺另半主体。当前只证实Boss所在遗迹室，未找到墓位、遗体安置或祭祀功能证据，不能因temple名称计入义庄/墓园。',
      proportion='保存23×11×21，较宽低的中心空间，屋盖低于平面长边。没有将11格高、两条饰带或四个凸出体解释为多层/多座。',
      facade='两条水平石质饰带穿过角部和外凸廊体；厚墙之间有小开口，角部体量与廊体交错。它不自动等同于原义庄或真实中国祠堂。',
      roof='平厚顶盖被苔藓和植被占据，边缘保留矮框与不规则破损；图中有屋面覆盖，不把绿色植被空隙补成已知天井。',
      materials='stone_bricks533、cobblestone256、stone_brick_stairs221、moss_block186、stone_brick_slab147、chiseled_stone_bricks109等。只借鉴石壳与植被边界的读法，分类色图不证明原生材质、明暗或碰撞。',
      circulation='普通门/梯0，低层切面有四向开口和单一中心空间，实际门洞形状与通行未运行验收。原实体overgrown_colossus1只，不是祭祀人员或额外建筑。',
      terrain='薄地脚和外围土石同模板，作者地表heightmap/beard_thin配置直接选择本体；尚未验证随机坡地入口和土台相接。完整主体与目标用途相关性分开，当前信用0。'),dict(
      layout='四角墙/柱组围住单一中心大空间，四向中部开敞，连续低檐和收分顶盖属于一座完整小屋；不是四座亭子或冰平台组件。作者Boss用途明确，义庄/墓园及村落祭祀功能未证，保持适用性待查。',
      proportion='保存21×14×21，低层宽跨中心室，上部收分冰雪屋盖；14格保存高度不等于14格净室高，不跨记到守备单塔。',
      facade='四面中部开口与角部短墙、立柱交替，连续低檐在角部转折；这是开口组织观察，不把雪色或冰色当作独立设计依据。',
      roof='多级冰雪收分屋盖带水平外挑檐和顶端短起伏；整体不是四个分离屋顶，屋盖和室内空间关系可读。',
      materials='snow_block427、smooth_quartz_slab179、blue_ice148、smooth_quartz_stairs126、packed_ice124、powder_snow80、diorite_wall40等；粉雪原状态未替换，不推定其安全或碰撞。',
      circulation='普通门/梯0，四向开口通向中心，冰与粉雪的原生接触效果未测。frostbitten_golem1只是原实体，不证明宗教仪式；没有以Boss名称替代用途证据。',
      terrain='底层薄雪/冰地面和四角落柱同一模板，未见外部必须补齐的结构接口；地表投射配置不是实机支撑验收。邻近积雪变化不能建立新建筑身份。'),dict(
      layout='与F02同一中心大室、四角墙柱和四面中开口；内部多了局部冰块、底层覆雪变化，没有新的院落、附室或通路组织，按同设计家族不另计。',
      proportion='同为21×14×21，主体跨度和屋盖层级不变，边缘部分积雪/地面差异不当成规模创新。',
      facade='实看整体与F02四角墙柱、檐口及洞口一致；部分底部露出和覆雪变化不形成第二套立面设计。',
      roof='顶盖轮廓与F02相同，原石英楼梯/半砖/墙柱/灯笼位置状态逐项比较；不是换一张图就增加一座。',
      materials='仍用雪、冰和石英主体；雪427→370、蓝冰148→156、浮冰124→133、粉雪80→112，并有15土块。差值保留，不归纳成纯换色或完全字节相同。',
      circulation='中心增加局部冰状态可能改变通行，未实机证明；原普通门/梯仍0，frostbitten_golem1只。语义家族合并不表示碰撞或玩法完全等同。',
      terrain='底边与地面覆雪/泥土状态有差异，未找到此变体的精确JSON选择，不能从缺少选择推断资产无用或已废弃；不组装、不替代F02作者放置证明。')]
    entries=[]
    for c,obs,names in zip(src['candidates'],observations,[['F01-whole.png','F01-details.png'],['F02-whole.png','F02-details.png'],['F03-whole.png']]):
        entries.append(dict(id='041-'+c['id'],source_candidate_id=c['id'],source_evidence=evidence(OUT/'sources.json'),observations=obs,
            template_body_boundary_confirmed=True,scope='COD4-1/11/13 architecture',credit=0,
            decision='SAME_FAMILY_VARIANT_NO_ADDITIONAL_CREDIT' if c['id']=='F03' else 'HOLD_FUNERARY_OR_VILLAGE_RITUAL_RELEVANCE',
            native_acceptance=False,independent_human_review=False,actual_images_viewed=[evidence(OUT/n) for n in names]))
    dump('manual-review.json',dict(batch=41,date='2026-11-03',new_source_templates=3,actual_images_viewed=5,independent_references_added=0,
        entries=entries,generated_not_claimed_viewed=['F01-plan.png','F01-vertical.png','F02-plan.png','F02-vertical.png','F03-plan.png','F03-vertical.png','F03-details.png'],production_changes=0,checklist_deletions=0))
    coord=OUT.parents[1]/'cod4/audit-20261022/coordinator-building-036-boundary-review-20261103.json'
    assert evidence(coord)['sha256']=='57e4ad311f42621fa79176739c1c36c43eed954bf99162f056ae5e8756e772af'
    dump('scope-status.json',dict(funerary=dict(baseline=evidence(BASE/'continuation-20261022/references/full-buildings.json'),formal_baseline=148,
        batch_proposed_credit=0,formal_register_written=False,remaining_formal=852,production_allowed=False),
        guard=dict(prior_local_observation_scope=evidence(BASE/'research-20261103-dungeons-040/scoped-reference-update.json'),
            historical_local_observation_counts=[9,10,1],historical_local_counts_are_not_coordinator_formal_counts=True,
            coordinator_review=evidence(coord),reference_036_F01_formal_credit=0,reference_036_F01_layout_observation_retained=True,
            original_scope_definition_changed=False,flag_cropped=False,formal_total_not_recomputed=True,new_credit=0),
        new_scope_definitions=False,other_scope_credit_added=0))
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=41,status='FUNERARY_RELEVANCE_REVIEW_PENDING_INTEGRITY',
        previous_receipt=evidence(BASE/'research-20261103-dungeons-040/RECEIPT.json'),
        formal_funerary_baseline=148,new_proposals=0,production_allowed=False,
        next='优先未读的明确埋葬场地，实看完整边界和墓葬动线；两份冰雪遗迹按一设计家族，Boss室不靠temple名称凑义庄参考。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    print('Recorded 3 source templates / 5 images,0 credit, explicit036 formal hold and one ice-temple family.')

if __name__=='__main__':main()
