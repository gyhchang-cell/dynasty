"""Publish reviewed evidence without treating geometry or pixel counts as visual passes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/weapon-visual-acceptance'
rows=(R/'docs/cod4/audit-20261022/cod4-remaining.txt').read_text().splitlines()
def row(key):
 found=next((x for x in rows if x.startswith('| '+key+' |')),None)
 if found:return found
 previous=json.loads((D/'acceptance.json').read_text());return next(x['exact_original'] for x in previous['decisions'] if x['key']==key)
def proof(run,case,png,review):
 fs=json.loads((D/run/(case+'-frames.json')).read_text());i,f=next((i,f) for i,f in enumerate(fs) if f.get('screenshot')==png)
 return dict(run=run,case=case,png=png,png_sha256=hashlib.sha256((D/run/png).read_bytes()).hexdigest(),frame_index=i,frameSerial=f['frameSerial'],tick=f['tick'],partialTick=f['partialTick'],age=f['age'],camera=f['cameraType'],screen=f['screen'],geometry={k:len(v) for k,v in f['geometry'].items()},pixel_delta=f.get('nativePixelDelta',{}),events=case+'-events.json',review=review)
evidence=[
 proof('run-05','yu_di-guard-glass-third-10fps','yu_di-guard-glass-third-10fps-f5320-t5391.png','两圈处于不同扩散年龄，浅绿外环及亮绿内环均肉眼可辨；人物和玻璃局部遮挡合理，不声称所有方向可见。'),
 proof('run-05','tang-swim-flags','tang-swim-flags-f6605-t6446.png','实际swimming=true的第三人称，青色两条尾迹位于人物后方，与水下背景可区分。'),
 proof('run-04','tang-first-turn','tang-first-turn-f6366-t7648.png','原残影、心粒子与通用VFX可见，专用TangWind实际像素为0；不得用通用绿光当该专用尾迹通过。'),
 proof('run-05','huan_shou_dao-clear-wall-sand','huan_shou_dao-clear-wall-sand-f69-t89.png','实体确有离地，沙色小块可辨；牛身/玩家遮住大部分弧光，不能仅据1367像素认定弧光完整清晰。'),
 proof('run-05','juque_sword-first-mobile','juque_sword-first-mobile-f388-t525.png','原残影和原版白扫击占主画面，专项弧光不易分辨。'),
 proof('run-05','seven_star_saber-guard-first','seven_star_saber-guard-first-f4514-t4721.png','左侧星芒可辨，但大量原版伤害心粒子遮住受击者；不足以通过七次依序完整观感。'),
 proof('run-05','dragon-part-flight','dragon-part-flight-f6073-t6138.png','真实末影龙头部事件/partSlot=1存在，但C2S记录中心距离6.377707且龙头离开合适画幅；渲染像素区域被左上小地图覆盖，不能当飞行部位可辨识验收。'),
 proof('run-04','qinggang_sword-side-night-10fps','qinggang_sword-side-night-10fps-f1337-t1410.png','协调独立抽查：淡青短痕存在，原版心粒子/白月牙遮挡辨识，保留质量问题。'),
 proof('run-04','xuantian_axe-third-glass','xuantian_axe-third-glass-f5858-t7137.png','协调独立抽查：头侧后裂纹可见，被玩家躯干和心粒子局部遮挡；不将nonzero表述为完整优质或全方向可见。'),
 proof('run-04','tianlang_bow-visible-third-10fps','tianlang_bow-visible-third-10fps-f10508-t10825.png','协调独立抽查：白蓝流星尾迹明显可辨。仅用于原生发射后尾迹；不能证明持续持弓观感。服务端该刻held=tianlang_bow；持握外观辨识有歧义，视觉观察不覆盖源记录。此图只验流星箭尾迹，不验持弓外观。'),
]
flute=row('yu_di')
decisions=[dict(key='yu_di',decision='可整条关闭',exact_original=flute,why='真实主/副手useItem触发3目标原减益，原生equipment_flute_debuff_applied，0/3/6刻三脉冲及完整消退帧；第一/第三人称、人体遮挡和修正玻璃平面已实际检查。仅验收现有音波，不包含新资产。',cases=['run-03/s04-flute-third','run-04/yu_di-side-day','run-04/yu_di-side-night-10fps','run-05/yu_di-guard-first','run-05/yu_di-guard-glass-third-10fps','run-05/flute-offhand-first'])]
for key,reason in [
 ('mu_mao / shi_ge / tong_dao / tie_jian','四材质原生命中和原残影均提交且有像素；短小材质碎片被目标、心粒子及白扫击遮挡，低帧率完整辨识仍不足。'),
 ('tang_dao','第三人称转向/移动/实际游泳已可辨；原生effect clear后专用几何停止已验。第一人称专项TangWind整个场景像素为0，不能以通用Vfx1代替。'),
 ('huan_shou_dao / juque_sword','真实抬升、落地、石/沙支撑和顶棚负例通过；沙尘可辨，但当前角度弧光经常被目标/人物/白扫击淹没，保留视觉辨识。'),
 ('qinggang_sword / gilded_mace / yitian_sword','三种节奏原生回执和渲染存在，明/暗、玻璃及10FPS已执行；短痕辨识受原版粒子干扰，不能宣称三种完整节奏肉眼清楚。'),
 ('seven_star_saber','完整提交序列和无伤害负例已有；部分星芒确实可见，七次完整观感仍被伤害粒子/人物遮挡。'),
 ('dragon_slayer','龙王/龙帝原生decal与重载后新触发存在；末影龙画幅/普通可达距离不足，重载中存活decal未证。不能整条关闭。'),
 ('pojun_axe / xuantian_axe','两把真实破甲(toughness .25→.125)与甲裂碎片可见；合理局部遮挡可过，受击者整体贴合/完整观感尚不能据高像素量通过。'),
 ('halberd_fangtian','真实横扫伤害成功，专用月牙从未发出：原生回执tick4991→END4992被r.tick!=now拒绝。详见issue-fangtian-native-receipt.json。'),
 ('长柄组（dragon_spear 等）','七把真实抬升和落地、石/沙地面、顶棚/墙面边界已记录；木矛等弧光短且常被身体/残影遮挡，未对七把都得出完整可辨识结论。混元杖未伪造近战。'),
 ('弓系','八把第一/第三人称原生24刻蓄力放箭及真实箭矢追踪/碰撞已执行。天狼白蓝尾迹明确可辨，其他尾迹有贡献；尚缺八把在玻璃/夜间/地面遮挡的完整观感矩阵。持弓外观不由发射后截图证明。原16/20刻HUD验收不重复、继续保留既有通过。')]:
 decisions.append(dict(key=key,decision='保留并可收窄',exact_original=row(key),remaining=reason))
counts={r:len(list((D/r).glob('*-result.json'))) for r in ['run-03','run-04','run-05']}
report=dict(jar_sha256='0e1fbac34942714cd90a18ec1b404303b5d4d5bf96ce7c96277e16e561fe5c27',cases=counts,total=sum(counts.values()),closed_exact_rows=[flute],decisions=decisions,reviewed_evidence=evidence,boundaries=[
 '所有150场景以独立整包86jar/96mod实例运行；run03/04/05均正常退出0。未写资产、正式Java、原清单或用户实例。',
 '原生MultiPlayerGameMode.attack/useItem/releaseUsingItem→实际服务器事件→正式反馈包→实际渲染→同frameSerial的PNG；没有直接假发反馈包。',
 '截图是RenderTick.END实际framebuffer；像素差是专项renderer调用前后读回，最终HUD可能再遮住效果，因此最终PNG肉眼判断独立保留。计数不是质量标准。',
 'run03及run04旧wall/glass平面与目标bbox相交，不能当干净遮挡正例；run05移至x=-2补测。旧ceiling有0.6空隙不能当零抬升，run05 top-slab紧顶棚补负例。',
 'run05/tang-clear-flags仍有上一场景向外扩散的水；其去除速度判定有效，不能称干燥地面去除场景。',
 '10FPS是请求上限，实际frameIntervalMs逐帧记录；像素读回增加开销，不用于未插桩性能认证。',
 '原生伤害导致大量原版心形粒子保留，没有为通过而禁粒子、隐藏身体、改VFX、修改资产。',
 '双客户端32边界由Herschel负责；本报告不冒充真人双人网络验收。未覆盖的新机制/资产条目不关闭。'])
(D/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
lines=['COD4 已有武器视觉实际客户端验收（阶段收尾）','Jar: '+report['jar_sha256'],'实测场景: '+str(counts)+'，总计 '+str(sum(counts.values())), '\n可整条关闭的精确原文：',flute,'\n关闭依据：'+decisions[0]['why'],'关联场景：'+', '.join(decisions[0]['cases']),'\n保留/收窄：']
lines += [d['exact_original']+'\n  '+d['remaining'] for d in decisions[1:]]
lines += ['\n关键原生PNG与同帧数据（全部路径相对本目录）：']
lines += [f"{e['run']}/{e['png']}\n  frameSerial={e['frameSerial']} tick={e['tick']} partial={e['partialTick']}，{e['review']}" for e in evidence]
lines += ['\n覆盖边界：']+report['boundaries']+['\n机器索引：各run/case-index.json；全部geometry/像素/同帧screen在*-frames.json；原生输入、伤害、箭矢、S2C在*-events.json。gallery.html只供定位，自动选图不代表通过。']
(D/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print(counts, 'total',sum(counts.values()), 'closeable',len(report['closed_exact_rows']))
