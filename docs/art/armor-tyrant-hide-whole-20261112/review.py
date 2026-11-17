"""Bounded native source review only: no mod/game execution or production asset writes."""
from pathlib import Path
import hashlib,json,re,zipfile
from PIL import Image
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bc(n):return (B/'bytecode/net/mayoi/radiationzonereborn'/n).read_text()
def body(t,name):
 s=t.index(' '+name+'(');s=t.index('    Code:',s);e=t.index('      LineNumberTable:',s);return t[s:e]
p=json.loads((B/'provenance.json').read_text());assert sha(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:
 for n,h in p['entries'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h==sha(B/'source'/n)
for n,h in p['disassemblies'].items():assert sha(B/n)==h
reg=bc('init/RadiationZoneRebornModItems.class.txt');static=reg[reg.index('  static {};'):reg.index('BootstrapMethods:')]
assert '// String radiation_zone_reborn' in static and 'DeferredRegister.create:' in static
maps={'Helmet':{'head':'Head'},'Chestplate':{'body':'Body','left_arm':'LeftArm','right_arm':'RightArm'},'Leggings':{'left_leg':'LeftLeg','right_leg':'RightLeg','body':'Body2'},'Boots':{'left_leg':'LeftLeg2','right_leg':'RightLeg2'}}
rows=[]
for i,(part,cls,slot) in enumerate([('helmet','Helmet','HELMET'),('chestplate','Chestplate','CHESTPLATE'),('leggings','Leggings','LEGGINGS'),('boots','Boots','BOOTS')]):
 m=re.search(r'String tyrant_skin_armor_'+part+r'\n.*?InvokeDynamic #(\d+):get',static,re.S);assert int(m[1])==121+i
 boot=re.search(r'\n  '+str(121+i)+r':.*?(?=\n  \d+:|\Z)',reg[reg.index('BootstrapMethods:'):],re.S).group(0)
 assert f'REF_newInvokeSpecial net/mayoi/radiationzonereborn/item/TyrantSkinArmorItem${cls}."<init>"' in boot
 t=bc(f'item/TyrantSkinArmorItem${cls}.class.txt');own=t[t.index('\n{'):];assert f'ArmorItem$Type.{slot}:' in own
 tex=body(t,'getArmorTexture');assert '// String radiation_zone_reborn:textures/entities/tyrant_skin_armor_layer.png' in tex and 'areturn' in tex
 assert f'TyrantSkinArmorItem${cls}$1' in body(t,'initializeClient') and 'Consumer.accept:' in body(t,'initializeClient')
 ext=body(bc(f'item/TyrantSkinArmorItem${cls}$1.class.txt'),'getHumanoidArmorModel')
 fields=re.findall(r'getfield\s+#[^\n]+// Field net/mayoi/radiationzonereborn/client/model/Modeltyrant_skin_armor\.(\w+):',ext)
 assert fields==list(maps[cls].values())
 # Confirm preceding native target key and layer bake call for each nonempty part.
 cursor=0
 for key,field in maps[cls].items():
  start=ext.index('// String '+key,cursor);end=ext.index('Modeltyrant_skin_armor.'+field+':',start)
  assert 'Modeltyrant_skin_armor.LAYER_LOCATION:' in ext[start:end] and 'EntityModelSet.m_171103_:' in ext[start:end];cursor=end
 icon=json.loads((B/f'source/assets/radiation_zone_reborn/models/item/tyrant_skin_armor_{part}.json').read_text());assert icon['textures']['layer0']==f'radiation_zone_reborn:item/tyrant_skin_{part}'
 rows.append({'id':f'radiation_zone_reborn:tyrant_skin_armor_{part}','bootstrap_direct_constructor':121+i,'armor_type':slot,'custom_part_mapping':maps[cls],'texture':'radiation_zone_reborn:textures/entities/tyrant_skin_armor_layer.png','icon':icon['textures']['layer0']})
mod=bc('init/RadiationZoneRebornModModels.class.txt');assert re.search(r'Modeltyrant_skin_armor.LAYER_LOCATION:.*?InvokeDynamic #46:get:.*?registerLayerDefinition:',body(mod,'registerLayerDefinitions'),re.S)
boot=re.search(r'\n  46:.*?(?=\n  \d+:|\Z)',mod[mod.index('BootstrapMethods:'):],re.S).group(0);assert 'Modeltyrant_skin_armor.createBodyLayer:' in boot and '.CLIENT' in mod and '.MOD' in mod
model=bc('client/model/Modeltyrant_skin_armor.class.txt');factory=body(model,'createBodyLayer');assert re.search(r'sipush\s+128\n.*bipush\s+64\n.*LayerDefinition.m_171565_',factory)
lines=factory.splitlines();uv=[];part=None
def integer(s):
 m=re.search(r'iconst_(\d+)',s)
 return int(m[1]) if m else int(re.search(r'(?:bipush|sipush)\s+(-?\d+)',s)[1])
for i,l in enumerate(lines):
 m=re.search(r'// String (\w+)',l)
 if m:part=m[1]
 if 'CubeListBuilder.m_171514_:(II)' in l:uv.append({'declared_child':part,'uv':[integer(lines[i-2]),integer(lines[i-1])],'instruction_offset':int(l.split(':',1)[0])})
assert [r["uv"] for r in uv]==[[0,48],[0,32],[32,56],[32,56],[32,56],[32,56],[0,16],[0,0],[41,0],[25,0],[41,0],[25,0],[64,0],[64,12],[64,12],[96,9],[96,0],[96,9],[96,0]]
for field in ['Head','Body','RightArm','LeftArm','Body2','RightLeg','LeftLeg','RightLeg2','LeftLeg2']:
 assert '// String '+field in factory
images={n:list(Image.open(B/'source'/n).size) for n in p['entries'] if n.endswith('.png')};assert len(images)==5
assert images['assets/radiation_zone_reborn/textures/entities/tyrant_skin_armor_layer.png']==[128,64]
base=json.loads((ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert all(sha(ROOT/n)==h for n,h in base.items())
s={'case':'radiation_zone_reborn:tyrant_skin_armor','bindings':rows,'native_images_actually_viewed':images,'view_page':'whole-native-source.png','uv_starts_not_face_acceptance':uv,'model_size':[128,64],'model_event_bootstrap':46,'observations':['暗苔绿皮革作大主面，白骨集中头口、胸V边、肩与靴口，软皮承托硬骨，不把骨白高光铺满全身。','库存胸甲短宽但外沿锯齿更强；裤脚和靴口都有白边，需要靠实际专用腿/靴UV分开，而不是从图标猜同一模型。','Body与Body2分别给胸和裤腰；LeftLeg/RightLeg与LeftLeg2/RightLeg2分给裤和靴，同一128×64并不等于相同取样。','128×64图集上白骨条有明确皮革相邻区；部分灰绿小块较散，修普通皮甲不照搬杂点。只学习皮/骨的材料面积与收边，不复制原图。'], 'semantic_dedup':{'existing_case':True,'existing_group':'creature_hide_shell_vests','new_names':0,'new_groups':0,'new_validated_design_credit':0},'applicability':'未修皮/布袖口及织锦材料范围：借材料边界结束方式，保留获选图标；骨片不是所有布皮甲的通用装饰。','limits':['Layer and consumers are static source declarations, not actual event/bake/hook runtime acceptance','19 UV starts and nine native root parts do not prove full per-face UV, world transforms, seams or visual wearing','same whole armor already in pool; components and alias do not add design credits','No production art or main checklist edits; validated applicable1000 gate unmet']}
emit('whole-reference-study.json',s)
emit('verification.json',{'result':'PASS_BOUNDED_STATIC_WHOLE_SOURCE','native_entries':len(p['entries']),'actual_native_png_viewed':5,'four_slot_consumers':4,'custom_root_parts_used':9,'uv_starts_not_designs':len(uv),'protected_paths_unchanged':len(base),'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0})
print('PASS 22 native entries / 5 viewed PNG / four custom consumers / 19 UV starts / 289 protected')
