"""Human-readable observations transcribed after viewing each research card.
This is a reference ledger, not an art export or runtime validation.
"""
from pathlib import Path
import json,hashlib,html,collections
ROOT=Path(__file__).resolve().parents[3];CACHE=ROOT/'build/bestiary-v43/marshal-reference';DOC=ROOT/'docs/art/bestiary-v43'
# Each line corresponds to the numbered, actually inspected anatomy/atlas card.
OBSERVATIONS='''
高肩、长后腿与阶梯尾连成前后轴；蓝紫皮面分区集中在头颈与足端，借鉴关节不靠逐块黑框分开。
长低躯干接厚尾，四肢从腹侧伸出；橄榄褐斑按身体大面分布，借鉴头躯的长轴连接，不采用鳞皮配色。
细吻接到低头、前肩与长尾；浅颊、深背和肩侧宽带相接，借鉴跨体块的色带，不复制食蚁兽脸。
前胸高、口鼻下伸，暗红肌理与青色局部反差强；借鉴识别区集中，不能把满身红肌理移植到骨马。
海兽背鳍、黄绿覆面与棕头为主；与骨马及军龛的材质和支撑关系太远，仅作看过的辅助资料。
短四足、条纹尾与黑色眼罩很清楚；小型毛兽的尾纹与本目标不相近，排除本目标计数。
高肩承接低头，腹后体量收束；深褐身体留大面、角浅，借鉴前胸比后躯更有重量。
躯干用大圆褶状像素簇，象牙独立浅色，头与厚前腿连在前躯；借鉴硬骨与暗壳分明，不采用鼻子。
高颈、细腿和角构成竖向重心，腹侧浅面连续；借鉴下颌和喉部的连续明度，不把骨马涂成羊。
厚肩与短脖相接，嘴边浅、躯干褐色下行簇；借鉴头躯重叠仍可由材质交界读出。
高腿长耳接细长躯干，橙背、浅颊、深足分三层；借鉴支撑端压暗而观察区保持清楚。
背肩高于后腰，头下垂长吻与暗喉区相接；借鉴肩到颈的承重轴和腹部较浅区域。
粗前躯与低头形成整体，灰皮用粗横簇，角尖独立；借鉴大面可干净，攻击端少量提亮。
长尾从骨盆延续，浅体大块灰黑斑有规则；借鉴尾根连贯，斑点不适合直接用于骨质。
脸颊白、眉眼黑、背部条带连续；借鉴脸的朝向由眼周大片关系支撑，不只是一个发光点。
巨牙在低头两边，浅颈鬃接到暗肩背；借鉴骨牙与暗躯的明度分工，不复制鬃毛。
开敞的细肋与长吻为主，骨白略带绿影；借鉴骨表面不必满裂纹，空隙应由真实几何保留。
上躯有真实开口，暗蓝石面与浅软组织分离；借鉴开口周边暗而里面有明度层次，不画假洞。
帽沿与脸处冷浅色集中，暗靛服装与白色下缘分开；仅借鉴幽灵识别区对比，不采用人形骨架。
中央主体很暗，外伸手臂浅紫，亮绿小区独立；借鉴主核、外肢不同明度，不复制漂浮多臂结构。
高角和细颈承接低长躯干，原图集背褐腹浅、侧面点纹有限；借鉴背腹方向，不添加鹿角。
宽躯短腿与弯角简单，脸鼻浅而毛色大块干净；借鉴少色也能把脸与身体分开。
低头、宽背、外伸吻一眼可读，腹侧与口周浅色连贯；借鉴头颈的宽窄过渡。
深灰衣袍靠少量灰簇分折向，白脸为最大明度点；借鉴誓布压低对比、盲面更醒目。
宽肩巨臂与小头有明确主次，原图集白壳、褐连接分材质；借鉴承重点不与外甲同色。
浅骨头颅、绿暗衣袍和灰骨架分区；借鉴骨与覆物能由明度、纹理方向共同分开。
修正后原图集可见骨白头胸、暗紫袍与少量金饰；借鉴把注意力留在头胸，而非金边；原错误局部图不另计。
小头陷在宽肩上，灰绿大面、淡色眼周与胸部斑组织有限；借鉴压低肩壳装饰密度。
头颈前伸、背刺与粗前肢连贯，暗体里骨白吻和红眼局部清楚；借鉴骨马观察中心与躯壳分开。
头、腹与多节支撑肢有连接，图集中青纹只属于深壳局部；借鉴节间暗连接，不套用蛛形。
马首与颈的折向连续，蓝色身体有较浅腹部，背鳍独立；借鉴额、颊、喉部不同明度，不复制鳍。
鸟喙马身与四足连接明确，暗羽、棕鞍与浅嘴爪分材质；借鉴马身连接与附着装备，黑色只计一种皮肤。
独眼位于眉压下，皮肤浅暖、腰布深、口内暗；借鉴眼窝由眉面支持，不用孤立小方眼。
巨臂、前探颈和弓背压低重心，暗体和浅獠牙分开；借鉴前压的视觉方向，不改现有姿态。
暗紫毛皮保持大面积完整，白牙与红眼只在脸前部；借鉴黑材质仍保留头与下颌层次。
前臂厚、下肢弯曲、口鼻前伸，暗紫外壳与骨白局部对立；借鉴骨铁分材质，不采用多余兽化零件。
四足承托背上装备，蓝绿金属连接与褐色躯干清楚；借鉴装备必须跟着身体承重，不照搬装甲马。
这里只还原了盔甲架基体，穿戴盔甲由其他层提供；不将该卡当成完整空甲怪模型计数。
头部骨灰大面与亮小眼相接，连接节和獠牙另分色；只借鉴骨面层级，不将头部动画或连接长度当已研究。
深蓝斗篷内外明度不同，脸与手更浅；借鉴哀带在暗色里仍有折向，不改军龛形体。
蓝灰脸围住深眼窝，口部浅、衣下摆近黑而非全黑；借鉴观察孔周边需要过渡面。
暗衣料留大空面，骨爪与金属饰件局部露出；借鉴边缘破损集中，不能每条哀带都撕满。
浅灰骨面、鼻口暗、肋条单独展开；借鉴骨面用少数关节暗簇，避免米白塑料。
黑帽与暗袍轮廓连贯，浅色小区围住眼部和上胸；借鉴一个视线中心比全身亮点更明确。
骨架、棕皮革和浅铁部件分区，武器有亮刃暗面；只借鉴材质分工，不接管或改造武器。
黑铁甲把脸口包住，内部连接与绿旧布不同；借鉴盲面与甲框对比，保持不新增派系纹章。
浅骨上附着绿色水生痕迹，紫色小区集中，肋条仍清楚；借鉴附着物不能盖住骨结构。
冷灰盔口与深蓝衣、暗铁腿、少量古金分层；借鉴身份饰边只放头肩与关键接缝。
金色主要在盾缘与腿端，脸灰、身壳深；与同源守卫共享部分构造，只研究实际不同的护甲配色组织，不宣称独立骨架。
骨白脸、暗衣和灰铁护具分明，躯干大面很干净；借鉴内外层与饰边密度不同。
重甲围住凹下核心，暗石铁与骨白支撑分开；借鉴军龛内壁与残留誓物的深浅关系，不复制墓碑。
灰壳大面由红色关节和核心打破，裂纹位置集中；借鉴主壳保持完整，不能把每个部件全描边。
全身冰晶蓝白是这个角色的主材质；与本目标骨铁誓布不相近，仅保留辅助观察，不计入目标门槛。
青灰脸、暗蓝绿衣料，眼口有清楚凹陷与周边色面；借鉴白骨面附近的暗眼窝形状，不照搬颜色。
露骨头颅和黑甲、大红褐覆物互相分开；借鉴内骨可见而外甲不抢眼，不采用全身撒血纹。
暗皮具、锁甲和布面分工，浅脸在上、武器在侧；借鉴连接部用暗但有层次的铁色。
深青面部与暗衣相接，紫色只在少量衣片、金色沿下摆；借鉴色彩有范围，不向每条哀带复制。
浅青幽体的眼口为大深色簇，身体保留几档浅色；只借鉴面部对比，不给军龛全身透明化。
骨白肋架从深袍中显出，金属和暗红仅局部；借鉴真实空腔和骨架的层次，不画在实心板上。
蜜獾的低体和黑白毛区很鲜明，但小型毛兽与军龛骨马材质目标太远，不计入本目标。
粗前臂和低头相接，黑毛可见蓝灰簇、口鼻暖浅；借鉴暗表面不直接填黑。
棕熊与同组熊类的研究用途重合；即使局部构造不同，本目标合并熊类家族，不靠毛色重复增加计数。
低首、厚颈与四足承重明确，褐皮与浅牙分开；借鉴支撑处不靠大脚板制造体量。
厚颈鬃连接头和肩，背褐腹浅、腿下压暗；借鉴长头颈在不同朝向下材质连续。
角、额、吻与长腿比例分明，背褐腹浅、下肢暗；借鉴头颈分区而不增加骨马零件。
双节前肢和肩背相接，褐毛沿体轴与下肢组织；借鉴同一材料跨关节不突然换纹理方向。
窄颈连厚胸，腹侧浅与背面褐色相接；借鉴胸到四足的支撑线，不复制瞪羚轮廓。
宽额与长鼻垂直相接，高肩背后接收细；借鉴骨马头部的颊面与鼻梁需要不同明度。
浅颈胸与暗背分明，颈下毛边靠透明图像呈现；借鉴材质交界用大簇，不建碎毛块。
头与肩的重叠自然，嘴周亮、暗褐背面长簇；借鉴观察部位与覆盖部位密度有别。
前端厚、背部鬃片薄，鼻口浅红、牙浅、身体暗褐；借鉴攻击端有自己的明度关系。
长颈下浅胸与深背连续，腿端略暗；借鉴骨马的额到下颌需要完整色面，不逐面独立填色。
厚肢从大躯干四角承托，灰皮褶簇宽而牙浅；借鉴连接处暗面保留厚度，不复制皱纹。
长颈与身躯折向明显，斑纹跨多个部件组织，腹面浅；借鉴跨体块方向，不把斑纹移植到骨质。
大口与粗前胸相接，粉暗皮和浅牙分开；借鉴上下颌靠实际形体与材质共同成立。
暗颈鬃围住浅面，背腹和尾端成大区；借鉴头部周边压暗，突出观察中心。
厚灰躯壳留干净面，褶纹不抢浅角和前脸；借鉴大板甲无需逐块满纹。
马型身颈和四足连贯，黑白体色和棕红鞍具在一图集分材质；只计一个斑马模型，不把鞍区另算生物。
头盔、暗甲、赤金边与巨刃有主次；借鉴金属边只支持主面、内层更暗，不复制火焰纹和兵器造型。
中央骨体与暗外围盾板分区，浅骨在上；借鉴军龛内核与外框分权重；本卡未展示全部盾纹层，不宣称完整外层研究。
巨肩前臂和暗体以少量紫色核心聚焦，足部信息少；借鉴视线先到头胸，支撑不抢镜。
浅外甲与暗紫内构造相反衬，主手更暗重；借鉴内外层有清楚明度差，不复制石砖肤质。
长吻、前伸骨臂和开敞肋骨相连，骨表面有暖暗关节；借鉴骨白里保留结构根部的暗色。
前压巨臂、深外甲、骨白内躯与青眼有层级；借鉴盲面、空腔、接合处的主次，不移用盔冠。
马型长颈与四足承托，黄橙身体、褐鞍和浅吻分工；仅借鉴马颈接肩，不采纳糖果表面。
长背与低前吻连贯，粉口爪与暗褐背分开；借鉴前向观察区应比背部装饰更明确。
头面向前、背鳍与两臂分开，紫暗壳与浅腹局部分区；借鉴眼窝和面壳不是单独亮点。
此源码卡主要是头部构件，完整身体还依赖动态方块装配；未完整研究前不计为一个完整相关生物参考。
观察头壳为冷灰、主体为绿壳，前部指示区很小；借鉴观察口、动力与外壳分开，不加入科技设定。
长颈与双足、长尾形成重心，紫覆面与浅蓝腹分开；借鉴颈肩连接的覆层方向，不更改四足类别。
长吻与大胸接粗腿，绿背橙腹成清楚大面；借鉴上下材质区分，不将鳞纹铺到骨上。
这里只有悬挂锤体，配套卷扬结构未同卡查看；不将一个构件当成完整参考生物。
长颈与厚胸、四足承托，沙色皮面与暗鞍分开；借鉴背上军龛与承重躯体的材质分工。
高颈与细腿连在横向主体，灰褐大面和浅腹构成方向；借鉴喉到胸的连续浅区。
高角、长颈与下垂胸毛连接，紫褐背和浅颊、腹分层；借鉴附着物必须沿身体方向，不复制皮毛。
厚肩和短腿承重，长毛纹顺躯体往下，不等量铺在脸上；借鉴视觉重心在上、足部简洁。
黑背与宽白腰带围合完整躯干，脸口用很少像素；借鉴材质区跨相邻面连续，不能每块独立上色。
高肩前肢与小头前探，苔色表面大区和浅爪分明；借鉴头、躯干与支撑端不同纹理密度。
低身展开四足，暗绿背、褐色腹与背上附属结构分区；借鉴承重关系可读，不套用长鬃。
圆体大眼与短足，绿皮面的粗簇不盖住眼部；借鉴观察中心，身体纹理不平均铺满。
SmogMog与Mog是近缘构造，本目标合并成同一研究家族，不再重复计数。
下垂细肋和长肢围住前伸头，骨、破布和暗皮分开；借鉴空腔必须真实，骨根、布边与关节有层次。
暗焦油表面用冷暗层次与红眼分区；借鉴暗处保留轮廓和连接，不靠整体填黑。
头颅、外露肋架、皮肉和绿附着物各自分材质；借鉴骨色不是整齐塑料手套，关节有依据。
骨灰脸、暗颈和破衣下缘分明；借鉴盲面周围的阴影与哀带边缘，而不全身涂裂纹。
这里只有灵树的大脸部件，不能代替完整生物模型计数；木材纹理留作辅助，不计入目标门槛。
背部承托上层、粗腿接宽下躯，灰绿铁与棕皮具分开；借鉴承重面和附着装备在材质上属于同一存在。
骨白肋架露于黑铁与褐皮之间，暗面不吞没脸；借鉴军龛中骨、誓物和外铁的独立材质层级。
保留骨架主色，金色肩和前臂集中而足部暗；借鉴身份金属点到为止，不让边框压过主体。
暗甲覆在浅肋外，臂、肩、腿的主面密度不同；借鉴局部大甲面与骨关节的明暗，而非全身包框。
'''.strip().splitlines()
EXCLUDED={5:'水生背鳍与材质/支撑目标过远',6:'小型毛兽的主研究用途与本目标不相近',38:'盔甲架基体不含实际穿戴层',53:'主材质为冰晶，与目标材质不相近',60:'小型毛兽与骨马军龛目标不相近',62:'合并同源熊类研究家族，不重复计数',88:'完整身体依赖未同卡研究的动态装配',92:'只有悬挂锤体，未含完整构造',101:'与Mog合并近缘研究家族',106:'树脸只是完整生物的一个部件'}
ANATOMY=set(range(1,17))|{21,22,23,29,30,31,32,35,36,37}|set(range(60,79))|{85,86,90,91,93,94,95,96,97,98,99,100,107}

