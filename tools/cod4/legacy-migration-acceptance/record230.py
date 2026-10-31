import json
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()));ix={r['candidate_id']:r for r in cs}
def s(i):return [r['candidate_id'] for r in cs if r['private_file']==ix[i]['private_file'] and r['candidate_id']!=i]
a='622d16311a60cc2ffe6d';b='50583cd3d3ea0c39b4ec'
moose=accepted(a,'alexsmobs-moose-antler-two-phase-durable-harvest-cycle','完整EntityMoose全文，旧AntlerTime缺省guard→两阶段脱角/再生→掉落与实际攻击能力消费者。','AntlerTime int、Antlered bool、JostlingCooldown int；SnowPerm/Snowy同owner支持。构造初始7..9天时间和默认有角。','contains AntlerTime才覆盖构造值；Antlered却直接getBoolean missingfalse。tick>0递减，到0有角→setfalse并spawn角、定2..4天；无角→settrue定7..9天。','计时与是否已兑现receipt组合决定收益，缺省guard不是所有字段一致；负timer不递减也不等0可停循环，未clamp。实际攻击有角7.5无角3、对Wolf/Orca2，canJostleWith还要有角与冷却0。临时jostlerUUID/jostleTimer未存，不能把它们当永久任务。与Grizzly直线产毛不同两阶段receipt owner、不同实物与攻击状态，不按共享Snow逻辑多计。','本类timer/drop段无显式server side guard；spawnAtLocation原生边界未全读，不称双端都真实掉实体。雪交互纯共享clone支持0。全文静态、未运行，不移植随机死亡惩罚或临时AI状态到Clone。',s(a))
toucan=accepted(b,'alexsmobs-toucan-paid-sapling-entitlement-repeat-planting-restoration','补读整个EntityToucan全文，实际付果→消费产生SaplingState/永久Enchanted→AIPlantTrees真实放块，而非仅变体恢复。','SaplingState blockstate compound、GoldenTime int、Enchanted bool；Variant显示支持，nativeHandItems上层保实际待吃果。','reader only compound readBlockState，air变null；setSaplingState始终覆盖可清旧值；gold0缺省/enchfalse。正gold每server tick减，-1永久；Enchanted还能单独令gold有效。','mobInteract copy1/usePlayerItem，吃>10tick heal返余物，金食12000或附魔金食-1+Enchanted，再getSaplingFor解析并设树苗后shrink1。真实种树近距plantTime>60且canSurvive/replaceable时setBlockAndUpdate，非enchanted清树苗、enchanted保留多次种；gold改encircle/cooldown速度，非纯外观。world放置返回bool未核即清普通资格，可能失败丢receipt，未runtime。SaplingTime accessor/条件存在但本类从不set，writer也不存，不能虚构完成的计时机制。此完整已付费种植owner独立1，普通/金/附魔/别名配置同链不拆。','配置fruit→sapling static map只是支持不计；未知block读air变null无原未知载荷旁存。AI目标位置/本次plantTime未存，重载重新找位可合理重建；不等于Player Clone。原生setBlock事件/网络authority/手持完整解析未全审，固定官方源码静态未运行、未改原资产正式源。',s(b))
toucan['reassessment']={'prior_status':'pending','support_batch':230,'reason':'完整实际付费种植消费者使状态有独立游戏收益，并非变体或纯显示；来源完整但未运行。'}
for f in (O/'reviews').glob('*.json'):
 rows=json.loads(f.read_text());changed=False
 for n,r in enumerate(rows):
  if r['candidate_id']==b:rows[n]=toucan;changed=True
 if changed:f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
record(230,[moose],[ix[b]['private_file']])
(O/'semantic-reassessment-20261029-005.json').write_text(json.dumps(dict(candidate_id=b,prior_status='pending',credit_change=1,support_batch=230,regeneration='Rerun record230 after regenerating earlier coordinator003 import.',runtime_validation='not_run'),ensure_ascii=False,indent=2)+'\n')
