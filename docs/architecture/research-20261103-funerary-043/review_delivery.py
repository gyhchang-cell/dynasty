"""Save same-agent research review; no automatic credit or main-list mutation."""
import json
from pathlib import Path
from read_recipe import OUT, ROOT, sha
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    refs=ROOT/'docs/architecture/continuation-20261022/references'
    old_index=refs/'whole-candidates-004/candidates.json';old_review=refs/'whole-candidates-004/review-batch-004.json'
    old=next(c for c in get(old_index)['candidates'] if c['id']=='D010')
    src=get(OUT/'recipe-source.json');layout=get(OUT/'layout-evidence.json')
    assert old['member']==src['templates'][0]['member'] and old['nbt_sha256']==src['templates'][0]['sha256']
    prior=OUT.parent/'research-20261103-funerary-042/scope-status.json'
    scope=get(prior)
    # Coordinator accepted 042 after its immutable specialist receipt was written.
    accepted=ROOT/'docs/cod4/audit-20261022/coordinator-building-042-boundary-review-20261103.json'
    assert sha(accepted.read_bytes())=='db8ba566b809e6a6c307a2021c5b5947196076a67b58406d7cc0b8ca491f2975'
    formal=refs/'full-buildings.json'
    scope['funerary']=dict(baseline=evidence(formal),formal_baseline=149,remaining_formal=851,
        current_batch_proposed_credit=0,formal_credit_added=0,formal_register_written=False,
        production_allowed=False,previous_W028_proposal_accepted_by_coordinator=True,
        coordinator_acceptance=evidence(accepted),coordinator_acceptance_pending=False)
    scope.update(batch=43,prior_scope_status=evidence(prior),current_batch_formal_credit_added=0,
        current_batch_proposed_credit=0,current_batch_old_case_retained='COD4-R004-D010',
        previously_accepted_proposal_identities=['COD4-R001-W028'],pending_proposal_identities=[])
    dump('scope-status.json',scope)
    review=dict(batch=43,date='2026-11-03',old_identity='COD4-R004-D010',newly_discovered_design=False,
        old_index=evidence(old_index),old_review=evidence(old_review),old_hold_reason=get(old_review)['not_credited']['D010'],
        source_recipe=evidence(OUT/'recipe-source.json'),source_class=evidence(OUT/'class-evidence.json'),
        source_layout=evidence(OUT/'layout-evidence.json'),source_url='https://www.curseforge.com/minecraft/mc-mods/the-twilight-forest',
        source_url_basis='同一固定Jar的META-INF/mods.toml；本轮未联网访问。',
        actual_images_viewed=[evidence(OUT/n) for n in ['D010-base-and-layout.png','D010-layout-sections.png']],
        observations=dict(
            layout='22×4×13原围界与草地，不是独立完整墓园证据。读同版本放置字节后，NONE/NONE下墓位原点x=3/8/13/18、z=2/4/8/10，共16位；中间z=6一排被跳过。三墓碑模板是每位的随机替代，不是三个墓区，也不是三栋建筑。',
            proportion='原外框存储22×4×13，实际非空气只占3层；墓碑模板3×3×1，原点在平均地面-1。研究图只平移坐标显示，不放大墓碑、不截短围栏、不把4×4墓位或零散陷阱计作完整建筑。',
            facade='原外框y=2恰好66格canopy_fence构成22×13闭合周界；普通门、栅栏门和jigsaw均0。木围界与低石墓标形成明确内外分隔，但实际处理器可能改变结果，不能据示意断言原生围墙完整。',
            roof='墓园开敞，无屋顶和附属用房。可借鉴开放墓区与围界的组织，不能拿它替代义庄大厅、停灵房或供奉建筑的屋面设计参考。',
            materials='原外框dirt286、grass_block286、canopy_fence66，其余air506。Full墓碑用苔圆石、苔圆石墙及下半平滑石台阶。分类图把栏杆/墙/半砖按整格绘制，绿色墙体也不代表草皮；实际材质、网格与碰撞未验。',
            circulation='研究示意可见中央较宽留白、墓位间隔与外围空隙。闭合围栏没有明示门；没有把留白自动称作与外部相连的入口，也没有认证玩家跨栏或连续行走路线。Full只是间距图符，不是已证明可生成的全Full种子。',
            terrain='同版本offsetToAverageGroundLevel读取高度样本，标准差>2即失败；取四舍五入均值调整高度后检查区域。配置为OCEAN_FLOOR且避开占地结构。可学习低平场地统一墓位标高；没有执行地形生成、填土、实体、陷阱或处理器。'),
        bytecode_read_findings=[
            dict(member='GraveyardFeature.class',method='m_142674_',pc_ranges=[[395,460],[482,508],[608,801],[840,980],[981,1255],[1256,1311]],
                observation='原外框放置→墓位边界与旋转镜像修正→5/2步进与中线排除→随机墓碑→可选箱/TNT/亡灵。墓碑复用含Web处理器的同一settings19。'),
            dict(member='GraveyardFeature$GraveType.class',method='<clinit>',pc_ranges=[[0,51]],
                observation='Full/Upper/Lower分别引用同Jar三个墓碑，三者大小相同。'),
            dict(member='GraveyardFeature$WebTemplateProcessor.class',method='process',pc_ranges=[[0,54]],
                observation='比较Blocks.f_50440_后抽样nextInt(5)；命中分支以aload_2位置与Blocks.f_50033_构造替换，不可直接当普通原地换材。此处保留SRG字段与参数位置，不依赖现代源码猜测同版本坐标语义。')],
        parser_correction='本批反汇编bipush/sipush用有符号数；-8与-2已修正，当前证据均为修正后结果。未改原Jar或旧批文件。',
        modern_cached_source_used_as_same_version_proof=False,
        resolved_part_of_old_hold='已用同Jar实际代码补出围界与16墓位的作者布局关系，明确3个随机墓碑及可选陷阱不能独立计数。',
        retained_part_of_old_hold='研究示意未执行随机处理器、地形和数据方块后处理，不是一个实际生成完整实例；真实入口与连续路线仍未知。',
        decision='HOLD_ZERO_AUTHORED_LAYOUT_SUPPLEMENT_NOT_NATIVE_WHOLE_INSTANCE',
        formal_credit_added=0,proposed_credit=0,independent_human_review=False,
        production_allowed=False,java_run=False,game_run=False,network_requests=0,
        checklist_deletions=0,production_changes=0)
    dump('manual-review.json',review)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=43,status='REVIEWED_D010_LAYOUT_SUPPLEMENT_HOLD0',
        previous_receipt=evidence(OUT.parent/'research-20261103-funerary-042/RECEIPT.json'),
        formal_funerary_baseline=149,new_first_scope_proposals=0,previous_042_proposal_pending=False,
        previous_042_coordinator_acceptance=evidence(accepted),
        production_allowed=False,next='保留D010入口/完整生成未知，不以新种子、墓碑或重复图加数；沿固定本地完整相关建筑继续实际研究。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第43批：旧 D010 墓园组装补证，hold0

