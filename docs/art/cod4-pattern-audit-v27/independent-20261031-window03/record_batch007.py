from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import record_source_methods as M
def rec(repo,path,method,cache='build/item-use-references',index=0):
 r=M.record(repo,path,method,index,'CONTEXT_ONLY_NO_COUNT','本轮完整读取的新上下文；不是新增参考。',cache_root=cache);r['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';return r
def excluded(repo,path,method,observation,contexts=(),cache='build/item-use-references'):
 r=rec(repo,path,method,cache);r.update(targetScope='EXCLUDED',reviewMode='READ_SOURCE_EXCLUDED_NO_COUNT',countsTowardReferenceGate=False,observation=observation)
 r['callContext']=[rec(repo,p,n,cache,i) for p,n,i in contexts];return r
out=[]
p='src/main/java/divinerpg/client/renders/item/DivineShieldRenderer.java';q='src/main/java/divinerpg/items/base/ItemDivineShield.java'
out.append(excluded('DivineRPG/DivineRPG',p,'renderByItem','完整读取DivineShieldRenderer与ItemDivineShield全类。真实物品initializeClient把RenderProps交给扩展，getCustomRenderer构造原版ModelLayers.SHIELD；物品两个构造器均以entity/shield/<name>_shield形成资源名。renderByItem先调用父实现，再对本类物品翻转YZ；Material采用SHIELD_SHEET图集及该资源，通过sprite.wrap包装foil消费者，handle/plate分别按原模型几何提交。没有生成新UV、独立学校/皇权纹章或实际banner pattern叠层；类TODO也只说未来支持非矩形盾，不是现有功能。图集sprite.wrap机制已在多项装备trim/模块盾源研究，换项目、资源路径、handle/plate不能拆新实现。未追到该sprite实际stitch/资源内容，不声称纹理已加载、外观相符或Forge1.20.1可移植。仅记录范围/语义排除，零信用。',[(p,'DivineShieldRenderer',0),(q,'ItemDivineShield',0),(q,'ItemDivineShield',1),(q,'initializeClient',0),(q,'getCustomRenderer',0)]))
p='src/main/java/com/lothrazar/cyclic/render/ShieldBlockEntityWithoutLevelRenderer.java'
out.append(excluded('Lothrazar/Cyclic',p,'renderByItem','完整读取全类。资源重载重新烘焙两个同为ModelLayers.SHIELD的模型；BANNER_PATTERNS组件存在与否只决定base/no-pattern材质和两个同形模型。木/皮/燧石/骨/黑曜石分支仅换Material；最终sprite.wrap加foil后一次renderToBuffer。正文没有遍历组件中的实际图案或调用BannerRenderer，不能把isBanner命名、组件存在或SHIELD_BASE材质解释成已经绘制自定义旗纹，也不能认为空图案组件等价没有组件。这是原版盾材质包装，与已有盾图集/trim技术同类，不按五材料、两模型或reload算新参考。只读局限记录，未改Cyclic或Dynasty，未进行游戏验收。',[(p,'onResourceManagerReload',0),(p,'onRegisterReloadListener',0)]))
p='src/main/java/com/bobmowzie/mowziesmobs/client/render/entity/layer/UmvuthanaArmorLayer.java'
out.append(excluded('BobMowzie/MowziesMobs-Public',p,'renderArmor','完整读取全类。render从指定MowzieGeoBone取pose，identity后直接乘骨pose；HEAD槽必须ArmorItem且类型HELMET才逐材质层取扩展纹理，旋转Z180度、1.511缩放、位移后绘制完整hook HumanoidModel。getArmorModelHook对非Humanoid回退默认PLAYER_INNER_ARMOR。不同于已接受GeckoArmorLayer逐pass矩阵消费，这里没有新UV映射或额外模型转换，只是指定骨挂头盔、缩放、标准材质层。没看到本类设置只显头部，也没复制宿主属性或应用layer tint；不能把完整model.renderToBuffer当成已保证只画头盔，不能声称多层染色/自定义模型完全支持。mask未做null保护；回切buffer不是恢复任何可验证全局材质状态。不按骨名、层数、比例或装备换项目计数。',[(p,'render',0),(p,'getArmorModelHook',0),(p,'UmvuthanaArmorLayer',0)],cache='build/creature-reference-1000'))
p='src/main/java/mekanism/client/render/armor/ChestArmor.java'
out.append(excluded('mekanism/Mekanism',p,'render','完整读取ChestArmor全类。取CHEST_CONTEXT的ItemStackRenderState，宿主body变换后按幼体/成人与jetpack/scuba区分位移和YZ负尺度，再submit。未改UV、材质身份、贴面纹章或裁切；与既审MekaSuitArmor挂点/延迟提交原则同类，jetpack和scuba不是两种新UV机制。本方法未追到context写入注册，不能推断任意胸甲都会走此路径；新版本SubmitNodeCollector接口只作源码研究，不移植Forge1.20.1。',[(p,'isVisible',0)]))
p='src/main/java/mekanism/client/render/armor/FreeRunnerArmor.java'
out.append(excluded('mekanism/Mekanism',p,'applyTransforms','完整读取FreeRunnerArmor全类。render只在对应腿visible时push独立栈，应用该腿translateAndRotate，幼体ageScale与下移，再用左右不同xo、同y/z及YZ翻转提交各自ItemModelHelper。两腿、普通/armored model不是两套UV变换；此处全是标准附着几何变换，未见新的UV或纹章身份处理，归重复包装排除。isVisible是左右腿或，不代表两腿均可见；foil取同一栈。未追到模型Helper烘焙底层，不声称左右贴图正确或游戏穿戴通过。',[(p,'render',0),(p,'isVisible',0)]))
(D/'batch-007.json').write_text(json.dumps({'reviewed':0,'rows':[],'excluded':out,'parentReview':{'status':'LOCAL_ONLY_FRESH_SOURCE_SEMANTIC_REVIEW','newImplementations':0,'newExclusions':5,'mainLedgerUpdated':False,'productionChanges':False,'networkRequests':0,'notRepeatingBatch003To006':True}},ensure_ascii=False,indent=2)+'\n')
print('batch007: five fresh-source exclusions; zero new credit')
