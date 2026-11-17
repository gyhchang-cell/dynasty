from pathlib import Path
import json,hashlib,re
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 page=json.loads((D/'page.json').read_text());reg=(D/'BloodMagicItems.bytecode.txt').read_text();verbose=(D/'BloodMagicItems.verbose.txt').read_text();armor=(D/'ItemLivingArmor.bytecode.txt').read_text();chains=[]
 for i,(suffix,typ,field) in enumerate([('helmet','HELMET','HELMET'),('plate','CHESTPLATE','PLATE'),('leggings','LEGGINGS','LEGGINGS'),('boots','BOOTS','BOOTS')]):
  bootstrap=97+i;method=93+i
  boot=re.search(r'^  '+str(bootstrap)+r':.*?(?=^  \d+:|\Z)',verbose,re.M|re.S).group();assert f'lambda$static${method}:' in boot
  func=re.search(r'private static net.minecraft.world.item.Item lambda\$static\$'+str(method)+r'\(\);.*?(?=\n  (?:private|public|static)|\Z)',reg,re.S).group();assert 'class wayoftime/bloodmagic/common/item/ItemLivingArmor' in func and f'ArmorItem$Type.{typ}:' in func
  registration=re.search(r'// String living'+suffix+r'\n.*?putstatic.*?// Field LIVING_'+field+':[^\n]*',reg,re.S).group();assert f'InvokeDynamic #{bootstrap}:get:' in registration
  model=D/f'source/assets/bloodmagic/models/item/living{suffix}.json';j=json.loads(model.read_text());assert j['textures']=={'layer0':f'bloodmagic:item/living{suffix}'};icon=D/f'source/assets/bloodmagic/textures/item/living{suffix}.png';wear=D/f'source/assets/bloodmagic/models/armor/livingarmour_layer_{2 if suffix=="leggings" else 1}.png'
  chains.append({'id':'bloodmagic:living'+suffix,'slot':typ,'bootstrap':bootstrap,'supplier_method':f'lambda$static${method}','registration_excerpt':registration,'supplier_excerpt':func,'item_model':str(model.relative_to(R)),'icon':str(icon.relative_to(R)),'wear_texture':str(wear.relative_to(R)),'input_hashes':{str(p.relative_to(R)):sha(p) for p in [model,icon,wear]},'runtime_acceptance':False})
 assert 'bloodmagic:models/armor/livingarmour_layer_1.png' in armor and 'bloodmagic:models/armor/livingarmour_layer_2.png' in armor
 page['actually_viewed']=True;page['prior_three_icons_reused_not_new_names']=True
 out={'scope':'Previously partial bloodmagic:living now complete four-part source-image and static register/type/texture chain','case_key':'bloodmagic:living','page_actually_viewed':page,'four_part_chains':chains,'actual_read':['BloodMagicItems static register namespace and four living entries','BootstrapMethods97..100 and supplier methods93..96','ItemLivingArmor constructor and full getArmorTexture','four complete inventory model JSON','six native images via page'],'observations':['新补胸甲：深红短宽胸片、内侧暗区、金色短横带及浅红肩线，与头盔金面框、裤腰红带和靴金护胫相连；不是完整人物插画。','L1正背/臂/靴为暗红大块，金条只占有限边区；L2腰和两腿以暗棕分开并在膝下留连续红横带。可借鉴同材质大分区与克制点缀，不复制其具体带纹。','前三图与历史SHA相同，本批有效新图阅读是胸甲及L1/L2；一套设计只升级完整性，不将六PNG、四部位或旧图复读当新增设计。'],'conditions':['getArmorTexture按实际Item对象身份选择：头/胸/靴L1，裤L2，否则null；不是臆造按槽字符串。','通过javap只读反汇编固定class，无加载或执行模组类；不是Java游戏/原生运行验收。','未排除外部图层或可选集成，不宣称完整实机穿戴。','旧sentient仅有残留像素/工具记录，本批未找到其四个物品模型或盔甲类；不能用遗留PNG认定当前可获得整套。仅记录边界，不对游戏提修复。'],'new_names':0,'new_conservative_learning_groups':0,'new_validated_independent_design_credit':0,'one_existing_partial_case_completed_static':True,'reference_gate_met':False,'game_acceptance':False,'production_changes':0}
 (D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Living4 static chains closed,1existing partial case completed; no new name/design credit.')
if __name__=='__main__':main()
