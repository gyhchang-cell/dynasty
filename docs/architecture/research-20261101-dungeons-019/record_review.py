#!/usr/bin/env python3
"""One bounded garrison reference; keep ruin completeness unresolved."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def main():
 s=importlib.util.spec_from_file_location('common',BASE/'research-20261101-dungeons-017/record_review.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 src=m.get(OUT/'sources.json');data=[
 ('ACCEPTED_ONE_COMPLETE_GARRISON_LAYOUT',1,'DUN03-MEDIUM-GROUND-GARRISON',[
  '31格方院四边完整围合，四角为低于主塔的独立角塔，东边中部嵌一座高守望段；内院大面积留空，两侧低棚带与环墙平台分开。与旧010-F01破碎围院、F02竖向叠台、F03长屋高围栏、F05高长厅加低翼均不同；只计整个堡院一例，不把五塔拆开。',
  '存储31×30×31且实占y0..29，院墙／步道远低于东侧高塔。y28/29为塔帽尖部，不当新楼层；占地及保存高度符合现有中型驻防堡／营院范围。',
  '四边墙身用水平横带与连续墙垛围院，角塔小帽构成节奏，东侧主塔较宽且高；西侧门位没有被强行挪到高塔下，避免用假对称解释原设计。',
  '院心开放；沿边低棚为独立浅盖，四角小塔及东侧高塔分别叠小帽。屋盖与院墙高差服务内外分区，不以帽色或尖顶数量作为独立设计数量。',
  'cut_sandstone1895、sandstone489、smooth_sandstone_stairs361、smooth_sandstone353、sandstone_wall283，另jungle_planks182和stripped_spruce_log172。只学习围院与高低组织，不直接复制贴图或把砂岩当成国风夯土成品。',
  '四处下半门在(2,1,14)/(4,1,14)/(2,1,16)/(4,1,16)，沿西墙两条平行位置成组；高塔内梯(28,15)y10..22。原阶块含坡饰、棚沿及较低台阶，均原样保留；入口—院—边带—高塔是观察到的空间组织，未声明原生碰撞下全程可走。',
  '31格完整平底与四边外墙在同一保存模板中，外接5个道路接口、4个居民接口、1个铁傀儡接口，未把外村落算入堡院。单级池检查不等于道路、地形处理器和生成位置验收。']),
 ('HOLD_COMPLETE_RELEVANT_BUILDING_EVIDENCE',0,None,[
  '原存为近环状破石墙筒和零散外脚，多个高度留洞，不见完整多房间群或横厅。现存残墙不足以确定完整原岗亭的室层和平台关系，不推想修复后的建筑。',
  '23×27×23，实际占y0..25，y23..25仅各1格尖残柱；满足包围盒筛选不代表保存了25格高完整驻守空间。地脚散石也不能膨胀主体使用面积。',
  '石柱／墙缝多处断裂，周边散石呈破损轮廓；不能从缺损立面反推已消失的多层房间。',
  '现存没有完整屋盖，只保留高低不等的墙柱尖；不把缺顶状态画成原创新屋顶或当恢复设计。',
  'stone_bricks225、cobblestone169、gravel110、andesite107、cracked_stone_bricks99和stone_brick_stairs54；破损材料不证明它与其他塔原型独立。',
  '无普通门／梯，原阶块分散于y0..19，局部似墙缘或残梯；不得宣称存在连续爬升和现成入口。原始状态存档供后续开口／断层复核。',
  '单个NBT无jigsaw，零散砾石／石脚；归档内JSON未找到选择本体的池证据。无接口只说明此存档未见外接，不能独自证明用途、作者完整设计边界或生成有效性。'])]
 entries=[]
 for c,(decision,credit,scope,obs) in zip(src['candidates'],data):
  entries.append(dict(id=c['id'],source=c,decision=decision,credit=credit,scope_id=scope,
   observations=dict(zip(m.ASPECTS,obs)),actual_images_viewed=[m.ev(OUT/(c['id']+suffix)) for suffix in ['-whole.png','-plan.png','-vertical.png','-details.png']],
   native_acceptance=False,
   next_evidence=None if credit else '先确认该残塔作为完整独立建筑设计的作者边界及相关用途，再审原层板／入口拓扑并与旧废塔语义去重。没有这些证据不加例。'))
 comparisons=[(10,'F01'),(10,'F02'),(10,'F03'),(10,'F05'),(6,'F04'),(12,'F01'),(13,'F01')]
 m.dump('manual-review.json',dict(entries=entries,templates_studied=2,actual_new_images_viewed=8,
  historical_comparison_views=[m.ev(BASE/f'research-20261101-dungeons-{b:03d}/{i}-whole.png') for b,i in comparisons],
  independent_references_added=1,credited_ids=['019-F01'],
  semantic_dedup=[
   dict(id='019-F01',compared_ids=['010-F01','010-F02','010-F03','010-F05'],
    conclusion='完整方形环墙院、四角塔加单侧中塔及偏置门位，不是叠台堡、中央长屋高篱院或高长厅低翼的材料／屋盖／旋转变体；四角塔不分算。'),
   dict(id='019-F02',compared_ids=['006-F04','012-F01','013-F01'],
    conclusion='006-F04为带侧院的完整房屋、012-F01有外长梯及偏置台、013-F01多室群；不能据不同外形自动接纳残塔，完整相关建筑边界仍待查。')],
  old_two_holds_reopened=False,old_two_holds_retained=['011-F04','012-F03'],
  image_limits='实际查看的8幅新图及7幅旧整体图逐项有哈希。分类色整方块近似，不认证原生碰撞、材质、外村落或地形。',
  network_requests=0,java_run=False,game_run=False,production_changes=0,checklist_deletions=0,independent_human_reviewer_claimed=False))
 m.dump('scoped-reference-update.json',m.scope_record(19))
 print('019: 1 complete courtyard garrison added; ruin held. Scopes 5/7/1 of 1000 each.')
if __name__=='__main__':main()
