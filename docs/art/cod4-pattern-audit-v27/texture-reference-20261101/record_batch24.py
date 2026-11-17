"""Reviewed relief faces + exact source atlas crops, not architecture/model production."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageOps,ImageDraw
from zipfile import ZipFile
import hashlib,json
D=Path(__file__).resolve().parent;rows=json.loads((D/'batch-24-candidates.json').read_text())['rows']
notes=[
'正面六档灰绿：上宽方折、下横梁与小格，阴槽比正面略深，不靠纯黑勾每个小像素。',
'背面大暗竖龛与窄边，中部留大整面，顶部两角阶梯收拢；与正面密纹分主次。',
'左侧单枚深眼、短吻、外绕方折卷纹，龙头身份用眼/吻/方角组织；不复制作者龙纹。',
'右侧与左侧解码RGBA完全水平镜像；不是第二个龙纹案例，非对称字形不得套此镜像法。',
'顶面五档灰绿，宽U折与中央短横，边框留足宽度，与细密鳞片堆砌不同。',
'底面与背面同竖龛语汇，灰阶细节不同但同一物件，不增加新设计。',
'64px图集包含相同16px六面岛，源模型有负向UV；不是第二只龙雕/第二栋建筑。读到item/blockstate均引用六面版本，未证该额外模型运行时使用。',
'普通石材用宽暗横槽和两三片灰绿碎面，噪点克制；只有材料参考，不充纹样身份。',
'方框内上方W形压槽、下方深块台阶，单个大主纹比多层小金边更易读。',
'几重近方形回折环绕中央小孔，粗暗槽与浅受光边分开；是单幅石刻，不是完整相关建筑。',
'十字宽槽分四象限，中央小方孔与外窄方框，和多环回折的留白组织不同。',
'与无苔四分砖相同主槽和大石片，局部加粗绿色苔块，换材/覆苔合并。',
'四块大石片以粗十字暗槽分隔，只少量灰绿阶梯纹，不称四个符。']
for idx,(r,note) in enumerate(zip(rows,notes)):
 n=int(r['reference_id'].split('-')[1]);im=Image.open(r['local_path']).convert('RGBA');pix=list(im.get_flattened_data())
 if n<=934:family,rep='samurai-dragon-stone-six-surface-relief',928
 elif n==935:family,rep='EXCLUDE_PLAIN_STONE_BASE',None
 elif n==936:family,rep='samurai-stone-w-notch',936
 elif n==937:family,rep='samurai-stone-stepped-nested-square',937
 elif n==938:family,rep='samurai-stone-cross-center-hole',938
 else:family,rep='samurai-stone-four-panel-cross',939
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',semantic_family=family,scope='surface_pattern_context',distinct_family_proposed_credit=int(n==rep),observation_zh=note,
 source_alpha_bbox=im.getchannel('A').getbbox(),source_partial_alpha_pixels=sum(0<p[3]<255 for p in pix),source_nonzero_alpha_pixels=sum(p[3]>0 for p in pix),
 applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0,limitation='只研究纹理主次/硬边/留白及来源UV，13PNG合5背景族不充1000建筑或装备案例，不复制纹理/模型。')
 if rep:r['family_representative']=f'VIS-{rep:03}'
(D/'review-batch-24.json').write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=13,proposed_distinct_design_families=5,coordinator_accepted_new_visual_credit=0,production_gate_met=False,policy='All2overview and4integer-detail pages actually opened. Six faces+atlas merge; moss variant merges. No architecture credit.',rows=rows),ensure_ascii=False,indent=2)+'\n')
chain=json.loads((D/'batch24-primary-model-chain.json').read_text());m=chain['models'][3]['content'];im=Image.open(rows[6]['local_path']).convert('RGBA')
comparisons=[];canvas=Image.new('RGB',(650,1240),(60,66,70));draw=ImageDraw.Draw(canvas);draw.text((10,6),'PRIMARY SOURCE PIXELS / signed atlas crop vs named face / NO GAME',(255,255,255))
refs={'north':928,'east':931,'south':929,'west':930,'up':932,'down':933}
for i,(face,source) in enumerate(m['elements'][0]['faces'].items()):
 u0,v0,u1,v1=source['uv'];sx=im.width/16;sy=im.height/16;bounds=[int(min(u0,u1)*sx),int(min(v0,v1)*sy),int(max(u0,u1)*sx),int(max(v0,v1)*sy)];patch=im.crop(bounds)
 if u1<u0:patch=ImageOps.mirror(patch)
 if v1<v0:patch=ImageOps.flip(patch)
 ref=next(r for r in rows if r['reference_id']==f'VIS-{refs[face]}');target=Image.open(ref['local_path']).convert('RGBA')
 ops=[('same',patch),('rotate180',patch.transpose(Image.Transpose.ROTATE_180))];match=next((name for name,img in ops if img.tobytes()==target.tobytes()),None);assert match
 comparisons.append(dict(face=face,source_model_entry=chain['models'][3]['entry'],uv=source['uv'],png_dimensions=list(im.size),pixel_bounds=bounds,flip_u=u1<u0,flip_v=v1<v0,signed_crop_rgba_sha256=hashlib.sha256(patch.tobytes()).hexdigest(),named_reference=ref['reference_id'],named_face_match_after=match))
 y=30+i*200;draw.text((10,y),face+' / signed crop',(255,255,255));draw.text((310,y),ref['reference_id']+' / named source / match:'+match,(255,255,255))
 canvas.paste(patch.resize((160,160),Image.Resampling.NEAREST),(10,y+24));canvas.paste(target.resize((160,160),Image.Resampling.NEAREST),(310,y+24))
sheet=Path('build/art-reference-20261101/batch24-signed-atlas-comparison.png');canvas.save(sheet)
old=[r for p in D.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']];jar=next(r['jar'] for r in old if Path(r.get('jar','')).name=='client.jar');entry='assets/minecraft/models/block/cube.json'
with ZipFile(jar) as z:data=z.read(entry)
dst=Path('build/art-reference-20261101/batch24-resource')/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
(D/'batch24-face-correspondence.json').write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),source_comparisons=comparisons,comparison_sheet=str(sheet),comparison_sheet_actually_opened=False,
 primary_vanilla_cube=dict(jar=jar,jar_sha256=hashlib.sha256(Path(jar).read_bytes()).hexdigest(),entry=entry,local_path=str(dst),sha256=hashlib.sha256(data).hexdigest()),
 source_declaration={'north':'front','east':'right','south':'back','west':'left','up':'top','down':'bottom'},
 findings_zh=['当前item/blockstate引用六面纹理模型，父模型把front/right/back/left/top/bottom分别映射north/east/south/west/up/down。','额外64px atlas模型六片经源有符号UV裁出后五面与16px源面完全同像素；up再转180才与named top同像素。记录差异，不判游戏朝向bug，额外模型的实际使用尚未证明。','左右16px纹理RGBA为精确水平镜像，同对象不扩案例；建筑参考0。'],formal_new_credit=0,production_changes=0),ensure_ascii=False,indent=2)+'\n')
print('13PNGs/5contextgroups recorded;6exact atlas comparisons generated, need actual opening.')
