"""Read only the already available mapped SOURCE archive; no production Jar/game access."""
from pathlib import Path
import json,hashlib,zipfile,sys,datetime
D=Path(__file__).resolve().parent;A=D.parent;R=A.parents[2];sys.path.insert(0,str(A));import record_source_methods as M
meta=json.loads((A/'framework-source-evidence-v54-20261031.json').read_text());archive=Path(meta['sourceArchive'])
assert archive.name.endswith('-sources.jar') and '1.20.1-47.4.10_mapped_official_1.20.1' in str(archive)
specs={
 'net/minecraft/client/model/geom/builders/CubeListBuilder.java':[('addBox',8),('texOffs',0)],
 'net/minecraft/client/model/geom/builders/CubeDefinition.java':[('bake',0)],
 'net/minecraft/client/model/geom/builders/LayerDefinition.java':[('create',0),('bakeRoot',0)],
 'net/minecraft/client/model/geom/builders/PartDefinition.java':[('addOrReplaceChild',0),('bake',0)],
 'net/minecraft/client/model/geom/ModelPart.java':[('Cube',0),('Polygon',0),('compile',1),('render',1),('translateAndRotate',0)],
 'net/minecraft/client/model/HumanoidModel.java':[('createMesh',0)]
}
files=[];records=[]
with zipfile.ZipFile(archive) as z:
 for path,spec in specs.items():
  data=z.read(path);t=M.parser.parse(data);nodes=[];todo=[t.root_node]
  while todo:
   n=todo.pop();todo.extend(reversed(n.children))
   if n.type in ('method_declaration','constructor_declaration'):nodes.append(n)
  dest=D/'framework-source-012'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  files.append({'archiveEntry':path,'local':str(dest.relative_to(R)),'sha256':hashlib.sha256(data).hexdigest(),'reviewMode':'SELECTED_FULL_METHODS_ONLY' if 'HumanoidModel' in path else 'READ_FULL_SOURCE_FILE_NO_COUNT'})
  for name,index in spec:
   ns=[n for n in nodes if n.child_by_field_name('name').text.decode()==name];n=ns[index];assert not n.has_error
   records.append({'path':path,'method':name,'index':index,'start':n.start_point.row+1,'end':n.end_point.row+1,'source':data[n.start_byte:n.end_byte].decode(),'sourceSha256':hashlib.sha256(data).hexdigest(),'countsTowardReferenceGate':False})
# Exact arithmetic derived from the read Cube constructor, not a rendering test.
u,v,w,h,depth=-17,94,14,0,17
a,b,c,d,e,f=u,u+depth,u+depth+w,u+depth+2*w,u+2*depth+w,u+2*depth+2*w
v0,v1,v2=v,v+depth,v+depth+h
faces={'DOWN':(b,v0,c,v1),'UP':(c,v1,d,v0),'WEST':(a,v1,b,v2),'NORTH':(b,v1,c,v2),'EAST':(c,v1,e,v2),'SOUTH':(e,v1,f,v2)}
arithmetic=[{'face':face,'pixelBounds':list(bounds),'uvAreaAbs':abs((bounds[2]-bounds[0])*(bounds[3]-bounds[1])),'normalizedBounds':[x/128 for x in bounds],'allCoordinatesWithinAtlas':all(0<=x<=128 for x in bounds)} for face,bounds in faces.items()]
assert {x['face'] for x in arithmetic if x['uvAreaAbs']>0}=={'UP','DOWN'}
assert all(x['allCoordinatesWithinAtlas'] for x in arithmetic if x['uvAreaAbs']>0)
dark=R/'build/creature-reference-1000/AlexModGuy__AlexsCaves/src/main/java/com/github/alexmodguy/alexscaves/client/model/layered/DarknessArmorModel.java';data=dark.read_bytes()
out={'status':'LOCAL_MAPPED_SOURCE_CONTRACT_SUPPLEMENT_NO_REFERENCE_CREDIT','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceArchive':str(archive),'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'artifactCoordinate':'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources','countsTowardReferenceGate':False,'newImplementations':0,'mainLedgerUpdated':False,'productionChanges':False,'networkRequests':0,'javaOrGameRun':False,'files':files,'records':records,'existingAssetSource':{'local':str(dark.relative_to(R)),'sourceSha256':hashlib.sha256(data).hexdigest(),'start':45,'end':51,'source':'\n'.join(data.decode().splitlines()[44:51]),'priorAcceptedRecord':'consolidated-reviewed.json:DarknessArmorModel.createArmorLayer; no new credit'},'derivedArithmetic':arithmetic,'observations':[
 '完整读取原版CubeListBuilder、CubeDefinition、LayerDefinition、PartDefinition和ModelPart，并完整读取HumanoidModel.createMesh；不把整个HumanoidModel其余方法说成已读。标准人形head8×8×8、body8×12×4、arms/legs4×12×4，各有固定texOffs和镜像腿臂；这是今后保持MC盔甲比例/UV契约的底层依据，不是当前制作授权。',
 'LayerDefinition.bakeRoot把图集宽高传给PartDefinition递归bake；CubeDefinition把图集尺寸乘texScale后送Cube。ModelPart.Polygon按该有效宽高归一化每顶点UV，mirror反转顶点序并反转normal.x；几何inflate发生在位置，UV净尺寸仍按原始宽高深。Cube.compile使用原有u/v实际提交。',
 'Darkness capeTail明确14×0×17、grow0、textureOffset(-17,94)、图集128×128。按已读Cube公式，DOWN正面积区域[0,94]到[14,111]，UP反向V区域[14,111]到[28,94]；其余四面V同为111。WEST虽U到-17，但该侧几何和UV均为零面积。因而先前保留的“负offset是否必定可见面越界”源码疑点可缩小：在此模型输入和1.20.1标准烘焙契约下，不构成两片有面积披风面UV越界；不因此宣称实际贴图接缝、过滤或游戏外观通过。',
 '此结论依赖grow0及已读MC1.20.1契约；非零inflate、另一个烘焙器/着色器、不同版本或动态修改模型需重核，不能推广为所有负UV均安全。原版archive是本地已有47.4.10源码来源，未宣称它与所有外部项目精确Forge补丁版一致。',
 '未把ironspell较新API里的cape texScale(1,.5)和本1.20.1源码当成精确版本调用链。没有修改旧主记录，只在独立目录保留可核查证据。'
]}
(D/'framework-supplement-012.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
# Verify extracted source bytes against the same existing SOURCE archive, plus AST bodies.
with zipfile.ZipFile(archive) as z:
 for f in files:assert (R/f['local']).read_bytes()==z.read(f['archiveEntry'])
 for rec in records:
  b=z.read(rec['path']);assert hashlib.sha256(b).hexdigest()==rec['sourceSha256'];assert '\n'.join(b.decode().splitlines()[rec['start']-1:rec['end']]).strip()==rec['source'].strip()
print(json.dumps({'status':out['status'],'frameworkFiles':len(files),'fullSelectedMethods':len(records),'positiveAreaFacesWithinAtlas':True,'newReferenceCredit':0,'sourceArchiveOnly':True},ensure_ascii=False))
