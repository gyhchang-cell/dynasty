"""Primary review of 007: observed complete critical methods; support is never credit."""
from ledger import B,O,record,verify
import json,hashlib
D=O/'helpers/herschel-immune';b=json.loads((D/'batch-007.json').read_text());m={s['repo'].replace('/','__')+'/'+s['path']:s for s in json.loads((D/'source-manifest-007.json').read_text())['sources']}
ir='src/main/java/io/redspace/ironsspellbooks/';ar='src/main/java/com/hollingsworth/arsnouveau/';se='src/main/java/net/spell_engine/'
reasons={1:'计1：原生长施法对指定伤害拒绝打断；毒伤一次标记、来源tag、真装备护符是一处最终决策，非3信用。补读实际被调Utils单参数重载442–444：只CONTINUOUS传triggerCooldown=true；LONG此入口false，不能把未被调boolean重载当真实入口。时间戳零/负差及short-circuit残留限制保留。',2:'计1：已读EntityMixin全文件含原生setRemainingFireTicks HEAD/cancellable注解，正时长拒写与clearFire，不是火伤免疫；普通玩家没有Boss灰字要求。Soaked未覆写周期判定，不宣称仅applyEffectTick存在就周期清火。',3:'计1：实际SOAKED tag增删服务端生产与旁观客户端有损副本策略；补读实际Entity重载117–119再进chunk tracking，不靠BlockPos重载猜路由。只读结论，不能证明两TCP画面一致。',4:'计1：原生战斗触发消费STASH并延迟按类型重查替换的独立生命周期位点；与004触发cap/roll共用evaluateTrigger但不是重计同门。TRANSFER无arrow仍可能消费，PERFORM忽略bool；delayed旧newAmplifier可覆盖新代effect，仅静态风险。没有具体外部STASH内容装载/实机证据。',5:'计1：minimum_distance不足的明确fizzle生产点；同performImpact方法其他已记状态/伤害/area门0额外。补读findSolidBelow242–269和findSolidBlockBelow274–280发现FORWARD无safe destination时先传null给position.add，异常会在fizzle之前落catch，因此不能称所有缺目的地都有失败提示。可达的非null短位移路径仍有明确fizzle。includeSourceEntity=false只清payload id，仍向当事玩家发；AREA forceSuccess/其他impact/提前attemptCD保留。',6:'计1：Sensitive GLOWING目标颜色接纳/原team优先/0清除哨兵为一个实际反馈策略；hasEffect含已有状态，不能当本次addEffect成功。0不能表示RGB黑；目标未加载丢包、缺UUID/dim/代际、未见remove自动清色，未验原生outline渲染/深度。',7:'支持0：通用延迟目标/world快照，归已有native触发器/生命周期支持；没有新明确拒控或反馈点。',8:'支持0：直接motion在addEffect之前与已有Snare/Gravity家族合并；脉冲/圆锥/技能名不添数。',9:'支持0：AI清仇恨/纯嘲讽不当最终控制拒绝或免疫回执；与006隐身统一范围，守卫旧账0。',10:'支持0：直接remove绕hurt与已有Disintegration家族合并，不以献祭模型或技能名新增。'}
extra={1:[(ir+'api/util/Utils.java',442,448)],2:[(ar+'common/mixin/EntityMixin.java',1,82)],3:[(ar+'common/network/Networking.java',117,119)],5:[('common/src/main/java/net/spell_engine/utils/TargetHelper.java',242,280),('common/src/main/java/net/spell_engine/utils/TargetHelper.java',291,303)],6:[(ar+'common/mixin/EntityMixin.java',1,82),(ar+'common/network/Networking.java',117,119)]}
keys=[];decisions=[]
for row in b['rows']:
 n=int(row['id'].split('-')[-1]);accept=n<=6;rr={'helper_id':row['id'],'decision':'accept' if accept else 'support','research_credit':int(accept),'reason':reasons[n]}
 if accept:
  refs=[];repo=None
  for ref in row['source_refs']:
   s=m[ref['source_key']];repo=repo or s['repo'];assert repo==s['repo'];v=(B/'sources'/repo.replace('/','__')/s['path']).read_bytes();assert hashlib.sha256(v).hexdigest()==s['sha256'];refs.append((s['path'],*ref['lines']))
  refs.extend(extra.get(n,[]))
  existing={x['id'] for x in json.loads((O/'reviewed.json').read_text())}
  if row['semantic_dedup_key'] not in existing: record(row['semantic_dedup_key'],repo,list(dict.fromkeys(refs)),row['native_chain'],row['observation']+' 主岗修正/复核：'+reasons[n],row['application'],row['limits']+' 完整关键原生方法及相关上下文逐项主审；支持0家族只复核核心调用，未宣称其所有辅助源码全文。Java49文件hash/计算blob校验，Iron仅固定库存证明，Ars/SpellEngine有helper tree证明。Mixin原有注册资源缺口保留，未取外网/未启动游戏/未改正式Java资产待办，不给普通阴阳加灰字。','native_control_refusal_and_target_receipt_lifecycle')
  keys.append(row['semantic_dedup_key']);rr['master_id']=row['semantic_dedup_key']
 decisions.append(rr)
(O/'HERSCHEL-007-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-007.json').read_bytes()).hexdigest(),'rows_reviewed':10,'promoted':len(keys),'guard_credit_transferred':0,'helper_system_error':'502 Provider unreachable certificate verification; preserved delivered files, no retry loop','decisions':decisions},ensure_ascii=False,indent=2)+'\n')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'herschel-007-primary-reviewed','credited_chains':keys,'rationale':'6独立职责；01打断拒绝，02原生点燃状态拒写，03真实效果旁观副本增删，04战斗效果栈消费代际，05明确短位移fizzle，06目标发光色回执。07通用延迟、08直接motion同族、09仇恨、10直接移除同族0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
