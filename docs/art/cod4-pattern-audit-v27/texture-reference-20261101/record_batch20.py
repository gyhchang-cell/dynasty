"""Material observations from43actually opened armor sources; no tier/recolor inflation."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-20-candidates.json').read_text())['rows']
notes={
746:'蓝底横向短甲片用两档蓝灰，黑色连接底与白灰细扣分开；light图另排许多小岛，不据此推定身上实际块数。',
747:'master图大量黑底宽片，蓝灰细甲带与中间褐色绑带分开；同材升级图重新排岛，非另套身份。',
748:'普通128×64图集上蓝色甲片横排、灰包边、褐色腰束，黑暗底衣保留；身体/脚/小饰件未据整图颜色直接推断。',
749:'红底图用金黄横甲条和黑底布，金属线较亮；与蓝light共布局，改色不新增装备。',
750:'红master仍有黑色大片、黄甲条与褐带，亮金集中小岛边端；不能把整图金色占比直接当胸部金覆盖。',
751:'红普通甲片红暗槽与橙金条明显，皮带褐与肤色小岛独立；与蓝普通保守同族。',
752:'铁light以银灰短横线配黑暗底和少量红扣，近横甲片格局；颜色与金红版不同不是新身份。',
753:'铁master是黑大片/灰线、褐带和几段银边，不铺全身高亮噪点；同升级族。',
754:'铁普通甲片由白灰两色横带和黑槽区分，深皮带不染成金属；保留材质对比。',
755:'下界light金线围暗棕甲片，黑衣/红窄带仍可分；亮边强，作为避免全边高光过多的参考边界。',
756:'下界master的亮金短条集中几块，褐带用更低对比小孔；不把升级图单独计套装。',
757:'下界普通金边/暗棕横片、灰暗臂区、褐绑带，同排岛版本；三档只保守同甲族。',
758:'mask文件比普通图多出下部黑紫面罩与白牙状岛，原普通甲片仍在；整份覆图不当第二套甲。',
759:'紫晶甲片为浅紫两条宽亮带、深紫暗槽，黑灰边扣；浅色中心较多，避免后续全套过曝。',
760:'紫晶mask保留同甲片并在下部加黑面罩/白尖，不能以新增像素或128方图尺寸算独立装备。',
761:'new文件主体紫甲、褐带、下侧小岛近似原版；旧新版本暂同族，不以名字当新作。',
762:'etyrite用灰黑大板和暗绿边，局部靛紫绑段；对比低但材料边界能沿大条读出。',
763:'gray版去弱紫，主体布局和灰绿横片相同；保守并同装备。',
764:'石英源图用米白宽片、深紫红布带与黑边扣，白色仍分两三大档；不依据名字猜宝石材质用途。',
765:'石英mask加下排黑面罩和白牙，甲片同764；合并覆图。',
766:'和服图用低对比暗紫布块，只有领口红橙斜带与一条米白横束明显；长袖褶用稀疏纵折，不靠满布细纹。',
767:'忍者铁款紫黑大布块中留眼口孔，布上低对比交叉束线，独立银色扣/板；同金与下界款同布衣格局。',
768:'忍者金款只将分离扣/甲件换亮金，主布保留黑紫，腰带金条更醒；不增加角色数。',
769:'忍者下界款将扣/甲件压暗褐，主布暗紫一致；低对比作为暗物体阅读局限记录。',
770:'草帽32px图用四个大小阶梯三角岛，麦黄/棕两大档和少数浅草点；没有密密编织噪点，图集中的多面不算多顶帽。',
771:'草帽+面罩128px图仍是小草帽岛加黑紫面罩、白牙；是组合部件复用，不拆独立草帽身份。',
772:'鬼面罩源图用黑紫眉/鼻与一处嘴孔，离散白牙弧；无模型绑定不称实际脸宽或朝向。',
773:'红鬼面把面部换深红/朱红，牙弧仍米白；不拆换色。',
774:'白鬼面有深棕眉部、米白阶梯面与金牙弧；大色区清楚，与两鬼面仍同族。',
775:'狐面为米白长脸岛、两侧棕暗面和集中额/眼下的深红短笔；只读原图，不把特定文化面纹直接复制给目标。',
776:'机械护目款仍同横片甲的灰绿底/金片，图集中很小红绿点与暗小块不能凭名字认定护目镜实际显示。',
777:'mage联动款以高明紫片、金框与青绿下部小岛换材，原普通甲的横片节奏未变；过亮区域作警示。',
778:'钢甲64px改用银灰宽平板、灰紫暗槽，橙黄狭条与褐皮束分开；比横片族更连续，保守单材料布局族，不验槽位。',
779:'draco是黑底、紫边、灰小扣，横甲片仍相同，但对比太低可作反例；不按联动材料扩族。',
780:'fiery深红黑片配大亮金边与灰手臂，颜色集中黑/金两区；改材同甲。',
781:'tyr宝蓝甲片/金边、褐带，灰臂仍单独，沿用相同小片排列；同基础结构。',
782:'ignitium暗红片配亮金框，部分狭条朱红；是同甲材色参考，未检查发光或功能。',
783:'living鲜红横片配褐束/亮金边，灰臂低对比；不以living名称猜动态效果。',
784:'neptunium深青甲片与青绿亮横条，灰黑底/褐带能区分；比高亮粉白更易分主次，仍同甲族。',
785:'sculk深青片、灰绿框、青色腰带小岛，色数有限但底与框有层次；不声称源图生物发光。',
786:'铁木灰褐片与灰边、红褐束线，中性材质较稳；同横片布局合并。',
787:'法术联动黑款有亮金框、黑横片及青绿束带，甲岛位置仍同普通版；16染色目录只选黑白两张核看，不计16套。',
788:'法术联动白款把甲片米白、保留金框青绿束带；按同联动版换色合并。'}
for r in rows:
 n=int(r['reference_id'].split('-')[1])
 if n==766:family,rep='samurai-wide-cloth-sparse-collar',766
 elif 767<=n<=769:family,rep='samurai-dark-cloth-metal-inserts',767
 elif n in [770,771]:family,rep='samurai-stepped-straw-panels',770
 elif 772<=n<=774:family,rep='samurai-dark-mask-separated-teeth',772
 elif n==775:family,rep='samurai-cream-mask-short-red-marks',775
 elif n==778:family,rep='samurai-broad-steel-planes',778
 else:family,rep='samurai-lamellar-bars-leather-binding',746
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',semantic_family=family,family_representative=f'VIS-{rep:03}',
   scope='equipment_material',distinct_family_proposed_credit=int(n==rep),observation_zh=notes[n],
   applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0,
   limitation='只读固定JAR原PNG。变体、mask、新旧与联动材色保守合并；并未证明当前模型前后左右朝向、真实UV对应、renderer/tint或游戏效果，不充完整帝王护卫/装备案例。')
now=datetime.now(timezone.utc).isoformat()
out=dict(recorded_at=now,viewed_pngs=43,proposed_distinct_design_families=7,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='All four overview plus eleven full integer-detail pages actually opened;43PNGs conservative7material groups, not43unique armors. Full cultural designs not copied; global historical dedup still pending.',rows=rows)
(D/'review-batch-20.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Recorded43actual PNGs/7conservative groups/0accepted.')
