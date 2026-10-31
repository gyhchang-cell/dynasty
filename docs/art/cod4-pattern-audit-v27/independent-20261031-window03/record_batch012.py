from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import record_source_methods as M
def rec(repo,p,n,i=0):
 r=M.record(repo,p,n,i,'CONTEXT_ONLY_NO_COUNT','完整读取的方法，仅补上下文。',cache_root='build/creature-reference-1000');r['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';return r
def exc(r,note,ctx):
 r.update(targetScope='EXCLUDED',reviewMode='READ_SOURCE_EXCLUDED_NO_COUNT',countsTowardReferenceGate=False,observation=note,callContext=ctx);return r
repo='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/client/render/PoisonBoltRenderer.java'
r=exc(rec(repo,p,'renderTrail'),'完整读PoisonBoltRenderer全类；源码明确标注基于AlexsCaves WaterBoltRenderer，其主体负XY缩放1.25、yaw用rotLerp但pitch普通lerp，eyes材质固定15728640天空光与alpha.5。拖尾hasTrail后退回实体插值原点；sampleSize仅1，从历史点0直接接getTrailPosition(8)，不是8段连续带；固定世界Y向上下.25、zRot0，单quad，UV按tick%8步进半纹宽，非相机朝向。实体历史生产正文未读，不能凭索引8声称8段验证；已有WaterBolt主色/overlay与历史带和其它轨迹框架参考，此处仅参数/缩水消费者，不计新弓纹实现。',[rec(repo,p,'render'),rec(repo,p,'getBlockLightLevel'),rec(repo,p,'getTextureLocation')])
repo='lender544/new1.20.1';pre='src/main/java/com/github/L_Ender/cataclysm/client/render/entity/';p=pre+'Laser_Beam_Renderer.java'
s=exc(rec(repo,p,'render'),'完整读Laser_Beam_Renderer全类：bake既有Laser_Beam_Model，负XY缩放，rotLerp yaw/普通lerp pitch，setupAnim后CMEyes层用输入packedLight画白色模型。没有新图片UV/纹样合成/轨迹生成，名字Laser不等于新的真实碰撞束机制。model正文未读，发光RenderType具体状态未核，不计学校/皇权纹章参考。',[rec(repo,p,'Laser_Beam_Renderer'),rec(repo,p,'getTextureLocation')])
p=pre+'Abyss_Blast_Renderer.java';q=pre+'Portal_Abyss_Blast_Renderer.java'
t=exc(rec(repo,p,'render'),'完整读取Abyss_Blast_Renderer和Portal_Abyss_Blast_Renderer全类，与已有RenderSolarBeam的插值端点、appear帧、第一人称单面/其余双面、相机+碰撞面端片同族，两个类只半径/旋转helper不同，合并排除一个模板族。长度取插值端点欧距，frame负值置6但没有上界夹取；256x32图集端片16x16、束体只拉伸一像素V条，不能称按世界长度重复UV。shouldRender恒true。两类非第一人称第一束面均把cameraXRot+90的度值直接送Quaternion.rotationY弧度入口，第二束面才乘PI/180，不能宣称两个面正确对称。collision字段生产与网络同步未读，命名不证明真实命中；这些是外部源码契约限制，未修改Boss/AI/游戏资源，不作实机效果验收。',[rec(repo,p,n) for n in ['renderBeam','drawBeam','renderEnd','renderFlatQuad','drawVertex','shouldRender']]+[rec(repo,q,n) for n in ['render','renderBeam','drawBeam','renderEnd','renderFlatQuad','drawVertex','shouldRender']])
(D/'batch-012.json').write_text(json.dumps({'reviewed':0,'rows':[],'excluded':[r,s,t],'parentReview':{'status':'THREE_FRESH_RENDERER_FAMILIES_EXCLUDED','newImplementations':0,'newExclusions':3,'mainLedgerUpdated':False,'productionChanges':False,'networkRequests':0}},ensure_ascii=False,indent=2)+'\n');print('batch012: three exclusions; four full renderer files read')
