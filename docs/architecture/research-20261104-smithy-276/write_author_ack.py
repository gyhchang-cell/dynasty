"""Specific author responses to Main's269 review, without changing sealed269."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
main=ROOT/'docs/cod4/audit-20261022/coordinator-architecture269-whole-stilt-house-preack-review-20261112.json';mb=main.read_bytes();m=json.loads(mb)
assert hashlib.sha256(mb).hexdigest()=='c992f8dda3a7f8904f15fab72faa970a15d57afb8e6c56e3f7ade0b8e8428afc'
assert len(m['Main_findings'])==12 and len(m['Main_limits'])==11
finding_responses=[
 '保留整栋“南有盖廊外作→闭南门→北一床居室→西北内梯→上小储阁”关系，仅最多1NPC06居作辅助候选。不是黑婆/NPC或大沼泽炼药楼成品，也不转COD4资格。此ACK不执行首次carry。',
 '确认Main此次独立查看6原PNG、全41状态Properties/12BE/entities[]与11层121RLE，另用stdlib新解原NBT比对847格；这与作者旧研究区分。本276只读Main保存的7维/23条与边界，不重看图/重读源，不把解码、格数或图片加建筑数。',
 '接受DV3337/7×11×11与387存=289nonair98air、460unknown。主屋x1..5/z1..5、南廊到z9是一完整保存主屋模板；未把支柱/道路/center/居民装入世界，模板完整不等自然落地成品。',
 '西口0,1,6头上0,2,6实木，明确不是可通入口。保留侧向north底阶0,1,8→0,2,7及对应显式头空→floor2南廊→3,3/4,5closed/south/left门的静态关系；不称原生碰撞、跨台或NPC连续路线已验。',
 '床脚3,3,2/床头4,3,2east是同一完整浅蓝床，绝不计两床；z3/4局部卧室air仅居住意图，源entities[]不产生黑婆/居民入住或永久无生物结论。',
 '承认内梯2,y3..8,2east及floor7留洞，东3,7,2TOP半砖/上8、9air的储阁落脚拓扑。4,8,4north箱前4,8/9,3与箱上4,9,4air只支持原格关系，不代表爬梯、开箱、NPC操作成功。',
 '屋盖是darkoak整木阶梯收缩体积：y8外0..6、y9内1..5、y10内2..4；不是木stairs构成的斜坡。南廊top/bottom半砖另分，原类色整格会覆盖薄件/开放栏形；不证明屋下净空、防雨/火或碰撞。',
 '4,3,6west炉原unlit/空Items/三计时0/RecipesUsed空，上4,y4..6,6三cobblewall只是户外作业/烟饰上下文，没有熬药/排烟运行。四魂灯也不当实机光照或黑婆夜间周期。',
 '六接口x1/5,y1,z1/5/9都是up_west/rollable/finalvoid，指向rigid八feature列表，并非六实存落地柱。原y0只有x0,z8/9两土径格；height63和七updater负偏移/邻水谓词只是配置，placementtag/引擎/实际地形没展开，不能保证63格柱或水浸适配。',
 '区分Main完整读取10JSON/3metadata与程序hash核值：houses27项本屋权3/street、root size6/max80/start0/terrainnone/expansiontrue、直swamp tag仅固定源；二center NBT未读，居民池1/1/10只是候选权重，不说三NPC或当前包已激活。',
 '保留原箱负seed-1372024240092464241、单pool3..8rolls十候选及random_sequence原vilage_swamp_house拼写。不改表名、不发奖励/编注册ID，不把候选loot当库存、NBT取得、付款或进度回执。',
 '比较使用旧239已更正的单东入口有效七维及原8/Main10限制；宽同层南工厅北服务/桶台无床梯，对照本窄南廊卧室内梯上储的整体。旧239只first243一次、现在0，不恢复历史双入口，不称穷尽全部近族。Main仍可MERGE0/HOLD0。',
]
limit_responses=[
 '这23条逐项回应送Main最终审查，尚不接受或首次carry269。最多1NPC06完整辅助空间，formal0，无炼药楼、NPC、交易、中文指南针或原任务整项验收。',
 '自然地基/柱落地/水位承托/道路接地均未证；没有运行feature或拼world。完整主屋source研究不能越级写成自然生成整栋已验。',
 '460unknown绝不改为98air；y11切面超过sizeY11，明确outside，不是源空气。类色图不能验真实材质、薄件形状或碰撞。',
 '接受最终48独立probe=47境内+1(3,11,3)境外，并非48都境内或作者200逐格全部重看。Main121RLE阅读/847解码核值不等847逐格人工源块语义，更不按位置计参考。',
 'Main独立stdlib新解码与作者脚本分开记录；原字节及24绑定仅身份/复现0额外语义信用。本276不运行作者旧脚本、Java或额外源研究。',
 '10完整JSON读与未展开placementtag/vanilla water/feature引擎、center/路/居民NBT/structure set/全包覆盖分别保留。mod/packformat/DV3337声明不当当前部署兼容证明。',
 'closed门、open竖活板/门栅、top/bottom半砖与梯朝向按原状态保留。未做爬梯/床箱炉操作、NPC路径、灯雨火、生存或性能原生验收，不用局部air补齐。',
 '一床两半、空炉、概率箱、六socket只整屋组成，不拆建筑或功能信用；269F01/F02有界材料预筛仍0，不借本次审查追认。',
 '旧239保存有效7维/原8/Main10限制供有界比较；更老嵌套历史、旧source/PNG本276未重新完整阅读，不声称全家族全局新颖。Main90KB全对象原样另存，不把保存等同全部人工读。',
 'COD4仍153缺847，所有NPC累计null；1000适用完整相关建筑仍未达，不制作。239first243、259first263、260first267及其后重复0保持，本276所有carry0。',
 '本次只有本地证据/ACK写入；无Java/游戏/网络/进程/显示/声亮/唤醒/焦点/实例原档/共享Jar/专业生产/主清单/Git/自动化/新聊天操作。未删提示词、未报主动工时或全部完成。',
]
assert len(finding_responses)==12 and len(limit_responses)==11
(OUT/'Main269-review-original.json').write_bytes(mb)
ack={'batch':276,'source_review':bind(main),'full_original_saved':bind(OUT/'Main269-review-original.json'),
 'actual_reading_scope':'Main own seven dimensions, all12 findings/all11limits, coverage/decision/boundaries and count correction fully displayed after initial large fullobject output clipped; nested full239 objects preserved but not claimed wholly reread this batch.',
 'Main_seven_dimensions_original':m['Main_seven_dimensions'],
 'finding_responses':[{'index':i,'Main_finding_original':x,'actual_author_response':y}for i,(x,y)in enumerate(zip(m['Main_findings'],finding_responses),1)],
 'limit_responses':[{'index':i,'Main_limit_original':x,'actual_author_response':y}for i,(x,y)in enumerate(zip(m['Main_limits'],limit_responses),1)],
 'maximum_269_whole_candidate':1,'current276_new_whole_studies':0,'formal_credit_added':0,
 'first_carry_added':0,'Main_final_pending':True,'native_acceptance':False,
 'old_NBT_PNG_newly_read':False,'sealed269_modified':False,'checklist_deletions':0}
put('author-ACK269.json',ack)
source=ROOT/'docs/architecture/research-20261104-smithy-269/RECEIPT.json';sr=bind(source);assert sr==m['source_receipt']
for f in json.loads(source.read_text())['files']:assert bind(f['path'])==f
prev=ROOT/'docs/architecture/research-20261104-smithy-275';s=json.loads((prev/'session.json').read_text())
s.update({'batch':276,'status':'AUTHOR269_SPECIFIC23ACK_PENDING_MAIN_FINAL','new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'previous275_receipt':bind(prev/'RECEIPT.json'),'author_ACK269':bind(OUT/'author-ACK269.json'),'269_first_carry_executed':False,'next':'269 author23ACK awaiting Main final;275/273 pending. Continue next distinct related whole source, no repeated carry.'})
put('session.json',s)
protected=[]
for r in json.loads((prev/'protected-inputs-current.json').read_text())['files']:
 before=r['current275'];now=bind(before['path']);protected.append({'previous275':before,'current276':now,'unchanged':before==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':0,'cod5_missing_not_invented':True})
put('active-checkpoint.json',{'batch':276,'status':s['status'],'session':bind(OUT/'session.json'),'author_ACK':bind(OUT/'author-ACK269.json'),'new_whole_studies':0,'formal_credit_added':0,'first_carry_added':0,'native_acceptance':False,'all_tasks_complete':False})
checks={'Main_current_binding_stable':bind(main)==ack['source_review'],'full_original_bytes_equal':(OUT/'Main269-review-original.json').read_bytes()==mb,'exact_findings12_original_preserved':[x['Main_finding_original']for x in ack['finding_responses']]==m['Main_findings'],'exact_limits11_original_preserved':[x['Main_limit_original']for x in ack['limit_responses']]==m['Main_limits'],'all23_specific_responses':len(finding_responses)+len(limit_responses)==23,'sealed269_receipt_and_all_files_unchanged':True,'protected8_unchanged':len(protected)==8 and all(r['unchanged']for r in protected),'zero_new_credit':True}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'passed':True})
put('RECEIPT.json',{'batch':276,'status':'SEALED_AUTHOR269_23ACK_PENDING_MAIN_FINAL','files':[bind(f)for f in sorted(OUT.iterdir())if f.is_file()and f.name!='RECEIPT.json'],'checks':checks,'new_whole_studies':0,'formal_credit_added':0,'first_carry_added':0,'tasks_deleted':0,'all_tasks_complete':False})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'ACK':bind(OUT/'author-ACK269.json')},ensure_ascii=False))
