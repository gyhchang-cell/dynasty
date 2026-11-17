"""Actual post-hit sacrifice eligibility and pre-kill resource settlement; whole1."""
from ledger import B,O,R,record,verify
import json,hashlib,datetime
from pathlib import Path
repo='WayofTime/BloodMagic';p='src/main/java/wayoftime/bloodmagic/';root=B/'sources'/repo.replace('/','__');key='bloodmagic-native-post-hit-execution-eligibility-and-altar-credit-before-final-damage'
files=[p+'common/item/ItemDaggerOfSacrifice.java',p+'util/helper/PlayerSacrificeHelper.java']
refs=[(f,1,len((root/f).read_text().splitlines())) for f in files]
refs += [(p+'common/item/BloodMagicItems.java',171,171),(p+'common/tile/TileAltar.java',88,92),(p+'common/tile/TileAltar.java',172,176),(p+'altar/BloodAltar.java',515,530),(p+'altar/BloodAltar.java',183,228),(p+'common/registries/BloodMagicDamageTypes.java',11,11)]
for f,a,z in refs:assert 1<=a<=z<=len((root/f).read_text().splitlines())
record(key,repo,refs,
 '完整Dagger类79/PlayerSacrificeHelper159、完整TileAltar dagger/startCycle转发与BloodAltar.sacrificialDaggerCall/startCycle方法、实际item注册与伤源key读。缓存Forge1.20.1-47.4.10 Player.attack完整1088–1242及ItemStack.hurtEnemy完整399–405读：实际target.hurt(playerAttack)true后才itemstack.hurtEnemy，后者itembool只控制ITEM_USED stat，不回滚原hurt。Dagger在此post-hit回调拒FakePlayer、client/非ServerPlayer、不能canChangeDimensions目标、Player、非Enemy幼体、非活/HP<.5、牺牲比<=0；只拒特殊处决，不保证拒先前普通攻击。按当前HP算LP/幼体半减；findAndFillAltar在目标坐标周边first IBloodAltar先充血/startCycle并true，再声/直接setHealth .00001/iframe0/hurt SACRIFICE10不读bool，最后无论如何item返回false。',
 '整体1：特殊处决资格在已接纳普通伤害后，资源credit在目标最终伤害/死亡之前承诺，构成独立final eligibility/settlement边界。区别Psi portal capability拒位移、Ars disintegration直接DISCARD后按XP耗source、ColdSweat onAttack一次stamp先额外hurt和Sentry contact直接setHP：这里post-hit奖励按当时剩HP计，并可能先充血再因最终hurt拒绝/override未死；不能声称全Boss可处决或明确免疫文字。findAltar不是注释所谓最近：x -2..2/y -2..1/z -2..2顺序首个，无距离排序；fill方法void对主池/lockdown输入池按capacity夹取，满池仍helpertrue，声音/濒死请求不证明实际新增LP或真正死亡。',
 'Boss免疫reason须标具体拒控阶段；item回调false、普通hurtfalse、处决资格false、最终死亡失败各不同。拒特殊处决不自动表示Boss纹丝不动，因为普通攻击/击退已先发生；免疫文字只对应明确控制策略，不能根据任意false或祭坛声推断。执行类机制若要防Boss必须在真正可能改HP/移动的入口保护，不能只拦最后hurt。研究不新增玩法，不提前制作普通阴阳或Boss功能。',
 '固定35f0188665e648d981095b6933cc75b0ca96eca5 tree/blob/manifest source核；native缓存方法仅本地source比较，非安装Jar或runtime确认，不给native基础设施额外信用。未展开ForgeHooks/原生hurt/setHealth所有override、getSacrificial API配置data自然加载、altar.checkTier/recipe查询内部/真实服务器反馈；故仅静态路径与请求顺序，不称实际复现奖励复制/必处决/全Boss免疫。getAltar/charge/startCycle所有完整方法已读，但只本体update不等于完整altar玩法自然验收。未游戏/编译/资产/正式源码/Jar/TODO操作。','native_post_hit_special_execution_admission_and_reward_settlement')
# Preserve exact local native context as support0; do not copy or alter another QA source.
aux=[]
for rel,a,z in [('net/minecraft/world/entity/player/Player.java',1088,1242),('net/minecraft/world/item/ItemStack.java',399,405)]:
 f=R/'tools/cod4/legacy-migration-acceptance/.work/sources/minecraft-forge-1.20.1-47.4.10'/rel;raw=f.read_bytes();aux.append({'path':str(f.relative_to(R)),'lines':[a,z],'file_sha256':hashlib.sha256(raw).hexdigest(),'research_credit':0,'role':'complete cached native containing method read; local source comparator only, no archive/runtime identity'})
f=O/'reviewed.json';rows=json.loads(f.read_text());r=next(x for x in rows if x['id']==key);r['auxiliary_refs']=aux;f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(O/'BATCH-180-REVIEW.json').write_text(json.dumps({'key':key,'credit':1,'native_comparator_credit':0,'native_refs':aux,'full_methods_manually_read':True,'not_a_generic_false_to_immune_inference':True,'production_changes':False,'game_started':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n')
s=json.loads((O/'semantic-dedup.json').read_text());s['groups'].append({'family':'batch180-post-hit-altar-first-execution','credited_chains':[key],'rationale':'Whole special execution qualification after accepted normalattack; reward committed before direct HP+last hurt, itembool stat outcome distinct. Compare capability/disintegration/onAttack stamp/directHP, no constant/species/wrapper credit.'});(O/'semantic-dedup.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');verify()
