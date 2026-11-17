"""Primary read of helper047; semantic support only, no ledger credit."""
from ledger import B,O,R
import json,hashlib,datetime
h=O/'helpers/herschel-immune/batch-047.json';d=json.loads(h.read_text());refs=[]
assert hashlib.sha256(h.read_bytes()).hexdigest()=='9e4e4bd6e597dfe5032bbc37e1fe4099dda77c44803d5456739e7ccaad93a7d2'
for row in d['rows']:
 for r in row['source_refs']:
  key,rel=r['source_key'].split('/',1);root=B/'sources'/key;raw=(root/rel).read_bytes();meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());blobs={v['path']:v['sha'] for v in tree['tree'] if v['type']=='blob'}
  assert meta['commit']==tree['sha']==r['fixed_commit'];assert hashlib.sha256(raw).hexdigest()==r['file_sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[rel]
  a,z=r['lines'];assert 1<=a<=z<=len(raw.decode().splitlines());assert r['url']==f'https://github.com/{meta["repo"]}/blob/{meta["commit"]}/{rel}#L{a}-L{z}'
  refs.append({'source_key':r['source_key'],'lines':[a,z],'file_sha256':r['file_sha256'],'url':r['url'],'method':r['method'],'credit':0})
out={'helper_file_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),'helper_original_credit':0,'main_review_new_effective':0,'state':'primary_reviewed_support_only','main_full_files_read':['EntityIceBarrier167','FrostBarrier135','EntityMagicConstruct197','EntityScaledConstruct68','RenderIceBarrier45','ICustomHitbox31','GhostEntity178'],'main_complete_methods_read':['RayTracer.standardEntityRayTrace77-82','RayTracer.ignoreEntityFilter93-97','RayTracer.rayTrace130-212','EntityForcefield.onUpdate82-216'],'registration_lines_read':['WizardryEntities160-174','ClientProxy912-922'],'source_refs':refs,'observations':[
'冰障server碰撞要实际AABB相交、排除MagicConstruct，再按带(1,0,1)偏置的目标位置计算面距离和sign推力，玩家原生速度包。没有调用isValidTarget/伤害/免疫准入，存caster不能推断友军保护。距离0时速度0，分支/packet不能替代实际位移。和已收录forcefield伤害独立推离/玩家速度同步同族，薄面、渐次升降、常量和模型变化均0。',
'原生attackEntityFrom先无条件deflect音再return父结果，未展开MC1.12 Entity.attack内部，不声称声音代表成功免疫。父构造noClip不是固体阻挡；法术server延迟收集生成，spawn返回忽略，不能凭true声称实际生成。NBT保存delay，但此类无writeSpawnData附加delay，父只写lifetime/caster当前整数ID/scale；客户端delay+1声音不等于服务器延迟已同步。',
'custom ray dispatcher按接口calculateIntercept，并没有启用注释中的canBeCollidedWith过滤。冰障用端点绝对面距离求比例，无显式异侧/分母0防护，不能据此推断所有原版攻击被墙挡。RayTracer的intercept在遍历外初始化、普通AABB未命中时未显式归null，存在上次值沿用的静态边界；未做上游/产品bug判断，不另计通用几何。',
'Ghost全文isInvulnerableTo是PROJECTILE || (MOTHER_RESISTANT_TO && super)，标签单独不保证拒绝，非投射物非标签也不进入super；tick在super周围开启noPhysics后关闭，保留noGravity；air回调飞行速度键控添加/非air移除。此处没有独立拒控回执，原有source-qualified rejection族覆盖，0。'],
'semantic_decision':'两单元全部支持0，无独立新最终免控/明确反馈链；不按方法、geometry或tag名字重复计数。','limitations':'静态固定上游版本；未展开native Entity damage/velocity consumer、Ghost父级/具体tag值、模型几何；未编译/测试/游戏，无像素/声音/TCP验收。','production_changes':False,'game_started':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'HERSCHEL-047-REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'helper':47,'ranges_verified':len(refs),'new_credit':0}))