固定本地 Twilight Forest 1.20.1-4.3.2508 Jar（SHA-256 `0bdc89263616d1b35c32ef82c5e9c14cbd20368e2fe8b468c72a28320be7a778`）内实际类字节及五份模板已读。Python只解码字节，不启动Java、加载类或运行游戏。Jar的mods.toml给出作者、项目主页；没有联网。

同版本作者逻辑补出 NONE/NONE 下16个墓位与中央留白。实际查看两张新研究图（双方向原框/间距示意，以及水平切层）。原框66格围栏闭合，无门或栅栏门。三种墓碑是随机替代，可选陷阱/箱子/亡灵均不是完整建筑。图中统一Full墓碑只表示间距，未证明该全Full结果的种子，也未执行蛛网处理器、地形或后处理。

因此原 `COD4-R004-D010` 保留hold0，不另造新身份、不新增提案。原暂缓原因中的“未知组合关系”得到补充，实际完整生成、入口和连续路线未知仍保留。七项观察、原始哈希及PC范围见 `manual-review.json`、`class-evidence.json`、`recipe-source.json`、`layout-evidence.json`。现代缓存源码不是同版本证据。

本批正式新增0、提案0。协调刚独立验收旧W028，正式墓葬/小型村落礼仪范围现为149/1000，缺851；验收收据SHA-256 `db8ba566b809e6a6c307a2021c5b5947196076a67b58406d7cc0b8ca491f2975`。仅更新本批检查点，不回写历史第42批。第36批保存高度40与固定17–30范围不符，仍hold0，不改范围或裁旗。没有制作/清单删除/共享session或Jar修改，没有Java、游戏、网络、声音亮度或屏幕操作；不声称10小时。
''')
    print('Saved D010 hold0 review, seven observations, scope and local session.')
if __name__=='__main__':main()
