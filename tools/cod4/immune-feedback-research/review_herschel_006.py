"""Primary full-method and cross-family review. Helper suggestions are not credit."""
from ledger import B,R,O,record,verify
import json,hashlib
D=O/'helpers/herschel-immune';b=json.loads((D/'batch-006.json').read_text());m={s['repo'].replace('/','__')+'/'+s['path']:s for s in json.loads((D/'source-manifest-006.json').read_text())['sources']}
ir='iron431/irons-spells-n-spellbooks';ar='baileyholl/Ars-Nouveau';ip='src/main/java/io/redspace/ironsspellbooks/';ap='src/main/java/com/hollingsworth/arsnouveau/'
extra={6:[(ip+'registries/DataAttachmentRegistry.java',25,33),(ip+'effect/EchoingStrikesEffect.java',1,43)],7:[(ip+'entity/spells/echoing_strikes/EchoingSword.java',1,47),(ip+'registries/EntityRegistry.java',671,681)],3:[(ap+'common/block/tile/RuneTile.java',42,70),(ap+'setup/registry/APIRegistry.java',104,104)]}
reasons={1:'真实招架状态门与成功伤害后效分离，合计1；不能把CANT_PARRY读成所有伤害免疫，空斩轨迹/声音不等于实际击中。击退scale结果被丢弃。',2:'支持0：这条实际是隐身导致AI目标获取排除/清仇恨，没有最终拒伤或拒控，也无免疫回执；与先前TwilightCloak相同范围判定，不因改语义键放宽。保留原生攻击尝试撤隐身的观察，不计守卫旧账。',3:'真实延迟战斗收件目标与过滤对象不一致，且无论resolver结果都消耗Rune，计1；共用SpellResolver门/方法包装不另计。filter检查entityIn却缓存entities.first，scheduled callback再读可变引用，非目标身份确认。',4:'原生近战服务端关系/距离/结算与请求内音效预算合计1；void attack后声音不证明伤害成功，rawIDs不去重，重放请求预算重置，无发行nonce。无效spell解引用落catch，临时状态部分恢复不在finally。',5:'客户端原生tick档期和每ActiveAttack目标整数ID预标记合计1，独立于04服务端验证；append队列、打前预占、Item而非Stack快照，不能作为权威拒控节流。cast动作反馈无需等待实际受伤。',6:'Post伤害限定来源、防法术递归和实际可消费budget生产合计1，非多种武器名换壳。未显式newDamage>0；实际attachment INT codec保存hitCount且仅有剩余时序列化，vfxTimestamp不保存；不能据此声称跨死亡/所有存档路径已验收。',7:'延迟目标载体以旧坐标退路和原生25/45tick命中/清退计1；getHomingTarget server UUID重查、客户端spawn整数ID一次查找，removed与alive不同。声音在client return前触发，服务端hurt结果被忽略，既有爆波不当成功回执；不计同源EchoArrow变体。',8:'真实Touch resolve后的S2C坐标闪光和非paused客户端tick寿命合计1，通用LightManager/移植数学全0。world更换只clear sources不clear clientQueue；旧Fade event下tick能updateTracking再加旧world source，LightManager只查clientSide无当前world相等门，不能宣称切世界防串光完整。此为静态路径风险非实机复现。',9:'支持0：与已有短时本地施法模型表现家族合并；非每目标受击回执。Vanilla/Geo/时间戳/几何模板不拆数。'}
keys=[];decisions=[]
for row in b['rows']:
 n=int(row['id'].split('-')[-1]);accept=n not in (2,9);rr={'helper_id':row['id'],'decision':'accept' if accept else 'support','research_credit':int(accept),'reason':reasons[n]}
 if accept:
  refs=[];repo=None
  for ref in row['source_refs']:
   s=m[ref['source_key']];repo=repo or s['repo'];assert repo==s['repo'];p=B/'sources'/repo.replace('/','__')/s['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'];refs.append((s['path'],*ref['lines']))
  refs.extend(extra.get(n,[]));record(row['semantic_dedup_key'],repo,list(dict.fromkeys(refs)),row['native_chain'],row['observation']+' 主岗复核：'+reasons[n],row['application'],row['limits']+' 主岗完整方法/调用上下文及注册静态复核；Java固定commit源哈希核验；Mixin资源沿用已有web全文显示转录，raw资源仍未核验且失败未重试。未启动游戏、未改正式代码/资产/TODO，普通阴阳不加灰字；静态不证明实际可见/可听。','native_combat_target_receipt_throttle_lifetime');keys.append(row['semantic_dedup_key']);rr['master_id']=row['semantic_dedup_key']
 decisions.append(rr)
(O/'HERSCHEL-006-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-006.json').read_bytes()).hexdigest(),'rows_reviewed':9,'promoted':len(keys),'guard_credit_transferred':0,'registration_resources_credit':0,'decisions':decisions},ensure_ascii=False,indent=2)+'\n')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'herschel-006-primary-reviewed','credited_chains':keys,'rationale':'7独立实际游戏职责：招架/命中结果；Rune延迟收件/消费；服务端近战验证；客户端目标预标记；伤害后递归过滤消费；延迟目标载体；Touch坐标闪光寿命。AI清仇恨/隐身0，本地重影模板0，基础LightManager0，守卫旧账0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
