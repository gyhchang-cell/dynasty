from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import record_source_methods as M
repo='iron431/irons-spells-n-spellbooks';p='src/main/java/io/redspace/ironsspellbooks/render/GlowingEyesLayer.java'
def rec(n,i=0):
 r=M.record(repo,p,n,i,'CONTEXT_ONLY_NO_COUNT','完整方法上下文，零额外计数。');r['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';return r
r=rec('render',0);r.update(targetScope='EXCLUDED',reviewMode='READ_SOURCE_EXCLUDED_NO_COUNT',countsTowardReferenceGate=False)
r['observation']='完整读GlowingEyesLayer全类（Vanilla/Geo两个实现及状态选择器/enum）。Vanilla用同一purple_eyes纹理的eyes层重画整个parent模型，RGB随effect变；Geo只找head骨并updateScale，再renderChildBones。颜色优先ABYSSAL_SHROUD后PLANAR_SIGHT，SHADOWWALKER_HELMET颜色分支注释掉但scale仍优先检测该头盔；所以仅戴该头盔且无两effect时eyeTypeNone，不会启用眼层。Vanilla直接scale共享PoseStack没有本方法push/pop，Geo改head scale也没有局部恢复；调用者是否隔离/后续重置未读，不能称状态安全。Geo取到原buffer参数继续传renderChildBones，未沿该较新API确认EYES缓冲重取契约，不能拿另版本GeckoLib4.8.4当精确消费者。图案是否仅眼区取决于实际PNG与模型UV，本轮未读像素，不能把名字eyes当遮罩局部匹配证明。与batch003 dyeable和batch015全模型emissive换色均属既有UV上选择材质/色/骨的wrapper，无独立装备纹样/UV新机制，不按效果/骨/框架两版拆计。'
r['callContext']=[rec('render',1),rec('getEyeType'),rec('getEyeScale'),rec('renderType')]
(D/'batch-016.json').write_text(json.dumps({'reviewed':0,'rows':[],'excluded':[r],'parentReview':{'status':'ONE_FRESH_EFFECT_LAYER_WRAPPER_EXCLUDED','newImplementations':0,'newExclusions':1,'mainLedgerUpdated':False,'productionChanges':False,'networkRequests':0}},ensure_ascii=False,indent=2)+'\n');print('batch016: one exclusion')
