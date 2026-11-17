"""Record the completed human source study; verify bindings, not gameplay."""
import json, hashlib
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
def get(n): return json.loads((OUT/n).read_text())
def put(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
    p=Path(p); b=p.read_bytes()
    return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

r=get('raw-source-audit.json')['candidates'][0]; d=r['nbt_decoded_original']; pal=d['palette']
mp={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
planes=get('all-original-planes.json')
reconstructed={tuple([x,p['y'],z]):s for p in planes['planes'] for z,row in enumerate(p['rows_z_ascending_x_ascending']) for x,s in enumerate(row) if s!=-1}
assert reconstructed=={tuple(b['pos']):b['state'] for b in d['blocks']}
assert len(planes['planes'])==11 and len(pal)==33 and len(mp)==243
columns=get('column-feature-context.json')
with ZipFile(r['source_archive']) as z:
    for c in columns['contexts']:
        bb=z.read(c['member'])
        assert hashlib.sha256(bb).hexdigest()==c['sha256'] and json.loads(bb)==c['json']

positions={tuple(b['pos']) for b in d['blocks'] if b.get('nbt') or any(t in pal[b['state']]['Name'] for t in ['stairs','door','carpet','lantern','cauldron'])}
positions.update((x,y,z) for x in [4,5,6] for y in [3,4,5,9,10] for z in [2,3] if (x,y,z) in mp)
positions.update([(1,1,1),(1,2,1),(1,4,1),(1,5,1),(0,5,2),(1,6,2),(3,6,2),(3,8,5)])
queried=[{'pos':list(p),'state':mp[p]} for p in sorted(positions)]
put('critical-original-states.json',{'states':queried,'omitted_not_air':[[0,0,0],[8,0,5]],'original_block_entities':[{'pos':b['pos'],'nbt':b['nbt']} for b in d['blocks'] if b.get('nbt')], 'native_collision_or_reach_verified':False})
assert all(tuple(p) not in mp for p in [[0,0,0],[8,0,5]])
put('complete-reading-integrity.json',{'original_planes':bind(OUT/'all-original-planes.json'),'palette_entries_actually_read':33,'original_planes_actually_read':11,'lossless_original_index_reconstruction':True,'original_stored_positions':243,'omitted_positions_not_air':351,'original_block_entities_actually_read':7,'original_entities':d['entities'],'current_generated_png':9,'current_png_actually_viewed':9,'unviewed_current_png':0,'extra_column_contexts_verified_against_fixed_archive':5,'column_context':bind(OUT/'column-feature-context.json'),'critical_states':bind(OUT/'critical-original-states.json'),'y11_panel':'renderer padding beyond height 11; not original twelfth plane','native_acceptance':False})

obs={
 'layout':'低西侧湿作业坪两满水缸，旁边双宽三步直升外阶，经西双扇门直接进抬高的微型封闭储藏室；湿坪在use1，储室floor3/use4，真正以高差分离湿/干。无同层工住L翼、露台折入冷室、内梯高亭、热炉或床。完整9图/33palette/11原层/7BE/entities[]读完，作为相关湿工与干储关系最多1待独立判定，不把它叫完整铁匠铺。',
 'proportion':'9×11×6/DV3337，594声明243原存=174非air69显式air，351省略不能补air。干储内只x5/6,z2/3四格，其中箱、两地毯及落地灯，绝非宽敞双层车间。y5..9内部高空腔无新增楼板，11高包含高屋盖；y10配图右y11是越界补白，不是原第12层。',
 'facade':'darkoakplanks36、strippeddarkoaklog26、darkoakwood36构抬高窄木房，西门x4,z2/3 facingeast不称东门；四门上下状态是一个双扇入口。西阶两侧x1,z1/4石墙脚y1、木栏柱y2..4、石墙头y5支低入口盖。上干室无玻璃/可独立外廊，围护不直接证明雨避/NPC藏身功能。',
 'roof':'西入口盖y5 x0,z1..4为TOP半块，y6 x1/2为BOTTOM、x3为TOP木半块；与高干储屋体的y8宽darkoakwood框、y9收进圈、y10四格木帽组成低入口/高主体。高房没有内梯、阁楼板或第二使用层。通用分类全格图不代表原贴图、半块碰撞或材质都是石头；不将高屋盖另算塔/建筑。',
 'materials':'低缸2,1,4及3,1,4均water_cauldron level3，下面为dirt，不是熔岩淬火系统。6,4,2 west/single/dry箱原tanneryloot及seed2868045043683423252；上6,5,2显式air，前5,4,2 whitecarpet不是air；5,4,3是hangingfalse灵魂灯，6,4,3红地毯。另两悬灯2,5,1及3,7,5，后者在外后边下方，不编造火炉烟构。无炉/高炉/砧/锻造台/砂轮/床/梯，箱loot非本项目奖励/付款证明。',
 'circulation':'入口socket0,1,2 west_up/aligned/empty/finalair。z2/3两列BOTTOM east踏步依次x1y1→x2y2→x3y3；x2y1、x3y2 TOP west为倒置支托而非另四步。接x4..6,y3,z2/3木地板，经4,4/5,2 left与4,4/5,3 right两扇east/closed门入小室。薄地毯/落地灯/箱占四格，不能写全空室内或已验NPC寻路、门碰撞、箱盖开启/箱前可达；仅原状态空间阅读。低湿坪与上干储无另一个房间或后接必需房翼。',
 'terrain_and_dedup':'5柱socket为1,0,1接cobblewall及4/7,2,1/4接darkoakfence，up_west/rollable/finalstructure_void，不是5栋屋或村民。实际柱feature向下、height63、allowed replaceabletag offset[0,1,0]；updater disk radius0/halfheight4仅更新邻水水浸状态，未执行生成/承托。当前swamp_vanilla house权2 single_pool_element rigid，实际street_swamp_vanilla规则在水旁改dirt/path等，不套中心houseprocessor；swamp单biome/root terrain none、size6/WORLD_SURFACE_WG只语境。对061F03抬台冷工同高室、075F01敞热工小棚、111同层对廊、120同高L工住湿凹坪、125内梯高亭逐项比较：本件低外湿坪旁直阶直接接上微型干储的整屋关系不同，max1提案，正式0；用途相关性和家族新颖性仍交独立判定，不凭文件名/木色/高度凑1000。'
}
comparison_notes={61:'旧侧外两步到南开敞砂轮/工具箱栏台再折入北锻造台冷室，两区同高use2；本件水缸留use1且直阶直接上use4微干储，无同高露天加工栏台。共同抬高小屋不能独自证明相同或不同；提案依据低湿/上干及直通关系，仍由Main判定。',75:'旧敞前低盖水/魂营火/高炉棚，无封闭干储；本件无热工，仅低两缸/升高小储间，不把职业差异单独算设计。',111:'旧中室及相对南北 coveredporches都同层，西入口三门，无垂直湿干分离。沿用四根竹柱各y1..3共12原状态勘误，不使用旧y1..2文字。',120:'旧swamp（非swamp_vanilla）大L工住：床/加工/三水缸凹坪同高use5，外阶先到NW廊；本件两缸在use1而干储use4，无床/L住翼，直阶直接进箱室。旧源池selected空/拼错slap不套当前有效池。',125:'旧swamp fletcher为抬高两分区、内梯上高亭且下射靶，空间组织不同；本件单微干室外直阶、低湿坪，无内梯/高亭/连续第三层。旧命名空间selected空不套当前。'}
comparisons=[]
for c,n in zip(get('pre-render-spatial-comparison.json')['comparisons'],[61,75,111,120,125]):
    j=json.loads(Path(c['binding']['path']).read_text()); case=next(x for x in j['cases'] if x['id']==c['case'])
    saved=case.get('observations',case.get('screening_observations'))
    assert saved
    comparisons.append({'binding':c['binding'],'case':c['case'],'complete_saved_observations_actually_read':saved,'current_complete_comparison':comparison_notes[n],'old_images_not_revisited':True})
put('complete-study-review.json',{'case':'F01','scope':'related wet-work/dry-storage complete building, not hot smithy','observations':obs,'comparisons':comparisons,'credit_proposal_maximum':1,'formal_credit_added':0,'independent_admission':False,'actual_images_viewed':['whole','cutaway','y0','y2','y4','y6','y8','y10','vertical']})
ctx=get('source-context.json')['candidates'][0]
pool=next(x['json'] for x in ctx['contexts'] if x['member'].endswith('/houses.json'))
root=next(x['json'] for x in ctx['contexts'] if '/worldgen/structure/' in x['member'])
rv={'id':'F01','source_stats':[3337,594,243,174,69,33,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_absent_positions':[[0,0,0],[8,0,5]],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']} for b in d['blocks'] if b.get('nbt')],'selected':[e for e in pool['elements'] if e.get('element',{}).get('location')==ctx['location']],'root_fields':root,'viewed':['whole','cutaway','y0','y2','y4','y6','y8','y10','vertical'],'observations':obs,'written_comparisons':comparisons,'full_study':True,'credit_proposal_maximum':1,'context_reading':'八主context和另外五柱feature/tag原JSON实际读；house为single/rigid权2街道处理器，中心house规则仅语境；柱向下height63与邻水updater不冒充世界承托验收。原版tanneryloot仅单Jar missing，不宣称全环境缺。元数据Trek B0.6.1 MIT作者hotsuop/Hugger/ALDgamer仅来源记录。'}
cfg={'batch':150,'history_pairs':get('pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'ONE_COMPLETE_RELATED_WET_DRY_WORKSHOP_STUDY_PENDING_MAXIMUM_ONE','scope':'COD3 NPC01 related complete workshop spatial research; no production','cases':[rv],'image_counts':[9,9,0],'pre_render_spatial_comparison':bind(OUT/'pre-render-spatial-comparison.json'),'complete_study':bind(OUT/'complete-study-review.json'),'complete_reading':bind(OUT/'complete-reading-integrity.json'),'limits':'完整原图9/9、33palette、11原层、7BE/entities[]已读；重建243存与351省略，额外5柱JSON已核原Jar。微型湿/干分离相关建筑max1提案未独立通过/正式0，非完整热工铁匠铺或成品。旧141142 first144只carry0，不重验。无Java/游戏/贴图/生产/主清单。','next':'继续151固定本地直接相关完整作坊，先做家族差异判断，再全原图及全原层阅读，1000不足不制作。','handoff':'150 Trek swamp_vanilla tannery1完整研究1、最多1待Main独立判定、正式0：低use1双湿缸旁双宽三步直阶→西双门→上floor3/use4微型干储室，高空腔非二层。9PNG全读/33palette/11层/7BE/entities[]，594声明243存174非air69air/351省略，八主context+五柱feature/tag已读。061/075/111/120/125整屋关系逐项比较，家族新颖性与用途适配未自验通过。Main原141142first144只carry0。没有Java、游戏实例、生产、声音亮度或主清单操作。'}
put('review-config.json',cfg)
ad=json.loads((OUT.parent/'research-20261104-smithy-149/latest-independent-admissions.json').read_text())
ad['all_prior_acceptances_carry_only_no_current_increment_150']=True
put('latest-independent-admissions.json',ad)
sealer=(OUT.parent/'research-20261104-smithy-148/seal_screening.py').read_text()
sealer=sealer.replace('旧其他pending不取消；COD4仍153差847。','141F01/142已first144独立完成且仅carry0；当前150仅max1待独立判定，COD4仍153差847。')
(OUT/'seal_screening.py').write_text(sealer)
print(json.dumps({'queried_positions':len(queried),'all_images_read':9,'complete':1,'maximum_proposal':1,'formal_credit':0},ensure_ascii=False))
