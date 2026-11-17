from pathlib import Path
import json,hashlib,math
from PIL import Image
B=Path(__file__).resolve().parent;root=Path.cwd();names=['evocation_robes','mercenary','reinforced_mail'];slots=['helmet','chestplate','leggings','boots'];R=B/'source/src/main/resources/assets/dungeons_gear';G=B/'source/src/generated/resources/assets/dungeons_gear';prior=root/'docs/art/armor-bumblebee-whole-20261114/combined-semantic-ledger.json';old=json.loads(prior.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
rows=[]
for n in names:
 geo=json.loads((R/'geo/armor'/f'{n}_armor.geo.json').read_text());assert len(geo['minecraft:geometry'])==1;g=geo['minecraft:geometry'][0];desc=g['description'];atlas=R/'textures/models/armor'/f'{n}_armor.png'
 with Image.open(atlas) as im:assert im.size==(desc['texture_width'],desc['texture_height'])
 bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones']);boxes=[]
 for bone in g['bones']:
  if 'parent' in bone:assert bone['parent'] in bones
  chain=set();p=bone
  while 'parent' in p:
   assert p['name'] not in chain;chain.add(p['name']);p=bones[p['parent']]
  for i,c in enumerate(bone.get('cubes',[])):
   assert len(c['size'])==3 and all(math.isfinite(v) and v>=0 for v in c['size']);assert isinstance(c['uv'],list)
   u,v=c['uv'];w,h,d=c['size'];bounds=[u,v,u+2*(w+d),v+d+h];assert 0<=u<=bounds[2]<=desc['texture_width'] and 0<=v<=bounds[3]<=desc['texture_height'],(n,bone['name'],i,bounds)
   boxes.append({'bone':bone['name'],'index':i,'source_cube':c,'nominal_box_net_bounds':bounds})
 item_rows=[]
 for slot in slots:
  model=G/'models/item'/f'{n}_{slot}.json';m=json.loads(model.read_text());assert m['parent']=='minecraft:item/generated';assert m['textures']=={'layer0':f'dungeons_gear:item/armor/{n}_{slot}'}
  tex=R/'textures/item/armor'/f'{n}_{slot}.png';assert tex.exists()
  with Image.open(tex) as im:size=im.size;alphas=im.convert('RGBA').getchannel('A').getextrema()
  item_rows.append({'slot':slot,'id':f'dungeons_gear:{n}_{slot}','native_size':size,'alpha_range':alphas,'model_path':str(model.relative_to(B)),'texture_path':str(tex.relative_to(B))})
 config=json.loads((B/'source/src/main/resources/data/dungeons_gear/gearconfig/armor'/f'{n}_armor.json').read_text())
 rows.append({'whole_key':f'dungeons_gear:{n}/default_config','design':n,'slots':item_rows,'gear_config':config,'geo_description':desc,'bones':g['bones'],'boxes':boxes,'box_count':len(boxes),'binding_status':'ItemInit registers four actual ArmorGear items and explicit matching geo/texture/default animation. Separate consumer branch source context is version3.0.12 vs requested3.0.10, so full consumer binary equivalence not proven.'})
save('three-whole-bindings.json',{'scope':'Fixed source resources and declarations; no runtime/final UV projection','box_net_check':'Nominal Bedrock list-UV bounding-net extents only; NOT signed faces/mirroring/inflate/pivot/pose/final projected UV proof','designs':rows})
obs={
'evocation_robes':{
 'read':'宽沿蓝帽、棕帽带和单个亮黄扣；胸部大蓝底配两条黄衣缘与暗红中襟，裤为棕腰蓝直腿，靴为棕筒与亮黄上口，材料分区清楚且没有满幅金纹。原生穿戴图160×65，不能套标准64×32。',
 'limit':'帽檐16×1×16和高帽8×14×8、折顶8×8×4是法师职业专属比例；长胸襟不能当普通短宽胸甲模板。靴口高亮近火焰，普通布甲不学发光效果。',
 'old_groups':['wizard_hat_robe_variants','immersive_robe_open_front'],
 'dedup':'此前铁魔法/巫师帽袍已有大底布+窄衣缘原则；此次新来源的折顶帽与黄蓝暗红组合不自动产生语义信用，保守保留为同类候选/对照。'},
'mercenary':{
 'read':'倒U灰盔有一条短亮鼻梁；不对称单肩钢片、大片棕皮背片、斜胸护片与腰带构成材料主次，裤图标只画两块灰膝片，双靴为直灰筒。配置明确heavy_plate，不因棕色连接编成皮甲。',
 'limit':'护腿图标缺少腰与直腿，是本项目普通裤甲辨识度反例；不对称肩只适用于获授权特色装备，不以大肩片统改认可稿。',
 'old_groups':['complete_hard_leather_metal_shoulders'],
 'dedup':'旧hard_leather已有棕皮/灰肩和膝片；本次单侧肩臂结构与28度独立胸子骨可作区别候选，仍需完整旧图语义比较，不能按命名空间新就加信用。'},
'reinforced_mail':{
 'read':'灰盔额前横条与两侧护颊保持面孔开口；胸由深浅灰锁网、窄纵金属带、下缘棕带组织；靴为两枚灰护片。穿戴图96×64，胸双5×4×2小护片附在主体，四肢仍长方体。',
 'limit':'裤图标只是棕色腰带，靴图标短扁，均不适合作为用户要求的完整MC腿/短直靴比例模板。锁网细棋盘只作为材质区域例，不能给布皮甲加密噪点。',
 'old_groups':['magistu_chainmail_rust_family'],
 'dedup':'与旧包头锁甲/皮边的粗网格有明显重叠，新胸分片不能自行证明新完整设计。保留候选与反例，不记新已验收信用。'}}
casekeys=[];reviewrows=[]
for n in names:
 key=f'dungeons_gear:{n}/default_config';casekeys.append(key);assert key not in old['reviewed_pending_whole_keys'];assert not any(k.startswith('dungeons_gear:') for k in old['reviewed_case_keys'])
 related=[]
 for gn in obs[n]['old_groups']:
  group=next(g for g in old['groups'] if g['semantic_group']==gn);related.append({'group':gn,'cases':group['cases'],'observation_read':group['observations'][:1]})
 reviewrows.append({'whole_key':key,'whole_slots':4,'observations':obs[n],'prior_related_records_read':related,'new_validated_credit':0,'semantic_novelty':'UNACCEPTED; actual design overlap with old groups requires independent review','applicability':'Material/edge contrast/MC item readability reference and limitations only; not license to redraw approved priority targets'})
review={'batch':'D88','status':'THREE_NEW_SOURCE_WHOLE_REFERENCES_ACTUALLY_VIEWED_PENDING_ACCEPTANCE','new_source_whole_cases':3,'new_independently_accepted_designs':0,'new_learning_groups':0,'whole_slots_not_separate_designs':True,'native_png_viewed':15,'viewed_pages':['evocation_robes-source-study.png','mercenary-source-study.png','reinforced_mail-source-study.png'],'design_reviews':reviewrows,'requirements':{'global_sha256':sha(B/'global-texture-requirements.txt'),'project_sha256':sha(B/'project-texture-requirements.txt'),'targets':'70 armor priority resources unchanged; no target proven both never-redrawn and crude','actual_production':False},'source_versions':{'gear':'5.0.6-beta / MC1.19.2 / Forge43.2.8 / GeckoLib3.1.40 / requests Libraries3.0.10-beta','consumer_context':'Libraries3.0.12-beta / MC1.19.2 / Forge43.2.8 / GeckoLib3.1.39; NOT proved equal to requested binary'},'global_gate':{'met':False,'accepted_total':None,'remaining_gap':None},'pending':['Independent source and semantic applicability acceptance','Exact requested Libraries3.0.10 and Gecko3.1.40 consumer/binary match','Slot visibility/final signed UV/mirror/pose/seams/fiveviews and silhouette in real client','Native materials/loot/acquisition/payment not verified','No priority target yet justified for redraw','Global1000 accepted applicable independent total and exact gap unverified']}
save('semantic-review.json',review)
new=json.loads(prior.read_text());new['current_batch_prior']={'path':str(prior),'sha256':sha(prior)}
for key in casekeys:
 new['reviewed_pending_whole_keys'].append(key);new['pending_whole_families'].append({'primary_whole_key':key,'review':str(B/'semantic-review.json'),'sha256':sha(B/'semantic-review.json'),'already_recorded_case':None,'whole_slots':4,'new_learning_groups':0,'new_validated_credit':0,'pending':review['pending']})
save('combined-semantic-ledger.json',new);print([(r['design'],r['box_count']) for r in rows])
