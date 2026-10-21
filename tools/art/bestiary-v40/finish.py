from pathlib import Path
import json,hashlib,subprocess,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/bestiary-v40';LIB=R/'build/creature-reference-1000'
refs=json.loads((LIB/'render-manifest.json').read_text());choices=['AlexsMobs-ModelTiger','AlexsMobs-ModelGazelle','twilightforest-DeerModel','twilightforest-BoarModel'];rows=[]
notes=['头不是身体前端贴片：颊、短吻与前胸有互相包覆的体量；年兽只借捕食兽连接和毛色方向。','细长下腿与较厚足根形成差异；麒麟只借轻捷支撑与颈根关系。','角枝少量大折段即可成立；麒麟角骨独立承托，不复制鹿角排列。','一个主躯干加口鼻与肩前压，比平均堆方块更像生物。']
for name,note in zip(choices,notes):
 row=next(x for x in refs if x.get('name')==name);rows.append({'name':name,'source':row.get('source'),'source_sha256':row.get('sha256'),'viewed_image':row.get('image'),'observation':note,'view_scope':'static source reconstruction; no animation/runtime claim'})
for name,path in [('Alex tiger','AlexModGuy__AlexsMobs/src/main/resources/assets/alexsmobs/textures/entity/tiger/tiger.png'),('Twilight deer','TeamTwilight__twilightforest/src/main/resources/assets/twilightforest/textures/entity/wilddeer.png')]:
 p=LIB/path;rows.append({'name':name,'local_source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'view_scope':'actual source PNG','observation':'背腹分区与眼鼻对比；只研究组织，没有采样参考像素'})
existing=json.loads((LIB/'visual-review.json').read_text());(D/'references.json').write_text(json.dumps({'inherited_library_records':len(existing),'inherited_accepted_samples':sum(bool(x.get('accepted')) for x in existing.values()),'new_personal_view_count':6,'not_new_1000_review':True,'references':rows,'external_pixels_copied':False},ensure_ascii=False,indent=2)+'\n')
images=[Path(x['viewed_image']) for x in rows if x.get('viewed_image')];sheet=Image.new('RGB',(1200,560))
for i,p in enumerate(images):sheet.paste(Image.open(p),(i%2*600,i//2*280))
sheet.save(D/'references.png')
owned=[R/'src/main/java/com/dynasty/client/BestiaryQuadrupedLayers.java']+[R/f'src/main/resources/assets/dynasty/textures/entity/bestiary/{k}.png' for k in ('nian_beast','qilin')]
owned += [D/k/n for k in ('nian_beast','qilin') for n in ('model.geo.json','model.animation.json',k+'.bbmodel','uv.json','design.json')]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in owned}
subprocess.run([sys.executable,str(R/'tools/art/bestiary-v40/build.py')],check=True)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items()),'Nonrepeatable output'
connection=json.loads((D/'connection-check.json').read_text());assert all(not x['connection_issues'] for x in connection.values())
# No old shared creature texture was overwritten. Compare known git blobs where available.
protected={}
for n in ('nian_beast','qilin','phoenix','nine_tailed_fox'):
 p=R/f'src/main/resources/assets/dynasty/textures/entity/{n}.png';protected[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
record={'status':'BOUND_RESOURCES_SOFTWARE_CHECKED_NATIVE_PENDING','entities':['dynasty:nian_beast','dynasty:qilin'],'geometry_authority':'tools/art/bestiary-v40/build.py exports native BestiaryQuadrupedLayers.java','renderer_binding':'DetailedBeastModel selected by unchanged registered entity renderers; dedicated bestiary textures','repeatable_export':True,'new_ids':False,'combat_or_collision_modified':False,'old_shared_texture_hashes':protected,'java_started':False,'native_acceptance':'pending','owned_hashes':{str(Path(p).relative_to(R)):h for p,h in before.items()}}
(D/'DELIVERY.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(D/'README.md').write_text('''# 原有神兽补缺：年兽与麒麟

实际链路：DynastyEntities注册→DynastyClientEvents→DetailedBeastModel→BestiaryQuadrupedLayers→textures/entity/bestiary/{id}.png。此前Kind.NIAN与Kind.QILIN共用buildQilin，缺少独立体态；这是本轮筛选依据。保留注册、行为、属性、碰撞和影子设置。

年兽：前胸压低、颈根厚实、宽短吻与獠牙、前重后轻，蓝黑兽皮配浅鬃。麒麟：较窄腹腰、竖颈、少量角枝、下腿收细与分蹄，绿鳞、浅腹与朱鬃。每只30个Cuboid/31骨骼；只用长方体和粗折段。胸腰没有通过装甲零件遮蔽，身体与四肢在完整步态保持连通。

build.py为权威制作源，导出原生Java模型层、原创256²像素图集和Blockbench/Gecko格式编辑副本。原生运行使用Java层，文档内geo/animation用于编辑和软件检查，不能误称为Gecko实体运行绑定。render只绘制层级根一次；子件依父骨运动；对角腿交替，下段屈曲，尾根轻摆。旧凤凰与九尾狐仍走原有分支。

使用原生Cube的盒UV展开，每块1像素/单位，独立岛无越界与重叠。底面V反向与原版一致。头部眼窝与鼻口优先，主体只安排顺毛流或顺身体鳞纹，没有随机噪点。共面外表面使用0.125单位避让，修复首轮颈鬃与胸腿闪烁。独立图集避免覆盖旧nian_beast.png及其其他引用。

参考：继承已有1000条accepted样本库。本轮本人查看4张模型结构卡和2张真实PNG，来源与范围见references.json；没有冒称本轮新看1000只，没有将其他模组图片复用到生产资产。

验证：可重复生成的模型/UV/PNG/BB字节一致；UV边界/重叠、骨骼父链、81个步态采样有限值、21个姿态整图OBB连通、嵌图与生产PNG字节一致通过。五向、灰模、黑剪影、原色、头部、同尺度玩家及前后对照见index.html。软件步态是原生运动参数的设计预览，不替代游戏完整运动验收。未启动Java/游戏；构建、实际资源重载、原生动态光照与脚步接地、自然攻击待主流程验证。未删除提示词。
''')
html=(D/'index.html').read_text();html+='<h2>本轮实际复看参考</h2><img src="references.png"><p><a href="references.json">来源、旧1000样本库与本轮查看范围</a></p>';(D/'index.html').write_text(html)
print('Repeatable generation + handoff complete')
