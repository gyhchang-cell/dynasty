"""Main semantic review: source methods read in full, registration web evidence bounded."""
from ledger import B,R,O,record,verify
import json,hashlib
D=O/'helpers/herschel-immune';b=json.loads((D/'batch-004.json').read_text());s5=json.loads((D/'batch-005.json').read_text())
manifest={}
for n in ('004','005'):
 for x in json.loads((D/f'source-manifest-{n}.json').read_text())['sources']:manifest[x['repo'].replace('/','__')+'/'+x['path']]=x
supp=s5['support_for_prior_batches'][0]['source_refs']
reasons={1:'实际IMMUNITY producer的期限/来源约束→原生拒伤consumer合计1；addStatusEffect的effectAnyHarmful=true没有生产者不加数。查询不自行查期限、无去重、缺DamageType可拓宽匹配均保留。',2:'不同最终边界：PRE回调之后再次决定是否执行内部applyDamage；不是01的grant/query包装，也不能由内部skip反推外层false或没有POST。完整SpellExecution校验保留，不把配置可能等于本击必免。',3:'原生闪避以明确原因拒伤并发EVASION/动画/声音；随机、角度、busy条件同一决策合计1。末次source无清空；tag默认内容未知，不声称所有来源可闪。',4:'弹原生命中另一个最终副作用边界，以同一DamageSource对象识别已闪避才拒绝后续点火等；不同于03拒伤生产。原版字节码未读，nullable比较不推定已发生误判，非所有弹种通用。',5:'实际STATUS ADD/SET执行点按Boss与动态控制分类拒绝；不是纯tag常量。分类扫描阈值、amp0、缓存未清和非本dispatcher入口不覆盖均保留；普通addStatusEffect返回被忽略不算实际接纳回执。',6:'实际STATUS ADD/SET/REMOVE前独立maxHealth/法强资格门；残血无例外，不是伤害值或source常量变体。与05Boss控制分类是不同语义拒绝点。',7:'实际玩家被动战斗每spell额度/共享抽签与原生tick清理合计1；不是每目标反馈节流，不按多个条件/回调/Map方法拆数。',8:'support0：真实负面状态拒绝consumer，五参实际producer永远false；未找到true producer，不把外部可调用API能力当接活。',9:'support0：击退缓存consumer存在，但flag默认false且完整缓存无configure启用者；setVelocity不经过此点。'}
review=[];keys=[]
for row in b['rows']:
 n=int(row['id'].split('-')[-1]);reason=reasons[n];decision='accept' if n<=7 else 'support'
 rr={'helper_id':row['id'],'decision':decision,'research_credit':0,'reason':reason}
 if decision=='accept':
  refs=[]
  for ref in row['source_refs']+supp:
   s=manifest[ref['source_key']];p=R/'tools/cod4/immune-feedback-research/sources'/s['repo'].replace('/','__')/s['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'];refs.append((s['path'],*ref['lines']))
  record(row['semantic_dedup_key'],'ZsoltMolnarrr/SpellEngine',list(dict.fromkeys(refs)),row['native_chain'],row['observation']+' 主岗：'+reason,row['application'],row['limits']+' 补证：005固定Java入口及原生注册全文已读/源码blob核验；同commit三资源完整web观察见helpers/herschel-immune/registration-web-observations-005.json。原始资源字节TLS失败未重试，故不声称资源blob已核验/运行Mixin已通过。注册网页支持0，Java链逐条主岗全文复核；不启动游戏，普通阴阳体质不加灰字，守卫旧账0。','native_control_rejection_or_explicit_game_feedback')
  keys.append(row['semantic_dedup_key']);rr.update(research_credit=1,master_id=row['semantic_dedup_key'])
 review.append(rr)
(O/'HERSCHEL-004-REVIEW.json').write_text(json.dumps({'batch_sha256':hashlib.sha256((D/'batch-004.json').read_bytes()).hexdigest(),'rows_reviewed':9,'promoted':len(keys),'supplement':'005 Java entrypoints and fixed-commit full web resource observations; raw resource blob incomplete after TLS; no runtime proof','guard_credit_transferred':0,'decisions':review},ensure_ascii=False,indent=2)+'\n')
p=O/'semantic-dedup.json';d=json.loads(p.read_text());d['groups'].append({'family':'herschel-004-primary-reviewed','credited_chains':keys,'rationale':'7个独立原生游戏拒绝/反馈/预算位点；同链包装与来源变体0，孤立harmful status/knockback consumer0，005网页注册补证0。'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
