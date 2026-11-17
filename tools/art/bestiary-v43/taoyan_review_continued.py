"""Manually written observations of 131 inspected model/atlas candidates.

This writes research evidence only. It does not author or validate game assets.
All counts derive from explicit decisions, never from downloaded file counts.
"""
from pathlib import Path
import hashlib, html, importlib.util, json, os
ROOT=Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/art/bestiary-v43'
spec=importlib.util.spec_from_file_location('seed_review',Path(__file__).with_name('taoyan_review.py'))
seed=importlib.util.module_from_spec(spec);spec.loader.exec_module(seed)

MORE_NOTES='''
叠壳压住短颈与四肢根，褐背和浅口部明确分区；借鉴硬壳外壁与下方连接不同明度，不能把壳纹复制到口内。
长口器从小头伸出，暗褐躯与红色腹端、淡翼分工；只借鉴攻击端和躯壳分区，不学习飞行或新增口器。
球头、细杆和薄肢构成病毒状浮体；与铸鼎的承重壳体、骨腿和大口关系不足，排除。
背部成层硬片、短足从低腹接出，石质甲与暖色腹足分开；借鉴上壳大面、腹下连接简化，不把每片描整圈。
深蓝节体、橙色薄翼和关节冷色簇分开；只研究多足根部与躯壳的色区，翅翼不用于本目标。
背壳黄褐大区、头足暗蓝，颈根缩在壳前缘；借鉴外壳与内部承托不同明度，保持大面清楚。
低宽主壳压住短腹，细肢和尾在侧后；棕壳用少量深色带分层，借鉴鼎壁与外围附属构件不同密度。
厚腹与头胸、粗前肢形成主次，紫暗壳围着少量青亮区；借鉴动力重点集中，不把所有足端点亮。
短颈接横向厚身、多条短足承托，原图集蓝色斑面较密；只借鉴无肩臂的多足连接，纹理密度需比它克制。
宽口与鼓腹比四肢大，青色上躯与暖腹分区；借鉴口、内腹、外壳不同材质，不复制蛙形与配色。
前端两只眼、扁长背壳和薄侧肢明确，红褐口与背部棕色带区分；借鉴背壳与口端连续但不混色。
小壳带放射状尖构件，暗铁大面、接缝与红观察点区分；借鉴铸件外壳和内部装置分工，不引入水雷机制。
糖果红白条与直立玩具式肢体和本目标不相近；不以图集复杂当作相关参考，排除。
前压上躯、大口和长肢相连，深褐皮层中口内浅牙集中；借鉴巨口内外明度，不能给鼎身画满皮肤纹。
生化躯体、绿色皮肤与粉色脑区更接近巨型僵尸；不足以服务多足铸鼎材质，排除。
直立核装置与明绿电路面属于现代设备语汇；不把科幻面板搬到古鼎，排除。
宽腹、头胸和多段粗足有实际连接，棕壳大面用有限块面；借鉴背壳重量经腿根传到多足，关节更暗。
小飞虫的薄翼、毛体和细足，无法补足重壳、承重肢与口内研究；排除。
两段柔软蛆体与黑黄原图集，缺少硬壳和明确承重结构；排除，不因亡灵题材就算相关。
鱼体、鳍与口端虽有尖牙，但与鼎体承重连接、壳腹关系不近；与首批鱼形候选同标准排除。
上胸厚壳、骨色面与深铁躯区分，腹部连接有真实层叠；借鉴暗壳不吞掉内构，骨色只在身份位置。
厚石躯、红色内核和关节暗面不同明度，手足简洁；借鉴主壳、动力区、活动连接三层，不能将裂纹全身复制。
巨壳前方留有口与内槽，炉红集中、灰石面留白；借鉴开口及内腔有深浅层，不把鼎口画成平黑面。
中央火体被暗铁笼架围合，底部短支撑与上口分工；借鉴笼/壳与内容物分材质，亮处限于内部。
中心头体、水平环片与悬垂构件明确，原图集暖核心对冷灰笼架；借鉴活器物的中心与外围不同亮度。
中央火体外有独立护面，面片内外明暗不同；借鉴外围防护不应与核心一样亮，不新增火焰结构。
暗绿腹、头与白网区有范围，粗足从胸部接出；借鉴多足主躯与足根同材质而内侧更暗。
长腿支起两个短主块，黑体内少量黄绿集中；借鉴关节与内部驱动力可读，不能把它的细长比例用于重鼎。
宽口的白齿集中在暗色口缘，棕内层与外层相分；借鉴口边与内壁不同材质密度，不新增牙形几何。
直立细躯与四肢、近黑皮纹的重点不足以服务铸鼎；排除，不能只因有观察点就计入。
犬体、骨色毛与四足属于另一类兽形研究；与本目标的铸壳、多足和内腔不足相近，排除。
厚方主躯与粗短四足形成重量，灰褐外皮和冷暗下层分开；只借鉴承重点和下腹明度，不照抄兽头。
大口位于前躯，后部鼓起、四足压低，绿壳与粉色口内分区；借鉴口内外与支撑部分工，不改变现有鼎类主题。
重壳压低、前钳明显大于侧足，紫晶只在少数部位；借鉴攻击端和普通足纹理密度不同，铜壳不能涂成晶石。
巨型深色铸壳、口腔和暖内部连贯，亮边并非覆盖所有面；借鉴内腔重点、壳面留白和活动端的磨损位置。
头身紧凑、两侧短肢与底足接近整体壳，暖口对冷外壳；借鉴小器物角色如何保持中心，不能另计它的换色皮肤。
厚石片与重前肢相连，灰底、少量珊瑚色和内槽有主次；借鉴附着层不应掩盖主壳，材料边界对应现有部件。
弯曲大臂压在低躯侧，红硬表层与浅内层分开；借鉴外壳、接合面和内侧不同色阶，不沿用珊瑚纹。
低头胸、腹部与多足连接，深蓝紫大面中眼和端部点亮；借鉴暗壳保留关节层次，不以纯黑填足根。
巨钳侧倾压住细多节足，橙壳和蓝色少量区域分工；借鉴钳/足功能层级和节间暗面，不新增枪械外观。
深色上壳和外围刺、下方支撑相接，白观察区集中；借鉴暗壳识别点与安静附属构件，不复制海胆造型。
这份是持械海族混合体，头冠和手持结构占主导；与多足鼎的壳腹关系不够相近，排除。
前方打击端、厚机身和履带式底座层次不同，铁灰、红内核与连接分区；借鉴活动装置与壳体分材质，不沿用科技主题。
小机械观察中心接外围构件，浅灰壳与红内核有界；借鉴内部动力可读而壳面不全发光，不将浮体当承重范例。
头部观察器、中心铁壳、两侧构件的明暗不同，红只在局部；借鉴主壳和动力中心的主次，不能复制火器轮廓。
中心骨色面、暗甲与外围防护有实际间隔；借鉴封闭防护和内部意志中心区分，不把甲面全部画亮框。
大胸壳、巨臂与短下盘分工，浅硬材和暗紫内层有对比；借鉴厚外壳的受力边与内部连接，不复制纹章。
骨性多足从低前躯接出，深铁壳与骨白暗纹不同；借鉴二阶段骨腿与鼎体的材质交界，眼部亮色只少量。
开口由几块大颚包围暗内层，绿叶外层与红口区分；只研究大口可读性，不把鼎类改成食人花。
石壳带突出矿晶，足端暗而眼和面部浅；借鉴厚壳、附着物、支撑末端不同材质，不复制矿石皮肤。
头低、背高、足从壳侧伸出，深紫壳与浅蓝口端分区；借鉴上壳覆盖腿根、前端观察区更清楚。
与ChargerEetle同族共享大量躯壳和图集语言；作为翼壳对照合并研究，不额外占一个相近参考名额。
宽口、鼓腹和粗短支撑互相连接，深紫背与浅腹分开；借鉴器皿外壁和内侧/腹下的明度边界。
上方独立螺壳承托软体，浅壳与暗底、头部不同材质；借鉴硬质器皿与内部活体相互区分，不复制螺旋纹。
壳盖成完整主块，红壳与绿软体颜色断开；借鉴活器物不是一体涂同色，支撑末端更暗更简单。
树皮躯体与枝叶附肢的题材和材料不对应铜、骨、铁；只读后排除，不把木材参考硬塞进活鼎门槛。
近黑表面仍用少量褐灰与口部红区辨出前后；借鉴鼎内暗材有层次，不能靠纯黑抹掉深度。
宽大颌口覆住头胸，细长舌与口内颜色集中；借鉴已有口部和内腔应先清楚，不擅自新增舌器官。
抬高腹壳、下方小头和多足连在一起，暖壳浅腹明显；借鉴主体重量由细连接过渡到多个足根，纹理不逐节描框。
整体石壳里有前端观察口，冷灰与少量暖黄分别对应外壳和附着层；借鉴活石/活器物有清楚的驱动中心。
口样大开口位于壳体中，内壁分层、外层冷灰简洁；借鉴器皿内外有真实空间时再用色阶强调，不画假洞。
主体厚、短足低、口内红与浅齿集中，外壳留大暗面；借鉴口部是意志中心，腿足降低对比。
此份是普通石质人形加衣料，缺乏目标的壳腹、多足与口部关系；排除。
长身与两端低块以少量黄褐区分上下，细节稀疏；借鉴低伏外壳连接短支撑，不把留白误作未完成。
正面张口围绕暗内区，外围附肢与主体不同密度，牙区有范围；借鉴饕餮开口与壳壁的视觉等级，不照抄牙列。
厚腹与头胸、侧后多肢相连，暖壳保留大面，眼点局部集中；借鉴腹壳与连接不同信息量。
悬体下有分叉肢，深蓝外表用成组横层，浅面只在前；借鉴口端、腹壳和支撑分材质，不借用飞行方式。
层叠壳片与短顶核相连，深蓝纵纹与端面分区；借鉴重复外层仍有长轴方向，不把相同线条四面复制。
与Termasect近似的层叠躯壳作并列研究，当前变化不足以另占一个独立参考；合并不计数。
此份主体更近普通双足战斗角色，黄绿表皮不能支撑本轮铜骨材质研究；排除。
与上一份同类直立爬行者，缺乏目标壳腹和多足重心；不因名称有Crawler就计数，排除。
紫色直立角色、细臂与头部符号和目标不相近；排除。
虽然叫InsectFourteen，实际是普通双足装束角色，不能仅按名字当甲壳生物；排除。
低主壳盖住侧肢连接，绿背、紫暗下腹和末端差异清楚；借鉴外壳与腹下支架的明度，不复用花斑。
宽壳压住口和短足，深绿外壁、浅齿与暗嘴有区别；借鉴厚壳保留干净面、注意力在口缘。
铸石大胸与短支撑、巨前肢相接，灰壳与橙内层分开；借鉴外部承重与内部能量区域不混同材质。
简单人形底模与单一绿皮图集，缺少目标相关结构与可用材质组织；排除，不用低质量例子凑数量。
普通石质人形大面纹理近均匀，不能补目标的内腔、口部和多足研究；排除。
'''.strip().splitlines()
MORE_EXCLUDED={
 3:'病毒浮体与目标不相近',13:'糖果材质及玩具式身体不相近',15:'巨型僵尸材质不相近',16:'现代核装置语汇不适合目标',
 18:'细飞虫不足以支撑目标的重壳研究',19:'软蛆体不相近',20:'鱼形与目标壳腹/承重关系不相近',30:'细长直立皮体不相近',31:'犬形毛体不相近',
 42:'持械海族形态与本目标不相近',52:'并入ChargerEetle同族壳体研究，不重复计数',56:'树皮枝叶材料不相近',63:'石质衣着人形不相近',
 69:'并入Termasect近似层叠躯壳研究',70:'双足爬行者不相近',71:'双足爬行者不相近',72:'直立角色不相近',73:'并非本轮需要的甲壳结构',
 77:'简单人形与材质不足以支撑本目标',78:'普通石质人形与目标不相近',
}
BOUND_NOTES='''
六足分从三节躯壳接出，头胸腹的褐色纹路不同密度；借鉴二阶段腿根和主壳相连，沙漠/丛林皮肤只取一种。
与工蚁共用肢体基础，但源码头9×6×11、颚4×2×11，工蚁头8×6×10、颚4×2×6；借鉴攻击器官与承重肢分工，不声称独立骨架。
后腹明显扩大，前躯和六足仍连贯，暗褐腹与小亮眼分区；借鉴巨大主壳下的支撑分布，不等比放大足板。
上躯抬起、前肢弯折而后足支地，壳面长轴与横向腹节不同；借鉴攻击端与支撑端材质密度区别。
翼壳薄面覆盖节体，棕壳与浅翼膜不同材质；只研究外壳覆盖与躯体连接，不增加翅膀或另计不同皮肤。
长节身前端口器突出，骨浅外层与暗口内、节间有边界；借鉴骨鞭沿长度组织材质，不能满身撒裂纹。
宽低蟹壳、粗钳和多条侧足连接，红背、浅腹与暗关节分区；借鉴主壳大色面和腿根明暗，不复制蟹造型。
厚壳承托背部几块高体量，浅口、暗底和石壳分开；借鉴鼎上口、侧壁和脚部不同层级，额外矿层未当独立参考。
这是StoneMinistrosity绑定，冷石外壳、暖眼与暗口分区；借鉴紧凑活器物的观察中心，不把Redstone换皮另算。
源码含八条重叠的构造腿，运行腿姿由动画决定，不能把本卡当步态；骨白脸与深红体明确，借鉴骨端/暗连接分材质。
蟹足多节从低壳两侧伸出，暖棕壳、浅腹与暗足端不同；数据中red为实际物种皮肤之一，只研究一张，不数其他换色。
大腹、低头胸与外展粗足相接，深躯配橙色节段集中；借鉴骨足分节的材质节奏，但不把每段都加亮箍。
双壳围住真实开合空间，暗蓝内壁与暖浅壳纹分开；借鉴鼎口、内壁和外壳不是同一种材质，不把壳面画成平黑洞。
扁壳、伸颈、四肢沿壳根接入，浅腹和绿背分区简洁；借鉴少像素仍分清上下层和支撑，不照搬动物形态。
这份以游泳薄鳍为主要附肢，和重鼎的承重足、骨鞭关系不足；排除，不因同为节肢类就放宽标准。
小甲虫靠极少深浅棕大色区分头胸、背与足，背面留白；借鉴低分辨率分区，不能用随机黑点代替结构。
兔形巨体与毛、蘑菇的组织不对应本目标；排除，不把体型大等同相近。
无正常肩臂的厚躯，观察孔大而支撑简洁，暗紫壳和浅重点区分；借鉴活器物驱动力可读，不复制蘑菇主题。
长主躯覆深色硬壳，腹下暖色、头端与支撑颜色有主次；仅借鉴热内层/冷外层与连接分区，不将鼎改成长颈动物。
粗头胸和张口通过关节连接，绿背、浅口缘与暗内层分开；借鉴口内空间及下颌的材质组织，不新增蛙形结构。
低宽主躯、四足与大口在同一方向，暗紫外层中亮眼浅齿集中；借鉴核心位于头口而非平均点亮所有脚。
普通直立腐化角色的衣皮和瘦四肢不对应铜骨鼎体；排除。
厚颌、前躯与折足相连，石质外层中口内暖色很少；借鉴头口为重点、足外面保持安静，不复制翼/耳结构。
长壳体两侧分布多组关节足，蓝色图集仅少量浅色环集中；借鉴一条主躯与多足的连续配色，不复制蓝色主题。
低宽重躯与口鼻、粗短支撑相接，深色外皮与骨白攻击端区分；借鉴骨质接触端和暗壳的主次，不使用皮毛纹。
兽形皮毛虽有四足，但冰白/腐皮与当前铜骨鼎材质缺乏具体关联；排除，不重复泛化四足参考。
双躯直立人形、臂腿与本轮活鼎关系不足；排除。
紫色双足方躯与臂框主要是另一类构造，不足以补内腔、口部和多足研究；排除。
多臂人形昆虫士兵与本目标连接逻辑和材质组织不相近；排除，不按Insect名称凑数。
'''.strip().splitlines()
BOUND_EXCLUDED={15:'游泳薄鳍与承重壳体关系不足',17:'兔形毛体不相近',22:'直立腐化角色不相近',26:'兽形冰白/腐皮材质不相近',27:'双躯直立人形不相近',28:'双足方躯与目标不相近',29:'多臂人形不相近'}

