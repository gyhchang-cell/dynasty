from ledger import record,verify,O,B,R
import json,hashlib
p='src/main/java/com/github/L_Ender/cataclysm/'
record('cataclysm-boss-effect-allowlist-refusal','lender544/new1.20.1',[(p+'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java',228,230),(p+'entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java',290,292),(p+'init/ModTag.java',138,140),(p+'init/ModTag.java',164,166),(p+'util/LazyTagLookup.java',9,33),('src/main/resources/data/cataclysm/tags/mob_effect/effective_for_bosses.json',1,36)],
 '完整两个Boss基类canBeAffected→同一个EFFECTIVE_FOR_BOSSES_LOOKUP.contains→lazy registry tag对象→tag.contains；tag以mob_effect注册并提供实际默认资源。两个同构基类与全部白名单值合并1条，不按效果种类计数。',
 '未列入白名单的效果在调用super前直接拒绝。默认白名单含slowness/mining_fatigue等有害效果，因此不能称“Boss全体免控/免负面”。Lazy缓存的是ITag对象，未发现此小类主动重新获取逻辑；是否随数据包更新取决于Forge标签对象契约，静态不推测reload故障。拒绝处没有文字、声音、额外网络回执。',
 'Boss拒控文本应来自明确的canBeAffected/效果拒绝语义，不能从hasEffect=false推断（也可能未尝试施加）；Boss规则和普通玩家体质保持分域。',
 '这里只读原生覆写和全部自有辅助到Forge接口契约；未验调用者addEffect结果、原生网络同步或画面；JSON条目和通用Lazy包装都不另计。','immunity_rejection_semantics')
# 给已计的环境提示补真实语言资源，仍为同一条研究。
f=O/'reviewed.json';rows=json.loads(f.read_text())
for row in rows:
 if row['id']=='cataclysm-leviathan-environment-immunity-actionbar':
  for locale in ['en_us','zh_cn']:
   rel=f'src/main/resources/assets/cataclysm/lang/{locale}.json';q=B/'sources/lender544__new1.20.1'/rel
   row['source_refs'].append({'path':str(q.relative_to(R)),'source_path':rel,'lines':[84,84],'file_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'url':f'https://github.com/lender544/new1.20.1/blob/{row["commit"]}/{rel}#L84'})
  row['concrete_observation']+=' 已核对同提交en_us/zh_cn第84行分别为离水无敌英/中文提示，未声明GRAY样式。'
  row['limitations']='canSwim不等于简单isInWater，原版消息网络/GUI为平台契约；资源key与中英值已核对，不证明实机本地化。无游戏验收、无像素结论。'
f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
verify()
