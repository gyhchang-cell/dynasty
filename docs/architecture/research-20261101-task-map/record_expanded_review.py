#!/usr/bin/env python3
"""Manual review of old sources under the newly requested dungeon scope."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=ROOT/'docs/architecture/continuation-20261022/references/whole-candidates-004'
FIELDS=('layout','proportion','facade','roof','material','circulation','terrain')

NOTES=[
 ('D001',['DUN04','DUN07'],
  '方形多层塔体，各层围绕内部空间组织；y16平面显示侧向伸出的小室与局部内隔，区别于简单同心楼板。',
  '21×45×21为存储范围，顶层y44全空气，层高与檐带错落；约两倍高宽比适合研究垂直藏经/登台用房，不把它当完整山寺群。',
  '木立件、铜色檐层、重复的栏与窗格形成密集横向分节；底层门、上层侧室打破绝对四面同构。',
  '整体顶为有山面的多级斜坡盖，下层多个檐/平台带形成横向停顿；中心纵剖见坡顶空腔，不能照色块称石瓦屋面。',
  '去皮橡木/木板、云杉、红下界砖以及打蜡风化铜阶/板等；分类图灰色大屋盖实际主要为铜类，不复制原贴图。',
  '底层门位y1，上部另有y17/y22门，不应把门最多的y22误认地面入口；纵剖见各层偏置板带/阶构件，未运行逐层原生寻路或碰撞。',
  '底部仅中心朝下terrain_small接口、final_state为泥；塔身和屋盖自身连续存储，但外接底部地形件未组装，坡地支撑不能宣称通过。',
  '整塔设计可用于DUN04藏经阁/高差殿阁、DUN07多层回廊的相关性复核；不等于完整悬崖寺群或浮岛仙观，不给两个目标各自重复一份新信用。'),
 ('D011',['DUN09'],
  '63×62封闭场地内中央为大圆形祭/战台，南侧轴向入口由两条深色边线导向中央，外圈散置树形/墓场构件。',
  '38层选区中y37满层墓砖封顶；纵剖显示中央巨剑从圆台上升至接近顶盖，主体高而薄，圆台宽度与巨剑形成明确主次。',
  '外壳几乎为连续墓砖墙，南侧低位入口小；内侧景观和祭台比外立面丰富，必须看剖切而非把外盒当整座建筑设计结论。',
  '上盖是满层crypt_bricks封闭平盖，不是可见中式山顶屋盖；DUN09只借鉴巨剑与圆台/入口关系，不能搬用成山峰外形。',
  '墓砖、幽木、草泥、marble台面、crypt_stone、腐栅栏/骷髅堆等；当前没有原材质的像素外观与光照证据。',
  'y1/2平面见南侧入口开口、直向引导带和中央圆台外围可绕行空间；中央巨剑占位会阻断正中穿行，不将全圆形台面当无障碍平地。',
  '内部含草泥地基及固定树形构件，外围为封闭竖直壳，不是已适应真实孤峰悬崖的方案；外接山体、剑桥和返程均未见。',
  '只作为DUN09完整巨剑祭/战场设计候选，不能称完整万刃峰。旧1/2版本仍同一家族，不新增版本信用；完整场地与目标相近度待唯一主登记复核。'),
 ('D012',['DUN08'],
  '33×33高墓体围绕中央多层水室，y1/2下层中心设施、y9/10另一层水室及y24/25十字上部联接呈不同组织。',
  '选区高48但最高非空气层y41，顶部六层为空；外部塔形壳高于宽，内部至少多个水腔层段，不能只凭总高说48格实体墓楼。',
  '四角连续竖向构件、四面居中的垂水面与上部横带，入口/腔体位置需结合纵剖和楼层，未证实每个水帘都是陆地门。',
  '上部有厚实封顶与逐层收分屋盖，y30至36中心断面是实心墓砖带，y37起深色阶梯收分；厚顶不能误读为六七层可行走房间。',
  '海晶砖、暗海晶、海晶墙/阶/板、水、海灯与水草为主；分类图中的红色砖不代表赤砖实际外观，绿色许多是水草而非陆地草坪。',
  '纵剖可见下部多个中心水腔、实心楼板及局部上行联接；平面水草与水不等于空气净空，不能凭灰格宣布全路线可走或可呼吸。未运行游泳、气室、门口和碰撞验证。',
  '自身完整高壳、底板、屋盖和垂水保存在同一模板，无jigsaw补房；实际海底落点、周边水位与底部承托未生成，不能转为已验证雪山冰窟。',
  '对DUN08水下密室、分层水宫/坚冰封门后的空间有有限借鉴，气候、天然冰裂谷和滑梯不同；作为完整水下墓体候选待相关性复核，不自动成为镇岳汉墓或陆地义庄参考。'),
]


def main():
    source=json.loads((OUT/'scope-expansion-sources.json').read_text())
    byid={c['id']:c for c in source['candidates']}
    rows=[]
    for ident,parents,*content in NOTES:
        assert len(content)==8
        viewed=[str(OLD/(ident+'.png'))]
        if ident in ('D011','D012'):viewed.append(str(OLD/(ident+'-plan.png')))
        viewed += [str(OUT/n) for n in byid[ident]['new_research_images']]
        assert all(Path(n).is_file() for n in viewed)
        rows.append(dict(source_id=ident,target_specific_review_candidates=parents,
            source_metadata='scope-expansion-sources.json#'+ident,
            actual_viewed_images=viewed,seven_observations=dict(zip(FIELDS,content[:7])),
            relevance_limits_and_dedup=content[7],decision='目标扩展后的相关性复核候选；未改原排除账，未入正式有效参考',
            first_discovery=False,formal_new_credit=0))
    report=dict(date='2026-11-01',reason='用户最新扩展cod1/2/3/4/6建筑范围；原3例只因旧范围用途/规模不符而排除，现有新目标才重审',
        distinct_old_designs_reassessed=3,actual_image_views=sum(len(x['actual_viewed_images']) for x in rows),
        newly_rendered_images=7,formal_new_credit=0,cases=rows,
        principles=[
            '高塔最常出现的门层不必是入口；先找真实地面门与各层开口，再判断垂直动线。',
            '封闭墓壳必须同时看完整体量、水平剖面和纵向剖面，外盒与内部场地分别评价。',
            '剑峰参考应区分巨剑—祭台—入口的场地组织和整个山峰/捷径系统，不能用单场地替代整关。',
            '水室中的水草、水、实心顶与空气须按状态分清，水草配色不是陆地绿地；安全气室与可完成路线还需原生验证。',
            '参考对象的不同层、视图和变体只组成同一实例；目标扩大允许重审相关性，不允许重复发新信用。',
        ],limitations='方块整格近似和材质分类色；非原生贴图、网格、碰撞、地形放置或完整程序生成结果。')
    (OUT/'scope-expansion-manual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(reassessed=3,actual_image_views=report['actual_image_views'],new_rendered=7,formal_new_credit=0)))


if __name__=='__main__':main()