def main():
 rows=[];unprepared=[];batches=[]
 for directory,notes,excluded in [
  ('taoyan-reference',seed.NOTES,seed.EXCLUDED),
  ('taoyan-reference-more',MORE_NOTES,MORE_EXCLUDED),
  ('taoyan-reference-bound',BOUND_NOTES,BOUND_EXCLUDED)]:
  cache=ROOT/'build/bestiary-v43'/directory
  data=json.loads((cache/'candidates.json').read_text())
  if len(data['items'])!=len(notes):raise RuntimeError('Explicit notes missing for '+directory)
  batch_rows=[]
  for r,note in zip(data['items'],notes):
   card=cache/r['card']
   if hashlib.sha256(card.read_bytes()).hexdigest()!=r['card_sha256']:raise RuntimeError('Card changed since inspection: '+str(card))
   row={**r,'batch':directory,'batch_number':r['number'],'number':len(rows)+1,
        'card_relative_to_gallery':os.path.relpath(card,DOC),'viewed':True,
        'accepted_for_target':r['number'] not in excluded,'observation':note,
        'excluded_reason':excluded.get(r['number']),
        'limits':'Literal source-constructor view plus original atlas, not a fully textured native render or animation playback. Shared rigs, variant skins and combined families are disclosed.'}
   rows.append(row);batch_rows.append(row)
  batches.append({'directory':directory,'viewed':len(batch_rows),'accepted':sum(x['accepted_for_target'] for x in batch_rows)})
  unprepared.extend({'batch':directory,**r} for r in data['excluded'])
 identities=[r['identity'] for r in rows]
 if len(identities)!=len(set(identities)):raise RuntimeError('Repeated creature across research batches')
 accepted=sum(r['accepted_for_target'] for r in rows);remaining=max(0,100-accepted)
 out={'target':'dynasty:taoyan_zhishi','scope':'One already registered living cauldron, including its existing bone-leg second form.',
      'viewed_candidates':len(rows),'accepted_for_target':accepted,'excluded':len(rows)-accepted,'required':100,
      'gate':'REFERENCE_STUDIES_COMPLETE_ART_NOT_STARTED' if accepted>=100 else 'INCOMPLETE_NO_ART_PRODUCTION',
      'identity_basis':'Published creature/model designs and relevant anatomy/material studies; one skin per design. Shared rig is not an independent rig. GliderEetle and Termid merged with related studies.',
      'batches':batches,'items':rows,'unprepared':unprepared,
      'source_reading_exclusions':[
       {'source':'Polarice3/Goety-2:EternalCauldron','reason':'HumanoidModel registered via CuriosRenderer/WearRenderer: wearable item, not creature.'},
       {'source':'DivineRPG:DemonFurnace/BoneChest/FrostedChest/EdenChest','reason':'Files are under client/models/block; block models, not creatures.'},
       {'source':'AoA1.16.5 pinned tree','reason':'Creature model source is present, matching original PNGs absent from inspected source tree; no extra target references counted.'},
       {'source':'DrZhark/mocreaturesdev pinned tree','reason':'Relevant model source found, no matching original PNGs in inspected tree; no target references counted.'}],
      'applied_principles':[
       '鼎壁外壳、口缘、真实内腔、下腹承托分大区；内腔有深浅，不画假洞。',
       '铜壳留完整大面，暖内层只在开口；暗铁集中腿根、轴和受力连接；骨端和骨鞭另设少量色阶。',
       '二阶段多足与主壳连贯配色，节间更暗，普通足降低细节和对比；口缘/核心先于装饰。',
       '不复制参考PNG/纹章/模型，不改变现有主体、武器、骨架、技能和时间轴。'],
      'runtime_changed':False,'compile_tests_or_game_run':False,
      'production_hazards':['Main16px PNG shared by spells and two block models: keep legacy consumers unchanged when actor UV is repacked.',
                            'Phase2 geometry uses phase1 texture for first32 transition ticks: phase atlases must use compatible UV/material semantics.'],
      'limits':'These are 100 relevant structure/material studies, not100 cauldron creatures,100 independent rigs or100 game screenshots. Source snapshots pinned, raw PNGs used for study only.'}
 (DOC/'taoyan-reference-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 page='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>饕餮之食 · 模型与原始贴图参考</title><style>body{max-width:1100px;margin:30px auto;padding:0 20px;background:#e9ebe4;color:#23312d;font:17px/1.65 system-ui}article{margin:24px 0;padding:18px;background:#f7f7ef}img{max-width:760px;width:100%;image-rendering:pixelated}a{color:#256b65}.skip{border-left:5px solid #957254}.use{border-left:5px solid #527e66}</style><h1>饕餮之食：多足铸鼎参考</h1>'''
 page+=f'<p>逐张看过{len(rows)}份候选，采用{accepted}份，排除{len(rows)-accepted}份。未补足数：{remaining}。每份含来源、固定版本、原始图集及独立观察。</p>'
 page+='<p>本页是源码静态构造和原始图集并排研究；不是逐面贴图后的参考截图，不是实机截图，也没有回放参考动画。不把100份研究说成100种活鼎或100套独立骨架。原始图集仅研究，不复制到Dynasty资源。</p><p>本轮仍是研究记录；运行模型、UV、PNG、骨架、武器、动画与游戏均未修改或运行。参考完成不代表美术资源完成。</p><h2>归纳用于现有角色的方法</h2><ul>'
 page+=''.join('<li>'+html.escape(p)+'</li>' for p in out['applied_principles'])+'</ul><p>已查明：原16px贴图另供技能/方块使用；二阶段开头32tick临时使用一阶段PNG。后续不能盲目扩大或各自乱排UV。</p>'
 for r in rows:
  page+=f'<article class="{"use" if r["accepted_for_target"] else "skip"}"><h3>#{r["number"]:03} {html.escape(r["identity"])} · {"采用" if r["accepted_for_target"] else "排除"}</h3><img loading="lazy" src="{html.escape(r["card_relative_to_gallery"])}"><p>{html.escape(r["observation"])}</p><a href="{html.escape(r["model_source"])}">固定版本模型源码</a> · <a href="{html.escape(r["texture_source"])}">原始贴图</a>'
  if r.get('binding_source'):page+=f' · <a href="{html.escape(r["binding_source"])}">纹理绑定来源</a>'
  page+='</article>'
 (DOC/'taoyan-reference.html').write_text(page+'</html>')
 p=ROOT/'tools/art/bestiary-v43/progress.json';d=json.loads(p.read_text());d['reference_gate_by_target']['taoyan_zhishi']=accepted
 d['taoyan_research_current']={'status':out['gate'],'viewed':len(rows),'accepted':accepted,'excluded':len(rows)-accepted,'required':100,'remaining':remaining,'record':'docs/art/bestiary-v43/taoyan-reference-review.json','binding_inspection':'docs/art/bestiary-v43/taoyan-binding-inspection.json','runtime_changed':False}
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 p=DOC/'unfinished-registered.json';d=json.loads(p.read_text());d.setdefault('research_progress',{})['taoyan_zhishi']={'reference_gate':accepted,'required':100,'art_started':False,'record':'docs/art/bestiary-v43/taoyan-reference-review.json'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 p=DOC/'research-resume-20261028.json';d=json.loads(p.read_text());d['current_reference_gates']['taoyan_zhishi']=accepted
 entry=f'Taoyan cumulative{len(rows)} source/atlas cards viewed;{accepted} adopted,{len(rows)-accepted} excluded; source-only/wearable/block candidates not counted'
 if entry not in d['completed_this_session']:d['completed_this_session'].append(entry)
 d['next'][0]=f'Taoyan reference studies{accepted}/100; actual material/UV production remains pending, not marked complete'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'research_viewed':len(rows),'adopted':accepted,'excluded':len(rows)-accepted,'remaining':remaining,'batches':batches,'runtime_changed':False},ensure_ascii=False))

if __name__=='__main__':main()
