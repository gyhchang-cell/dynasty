"""Record deterministic UV signals and the actual manual review; no repairs."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from PIL import Image

D=Path(__file__).resolve().parent
R=D.parents[2]

def read(p):return json.loads(p.read_text())
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

NOTES={
 'baihu':'白骨色胸前斜条与灰钢侧面、肩部有材料区别，头盔开口在NORTH；手臂/腿纹样在共享镜像UV上左右反向；腰带端盖透明是与腿相接的待实机观察处，不仅凭alpha差判破面。',
 'bamboo':'竹片与横绳按纵横簇区分，头盔前开口、后片横绳在对应面；四面靴筒同高。袖口末端透明，但UP端盖仍全不透明，确有孤立端面风险。',
 'beidou':'蓝银面料、胸前浅色纹与背部深色星形不同，前后未互换；手臂和腿侧星纹随左侧镜像反向，不能当反字错误。',
 'brocade':'胸前斜襟与背纹不同，领口位于body NORTH上端；袖口孤立端面风险；库存深紫/米白交领比穿戴旧紫褐/金线更明确，需材质一致性后续处理，保留图标。',
 'bronze':'穿戴头部含hat层均全不透明，正面无开口；layer_2躯干是整面胸口红块与渐变条，不是腰带区域。精致铜甲图标保持，穿戴旧模板单列。',
 'cinnabar':'正面符纸和背部段纹位于正确面，头开口在NORTH；穿戴主要为橙红/土黄，缺当前图标大块米白符纸身份，记录一致性差异，不重画图标。',
 'cloth':'布帽开口、胸前斜带和背部褶线可定位，身体下缘系带在同一高度；袖底端盖与四侧末行不相接，登记孤立端面风险。',
 'dark_iron':'蓝黑板片与铜带的上下位置稳定，前胸玉扣与背面板条可区分；前侧转角处色差对应材质包边，不能单看RGB差判UV错位。',
 'disha':'骨肋前胸与背部纵脊分开；头部开口在NORTH；臂部肋形随镜像翻转。腰带底端盖透明单列为关节遮盖待验，不认定已穿戴通过。',
 'draco_king':'紫鳞/金冠在头顶和额部，开口在前；肩上与身侧鳞行有变化，冠边与顶盖RGB不一致需作为材质接缝观察，未发现UV越界。',
 'dragon_scale':'头部额带与前开口、背片下沿可定位；前后鳞行相近但不是把前胸整图覆盖所有面；胸侧包金和鳞片的高对比不是自动接缝失败。',
 'general':'精致黑金红图标对应的穿戴仍是蓝灰条带/红色方块旧模板。头部head/hat正面均全盖，layer_2整胸重复胸章，属于穿戴材料/裁切待处理，保护图标。',
 'hongmeng':'前胸与背部方形纹不同，UV朝向正确；当前图标白金圣甲与穿戴蓝紫/少量金线明显不一致，不能因v25图标已接入就验收穿戴。',
 'hunyuan':'青玉前胸交叉条与背部曲折纹不同，顶盖玉环在DOWN/minY；头盔开口与腿上端方向正确，腰带底盖透明留关节待验。',
 'jade':'精致玉甲图标保护；穿戴仍是浅绿条带与胸前大色方块。head/hat全部不透明且layer_2整躯干覆盖，单列旧模板，不能声称UV已随图标重做。',
 'leather':'棕皮斜肩带在胸前，背部是搭扣；头部开口面正确；袖侧底行透明但手臂端盖不透明，登记独立端面风险。',
 'phoenix':'红橙V形羽纹前后连贯组织，前额与顶盖材料分区不同；头底盖透明是开口式头甲常见边界，不自动当缺失面。',
 'qilin':'绿白碎鳞与金色额带对应各面，前部开口保留；与当前简化物品图相比穿戴碎鳞更多，属于设计细节差异而非UV方向错误，不重画图标。',
 'qinglong':'青蓝胸甲前部鳞条、后部龙脊分开；帽顶符形位于DOWN/minY；手臂镜像前后条带未发现反向贴到另一面。',
 'sea_silk':'浅蓝交领与背部织纹可区分，额部开口朝前；袖子裁切与端盖有孤立端面风险，其他alpha差不直接归为破面。',
 'silver':'浅银亮面、深青边线、前部玉扣在对应面；不同面的竖亮带应视为离散明暗，不能因为左右面色值不同自动报缝。',
 'sky':'精致白蓝金图标保护；穿戴是深蓝条带、青色胸方块旧稿，head/hat全盖面且layer_2整躯干覆盖，列穿戴一致性问题。',
 'taiyi':'青玉/金色前襟与背部横甲分开，额带、臂口和靴筒的上下高度一致；内层腰带底盖透明，关节状态尚非实机证据。',
 'tiangang':'蓝钢前胸金中线、背部板条分开；头顶部竖中线不是背面纹误入前面；镜像腿部金条对称。',
 'xuantian':'精致金白玄天图标保护；穿戴仍是蓝灰条纹和青色方块，head/hat正面均不透明，layer_2整躯干覆盖，未随图标升级。',
 'xuanwu':'深青绿甲前胸与背部龟壳框有区别，帽顶和正面开口对应正确；内层腰带端盖透明须保留关节实机待验。',
 'zhuque':'红金V形前襟与背部羽结分开，臂腿羽纹镜像翻向在共享UV上属于预期；未见前后片互置。',
 'ziwei':'紫金前胸纵向星纹与背部框形分开，左侧共享纹样镜像符合源模型；库存亮紫/银白部分比旧穿戴显著，记录图标/穿戴未同步，不改图标。',
}

def main():
    inv=read(D/'face-and-seam-inventory.json')
    assert set(NOTES)=={r['material'] for r in inv['entries']}
    orphan=[];canvas=[]
    for r in inv['entries']:
        for p in r['parts']:
            cap=next(f for f in p['faces'] if f['direction']=='UP')
            edges=[s for s in p['seams'] if s['face_a']=='UP' or s['face_b']=='UP']
            if cap['visible_pixels'] and all(s['alpha_disagreement']==s['length'] and s['both_visible']==0 and all(c[3]>=26 for c in s['rgba_a' if s['face_a']=='UP' else 'rgba_b']) for s in edges):
                orphan.append({'material':r['material'],'layer':r['layer'],'part':p['part'],'cap_crop':cap['crop'],'cap_visible':cap['visible_pixels'],'cap_pixels':cap['total_pixels'],'edge_keys':[s['key'] for s in edges],'status':'PROVEN_UV_ALPHA_ISOLATION_GAME_APPEARANCE_PENDING'})
        if r['layer']==1:
            head=next(p for p in r['parts'] if p['part']=='head');hat=next(p for p in r['parts'] if p['part']=='hat')
            nf=lambda p:next(f for f in p['faces'] if f['direction']=='NORTH')
            if nf(head)['visible_pixels']==64 and nf(hat)['visible_pixels']==64:
                layer2=next(e for e in inv['entries'] if e['material']==r['material'] and e['layer']==2)
                body=next(p for p in layer2['parts'] if p['part']=='body')
                tex=Image.open(R/layer2['path']).convert('RGBA')
                rows=[sum(tex.getpixel((x,y))[3]>=26 for x in range(20,28)) for y in range(20,32)]
                canvas.append({'material':r['material'],'head_north_visible':64,'hat_north_visible':64,'layer2_body_north_row_visible':rows,'source_files':[r['path'],layer2['path']],'status':'WHOLE_MASK_AND_TORSO_COVERAGE_CONFIRMED_VISUAL_INTENT_PENDING'})
    assert len(orphan)==10 and {p['material'] for p in orphan}=={'bamboo','brocade','cloth','leather','sea_silk'}
    assert {p['material'] for p in canvas}=={'bronze','general','jade','sky','xuantian'}
    findings={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'OFFLINE_FACE_EDGE_AND_ORIENTATION_REVIEW_WITH_OPEN_FINDINGS','source_png':56,'geometry_face_instances':1680,'distinct_source_face_regions':1176,'geometry_edge_pairs':3360,'manual_priority_edges':112,'mirror_north_correspondences':84,'bounds_errors':inv['errors'],'orphan_caps':orphan,'whole_canvas_worn_sets':canvas,'approved_icons_to_preserve':112,'approved_material_mismatch_priority':[{'material':'hongmeng','difference':'白金圣甲图标仍配蓝紫旧穿戴'},{'material':'cinnabar','difference':'红白符纸图标仍配橙红土黄旧穿戴'},{'material':'brocade','difference':'深紫/米白交领图标仍配紫褐/金线旧穿戴'}],'decision':'不修改任何PNG或人物；完成参考门槛前只读核查。后续穿戴修订与图标保护必须分开。UV拓扑检查完成不代表这些视觉缺口完成。','game_acceptance':False,'checklist_deletions':0,'new_artwork':0}
    findings.pop('approved_icons_to_preserve')
    findings['protected_inventory_icons']=112
    findings['protection_categories']={'selected_original_icons':52,'fine_old_icons':20,'historically_redrawn_v15_icons':40}
    save('findings.json',findings)
    waist=[]
    for r in inv['entries']:
        if r['layer']!=2:continue
        tex=Image.open(R/r['path']).convert('RGBA')
        faces={}
        for name,x,width in [('NORTH',20,8),('SOUTH',32,8),('WEST',16,4),('EAST',28,4)]:
            faces[name]=[sum(tex.getpixel((i,y))[3]>=26 for i in range(x,x+width)) for y in range(20,32)]
        full=all(v==[8]*12 for k,v in faces.items() if k in {'NORTH','SOUTH'})
        bottom=(faces['NORTH']==faces['SOUTH']==[0]*8+[8]*4 and faces['WEST']==faces['EAST']==[0]*8+[4]*4)
        assert full or bottom
        waist.append({'material':r['material'],'path':r['path'],'body_face_rows_top_to_bottom':faces,
                      'classification':'WHOLE_TORSO_OLD_PATTERN' if full else 'BOTTOM_FOUR_MODEL_ROWS_WAIST_CORRESPONDENCE_CONFIRMED'})
    save('waist-coverage-review.json',{'model_body_y_down':True,'body_side_v_range':[20,32],
          'waist_source_v_range':[28,32],'rows':waist,'bottom_four_row_sets':23,'whole_torso_sets':5,
          'vanilla_comparison':'本地1.20.1铁/皮内层腰部为最后五行；本项目23套为最后四行，位置正确，差一行不自动判错。另5套整个躯干都不透明，单列旧模板。',
          'legacy_generator_note':'tools/art/gen_armor_layers.py关于v=18..20落在躯干下部的注释不符合实际模型UV。它不是当前23套腰带位置的证据；本轮未运行或修改该旧生成器。',
          'game_acceptance':False})
    save('manual-review.json',{'face_pages_opened':[f'faces-{i:02}.png' for i in range(1,15)],'seam_pages_opened':[f'seams-{i:02}.png' for i in range(1,8)],'mirror_pages_opened':[f'mirrors-{i:02}.png' for i in range(1,5)],'icon_match_pages_opened':[f'approved-icon-worn-match-{i:02}.png' for i in range(1,4)],'per_material':[{'material':k,'observation':v} for k,v in sorted(NOTES.items())],'seam_interpretation':'3360个相邻面边对按实际几何端点配对；112条优先信号打开查看。RGB差可来自包边/侧面离散阴影，透明差可来自开口，均未自动判坏。UP手臂端盖四侧均无alpha连接的10个实例另行证明并保留待修。','orientation_interpretation':'前胸开领/扣与后背纹按NORTH/SOUTH定位；源模型Y向下，DOWN=头顶/部位上端，UP=部位下端；镜像翻转由原生角点而非临时猜测。只有静态局部UV证据，没有游戏穿戴、关节动态或灯光验收。'})
    handoff=R/'docs/cod4/audit-20261022/attachment-interface-handoff-20261102.json';h=read(handoff);received=[]
    for entry in h['entries']:
        for p,digest in entry['inputs'].items():assert sha(R/p)==digest
        geo_path=next(p for p in entry['inputs'] if p.endswith('.geo.json'))
        geo=read(R/geo_path)['minecraft:geometry'][0]
        bone=next(b for b in geo['bones'] if b['name']==entry['attachment_bone'])
        assert bone==entry['attachment_bone_raw']
        received.append({'entity':entry['entity_key'],'attachment_bone':bone['name'],'parent':bone['parent'],'pivot':bone['pivot'],'cube_count':len(bone.get('cubes',[])),'native_item_id':entry['native_item_id'],'input_hashes':entry['inputs'],'body_modified':False,'next_scope':'仅物件自身，保留现有嵌入模型；不虚构独立物品ID，不添加任务获取目标。'})
    save('attachment-handoff-received.json',{'source':str(handoff.relative_to(R)),'source_sha256':sha(handoff),'entries':received,'status':'SOURCE_HASH_AND_RAW_BONE_MATCHED_NOT_IMPLEMENTATION','armor_priority_unchanged':True})
    print(json.dumps({'orphan_cap_instances':len(orphan),'affected_cap_sets':5,'whole_mask_torso_sets':len(canvas),'material_reviews':len(NOTES),'handoff_props_received':len(received)}))

if __name__=='__main__':main()
