import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main=R/'docs/cod4/audit-20261022/coordinator-architecture239-actual-whole-preACK-20261112.json';m=get(main);orig=R/'docs/architecture/research-20261104-smithy-239/manual-review.json';o=get(orig)
assert bind(main)['sha256']=='c95008b3d6237538633cef521c3edf604fc74c1de62ccc3758c41af7e8012e61'
assert m['complete_original_seven_dimensions']==o['seven_dimensions']and m['complete_original8limits']==o['limits']
raw=Path(m['raw_independent_audit']['path']);assert bind(raw)==m['raw_independent_audit']
responses_findings=[
'已实际逐条读Main全部11发现/10限制与其完整保存的原7维8限。承认Main独立解码/全对象和RLE对比、6PNG实际查看的范围；本242只对保存的原解码入口48条格记录作有界重读，未声称再次整栋看PNG/读NBT或新增参考。整栋仍仅1候选，不按4998格/74状态/6图加数。',
'接受21×14×17包含外展木台、阶、屋顶和烟饰；floor2/use3长厅+北桦木后间是一整栋，未见床/内梯/上经营层。修正旧“两侧入口外展”为“东入口阶和西侧木台外展”，不把宽度等同双入口。',
'确认原作者双入口判断有误：本次实际重读z10/11各4,0底阶及其4,2oak，3,1底阶紧上3,2oak。两组均被实木平台覆盖，不能建立成人连续入口。原manual及239比较judgment保留历史；新有效判断为西侧台下阶状装饰/支承几何，至少没有入口净空证据。绝不通过删木板或修源来圆原结论。',
'已核东z10/11三阶19,0→18,1→17,2各正上+1/+2皆air，16/15,y2spruceplanks且y3/4air。只保留一处东向静态登台组织；源格连续不等实时碰撞/NPC寻路/地形落地合格，西侧不作第二入口。',
'北后间宽口与三桶/craft靠厅可达格的空间组织仍保留，但比较205/206时改成“单东入口通同层服务长厅”，不是双入口优势。205floor4/7及未证梯背、206低室/高3双锅平台原7维9限全文保留在Main对象中，原HOLD均不升级。',
'接受木柱木板框架/砂岩围护/桦木后间与玻璃4原状态；y1局部air不能忽略y0低石底板，也不能从柱脚推天然水位和稳定吊脚结构。灰分类色只是绘图，不是实际纹理或石屋顶判断。',
'接受交叉屋脊和y6..11坡盖属非经营屋顶，10,3,13炉、上石柱、10,12,12hay及10,13,12lit营火+四open活板是原烟饰。没有证明安全排烟/防雨/可上屋顶或已烹饪，维持原限制。',
'接受三桶原同概率loot/no seed、craft与空unlit炉/timers0。炉前10,3,12air而头格10,4,12TOPsouth石阶/10,5,12cobble，不能称完整头高工作位；桶接近格也不能替代交互操作验收，无熬药设备或箱存货结论。',
'接受原up_west aligned接头与down_west的1×2×1原刷怪组件，完整zombie/钓竿/皮胸甲/编码玩家头原样保留为上下文0栋。它不是居民/女巫/人物艺术参考，不下载头纹理、不刷怪、不建模型。',
'原beach直tag、legacy/rigid/emptyprocessor、start-2/WORLD_SURFACE_WG/size3/max114都只在固定源范围内成立，不改称湿地落地验收。luckPotion保留NBT、set_damage200..249只保留源字面，无实际领取/付款/耐久或任务材料来源证据。',
'已重新对照cod3物理1127：黑婆是“大沼泽吊脚楼”，白天熬药、夜点灯、雨收蛊。当前仅同层抬升居作平台、后间储桶与工台邻接、带檐木屋可作为辅助空间观察；没有药锅/床/黑婆/收蛊空间功能，也有海滩根、zombie机关、低石基。相关性不足可判0，仅保留至多1whole待Main最终，不把NPC06名字当资格；226旧一次信用不重计。']
responses_limits=[
'保持239至多1辅助空间候选、formal0，等待Main最终。此次回应不是NPC06建筑、工作流或任务的完成收据。',
'把西阶被x3/4,y2木板覆盖与东单入口48条原格实际核查保存；原双入口文句只作历史，当前明确撤回。未更改源文件或认可资产。',
'六类色PNG为全方格近似，不证明薄件、光照、碰撞、纹理或地形。238RLE行/74palette/6BE只是审查单位，均不转换建筑信用。',
'固定本地DungeonsArise 2.1.58/1.20.x/DV3120原源，未宣当前实例加载成功/兼容性或远程作者身份已验。',
'根直#is_beach之外的标签内部、结构集、overlay、legacy执行与实际水位/地形仍未展开，不推沼泽适配或生存安全。',
'炉头障碍已承认，桶面、灯、栏、屋顶火、实际路径/工作周期均未运行。局部air不当整流程可用。',
'刷怪组件和编码头只上下文阅读0栋，不当居民/姿态/艺术参考；此批没有Java/作者代码运行，也没有创建生物。',
'候选loot及空Items/零计时不是存货或玩家付款回执，未改原ID、奖励或任务进度，也未新增功能。',
'205/206原完整7维9限通过Main保存对象保留，不再声称重读旧原源和PNG。226首次239后续仍0，COD4153缺847与各NPC累计未知不变。',
'未生产、改共享Jar/专业资产/存档/实例/cap，也未开游戏/进程检查/网络/屏幕声亮/焦点/Git/自动化/主提示词/pending/ownership；没有删除任务或申报工时/全部完成。']
assert len(responses_findings)==len(m['Main_findings'])==11 and len(responses_limits)==len(m['Main_limits'])==10
corrected={**o['seven_dimensions']}
corrected['layout']='一座原渔屋，宽南长厅floor2/use3与北窄桦木后间同层服务组织。东侧短阶提供单一静态登台依据；西长木台下的阶状几何被木板覆盖，未证成人入口。北宽口西叠桶东craft，南墙炉/烟柱与窗花槽。无床/药锅/内梯或独立经营上层。'
corrected['proportion']=corrected['proportion'].replace('21宽含两侧入口外展','21宽含东入口阶与西木台外展')
corrected['circulation']='东两条z10/11底west阶19,0→18,1→17,2各+1/+2air，接16/15,y2spruce木台及y3/4air。西4,0及3,1虽为底阶，其上4,2和3,2均oakplanks，特别3,1紧上实木，不能作第二成人入口；只保留台下装饰/支承或未证入口。台上横向组织与北后间宽口/桶工台接近格保留，炉前10,4,12TOP石阶及10,5,12cobble头高限制保留。所有薄件碰撞/NPC/真实操作仍未验。'
corrected['ground_support']=corrected['ground_support'].replace('两侧阶坪','东入口阶及西长木台/台下阶状几何')
put('239-actual-author-ACK.json',{'batch':242,'status':'ACTUAL_239_AUTHOR_11_FINDINGS_10_LIMITS_RESPONDED_PENDING_MAIN_FINAL','Main_preACK_binding':bind(main),'complete_Main_preACK_original':m,'Main_raw_binding_only_not_full_reread':bind(raw),'original239_manual_binding':bind(orig),'complete_original239_seven_dimensions':o['seven_dimensions'],'complete_original239_eight_limits':o['limits'],'finding_responses':[{'index':i+1,'Main_finding':f,'actual_author_response':a}for i,(f,a)in enumerate(zip(m['Main_findings'],responses_findings))],'limit_responses':[{'index':i+1,'Main_limit':f,'actual_author_response':a}for i,(f,a)in enumerate(zip(m['Main_limits'],responses_limits))],'corrected_effective_seven_dimensions':corrected,'supersession':'239 original manual and saved judgments plus240/241 copied comparisons remain immutable historical objects. Any double-entry wording in them is withdrawn as effective analysis by this242 ACK. Future comparisons use corrected single-east-entry findings. No retroactive mutation or credit.','maximum_new_whole_candidate':1,'formal_credit_added':0,'production':False,'native_acceptance':False,'old_PNG_NBT_reread':False,'bounded_saved_decoded_entry_cells_actual_reread':48})
prev=R/'docs/architecture/research-20261104-smithy-241';old=get(prev/'session.json')
common={**{k:v for k,v in old.items()if k not in ['previous240_binding','batch','status','next']},'batch':242,'status':'239_ACTUAL_AUTHOR_ACK_CORRECTED_SINGLE_EAST_ENTRY_PENDING_MAIN_FINAL','new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'new_whole_formal_credit_added':0,'next':'Main final239 review after actual21 responses;241NPC13 auxiliary remains pending. Continue different complete related references. Use corrected single-east-entry239 only; original historical copies immutable.'}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous241_binding':bind(prev/n)})
cl=R/'docs/cod4/audit-20261022/coordinator-architecture226-firstcarry239-actual-closure-20261112.json';put('accepted226-closure-reuse-zero.json',{'binding':bind(cl),'original_closure':get(cl),'credit_added_this242':0})
protected=[]
for a in get(prev/'protected-inputs-current.json')['files']:
 b=a['current241'];cur=bind(b['path']);protected.append({'last241_checkpoint':b,'current242':cur,'unchanged':b==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False})
a=get(P/'239-actual-author-ACK.json');checks={'Main_preACK_exact':a['complete_Main_preACK_original']==get(main),'Main11_findings_and10limits_responded':len(a['finding_responses'])==11 and len(a['limit_responses'])==10,'all_Main_quotes_exact':all(a['finding_responses'][i]['Main_finding']==m['Main_findings'][i]for i in range(11))and all(a['limit_responses'][i]['Main_limit']==m['Main_limits'][i]for i in range(10)),'original7dim8limits_exact':a['complete_original239_seven_dimensions']==get(orig)['seven_dimensions']and a['complete_original239_eight_limits']==get(orig)['limits'],'48_bounded_original_cells':len(get(P/'239-actual-bounded-entry-cells.json')['cells'])==48,'formal_credit0':a['formal_credit_added']==0,'all8protected_unchanged':len(protected)==8 and all(x['unchanged']for x in protected),'226_carry0':get(P/'accepted226-closure-reuse-zero.json')['credit_added_this242']==0}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'native_acceptance':False})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':242,'status':common['status'],'files':files,'formal_credit_added':0,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
