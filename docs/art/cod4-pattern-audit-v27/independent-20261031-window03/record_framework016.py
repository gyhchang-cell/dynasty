from pathlib import Path
import json,hashlib,zipfile,sys,datetime
D=Path(__file__).resolve().parent;A=D.parent;R=A.parents[2];sys.path.insert(0,str(A));import record_source_methods as M
archive=Path(json.loads((D/'framework-supplement-012.json').read_text())['sourceArchive']);assert archive.name.endswith('-sources.jar')
specs={'net/minecraft/client/model/HumanoidArmorModel.java':[('createBodyLayer',0)],'net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java':[('render',0),('renderArmorPiece',0),('setPartVisibility',0),('renderModel',1),('renderTrim',1),('renderGlint',1),('getArmorModel',0),('usesInnerModel',0),('getArmorModelHook',0),('getArmorResource',0)]}
files=[];records=[]
with zipfile.ZipFile(archive) as z:
 for path,ns in specs.items():
  b=z.read(path);dest=D/'framework-source-016'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);files.append(dict(archiveEntry=path,local=str(dest.relative_to(R)),sha256=hashlib.sha256(b).hexdigest(),reviewMode='READ_FULL_SOURCE_FILE_NO_COUNT'))
  t=M.parser.parse(b);todo=[t.root_node];nodes=[]
  while todo:
   n=todo.pop();todo.extend(reversed(n.children))
   if n.type in ('method_declaration','constructor_declaration'):nodes.append(n)
  for name,index in ns:
   n=[n for n in nodes if n.child_by_field_name('name').text.decode()==name][index];assert not n.has_error
   records.append(dict(path=path,method=name,index=index,start=n.start_point.row+1,end=n.end_point.row+1,source=b[n.start_byte:n.end_byte].decode(),sourceSha256=hashlib.sha256(b).hexdigest(),countsTowardReferenceGate=False))
 path='net/minecraft/client/model/geom/LayerDefinitions.java';b=z.read(path);dest=D/'framework-source-016'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);files.append(dict(archiveEntry=path,local=str(dest.relative_to(R)),sha256=hashlib.sha256(b).hexdigest(),reviewMode='ONLY_SELECTED_SOURCE_RANGES_READ'))
 ranges=[dict(path=path,start=a,end=e,source='\n'.join(b.decode().splitlines()[a-1:e]),countsTowardReferenceGate=False) for a,e in [(108,119),(223,231)]]
slots={'HEAD':dict(model='outer',textureSuffix='layer_1',visible=['head','hat']),'CHEST':dict(model='outer',textureSuffix='layer_1',visible=['body','rightArm','leftArm']),'LEGS':dict(model='inner',textureSuffix='layer_2',visible=['body','rightLeg','leftLeg']),'FEET':dict(model='outer',textureSuffix='layer_1',visible=['rightLeg','leftLeg'])}
legSizes={kind:dict(base=[4,12,4],deformation=deform-.1,actualExtents=[n+2*(deform-.1) for n in [4,12,4]],uvOffset=[0,16],leftMirror=True,pivotX=[-1.9,1.9]) for kind,deform in [('outer',1),('inner',.5)]}
out=dict(status='VANILLA_ARMOR_SOURCE_CONTRACT_ONLY_NO_REFERENCE_CREDIT',recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceArchive=str(archive),archiveSha256=hashlib.sha256(archive.read_bytes()).hexdigest(),artifactCoordinate='net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources',countsTowardReferenceGate=False,newImplementations=0,mainLedgerUpdated=False,productionChanges=False,networkRequests=0,javaOrGameRun=False,files=files,records=records,ranges=ranges,defaultArmorContract=dict(atlas=[64,32],standardAndSlimShareArmorLayerDefinitions=True,innerDeformation=.5,outerDeformation=1,slots=slots,derivedLegExtents=legSizes),observations=[
'完整读取HumanoidArmorModel与HumanoidArmorLayer，LayerDefinitions只读记录的两个范围，不称已读全部createRoots。原版玩家与细臂玩家分别注册skin模型，但内外盔甲注册复用同两个LayerDefinition；皮肤3px细臂不等于默认盔甲也自动变3px。默认盔甲图集64x32而skin64x64，不能把皮肤UV图当layer_1/layer_2直接复用。此为原版来源契约，非28套装备或1000参考门槛计数。',
'HumanoidArmorModel保留HumanoidModel标准体块，仅把两腿用tex(0,16)、4x12x4及pivotX±1.9替换，左腿mirror。腿deformation在全套deformation基础减.1，所以outer1→.9，inner.5→.4；derivedExtents只纯算术不是游戏渲染验收。结合framework012证明膨胀位置不改变UV净尺寸，不应为增加护甲厚度把像素UV也等比例拉大。',
'实际render顺序CHEST→LEGS→FEET→HEAD；只有LEGS走inner/layer_2，靴子仍outer/layer_1。setPartVisibility先全隐藏再按槽启用，胸不显示head/腿，裤显示body和腿，帽显示head+hat。不能把hat自动视作透明或保证不会与head叠图，实际PNG未读。',
'copyProperties及setPartVisibility发生在getArmorModelHook之前，hook返回任意Model后会直接用同一个返回对象绘base/染色overlay/trim/glint；新模型是否匹配可见槽、UV和姿态仍是扩展责任。不能把默认Humanoid条件推到所有Gecko/非人结构装备。',
'实际renderArmorPiece把hook结果局部变量声明为Model，调用明确走Model版renderTrim/renderGlint；源码另有A重载同名委派的表象，不据此误报本实际路径无限递归。trim通过inner/outer sprite.wrap消费模型0..1UV；base armorCutoutNoCull、glint独立renderType并复用模型，不能把图集sprite原坐标直接写进base armor PNG。',
'getArmorResource按材料名namespace、slot与overlay生成路径后交ForgeHooksClient改写，再按最终字符串缓存；拿到路径不证明实际资源存在或图案与名称相符。此补充没有复制任何作者材质、没有制作图像/覆盖模型、没有启动Java/游戏/声音或改屏幕存档。'
])
with zipfile.ZipFile(archive) as z:
 for f in files:assert (R/f['local']).read_bytes()==z.read(f['archiveEntry'])
 for r in records:assert '\n'.join(z.read(r['path']).decode().splitlines()[r['start']-1:r['end']]).strip()==r['source'].strip()
(D/'framework-supplement-016.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(files=len(files),fullMethods=len(records),sourceRanges=len(ranges),vanillaSlimUsesSameArmor=True,newReferenceCredit=0),ensure_ascii=False))
