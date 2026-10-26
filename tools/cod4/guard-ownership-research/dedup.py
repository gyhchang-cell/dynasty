"""Conservative semantic-family exclusions after reading complete implementations."""
import json,pathlib
R=pathlib.Path(__file__).resolve().parent;D=R.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research'
c=json.loads((R/'.work/candidates.json').read_text());out=[]
def reject(repo,file,method,reason,start=None):
 hits=[x for x in c if x['repo']==repo and x['path'].endswith('/'+file+'.java') and x['name']==method and (start is None or x['start']==start)]
 for r in hits:out.append({k:r[k] for k in ['id','repo','commit','path','start','end','name','url','excerptSha256']}|{'accepted':False,'reason':reason})
A='baileyholl/Ars-Nouveau';G='Polarice3/Goety-2'
reject(A,'FamOwnerHurtByTargetGoal','canAttack','与已接受FamOwnerHurtTargetGoal.canAttack同一ownerUUID排除+父canAttack模板，变量/类角色端口不另计。')
for method in ['readAdditionalSaveData','getOwnerFromID','addAdditionalSaveData']:
 reject(A,'EntityAllyVex',method,'与已接受SummonSkeleton同方法的owner/NBT模板语义相同；新实体种类和字段拼写不增加有效位点。')
for file in ['SummonWolf','SummonSkeleton','EntityAllyVex']:
 for method in ['getTicksLeft','setTicksLeft','setOwnerID','getOwnerUUID']:
  reject(A,file,method,'纯寿命/owner字段访问器或Optional包装，不以getter/setter凑数。')
reject(G,'ServantFollowOwnerGoal','start','与已接受Ars FollowSummonerGoal.start同一重算清零/保存并置零水寻路代价模板，未计。')
reject(G,'ServantFollowOwnerGoal','stop','与已有停止导航/恢复水代价模板近似，增加清owner缓存不足再作为独立控制流贡献计数。')
reject(G,'Minion','canContinueToUse','VexCharge持续条件与已接受Ars AllyVex相同，hasWanted/charging/存活，端口不另计。',188)
reject(G,'IOwned','copyTrueOwner','IOwnedBlock重载与IOwned成对复制UUID/clientID近似；接口端口不另计。',77)
for method in ['isGrudgedTowardsTag','isGrudgedTowardsType','isAllyWithType']:
 reject(G,'IOwned',method,'在线owner查询/离线UUID保存关系的参数类别变体；已接受实体关系版本，未重复计数。')
for file in ['SummonTargetGoal','ServantNaturalAttackGoal']:
 reject(G,file,file,'构造器参数转发/重载默认值不作为独立研究位点；只接受有策略控制流的goal方法。')
reject(G,'WitchServant','registerGoals','与已接受WarlockServant注册同一shootTarget活体缓存匿名goal，时间常量和类名替换不另计。')
reject(G,'WitchServant','targetSelectGoal','与WarlockServant相同HurtBy+SummonTarget注册模板，普通goal挂载并无独立过滤贡献。')
reject(G,'WarlockServant','targetSelectGoal','只注册HurtByTargetGoal和已研究SummonTargetGoal，未增加新的过滤控制流，不另计。')
reject(G,'WitchServant','mobInteract','与已接受WarlockServant同一货币交易owner/ally授权和owner专属装备控制流，实体类型端口不另计。')
(D/'semantic-exclusions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Explicit reviewed exclusions',len(out))
