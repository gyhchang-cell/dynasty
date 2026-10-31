from pathlib import Path
import json,hashlib,datetime
r=Path('/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration');d=r/'batch-031'
a=json.loads((d/'document-integrity.json').read_text())
(d/'HANDOFF.md').write_text('''# Halley → Kepler：第031批，credit0

PMMO官方固定 f83904c929457f5d36c384faa3125ee87b2900fd，复用029已验证来源。1条真实Vein charge capability持久资源→恢复→实际采掘消费→同步家族。71完整方法+19字段、18文件仅为90支持节点，不是90参考；所有建议credit0/accepted=false待主责核查。

pmmo:veind_data才是实际cap ID；未使用的vein_data/vein_charge不能当旧别名。DoubleTag读写没有明确版本/有限值/非负校验，仓库没有Player Clone复制入口。UUID选择器、shape/limit、marker与客户端预览不写这个DoubleTag，不能整体复制为永久资格。

实际tick守卫的AND意味着每个END加部分START都会恢复；当前charge消费者转int，消费可舍弃小数；恢复分支更新后再把额外一份rate同步给client。采掘按尝试位置先累计费用，再调用原生destroyAndAck，无成功回执。全部只是完整源码可见的静态边界，不声称运行复现或绕过原生破坏权限。

来源Git commit/tree/blob、source/excerpt/normalized哈希、AST完整范围检查错误0。主账机械primary匹配0不是语义去重结论。与029/030共享Core、BreakHandler、网络方法支持credit0；三个形状、槽位、getter、包不拆计。与其他持久能量资源广义相近，主责可按适用性合并或排除；不把这条可再生资源直接列入Clone永久白名单。

研究继续，不因已交批次停止；十小时尚未完成。没有游戏、编译、测试、上游执行、GUI/屏幕、主账/生产/待办/原存档写入。
''')
(d/'semantic-duplicate-review.json').write_text(json.dumps({'credit':0,'accepted':False,'reviewed_family_count':1,'support_nodes_not_credit':90,'master_primary_matches':a['master_primary_matches'],'manual_comparison':['029 UUID XP真值与030区块放置归属支持复用，不增加信用','charge所有读写/恢复/消费/包/三个shape合为一条','既有能量缓冲/资源存储存在广义相似，Kepler按实际迁移价值最终判定','没有Player Clone或旧ID fallback证据，不能将未使用常量当旧别名'],'not_counted':['189 reused files','71 methods','19 fields','per-item slots','packet variants','getter/setter','temporary selection maps']},ensure_ascii=False,indent=2)+'\n')
p=r/'CONTINUATION-20261028.json';x=json.loads(p.read_text());x['at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
if 'batch-030' not in x['delivered_to_Kepler']:x['delivered_to_Kepler'].append('batch-030')
x['manual_suggestions_not_accepted_credit']['batch-031']=1
for f in d.iterdir():
 if f.is_file():x['files']['batch-031/'+f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
x['current']='031 complete one resource family credit0; sending Kepler then selecting032 official source. Ten-hour incomplete.'
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
