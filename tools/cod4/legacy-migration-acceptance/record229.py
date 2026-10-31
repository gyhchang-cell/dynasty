import json
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()));root='a6595bbc42a69579f903';q=next(r for r in cs if r['candidate_id']==root)
s=[r['candidate_id'] for r in cs if r['private_file']==q['private_file'] and r['candidate_id']!=root]
a=accepted(root,'alexsmobs-crow-restored-cargo-route-and-pending-paid-owner-loss','补全文1134行整个EntityCrow、完整CreatureAITargetItems真实扣物、native Mob与TamableAnimal完整读写；重载货物和物流路由后实际投递。','HandItems完整原生ItemStack；Command int、MonkeySitting bool、PerchXYZ全有才恢复，Flying另存。owner由super Owner UUID/旧字符串桥，本类pending seedThrowerID和heldItemTime未存。','真实command3+非空主手触发AIDepositChests，从itemframe匹配相同item后取得背后handler，simulate再execute，将实际remainder设回主手；已保存command/perch不是纯宠物显示。','抓物AI先onGetItem(copy1/sethand/seedowner)再实际targetStack.shrink1；hurt成功或普通交互可drop cargo并清手。重载保原生HandItems但seedThrowerID丢失，tick>60仍可能耗掉可食物/回血而不能tame归投喂者；该负例由完整实际链证明非关键词缺失猜测。物流mode/真实cargo持久owner与已计BlueJay地图/Grizzly毛收益不同，不按普通petcommand或多个键再拆数。native Owner fallback是既有链共享支持0。','仅静态，nativeSlot/ItemHandlerHelper及目标仓库存储完整事务未深读，handlersimulate与execute不同/抛异常吞掉无回滚，不能声称exactlyonce。frame筛选背面方向与实际投递方向不同，未运行不判实际所有容器可用。Perch少键不清旧位置、Command无范围clamp，seedowner损失未原生重现；旧世界与正式源码未触碰。',s)
a['reassessment']={'prior_status':'pending','support_batch':229,'reason':'补完整实体、原生手持/Owner存储与实际扣物/投递消费者，不因普通命令NBT单独计数。'}
for f in (O/'reviews').glob('*.json'):
 rows=json.loads(f.read_text());changed=False
 for n,r in enumerate(rows):
  if r['candidate_id']==root:rows[n]=a;changed=True
 if changed:f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
r='tools/cod4/legacy-migration-acceptance/.work/sources/'
extra=[q['private_file'],r+'AlexModGuy__AlexsMobs/src/main/java/com/github/alexthe666/alexsmobs/entity/ai/CreatureAITargetItems.java',r+'minecraft-forge-1.20.1-47.4.10/net/minecraft/world/entity/Mob.java',r+'minecraft-forge-1.20.1-47.4.10/net/minecraft/world/entity/TamableAnimal.java']
record(229,[],extra)
(O/'semantic-reassessment-20261029-004.json').write_text(json.dumps(dict(candidate_id=root,prior_status='pending',credit_change=1,support_batch=229,reason=a['reassessment']['reason'],regeneration='If older original reviewer batch regenerated, rerun record229.',runtime_validation='not_run'),ensure_ascii=False,indent=2)+'\n')
