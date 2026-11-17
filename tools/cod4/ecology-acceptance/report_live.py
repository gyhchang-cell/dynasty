"""Human-readable live evidence receipt; partial results never become full ecology PASS."""
from pathlib import Path
import json,collections,datetime
R=Path(__file__).resolve().parents[3]; D=R/'docs/cod4/audit-20261022/ecology-acceptance'; L=D/'live-run1'
if (D/'static-handoff.json').exists():
 print('Static handoff preserved; report_live will not restore stale RUNNING status.');raise SystemExit(0)
s=json.loads((L/'summary.json').read_text());events=[]
for n,line in enumerate((L/'events.jsonl').read_text().splitlines(),1):
 try:e=json.loads(line)
 except json.JSONDecodeError:continue
 e['line']=n;events.append(e)
source=json.loads((D/'source-audit.json').read_text()); species={x['id'] for x in source['species']}
born={e['uuid']:e for e in events if e['kind']=='confirmed_natural_spawn' and not e.get('loaded_from_disk',True)}
death=[e for e in events if e['kind']=='natural_entity_death_drops' and e.get('actual_player_damage') and e['uuid'] in born]
missing=[m['id'] for m in s['material_proofs'] if not any(p['pickup_exact_uuid_verified'] for p in m['proofs'])]
rows=['自然生态专项原生跟进（进行中证据，不等于整条COD4完成）',f"生成时间UTC：{datetime.datetime.now(datetime.timezone.utc).isoformat()}",f"固定种子20261023；正常噪声Overworld；世界累计实际tick={s['latest_day_time']}（从0连续保存，无时间/天气改写）。",'原normal-run2的19/30位置、2自然结构证据完整保留，未覆盖。',f"有效原生NATURAL位置={s['native_valid_position_species']}/30；精确ItemEntity UUID拾取材料={s['material_pickup_exact_uuid_verified']}/10。",f"实际观察到自然出生的小怪种类={len({e['species'].split(':')[-1] for e in born.values()}&species)}/30；位置回调通过不冒充30种均实际出生。",'未完成材料：'+(', '.join(missing) if missing else '无（仅材料掉落/拾取专项）'),'尚未观察实际NATURAL出生的原物种：'+', '.join(s['remaining_actual_natural_birth_species']),'','材料成功证据：']
for m in s['material_proofs']:
 for p in m['proofs']:
  if not p['pickup_exact_uuid_verified']:continue
  rows.append(f"{m['id']}: {p['species']}，biome={p['spawn_biome']}，自然出生={p['spawn_pos']}，实体UUID={p['natural_mob_uuid']}；events.jsonl出生行{p['natural_spawn_event_line']}→死亡行{p['death_event_line']}→拾取行{p['pickup_event_lines']}，掉落ItemEntity UUID={p['actual_drop_entity_uuid']}；死亡tick={p['death_game_tick']}、拾取tick={p['pickup_game_ticks']}、间隔世界tick={p['pickup_delay_world_ticks']}（区块卸载期间物品不计实体年龄）。")
