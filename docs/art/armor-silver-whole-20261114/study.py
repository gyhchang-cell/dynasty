from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,copy
D=Path(__file__).resolve().parent;P=D.parent/'armor-sanguine-whole-20261114';R=D.parents[2]
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
t=D/'source/src/main/resources/assets/caverns_and_chasms/textures'
rows=[copy.deepcopy(x) for x in json.loads((P/'slot-face-uv.json').read_text())['rows'] if '/' not in x['part']]
assert len(rows)==10
out=Image.new('RGBA',(1050,1000),(54,58,62,255));draw=ImageDraw.Draw(out)
for i,x in enumerate(rows):
 im=Image.open(t/f"models/armor/silver_layer_{x['layer']}.png").convert('RGBA');draw.text((5,i*100+5),x['slot']+' '+x['part'],fill='white')
 for j,f in enumerate(x['faces']):
  rect=f['raw_crop_rect'];assert 0<=rect[0]<rect[2]<=64 and 0<=rect[1]<rect[3]<=32
  crop=im.crop(rect);f['nontransparent_pixels']=sum(v>0 for v in crop.getchannel('A').get_flattened_data());f['pixels']=crop.width*crop.height
  px=180+j*140;draw.text((px,i*100+5),f['source_direction'],fill='white');out.alpha_composite(crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST),(px,i*100+25))
save('slot-face-uv.json',{'scope':'10 slot cube instances/60 raw face rectangles, not designs','consumer_context':'same MC1.20.1 mapped source in Forge47.4.10, not exact47.1.3 loaded binary','orientation':'signed UP V and mirror flags retained from source; crop sheet NOT final vertex orientation, seam or posed rendering','rows':rows})
out.save(D/'raw-slot-face-crops.png')
imgs=json.loads((D/'original-image-paths.json').read_text())
for a in imgs:a['sha256']=h(a['path'])
save('original-image-paths.json',imgs)
sourcepaths=['source/src/main/java/com/teamabnormals/caverns_and_chasms/core/registry/CCItems.java','source/src/main/java/com/teamabnormals/caverns_and_chasms/core/other/CCTiers.java','consumer/blueprint713/com/teamabnormals/blueprint/core/api/BlueprintArmorMaterial.java','consumer/forge4713/net/minecraftforge/client/extensions/common/IClientItemExtensions.java','consumer/forge4713/patches/net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java.patch','consumer/forge4713/net/minecraftforge/common/extensions/IForgeItem.java','consumer/forge4713/net/minecraftforge/client/ForgeHooksClient.java']
reused=[{'path':str(P/n),'sha256':h(P/n)} for n in sourcepaths]
cp=json.loads((P/'consumer-provenance.json').read_text());reused+=cp['reused_MC_context'];save('consumer-reuse.json',{'sources':reused,'exact_Forge_version':'47.1.3 source checksum previously verified','Blueprint':'7.1.3 archive local SHA pinned; upstream checksum403, not independently checksum verified','MC_context':'1.20.1 Forge47.4.10 mapped source only; no loaded47.1.3 binary','source_registration_chain':'reuse D83 helper/register and source root proof; static chain only'})
L=json.loads((P/'combined-semantic-ledger.json').read_text());closest=[x for x in L['groups'] if x['semantic_group'] in ['souls_silver_enclosed_plate_family','iron_closed_plate','deepsilver_compact_center_plate','gem_plate_metal_variants'] or ('iron' in x['semantic_group'] and 'plate' in x['semantic_group'])]
save('historical-group-comparison.json',{'all_group_names_screened':len(L['groups']),'all_case_keys_screened':len(L['reviewed_case_keys']),'closest_stored_observations_read':closest,'whole_keys_screened':L['reviewed_pending_whole_keys'],'conservative_assignment':'silver enclosed plate overlaps old closed-face metal/vanilla-outline families; different repository/material is not semantic novelty','new_validated_credit':0,'old_PNG_reopened':False})
save('four-slot-source-binding.json',{'whole_key':'caverns_and_chasms:silver/default_untrimmed','material':'CCArmorMaterials.SILVER / BlueprintArmorMaterial(caverns_and_chasms:silver)','item_class':'SilverArmorItem extends ArmorItem; only constructor and attribute modifier override, no custom model/texture override','slots':{'HEAD':{'item':'caverns_and_chasms:silver_helmet','layer':1,'visible':['head','hat']},'CHEST':{'item':'caverns_and_chasms:silver_chestplate','layer':1,'visible':['body','right_arm','left_arm']},'LEGS':{'item':'caverns_and_chasms:silver_leggings','layer':2,'visible':['body','right_leg','left_leg']},'FEET':{'item':'caverns_and_chasms:silver_boots','layer':1,'visible':['right_leg','left_leg']}},'texture_fallback':'Forge material namespace + silver_layer_1 or2; IForgeItem default null; default IClientItemExtensions model returned','recipes':'4 native shaped recipes use forge:ingots/silver tag; native acquisition/tag resolving/runtime not accepted','trim':'4 base icons each10 predicate overrides; trim variants neither viewed nor counted','runtime_accepted':False})
print('rows',len(rows),'faces',sum(len(x['faces']) for x in rows),'transparent_hat',sum(f['nontransparent_pixels']==0 for x in rows if x['part']=='hat' for f in x['faces']))
