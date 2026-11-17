"""Faithful source study only: 64 PNGs, numbered/layer variants merged."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[3]
rows=json.loads((D/'batch-22-candidates.json').read_text())['rows']
# Every overview and integer detail page was opened before this record.
groups=[(832,833,'deep-one-water-bolt-layered',832),(834,841,'deep-one-foam-wave-layered',834),
(842,844,'EXCLUDE_SOFT_GENERIC_TRAILS',None),(845,852,'water-tremor-broken-rim',845),
(853,853,'flame-sigil-thin-rings',853),(854,856,'ignis-armor-sparse-cyan-cracks',854),
(857,859,'ignis-shield-branch-cracks',857),(860,865,'water-spear-tip-islands',860),
(866,870,'sea-wave-hard-color-islands',866),(871,871,'flame-sigil-thin-rings',853),
(872,872,'void-rune-purple-panels',872),(873,878,'ring-broken-rim',873),
(879,879,'EXCLUDE_GENERIC_DOUBLE_RING',None),(880,880,'minor-trail-chipped-ribbon',880),
(881,881,'hard-stair-wedge-trail',881),(882,885,'slash-short-arch-states',882),
(886,886,'hard-stair-wedge-trail',881),(887,887,'layered-wave-ribbon',887),
(888,889,'water-jet-inner-outer',888),(890,895,'crack-coarse-branch-states',890)]
notes={
'832-833':'灰白短条、卷端和水花小岛分布于透明图集；基础/overlay合并，未核三维UV绑定。',
'834-841':'白灰细泡沫带和短侧岛只占上左部分；四状态与四覆图合为一组波纹，不当八个设计。',
'842-844':'白色长楔/镜像菱形带软透明边，偏平滑；作反例，不充MC硬像素专属纹样。',
'845-852':'灰白粗方环由小孔扩为大环，后几图边缘断开；八编号只计一组环材，非学院身份。',
'853-853':'金橙细双环、稀疏辐条、中央弯折符形；细线密度偏高，只作构图反例/通用材料背景。',
'854-856':'青白锯齿裂纹及黑阴影分散在256px透明图集，编号后图簇数增加；不是完整盔甲展开证明。',
'857-859':'黑色细分叉集中在上中横带与下中片，后图更密；同盾裂纹状态，不算三面盾。',
'860-865':'蓝外缘/青亮芯的窄长水枪尖岛，状态改变端部与裂口；大透明区不是贴图缺失结论。',
'866-870':'蓝青大块平面、浅色弯带与下方锯齿泡沫分岛，有限硬色分材；不从平面推断模型面方向。',
'871-871':'与金橙法印同布局的青色版本，同族合并，不因换色算新法印。',
'872-872':'紫色长方板与下方狭片组成UV图集，不是可直接贴在地面的完整符字图标。',
'873-878':'粗白环依次变细、断为短弧直至稀疏方点；六编号一组通用环，未证明运行时序。',
'879-879':'紫色细双环、内侧短弧点，与通用环构图复用；排除新增身份案例。',
'880-880':'28×13白色短带下边有像素缺口，端部少量灰阶/半透明；不强制压到16px。',
'881-881':'32px右尖阶梯楔，以255/225/195/165四档不透明灰形成宽竖带，边缘无半透明。',
'882-885':'灰色短拱刃配下折端角，四源图小幅改变弧与灰像素；一组slash状态，不当四次攻击验收。',
'886-886':'与pointed同四档不透明灰阶的阶梯三角，非柔透明渐变；保守归同楔形族。',
'887-887':'32×16灰白宽波带有中间透明折隙；粗色片表现翻折，不误作羽毛或学院字形。',
'888-889':'inner为32×2蓝色长块；outer虽512×4，非零alpha只在左16×4内共56像素，三色全不透明，不能按预览留白判空图。',
'890-895':'8px灰白粗格裂缝由块到分叉/X与中柱；六小图一组状态材料，不算六件装备。'}
for r in rows:
 n=int(r['reference_id'].split('-')[1]);a,b,f,rep=next(g for g in groups if g[0]<=n<=g[1]);im=Image.open(r['local_path']).convert('RGBA');pix=list(im.get_flattened_data());alpha=im.getchannel('A')
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',semantic_family=f,scope='effect_pattern_context',distinct_family_proposed_credit=int(n==rep),
  source_alpha_bbox=alpha.getbbox(),source_partial_alpha_pixels=sum(0<p[3]<255 for p in pix),source_nonzero_alpha_pixels=sum(p[3]>0 for p in pix),source_visible_rgba_colors=len({p for p in pix if p[3]}),
  observation_zh=notes[f'{a}-{b}'],applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0,
  limitation='仅PNG/资源声明材料研究，通用水/环/裂纹不是学院/帝兵完整身份。编号、换色、层、镜像合并；没有Java/UV三维/游戏验收。')
 if rep:r['family_representative']=f'VIS-{rep:03}'
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),proposed_distinct_design_families=sum(r['distinct_family_proposed_credit'] for r in rows),coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='All6overview and16integer-detail pages actually opened. Numbered states/overlay/recolors merge; generic/soft counterexamples excluded. Context proposals are not accepted semantic cases.',rows=rows)
(D/'review-batch-22.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
# Read only exact primary JSON declarations, not code or inferred playback.
entries=[(832,'assets/alexscaves/particles/water_tremor.json'),(853,'assets/cataclysm/particles/ring_0.json'),(853,'assets/cataclysm/particles/shock_wave.json')]
declarations=[]
for ref,entry in entries:
 row=next(r for r in rows if r['reference_id']==f'VIS-{ref}')
 with ZipFile(row['jar']) as z:data=z.read(entry)
 dst=Path('build/art-reference-20261101/batch22-resource')/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 declarations.append(dict(jar=row['jar'],jar_sha256=row['jar_sha256'],entry=entry,local_path=str(dst),sha256=hashlib.sha256(data).hexdigest(),content=json.loads(data)))
res=dict(recorded_at=datetime.now(timezone.utc).isoformat(),declarations=declarations,formal_new_credit=0,
 finding_zh='water_tremor列八纹理、ring_0列六纹理；列表并不声明帧时长、按龄/随机选择或实际顺序。shock_wave为{}不能据此认定无效，Java绑定未读。',no_runtime_claim=True)
(D/'batch22-resource-declarations.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print('Recorded',len(rows),'PNGs,',out['proposed_distinct_design_families'],'context families, 3 primary JSONs; accepted0.')