def main():
 data=json.loads((CACHE/'candidates.json').read_text());rows=data['items']
 if len(rows)!=110 or len(OBSERVATIONS)!=110:raise RuntimeError('Manual observations must match the actually viewed cards')
 review=[]
 for row,note in zip(rows,OBSERVATIONS):
  n=row['number'];card=CACHE/row['card']
  if hashlib.sha256(card.read_bytes()).hexdigest()!=row['card_sha256']:raise RuntimeError('Reference card changed after study')
  review.append({**row,'viewed':True,'accepted_for_target':n not in EXCLUDED,'target_use':'四足/头颈连接与背负结构' if n in ANATOMY else '骨、铁、盲面、暗布与空腔的材质主次','observation':note,'excluded_reason':EXCLUDED.get(n),'evidence_kind':'Literal source-constructor reconstruction alongside original source atlas; NOT textured runtime/game capture','limits':'No claims of100 independent rigs,100 bosses, full animation inspection or exact runtime layers. Related anatomy/material studies, no copied art.'})
 accepted=sum(q['accepted_for_target'] for q in review)
 output=dict(target='dynasty:gongsun_wuwang',viewed_candidates=110,accepted_for_target=accepted,excluded=110-accepted,required=100,gate='REFERENCE_STUDIES_COMPLETE' if accepted>=100 else 'INCOMPLETE',review_mode='18 original sheets (106 candidates), then corrected Lich +4 follow-up cards; card-level observations transcribed after actual viewing',qualification='100 related anatomy/material designs across several mods, not100 skeletal-horse bosses or100 distinct rigs',source_counts=dict(collections.Counter(q['identity'].split(':')[0] for q in review if q['accepted_for_target'])),rejected_during_preparation=data['excluded'],items=review)
 (DOC/'marshal-reference-review.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 sections=[]
 for q in review:
  flag='采用' if q['accepted_for_target'] else '排除'
  image_path=Path('../../../')/q['card']
  # Relative path is calculated to the actual cache, not a browser localhost workaround.
  import os
  image_path=os.path.relpath(CACHE/q['card'],DOC)
  sections.append(f'<article><h3>#{q["number"]:03} {html.escape(q["identity"])} · {flag}</h3><img loading="lazy" src="{html.escape(image_path)}"><p>{html.escape(q["observation"])}</p><p><a href="{q["model_source"]}">固定版本模型源码</a> · <a href="{q["texture_source"]}">原始贴图</a></p></article>')
 page='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>公孙无望 · 模型与材质研究</title><style>body{max-width:1280px;margin:32px auto;background:#e9ebe4;color:#23312d;font:17px/1.65 system-ui}header{max-width:1000px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:24px}article{padding:18px;background:#f7f7ef;border:1px solid #ccd2c9}img{width:100%;image-rendering:pixelated}a{color:#256b65}h3{font-size:17px}</style><header><h1>公孙无望：四足承重、骨铁和亡灵衣料研究</h1><p>实际查看110份候选，采用100份，排除10份。100指相关构造与材质案例，不是100个骷髅马Boss，也不声称有100套独立骨架。</p><p>图片是固定版本源码静态构造与原始像素图集并排查看，未将图集贴回这些参考模型；不是实机截图。部分模型有共享骨架、额外穿戴层或发光层，只研究实际看过的内容。资料仅用于学习，不向Dynasty复制外部像素或几何。</p><p>当前处于暂停测试期间：没有编译、启动客户端/服务器或游戏验收。研究完成不等于新模型或贴图完成。</p><p>采用原则：骨白盲面为第一识别点；冷暗铁军龛与暖骨分开；真实空腔内壁降低明度；哀带沿垂落方向而非每块包框；马额、颊、吻与喉面连贯；支撑端不抢主核；旧投射物及机关共用贴图必须保留。</p></header><main>'''+''.join(sections)+'</main></html>'
 (DOC/'marshal-reference.html').write_text(page)
 print('Research ledger saved:',len(review),'viewed /',accepted,'adopted /',110-accepted,'excluded; no runtime exports or tests.')
if __name__=='__main__':main()