rows+=['','目标来源的实际玩家击杀尝试（包括空掉落，原55%概率不改写）：']
sources={x['species'] for m in source['materials'] for x in m['existing_entity_loot_sources']}
attempts=collections.Counter(e['species'] for e in death if e['species'].split(':')[-1] in sources)
rows += [f'{k}: {v}' for k,v in sorted(attempts.items())]
rows+=['','夹具边界：真实自动化网络客户端EcologyQA，fixture提供既有未附魔鸳鸯钺（早期阶段为下界合金剑）、飞行/无敌/食物、传送观察/攻击/拾取点；不是完整生存资源路线，不是真人双人。所有计入来源均先记录NATURAL FinalizeSpawn后实际入世、非磁盘重载；phase3以后另记录NaturalSpawner栈。死亡源确为该ServerPlayer；同一ItemEntity UUID及同一玩家才计精确拾取。','原生竞争怪同样通过客户端普通攻击清理，未改mob cap、AI、刷怪权重、掉落概率，未spawn蛋或直接创建QA怪物，未手放建筑piece、改biome、改时间天气。环境死亡不算玩家材料证据。','QA阶段历史：phase1/2普通剑；phase3既有鸳鸯钺与精确拾取UUID；phase4归还观察点；phase5即时FULL区块高度查询修正；phase6正常攻击包括占同一monster cap的模组竞争怪；phase7在自然地面上方100格观察并记录原生天气及类别数量；phase8客户端通过原生ClickType.THROW丢出原版杂物腾背包，保留全部目标材料；仅尝试拾取仍存在的原UUID掉落实体，不重建或补发。旧失败/错误观察点事件、空roll均保留。','完整场景缺口继续保留：主世界荒村、完整义庄、地表墓园；地府枉死城存在实体鬼市生产链，后续run6找到候选但原生FULL招牌放置异常，30小怪另被现有地府维度/biome入口拒绝，详见../cross-dimension-audit.txt。未建新建筑，未改正式Java/资产/TODO，Kepler旧档进度修复未干预。']
(L/'report.txt').write_text('\n'.join(rows)+'\n')
(D/'live-progress.json').write_text(json.dumps({'status':'RUNNING' if not (L/'coordinator-complete.txt').exists() else 'SPECIALIZED_MATERIAL_POSITION_COMPLETE_SCENES_STILL_OPEN','baseline_preserved':'normal-run2 19/30 +2 structures','positions':s['native_valid_position_species'],'material_exact_pickups':s['material_pickup_exact_uuid_verified'],'remaining_materials':missing,'actual_natural_birth_species':s['actual_naturally_born_secondary_species'],'remaining_actual_natural_birth_species':s['remaining_actual_natural_birth_species'],'actual_world_ticks':s['latest_day_time'],'report':'live-run1/report.txt','cross_dimension_report':'cross-dimension-audit.txt','full_survival_or_all_original_scenes_pass':False},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'positions':s['native_valid_position_species'],'exact_material_pickups':s['material_pickup_exact_uuid_verified'],'remaining':missing},ensure_ascii=False))

# Keep the old zero-player result as an immutable named historical receipt; top-level report is current.
history=D/'normal-run2-historical-report.txt'
if not history.exists(): history.write_bytes((D/'report.txt').read_bytes())
header=['COD4-1 / COD4-11 自然生态当前入口（仍在运行，完整场景待证明）',f"更新时间UTC：{datetime.datetime.now(datetime.timezone.utc).isoformat()}",f"当前独立live：30种分母，有效NATURAL位置{s['native_valid_position_species']}/30；实际自然刷出{len({e['species'].split(':')[-1] for e in born.values()}&species)}/30；自然玩家击杀目标掉落{s['natural_material_death_drop_verified']}/10；同一ItemEntity UUID拾取{s['material_pickup_exact_uuid_verified']}/10。",'待补拾取：'+', '.join(missing),'当前详情：live-run1/report.txt、summary.json、material-results.tsv、events.jsonl。','历史baseline：normal-run2-historical-report.txt，19/30位置与2自然结构；其中0/10材料仅指该次无玩家的旧阶段，不是当前live结果。','跨维度入口及枉死城有限搜索：cross-dimension-audit.txt / .json；地府有既有鬼市代码链；后续run6原生候选FULL生成异常，详handoff-urgent-native-failure.json，不得据旧有限搜索断言不存在；30小怪的现有地府维度入口和biome条件拒绝。','主世界荒村、完整义庄、地表墓园自然现场仍待证明。未改正式Java、资产或TODO；不称完整生存路线或真人双人。']
(D/'report.txt').write_text('\n'.join(header)+'\n')

(D/'handoff-progress.txt').write_text('\n'.join(header)+'\n\n'+(D/'cross-dimension-audit.txt').read_text()+'\n分工：Hegel负责真实双客户端30种交互，Rawls不重复C2S夹具。主协调TODO保持原状；仅提供专项证据，不自动宣告COD4整条通过。\n')
