"""Seal one private whole-source spatial study; never edits product or master tasks."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
a=json.loads((OUT/'raw-source-audit.json').read_text())['candidates'][0];n=a['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
assert len(cells)==len(n['blocks'])==1047
rle=[]
for y in range(10):
 for z in range(15):
  runs=[]
  for x in range(14):
   state=cells.get((x,y,z),{}).get('state',-1)
   if runs and runs[-1][0]==state:runs[-1][1]+=1
   else:runs.append([state,1])
  rle.append({'y':y,'z':z,'runs':runs})
put('F02-full-layer-rle.json',{'size':n['size'],'omitted':-1,'rows':rle,'generated_reproducibility_not_extra_reference_credit':True})
oldctx=ROOT/'docs/architecture/research-20261104-smithy-270/source-context.json';oc=json.loads(oldctx.read_text());ctx=json.loads((OUT/'source-context.json').read_text())
assert [(x['member'],x['sha256'],x['original_text'])for x in oc['metadata']]==[(x['member'],x['sha256'],x['original_text'])for x in ctx['metadata']]
put('metadata-exact-reuse.json',{'old_binding':bind(oldctx),'current_binding':bind(OUT/'source-context.json'),'all_three_original_metadata_exact_equal':True,'new_semantic_credit':0,'not_claiming_new_metadata_reread':True})
seven={
 'layout':'完整雪地木构复合屋：西低入口前厅接中东挑高书架/讲台阅读厅；北侧另西门通z2/3长窄低位单床/箱小间；厅内东向三阶接东侧局部上卧铺/炉/箱。南侧书架后两secret箱仍同屋附属，不拆参考；低位床y0、公共使用y1、上床y4三种使用标高，不称三完整经营楼层或两住宅。此处只提NPC13雪山木屋居住/遮蔽、分层夜宿组织辅助整栋最多1，原图书馆不是猎人完成品。',
 'proportion':'14×10×15/DV3953，2100声明位置1047存=880nonair167air，1053省略unknown。66palette/14BE/entities[]；8图覆盖10层0..9全看，624矩阵位置及另106记录实际读，二者有重叠不称730独立格。低床下y-1越界，不能证完整地下室基底；y9顶火/帽不当十楼，4床块为两完整床对。',
 'facade':'116spruce板、99去皮spruce log、64spruce log及少量轴向wood构框墙，40bookshelf分隔公共厅/窄道，3glasspane与5灯照明意图。西主门1,1/2,7west/right/closed；北侧室门4,1/2,3east/right/closed，不是双扇同门。原吊牌0,2,4 rotation5/attachedtrue仅正面Local Library/背面空，无中文。薄牌与链/灯不当实体住民。',
 'roof':'主屋东西长高双坡与西低横向门厅盖相接，195spruce阶及18spruce slab为主要木坡；西低檐19stonebrick阶/4stonebrick slab另材质明确，不能按类色灰把全盖当石瓦。80snowblock和87snow薄层1..4分布地边/屋盖层，是真雪不是白毛；高脊顶下梁和斜阶不自动成阁楼。东10,y5..8,5石砖烟柱上10,9,5lit火/活板帽仅原状态，不证通烟、防雨或火安全。',
 'materials':'低east蓝床foot10,0,3/head11,0,3，上north蓝床head11,4,6/foot11,4,7。低箱10,0,2west/上箱11,4,8west原library表；后箱7,1,12north与11,1,11west原library_secret表，均无seed或现存Items，不是保证奖品。lectern11,1,7west/has_booktrue，原Book={count:1,id:minecraft:writable_book}/Page=-1无pages内容，保留小写count不擅修成Count。上炉10,4,5south/unlit空Items三计时0/RecipesUsed{}；顶火littrue但Items[]/两组四零计时，不称夜烤火行为已验。',
 'circulation':'主入口0,1,7接口finalair，上2/3air，下path；1,1/2,7闭门，内2/3,y1/2,7air。侧入口0,1,3finalvoid，上2/3及x1/2,y1/2,3均unknown，x3,y1/2,3air→4,1/2,3闭门→5,0,3west底阶/6,0,3底半砖→低床区，但模板下方承托与步降碰撞未验。厅内7,1,8east底阶→8,2,8east底阶→9,3,8east底阶，每阶上两格显式air；10,3,8west TOP阶为反向支撑，不能写第四底阶。上落脚10,4/5,8air，经10,4/5,7air/下3为TOP slab靠床侧，未证明完整NPC通行。6,1,3open TOP竖活板、6,2,4横木低梁保留，不能称低室与大厅处处直接相通。',
 'terrain_and_dedup':'完整保存整屋，无必需续屋socket，两入口pool均empty；低床/箱底越界及省略地形不补air/地基。houses24项本栋weight4/single/rigid，特用remove_bookshelves_20_percent：原规则bookshelf概率.2→stripped_oak_wood axisX，不是清air/所有书架已删20%。root村snowy size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue、towncenter3自有+3vanilla僵尸池仅上下文，center/道路/vanilla biome体未读拼。先读256与270各7维10限制：256同主脊下床炉/局部上床箱单入口内转阶，270下织机/南院/短梯上床；当前两独立西向入口分主厅与低床、挑高阅读厅内东直三阶上局部炉床+后藏箱整体不同，不凭书架/多床/换材给新义；Main仍可因非猎人用途或同Trek雪屋近族HOLD0。',
}
limits=[
 '原木构图书馆的封闭夜宿/避雨及公共厅-私床空间与雪屋辅助研究有关系，但不是巴图捕猎/酒/黑獒/夜烤火/生成任务闭环；空间辅助相关性、尺度与近族全部待Main，可判HOLD0。正式0，不把图书馆改名猎户屋。',
 '66palette完整Properties、14BE及entities[]完整读；8PNG含全方向/两cut/两vertical及5双层平面覆盖0..9全看。624矩阵位+106附加记录有重叠不合计独立信用；150RLE行仅生成/复核，不宣2100格全人工语义逐格阅读。',
 '1053unknown与167air分开。低床y0下方模板外未保存，未证真实地下室/山坡地基；两个接口finalvoid/air分别保留，不能都当道路气隙。闭门、顶反向阶、底/顶半砖、竖活板、低梁和床箱/后secret箱操作均未原生验。',
 'source DataVersion3953显著新于同Jar其他雪屋3337，讲台书小写count/Page-1、secret附魔options标签等原状态不改。固定Jar名字/packmetadata不保证当前Minecraft兼容，不启动Java转换或试跑，也不把原source直接接生产。',
 '四上下文JSON与根/towncenter两JSON实际全文读；三个metadata与270精确全文复用绑定0新阅读。两个loot普通池3..8rolls各10候选，secret另20..39附魔书/treasuretrue/options#on_random_loot只是规则不是已领物。random_sequence原拼vilage保留，不擅改。',
 '当前processor20%将bookshelf换去皮橡木，不称移除成air，40源书架不是处理后保证数量。原版随机loot标签/biome体及其他运行处理器、center/路/terminators未读，不称自然生成、全NPC路线或配方付款验收。',
 '256/270原7维和限制已先全文读保存，旧源图未开；其待审状态不当已通过。两床、两门、后两箱、楼梯/屋脊/截图不拆独立建筑，机器排重非语义独特证明。',
 'F01snowy_cartographer仅材料/全BE/entities有界预筛0，未全读palette/逐层/图/context，不能计完整研究。275只完整F02最多1提议，正式0，NPC累计null。COD4旧153/847不变，1000未达不制作不删任务。',
 '仅本地Python -B证据，图为类色整格近似而非原材质/薄件碰撞。无Java/game/network/UI/进程/音亮唤醒焦点/原实例原存档/生产资产/共享Jar/主清单/Git/自动化，不声称全部完成或工时。',
]
images=[bind(p)for p in sorted(OUT.glob('*.png'))];assert len(images)==8
put('manual-review.json',{'batch':275,'case':'F02','source':{k:v for k,v in a.items()if k not in ['nbt_decoded_original','material_counts']},'seven_dimensions':seven,'limits':limits,'status':'COMPLETE_WHOLE_TIMBER_LIBRARY_RESIDENTIAL_SPATIAL_STUDY_PENDING_MAIN','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'formal_credit_added':0,'native_acceptance':False,'actual_reading':{'palette':66,'BE':14,'entities':0,'PNG_actual':images,'classified_layers':10,'matrix_records':624,'additional_key_records':106,'key_sets_overlap':True,'RLE_rows_generated':150,'all_original_cells_manually_read':False}})
with ZipFile(a['source_archive'])as z:
 bb=z.read(a['member']);fresh=read(bb);assert fresh==n and hashlib.sha256(bb).hexdigest()==a['nbt_sha256']
 contexts=ctx['candidates'][0]['contexts']+json.loads((OUT/'root-context.json').read_text());assert len(contexts)==6
 for c in contexts:
  bb=z.read(c['member']);assert hashlib.sha256(bb).hexdigest()==c['sha256']and json.loads(bb)==c['json']
for rr in rle:assert [s for s,count in rr['runs']for _ in range(count)]==[cells.get((x,rr['y'],rr['z']),{}).get('state',-1)for x in range(14)]
km=json.loads((OUT/'key-source-route-matrices.json').read_text())
for r in km['rows']:assert r['original_indices']==[cells.get((x,r['y'],r['z']),{}).get('state',-1)for x in r['xs']]
kc=json.loads((OUT/'key-source-entry-upper-cells.json').read_text())['cells']
for r in kc:assert r['original_state']==cells.get(tuple(r['pos']),{}).get('state',-1)
previous=ROOT/'docs/architecture/research-20261104-smithy-274';s=json.loads((previous/'session.json').read_text());protected=[]
for r in json.loads((ROOT/'docs/architecture/research-20261104-smithy-273/protected-inputs-current.json').read_text())['files']:
 before=r['current273'];now=bind(before['path']);protected.append({'previous273':before,'current275':now,'unchanged':before==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':0,'cod5_missing_not_invented':True})
s.update({'batch':275,'status':'WHOLE_LIBRARY_RESIDENTIAL_SPATIAL_STUDY_PENDING_MAIN','new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'formal_credit_added':0,'first_carry_added':0,'previous274_receipt':bind(previous/'RECEIPT.json'),'next':'275F02 pending scope/family;275F01 bounded0. Continue next related distinct whole design;273 remains pending and274 correction0.'})
s['active_pending'].append('275F02_SNOWY_LIBRARY_RESIDENTIAL_NPC13_AUXILIARY_SPACE');put('session.json',s)
put('active-checkpoint.json',{'batch':275,'status':s['status'],'session':bind(OUT/'session.json'),'manual':bind(OUT/'manual-review.json'),'new_whole_studies':1,'proposal_maximum':1,'formal_credit_added':0,'COD4_accepted':153,'COD4_gap':847,'NPC_totals':None,'native_acceptance':False,'tasks_deleted':0,'all_tasks_complete':False})
checks={'source_fresh_equals_saved':fresh==n,'fixed_jar_sha':bind(a['source_archive'])['sha256']==a['source_archive_sha256'],'RLE150_verified':len(rle)==150,'key624_verified':sum(len(r['xs'])for r in km['rows'])==624,'additional106_verified':len(kc)==106,'contexts6_verified':len(contexts)==6,'metadata3_exact_reuse':len(ctx['metadata'])==3,'palette66':len(pal)==66,'BE14':sum('nbt'in b for b in n['blocks'])==14,'images8_read':len(images)==8,'prior2_whole7dimensions_limits10':all(len(d['own_seven_dimensions'])==7 and len(d['original_limits'])==10 for d in json.loads((OUT/'saved-prior-whole-comparison.json').read_text())),'protected8_unchanged':len(protected)==8 and all(r['unchanged']for r in protected),'no_native_or_task_completion':True}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'passed':True,'same_parser_reproduction_not_Main_independent_admission':True,'formal_credit_added':0})
put('RECEIPT.json',{'batch':275,'status':'SEALED_ONE_WHOLE_LIBRARY_STUDY_PENDING_MAIN','files':[bind(f)for f in sorted(OUT.iterdir())if f.is_file()and f.name!='RECEIPT.json'],'checks':checks,'new_whole_studies':1,'proposal_maximum':1,'formal_credit_added':0,'native_acceptance':False,'production_changes':0,'tasks_deleted':0,'all_tasks_complete':False})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'manual':bind(OUT/'manual-review.json')},ensure_ascii=False))
