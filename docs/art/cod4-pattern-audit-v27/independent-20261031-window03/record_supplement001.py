from pathlib import Path
import sys,json,hashlib,datetime
D=Path(__file__).resolve().parent;A=D.parent;R=A.parents[2];sys.path.insert(0,str(A));import record_source_methods as M
repo='bernie-g/geckolib';pre='Forge/src/main/java/software/bernie/geckolib/'
items=[]
for p,n in [('loading/json/raw/ModelProperties.java','deserializer'),('model/GeoModel.java','getTextureResource')]:
 r=M.record(repo,pre+p,n,0,'CONTEXT_ONLY_NO_COUNT','本地证据补充，不作为新实现。ModelProperties实际要求texture_width/height；GeoModel带renderer重载实际委派单参数纹理路径。');r['reviewMode']='READ_SOURCE_CONTEXT_NO_COUNT';items.append(r)
root=R/'build/item-use-references/bernie-g__geckolib';tree=json.loads((root/'tree.json').read_text());missing=[]
for path in ['Forge/src/main/java/software/bernie/geckolib/mixin/client/TextureManagerMixin.java','Forge/src/main/resources/geckolib.mixins.json']:
 e=next(e for e in tree['tree'] if e['path']==path);missing.append({'path':path,'revision':tree['sha'],'gitTreeBlob':e['sha'],'existsInLocalSourceCache':(root/path).exists(),'bodyRead':False,'meaning':'仅tree条目；不当作完整源码或运行接入已验证。'})
s={
 'status':'LOCAL_ONLY_UNCREDITED_EVIDENCE_SUPPLEMENT',
 'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'appliesTo':['batch-001.json','batch-002.json'],
 'newImplementations':0,'countsTowardReferenceGate':False,'records':items,
 'clarifications':[
  'batch002的texture_width/texture_height由GsonHelper.getAsDouble读取，是必须字段；本地所读ModelProperties未对零值/负值进行检查。不能把构造器声明或UI约束当输入已校验。',
  'batch001的GeoModel.getTextureResource(animatable,renderer)在默认实现中直接委派单参数方法；纹理选择链不是仅从名字猜测。',
  'batch001已实际读取AnimatableTexture的条件分支与同帧mask上传方法，但TextureManager将原始纹理替换为AnimatableTexture的mixin实现和配置未缓存；不可说实际示例一定走动画纹理类型。静态像素分区及同几何层的源码研究，与具体动画接入证据分开。',
  '两提案都只是独立技术研究提案，尚未被主协调接纳；source.json commit message为Update to4.8.4，仅版本来源线索，不等于逐字节验证本地运行Jar、启动实例或游戏内视觉。',
  '未下载/查看Gecko armor主PNG或mask；两个PNG在tree具有同blob只证明仓库对象一致，不能推论可见像素正确、透明边距或动画帧长。',
  'Geo渲染器默认缓存加载方法、注册字段和实际示例调用均有源证据；未验证完整mod启动总线注册/资源重载运行。不把源码存在当客户端已实测加载。',
  '本补充不改原提案hash或正式池，不引入按helper/重载/JSON字段计数。'
 ],
 'unresolvedLocalSourceGaps':missing,
 'networkRequests':0,'gameOrJavaStarted':False,'sharedProductionJarAccess':'NONE','mainLedgerUpdated':False,'productionChanges':False
}
(D/'supplement-001.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print('Saved source/scope supplement; zero new implementations')
