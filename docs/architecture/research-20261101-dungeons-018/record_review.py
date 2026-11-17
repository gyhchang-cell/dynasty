#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
DATA=[
 ('EXCLUDED_SCALE_SHARED_FAMILY','15格砂岩塔；低于既定高度，与本批其他三塔共用主体家族。',[
  '方形底室、缩进中身及宽顶回廊竖向叠置；底室四角支柱和顶回廊四角支柱相应，无横厅和院。',
  '15×21×15，实占y0..20，主要楼板y5/9/13，不能为了计数将既定25–53格高度下调。',
  '砂岩柱、短垛地脚、中身四面大开口及顶层回廊，收放关系与另外三塔相近。',
  'y18..20阶状浅四坡盖封闭回廊，屋盖材质变化不增加楼层或新设计。',
  'smooth_red_sandstone349、terracotta290、cut_red_sandstone207、chiseled_red_sandstone144；不以砂岩重色独立计例。',
  '无普通门和梯；原始阶块分布y1..13，实际上升段和饰边混合，不能把阶块总数当完整通行路线。',
  '原存平地脚y0、一个empty终止接口，不表示道路和营地已拼装；未验证沙地贴合。']),
 ('EXCLUDED_SCALE_SHARED_FAMILY','绯红塔是同一叠层回廊主体的下界材料／藤蔓变体。',[
  '与F01同占地方向、下室、中身和宽顶回廊；藤蔓挂在侧墙／檐下，不另成新室翼。',
  '存储15×23×15但实际仅y0..20，末两层为空；不能把空包围盒高度当额外塔高。',
  '木干角柱夹异色板墙，通透中段及顶层方廊保留；额外玻璃和藤蔓改变围护细节而非主体叠置。',
  '同浅四坡盖，屋檐局部阶块及藤蔓增加细节，非另一个不同的屋顶空间组织。',
  'crimson_planks333、crimson_stem297、warped_planks174、weeping_vines66；材料及局部状态差异不冒称字节一致。',
  '无普通门／梯，y1..13的阶块和F01对应，另外y19有4阶块；藤蔓不作为已认证可攀路线。',
  'nylium脚与末端empty接口；不推断下界熔岩环境或生成安全性，不产生新建筑例数。']),
 ('EXCLUDED_SCALE_SHARED_FAMILY','末地塔同主体重材，外接chorus及shulker接口不计建筑。',[
  '同一方形下室—窄中身—宽上回廊；紫块／黑墙和周边接口未形成新的平面或独立房间。',
  '15×21×15、楼板高度同F01，现存包围盒与尺度不足的判断一致。',
  'obsidian围护、purpur角柱和拱边保留中身开口；紫色jigsaw不误认成门。',
  '同阶状浅盖，屋盖几何位置近同；柱材料变化不作为独立比例证据。',
  'obsidian520、purpur_block297、purpur_pillar128、purpur_stairs81；jigsaw35是接口，非35栋。',
  '无普通门／梯；原阶块y1..13，必须区分拱饰与行走梯；原状态另存，未认证原生路径。',
  '21个chorus、13个shulker和1个empty接口；只审塔体，未装配植物或实体，外围件不增加有效例数。']),
 ('EXCLUDED_SCALE_SHARED_FAMILY','冰塔仍为同主体；整块替换阶块尤其不能证明原梯可走。',[
  '下层方室、中段细筒、上方宽廊和四角承托与F01相同，冰材未增加另一翼或院。',
  '15×21×15，实占y0..20、主要板层同其他塔；低于原范围保存高度。',
  '蓝冰角柱、冰壁和青玻璃开口保持收放轮廓，局部实心替换与原方块状态分别保留。',
  '同三层浅盖外轮廓，冰块替换后只证占位接近，不能宣称每处碰撞一致。',
  'ice565、blue_ice310、packed_ice249、cyan_stained_glass16；冰块替换台阶是实际结构状态差异。',
  '既无普通门／梯，也没有任何stairs方块；不能按相近外轮廓或青色格推断它有同样楼梯。',
  '平底冰脚和1个empty接口；未验证雪地高程、融冰或滑行效果，这些不属于布局参考验收。'])]
def main():
 s=importlib.util.spec_from_file_location('record',OUT.parent/'research-20261101-dungeons-017/record_review.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;m.DATA=DATA;m.main()
if __name__=='__main__':main()
