from pathlib import Path
from PIL import Image
import json,hashlib,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;R=D.parents[2];P=D.parent/'armor-material-resolver-20261114'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,a):(D/n).write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
L=json.loads((P/'combined-semantic-ledger.json').read_text());key='enderio:dark_steel/default_unpainted_no_faceplate'
assert not any(k.startswith('enderio:') for k in L['case_to_group']);assert key not in L['reviewed_pending_whole_keys']
S=D/'source/enderio-base/src/main';J=S/'java/crazypants/enderio';T=S/'resources/assets/enderio'
slots={'helmet':'HEAD','chestplate':'CHEST','leggings':'LEGS','boots':'FEET'}
rows=[]
for part,slot in slots.items():
 model=T/f'models/item/item_dark_steel_{part}.json';m=json.loads(model.read_text());assert m['parent']=='item/generated' and m['textures']['layer0']==f'enderio:items/item_dark_steel_{part}'
 rows.append({'id':f'enderio:item_dark_steel_{part}','slot':slot,'model':str(model),'model_sha256':h(model),'icon':str(T/f'textures/items/item_dark_steel_{part}.png'),'default_worn_texture':f'enderio:textures/models/armor/dark_steel_layer_{2 if part in ["helmet","leggings"] else 1}.png','model_default':'Item callback null -> ForgeHooksClient keeps passed default; exact ModelBiped box/face and slot visibility not studied here'})
save('four-slot-source-binding.json',{'key':key,'source_version':{'minecraft':'1.12.2','forge':'14.23.5.2847','endercore':'1.12.2-0.5.76'},'slots':rows,'non_default_routes':{'upgraded_helmet':'NightVision OR SoundDetector hasUpgrade => texture1','painted_helmet':'PaintUtil.hasPaintSource OR DSPAINT subcompound => PaintedHelmetLayer.no_render; item paint drawn separately at HEAD with bipedHead.postRender(.0625), translation/rotation/negative scale','end_steel_and_stellar':'same ItemDarkSteelArmor factory class, but not selected/studied as additional families'},'texture_route_condition':'getArmorTexture tests instance armorType, not passed slot; valid native equipment context assumed, not arbitrary mismatched slots','consumer':'exact declared Forge2847 LayerBipedArmor hook -> ForgeHooksClient model null fallback; LayerArmorBase -> ForgeHooksClient item texture return or default; no runtime/binary guarantee'})
root=ET.parse(T/'config/recipes/items.xml').getroot();recipes=[]
for r in root.iter('recipe'):
 out=r.find('./crafting/output')
 if out is not None and out.get('name') in [x['id'] for x in rows]:
  grid=r.find('./crafting/grid');recipes.append({'name':r.get('name'),'required':r.get('required'),'output':out.attrib,'grid_size':grid.get('size'),'cells':[x.attrib for x in grid]})
assert len(recipes)==4
save('native-recipe-declarations.json',{'recipes':recipes,'limit':'XML declaration only; DARK_STEEL alias parser/material origin and actual crafting acquisition not closed'})
a=Image.open(T/'textures/models/armor/dark_steel_layer_1.png').convert('RGBA');b=Image.open(T/'textures/models/armor/dark_steel_layer_2.png').convert('RGBA')
# Flat raw atlas region, deliberately no face/UV orientation claim without exact ModelBiped source.
rect=(0,0,32,16);aa=a.crop(rect);bb=b.crop(rect)
save('raw-head-region-comparison.json',{'rectangle':rect,'label':'raw upper-left atlas region, not declared face mapping or final head rendering','layer1_alpha_nonzero':sum(x>0 for x in aa.getchannel('A').getdata()),'layer2_alpha_nonzero':sum(x>0 for x in bb.getchannel('A').getdata()),'different_RGBA_pixels':sum(x!=y for x,y in zip(aa.getdata(),bb.getdata())),'not_claimed':'No fixed face boxes, top/chin mapping, mirrored seam or five-view wearing accepted'})
near=['souls_black_knight_dark_silhouette','complete_mechanized_dark_frame','cursed_knight_closed_visor','material_layout_skull_vent_metal_family','black_iron_buckled_vest','knight_metal_color_family']
save('historical-group-comparison.json',{'ledger':str(P/'combined-semantic-ledger.json'),'sha256':h(P/'combined-semantic-ledger.json'),'all_group_names_screened':len(L['groups']),'all_case_keys_screened':len(L['case_to_group']),'closest_stored_observations':[g for g in L['groups'] if g['semantic_group'] in near],'decision':'No new learning group or accepted credit; compact dark metal, V chest and small face band overlap existing groups. Source consumer difference is not semantic novelty.','scope':'Stored observations and registry screened; not claiming all historic PNG reopened'})
comparisons=[]
for k in L['reviewed_pending_whole_keys']:
 if k in ['eidolon:silver','thebetweenlands:syrmorite','thebetweenlands:valonite','tconstruct:plate/chosen_iron_leather']:
  reason='最接近的金属甲：短宽胸/分腿靴语言重合。银甲专用guard/短肩、板甲maille/plating分层或宝石变体属于来源具体差异，不能据此断言黑钢独立。'
 elif k=='oreganized:electrum/winged_gold_custom_uv':reason='短宽金属甲共有；翼冠/靴翼与黑钢紧凑无翼轮廓不同，但金/黑色差异不单独计设计。'
 elif k.startswith('thermal:') or k=='ad_astra:basic_space_suit':reason='整套功能防护语言有交集；防化、蜂网、宇航头罩的用途结构不同。黑钢升级面甲/染绘只是本套状态，不因功能拆成多套。'
 elif k.startswith('tconstruct:travelers') or k=='wizards_reborn:inventor_wizard' or k=='embers:ashen':reason='护目/功能配件有局部交集；皮革旅行服或发明家衣袍的主材/衣摆不同。不能只由护目形状给黑钢新套信用。'
 elif k in ['forbidden_arcanus:tyr','forbidden_arcanus:draco_arcanus','forbidden_arcanus:mortem','wizards_reborn:arcane_gold','wizards_reborn:arcane_fortress','thebetweenlands:ancient','atum:ra_atem_ceremonial_family']:reason='高级金属/仪式甲已有整体记录；黑钢低装饰紧凑轮廓与其材料/冠饰不同，仍须联合旧黑骑士族独立审查。'
 else:reason='已有整套的布、皮、毛、木、骨或水生主体记录保留；黑钢材质用途不同，材质差异本身不足新语义信用。'
 comparisons.append({'prior_whole_key':k,'comparison':reason,'prior_evidence_reused_not_reset':True})
for x in L.get('pending_whole_configurations',[]):comparisons.append({'prior_whole_key':x['configuration_key'],'comparison':'全九模块重甲与默认黑钢都是四槽装备；模块组合/铁色/几何数量不构成额外套装。没有重开或另计旧模型。'})
save('complete-old-whole-dedup.json',{'prior_keys_count':len(L['reviewed_pending_whole_keys']),'comparisons':comparisons,'accepted_whole_carry':L['local_independently_accepted_whole_families'],'not_new': ['4 equipment slots','6 native PNG','2 worn atlas layers','upgraded faceplate state','painted block/item helmet state','end/stellar material variants','source file/hash count'],'conclusion':'One newly studied whole source configuration, at most one pending candidate, zero new validated designs; historical dark-knight/mechanized overlap unresolved.','not_claimed':'This compares the complete old whole registry and stored observations; no claim all old native PNG or final game appearances re-viewed'})
print({'native_recipe_declarations':len(recipes),'old_whole_keys':len(comparisons),'native_png':6,'new_credit':0})
