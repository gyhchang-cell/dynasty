"""Primary full-method semantic review of Herschel046; one temporary control lifecycle."""
from ledger import B,O,R,record,verify
import json,hashlib,datetime
h=O/'helpers/herschel-immune/batch-046.json';sha=hashlib.sha256(h.read_bytes()).hexdigest();assert sha=='982d5cec356c652706bf764381f5915c2781ba6e9eeff4d715f40520a2457032'
d=json.loads(h.read_text());checked=[]
for row in d['rows']:
 for x in row['source_refs']:
  key,rel=x['source_key'].split('/',1);root=B/'sources'/key;raw=(root/rel).read_bytes();m=json.loads((root/'source.json').read_text());by={v['path']:v for v in m['files']}
  assert hashlib.sha256(raw).hexdigest()==x['file_sha256'];assert by[rel]['sha256']==x['file_sha256'];assert m['commit']==x['fixed_commit'];a,z=x['lines'];assert 1<=a<=z<=len(raw.decode().splitlines());assert x['url']==f'https://github.com/{m["repo"]}/blob/{m["commit"]}/{rel}#L{a}-L{z}'
  checked.append({'source_key':x['source_key'],'lines':[a,z],'file_sha256':x['file_sha256'],'url':x['url'],'credit':0})
repo='TeamTwilight/twilightforest';root=B/'sources/TeamTwilight__twilightforest';p='src/main/java/twilightforest/'
refs=[(x['source_key'].split('/',1)[1],*x['lines']) for x in d['rows'][0]['source_refs']]
for rel in [p+'entity/monster/RisingZombie.java',p+'client/renderer/entity/RisingZombieRenderer.java',p+'client/state/entity/RisingZombieRenderState.java',p+'client/model/entity/RisingZombieModel.java']:
 refs.append((rel,1,len((root/rel).read_text().splitlines())))
refs.append((p+'TwilightForestMod.java',41,97))
k='twilight-native-observer-triggered-immobile-actor-conversion-terminates-control-resistance'
record(k,repo,refs,
 '完整RisingZombie172行、renderer75/state7/model18与GraveyardFeature.place全文实际读；实际实体factory/属性、feature注册、主Mod constructor注册和client setup listener/具体renderer与layer绑定核对。真实graveyard的metadata spawner分支设置RISING_ZOMBIE类型；actor原生aiStep观察最近玩家并启动同步counter，server推进到>=130调用convertTo vanillaZombie，callback写原HP/方向。在该临时actor类型存续时isImmobile恒true、knockback/doPush/pushEntities空、ride/fluid/portal拒绝，类型替换后这些本类override不再属于继任者。同步counter同时驱动refreshDimensions/height、renderer shadow/rotations和model腿显示。',
 '一整套临时actor类型承担控制抵抗及原生转换结束生命周期1；不按七个空hook、130常量、影子或粒子拆计。与Iron corpse拒伤触发幂等唤醒并替换Boss、Vampirism永久block代理、Gorgon捕获保存或Wizardry方块还原不同：本例控制拒绝不靠可移除effect，本体可正常受其他伤害，观察触发有限存续然后普通类型继承。isInvulnerableTo只IN_WALL且不super，不可称出土期全伤免疫。native knockback空不证明setPos/直接速度写入也无效。',
 'Boss拒控灰字要绑定真实目标及其生命周期；actor替换可结束策略而不经effectRemoval，不能把旧目标缓存或粒子附给新类型。出土声/粒子是状态进展而非拒控收据，不建议引入转换玩法；普通阴阳仍无灰字要求。',
 '已全文主审上述本地文件和helper列出完整place/register/setup；Beanification外部扫描实现、继承isLookingAtMe/native convertTo内部与vanillaZombie控制未展开，不声称UUID保留/转换成功/精确LOS或130墙钟tick。首次counter写无serverguard，不能美化全权威；convertTo结果未检查，无自定义counter NBT保存。碰撞height0..130与render0..80..120不是同一边界。实际模板是否含marker/刷怪是否触发、声音及双端像素未测。CottonCandor/RockRider整类块注释本岗已全文读，排除0；本批仅1。','native_temporary_actor_control_refusal_and_type_replacement_lifetime')
(O/'HERSCHEL-046-REVIEW.json').write_text(json.dumps({'helper_file_sha256':sha,'helper_original_credit':0,'main_review_new_effective':1,'promoted_key':k,'checked_helper_ranges':checked,'provenance_boundary':'Fixed commit archive URL/archive SHA and cached source SHA/ranges verified; no tree.json for Twilight cache, no Git blob-tree claim.','main_full_rising_actor_render_state_model_place_read':True,'semantic_comparisons':['iron-corpse-refused-hit-triggers-idempotent-boss-awakening','vampirism-native-immobile-boss-vulnerability-proxy-versus-rejected-source','icefire-gorgon-native-gaze-final-admission-replacement-lifetime-type-cache','wizardry-native-block-hosted-statue-placement-denial-and-actor-restoration'],'support_exclusions':['CottonCandor and RockRider full files block-commented; already directly read, credit0.'],'production_changes':False,'game_started':False,'compile_run':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n')
s=json.loads((O/'semantic-dedup.json').read_text());s['groups'].append({'family':'batch165-temporary-actor-control-lifetime','credited_chains':[k],'rationale':'Whole observer-initiated temporary immobile actor policy until native type conversion; all empty force/ride/fluid hooks and renderer counters merged1. Not static species constants, corpse rejected-hit awakening, permanent proxy or capture/restoration.'});(O/'semantic-dedup.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');verify()
