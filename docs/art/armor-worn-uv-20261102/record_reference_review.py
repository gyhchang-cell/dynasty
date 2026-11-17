"""Save actual eight-page semantic review. No automatic design credit or art edits."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

D=Path(__file__).resolve().parent
R=D.parents[2]
OLD=R/'docs/art/armor-continuation-20261102'

def read(p):return json.loads(p.read_text())
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    provenance=read(D/'reference-variants-provenance.json')
    available={x['case_key'] for x in provenance['cases']}
    groups=[]
    def group(ns,names,key,observation):
        groups.append({'semantic_group':key,'cases':[f'{ns}:{n}' for n in names.split()],
                       'observation':observation,'counting':'保守学习组；颜色/同套部位/结构变体不分别加独立设计数。'})
    group('iceandfire','armor_amythest armor_black armor_blue armor_bronze armor_copper armor_electric armor_gray armor_green armor_red armor_sapphire armor_silver armor_white',
          'dragon_scale_family_conservative','弧角暗壳与冰刺冠存在差异，但胸片均为鳞纹短宽体、顶部小肩尖；按同一龙鳞装备家族保守合并。亮蓝/银白冠用阶梯块，褐铜胸甲用暗边包亮面。仅看图标，未据此证明三维模型独立。')
    group('iceandfire','armor_silver_metal','silver_metal_plume','银色分瓣面甲顶只有小紫羽与黄根；紫色裤布以两条银边框住。与鳞甲不同；页面只含头和裤，不虚构其余部件。')
    group('iceandfire','deathworm_red deathworm_white deathworm_yellow','deathworm_shell','三种颜色共享同心壳胸、黑色肩钩、平顶倒U头口和粗直腿，合并一组。红版靴子补充尖脚轮廓，不另算一个设计；结构借鉴用壳片大色圈，不复制像素。')
    group('iceandfire','dragonsteel_fire dragonsteel_ice dragonsteel_lightning','dragonsteel_tall_plate','火钢黑红中脊、冰钢浅蓝宽肩、雷钢紫黑角冠有局部差异；按同一系列的结构变体保守合并。竖板与侧面暗块有效，但胸甲瘦长，不能直接替代用户要求的短宽原版比例。')
    group('iceandfire','forest_troll_leather frost_troll_leather mountain_troll_leather','forest_troll_hide','绿灰、蓝灰和深青为同款方皮胸、细直护腿与骨护额；三色合并。皮革正面一整亮块、边缘更暗，不依赖密集斑点。')
    group('iceandfire','myrmex_desert myrmex_jungle','myrmex_shell','橙褐和青色共享虫壳胸的中心尖片、侧肩角、头部中缝；配色与局部明暗不能算两种独立结构。仅三部位。')
    group('iceandfire','sheep','sheep_fleece_vest','白羊毛为两块宽亮襟，棕皮在中部与腰区连成一块；盔顶羊毛留脸、靴子白边包棕侧。材料身份由大块对照表达，不能变成白色高光噪点。')
    group('iceandfire','tide_blue tide_bronze tide_deepblue tide_green tide_purple tide_red tide_teal','tide_fins','七色鳞甲共享青色双鳍头盔、浅青U形胸下沿和裤脚边；全数合并。用统一少量亮边保留材料身份，深色腿靴仍能凭两侧轮廓辨认。')
    samurai=[x.split(':')[1] for x in sorted(available) if x.startswith('samurai_dynasty:') and not x.endswith('_ninja') and x!='samurai_dynasty:steel']
    group('samurai_dynasty',' '.join(samurai),'samurai_plate_variants_conservative','十九个名称共享角兜、分开外挑肩片、短胸带与横片护胫；金红大冠与铁白小冠等有差异，但主要为同系列材质/冠饰变体，保守合并。学习胸腹留黑缝与三四条横片，不照搬巨大角冠，不把颜色数量变成参考数。')
    group('samurai_dynasty','diamond_ninja gold_ninja iron_ninja netherite_ninja steel_ninja','ninja_cloth_cowl','五种材质都以深紫布身、浅色V领、罩头和短靴表达忍者服；合并。侧肩块和靴筒只少量亮面，黑紫主体仍完整。铁版无裤图，不补造。')
    group('samurai_dynasty','steel','steel_samurai','钢武士为银色横片、橙色火角兜与红褐护胫，比彩色武士组更细窄；沿用上一轮同一学习组，非新增全局信用。角冠只学位置，不复制轮廓。')
    flat=[c for g in groups for c in g['cases']]
    assert len(flat)==len(set(flat))==57 and set(flat)==available
    old=read(OLD/'reference-review.json')
    old_prov=read(OLD/'armor-reference-provenance.json')
    old_cases={c for g in old['observations'] for c in g['cases']}
    retained=[]
    for g in old['observations']:
        overlap=set(g['cases'])&available
        if overlap:assert set(g['cases'])<=available,'Do not silently drop a partially overlapping group'
        else:retained.append(g)
    assets={(a['jar'],a['entry'],a['sha256']) for p in [provenance,old_prov] for c in p['cases'] for a in c['assets']}
    save('reference-variant-review.json',{
      'pages_opened':[f'reference-variants-{i:02}.png' for i in range(1,9)],
      'method':'实际打开八页原始PNG整数倍展示；合并同款换色、部位与保守同系列结构。沿用上一轮已查看证据，不重置历史学习。',
      'reviewed_name_families':57,'reviewed_png':194,'conservative_learning_groups':len(groups),
      'observations':groups,'prior_review':'docs/art/armor-continuation-20261102/reference-review.json',
      'overlap_name_families':sorted(old_cases&available),
      'combined_reopened_name_families':len(old_cases|available),
      'combined_unique_archive_payloads':len(assets),
      'combined_unique_png_sha256':len({a[2] for a in assets}),
      'combined_conservative_learning_groups':len(retained)+len(groups),
      'retained_prior_groups':[g['semantic_group'] for g in retained],
      'reference_requirement':1000,'fresh_global_reference_credit':0,
      'gate_status':'NOT_MET_INDEPENDENT_DESIGNS_NOT_ESTABLISHED',
      'count_boundary':'合并后的学习组只对已逐页查看的子集去重，不是全局1000独立设计达标证明。历史1000个PNG索引也不能当1000套盔甲。',
      'production_allowed':False})
    controls=read(D/'vanilla-control-provenance.json')
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
    # Non-overlapping 3x atlases plus exact NORTH-face crops; source pixels unchanged.
    sheet=Image.new('RGB',(1080,560),(68,73,78));draw=ImageDraw.Draw(sheet)
    draw.text((10,8),'VANILLA UV CONTROL / exact source pixels enlarged / NOT GAME VALIDATION',font=font,fill='white')
    for i,row in enumerate(controls['rows']):
        y=45+i*125;im=Image.open(D/row['local']).convert('RGBA')
        draw.text((10,y+8),Path(row['local']).name,font=font,fill='white')
        for x,box,label in [(235,(0,0,64,32),'atlas'),(480,(8,8,16,16),'head N'),(615,(40,8,48,16),'hat N'),(750,(20,20,28,32),'body N')]:
            crop=im.crop(box);scale=3 if label=='atlas' else 6
            crop=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST)
            sheet.paste(crop,(x,y),crop);draw.text((x,y+98),label,font=font,fill='white')
    sheet.save(D/'vanilla-controls-review.png')
    print(json.dumps({'reviewed_families':57,'reviewed_png':194,'groups':len(groups),'combined_families':len(old_cases|available),'combined_png':len(assets),'combined_groups':len(retained)+len(groups)},ensure_ascii=False))

if __name__=='__main__':main()
