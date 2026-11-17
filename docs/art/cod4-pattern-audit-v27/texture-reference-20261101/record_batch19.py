"""Record actually viewed heraldic masks, without treating UV placements as new designs."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-19-candidates.json').read_text())['rows']
notes={
'apostolic_cross':'双横杠长竖主干，旗帜左右各一份；宗教字面不适用当前学院或帝王身份。',
'bowl':'实心杯碗配细柄底座，杯口与两侧宽边清楚；通用器皿象形不充目标纹样。',
'bull':'正面牛首以宽额、双侧卷角及窄下颌成形，靠角内空隙而不是密线辨认。',
'chess':'整片双色棋格覆盖，图案空间与小主体不同；通用填充反例，不算独立学院纹。',
'crusader_cross':'四端外扩的短粗十字，中心实心；只保留负空间观察，宗教字面排除。',
'dragon':'侧立翼兽有长颈、外折翼、分叉爪和阶梯尾；盾形版本重新收窄，不能把西方翼龙直接当当前游龙身份。',
'eagle':'正面宽翼由少量粗齿切口与窄尾构成，单头和双头共用宽翼/身形组织，保守合为一族。',
'horse':'侧面扬蹄马以窄长头、前蹄断口、后腿与上翘尾形成姿势；小盾版删去细枝维持孔隙。',
'lily':'三瓣百合顶端尖、侧瓣外卷，茎部短；字面西式百合不套用当前目标身份。',
'lion1':'侧立狮以大头、外伸前爪和卷尾辨认，躯干短；与横走狮保守同动物族，不按姿态/载体多算。',
'lion2':'横走狮靠长身、四足断口及尾上钩辨认；与侧立狮保守同族，不能把姿态差异只叫换色。',
'orthodox_cross':'上下双横与下部斜横构成细竖十字；文化字面排除，不作本项目身份图。',
'snake':'折弯细干、上钩和底部回环，盾上缩成大S与一处孔；与既有折流构图相近，不新增泛符。',
'sun':'实心小中心外接八条弯折短辐，粗像素但有少量半透明边缘；通用放射符不扩成学院身份。',
'swords':'两剑斜交成X，刀柄护手只留少量端头；军武象形只可参考主次/留白，不证明护卫身份完成。',
 'tower':'三齿顶与宽直柱体、平底脚形成紧凑塔徽；这里只是平面纹章，绝不是完整建筑参考案例。',
 'tree':'细中干配三层外伸阶梯枝和下方短根，近既有树叉粗线组织；不新增通用树符族。',
 'two-headed_eagle':'两头以分离小钩表示，主体仍是宽齿翼与窄尾；与单头鹰合族，不因头数/盾形扩数。',
 'feather':'单根窄曲羽用白色宽芯和少数缺口辨认；已有翎片/羽形构图，保留为尺度校准，不增新族。'}
family={
 'bull':('heraldic-wide-horn-head',704),
 'dragon':('heraldic-winged-profile',707),
 'eagle':('heraldic-open-wing-frontal',708),'two-headed_eagle':('heraldic-open-wing-frontal',708),
 'horse':('heraldic-rearing-hoof-profile',709),
 'lion1':('heraldic-lion-profile',711),'lion2':('heraldic-lion-profile',711),
 'swords':('heraldic-crossed-blades',716), 'tower':('heraldic-battlement-emblem',717)}
for r in rows:
 motif=Path(r['path']).stem;n=int(r['reference_id'].split('-')[1]);carrier=Path(r['path']).parent.name
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',observation_zh=notes[motif]+('旗帜双份/镜像版不拆两例。' if carrier=='banner' else '盾面位置与另一个盾形是同纹样适配，不是新的独立设计。'),
   semantic_family=family.get(motif,('EXCLUDE_GENERIC_OR_CULTURALLY_UNSUITABLE_HERALDRY',0))[0],scope='pattern_context',
   distinct_family_proposed_credit=1 if motif in family and n==family[motif][1] else 0,
   applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0,
   limitation='白灰遮罩不是最终有色贴图；半透明与少量灰RGB像素不能凭背景/哈希猜用途。未读Java或运行时染色/UV绑定，不充帝王、学院或完整装备UV验收。')
 if motif in family:r['family_representative']=f'VIS-{family[motif][1]:03}'
 im=Image.open(r['local_path']).convert('RGBA');alpha=im.getchannel('A')
 r['source_mask_stats']={'alpha_bbox':alpha.getbbox(),'distinct_alpha_values':len(set(alpha.get_flattened_data())),
  'partial_alpha_pixels':sum(0<p<255 for p in alpha.get_flattened_data())}
by={r['path']:r for r in rows};comparisons=[]
for a in rows:
 if '/roundshield/' not in a['path']:continue
 b=by[a['path'].replace('/roundshield/','/pavese/')]
 pa=list(Image.open(a['local_path']).convert('RGBA').get_flattened_data());pb=list(Image.open(b['local_path']).convert('RGBA').get_flattened_data())
 comparisons.append(dict(a=a['reference_id'],b=b['reference_id'],motif=Path(a['path']).stem,
   rgba_hash_equal=a['rgba_sha256']==b['rgba_sha256'],
   all_rgba_different_pixels=sum(x!=y for x,y in zip(pa,pb)),
   alpha_different_pixels=sum(x[3]!=y[3] for x,y in zip(pa,pb)),
   nonzero_alpha_rgba_different_pixels=sum(x!=y for x,y in zip(pa,pb) if x[3] or y[3]),
   both_zero_alpha_rgb_different_pixels=sum(x!=y for x,y in zip(pa,pb) if not x[3] and not y[3]),
   mask26_different_pixels=sum((x[3]>=26)!=(y[3]>=26) for x,y in zip(pa,pb)),
   interpretation='同纹样的不同载体适配，不因RGBA不同新增。26只是与此前cutout基线可比的辅助统计，并不证明本遮罩运行时阈值。'))
now=datetime.now(timezone.utc).isoformat()
out=dict(recorded_at=now,viewed_pngs=44,proposed_distinct_design_families=7,coordinator_accepted_new_visual_credit=0,
 production_gate_met=False,policy='Four source pages plus all eleven full-detail pages actually opened. Seven generic composition groups, not44 new target cases. Shared glyphs/mirrors/UV placements merge.',rows=rows)
(D/'review-batch-19.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
analysis=dict(recorded_at=now,source_pngs=44,all_decoded_rgba_unique=44,paired_shield_masks=13,pairs=comparisons,
 findings_zh=['13对盾形只有龙纹的alpha与阈值26辅助二值轮廓有4像素不同；其他12对alpha一致。',
 '每对478处RGBA差异，同时存在零alpha区RGB差异及非零alpha区RGB差异，不能把全部差别说成透明区。',
 '多数面罩有多级alpha；源图不是纯二值硬边白遮罩，不直接复制或声称完全无抗锯齿。',
 '所有差异按同纹样适配合并；本阶段7组仅泛构图，不分摊给六个1000门槛。'],
 source_sheets_actually_opened=[f'build/art-reference-20261101/batch19-{i:02}.png' for i in range(1,5)],
 detail_sheets_actually_opened=[f'build/art-reference-20261101/batch19-full-detail-{i:02}.png' for i in range(1,12)],
 formal_new_credit=0,production_changes=0,source_file_changes=0)
(D/'batch19-mask-comparison.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+'\n')
print('Recorded 44 PNGs /7 generic stage groups /0 accepted;13 same-glyph pairs analyzed.')
