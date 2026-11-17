"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-031'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))

















def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('pmmo-player-vein-charge-capability-restoration-and-authoritative-mining-consumption-boundaries',
 pick('/features/veinmining/capability/VeinProvider.java','deserializeNBT')+whole('/features/veinmining/capability/VeinProvider.java')+whole('/features/veinmining/capability/VeinHandler.java')+
 pick('/setup/CommonSetup.java','onCapabilityRegister onPlayerCapabilityAttach')+
 whole('/features/veinmining/VeinMiningLogic.java')+whole('/features/veinmining/VeinShapeData.java')+
 whole('/events/impl/PlayerTickHandler.java')+whole('/events/impl/BreakHandler.java')+
 pick('/events/EventHandler.java','onPlayerTick onBlockBreak')+
 pick('/core/Core.java','setMarkedPos getMarkedPos getBlockConsume get isActionPermitted doesPlayerMeetReq')+
 whole('/network/serverpackets/SP_UpdateVeinTarget.java')+whole('/network/serverpackets/SP_SetVeinLimit.java')+whole('/network/serverpackets/SP_SetVeinShape.java')+
 whole('/network/clientpackets/CP_SyncVein.java')+whole('/client/utils/VeinTracker.java')+
 whole('/config/codecs/VeinData.java')+pick('/compat/curios/CurioCompat.java','getItems')+
 whole('/events/impl/LoginHandler.java')+pick('/network/Networking.java','registerMessages sendToClient sendToServer'),
 '真实Player capability以DoubleTag保存Vein charge；读回后服务端tick恢复、实际BreakEvent匹配选区起点时按挖掘工作列表扣费，登录/扣费/恢复同步客户端。完整资源生命周期一条；不宣称charge等于Clone永久资格。',
 'VeinProvider backend VeinHandler.charge默认0；真实cap ID为pmmo:veind_data，serialize DoubleTag.valueOf(getCharge)，deserialize nbt.getAsDouble→setCharge直接赋值。VeinMiningLogic中的vein_data/vein_charge常量没有用于这条NBT读写，不能虚构它们是旧别名。',
 'CommonSetup为每Player附新provider并注册VeinHandler；getCapability只按VEIN_CAP返回。没有本仓库PlayerEvent.Clone复制入口，不把新provider默认0误写为已验证死亡清零。没有version、旧键fallback、有限值/非负/当前装备cap校验或明确invalidatelistener；原生Forge存取生命周期未运行验证。UUID→maxBlocks/shape与Core markers、client VeinTracker均运行态map/字段，不在DoubleTag载荷。资源值是真实持久对象，但当前补充研究不是批准将它加入永久白名单。',
 'PlayerTickHandler实际守卫为phase!=END && tickCount%10!=0才return，所以每个END及10倍数START均可执行regenerateVein，不能描述为每10tick一次。恢复从装备/Curios中通过WEAR条件取得cap/rate，但仅rate present的item同时贡献cap，getMaxChargeFromAllItems却只要求cap可用；两处cap推导有区别。getCurrentCharge把double转int，恢复比较/登录包用截断值，未达cap分支先setCharge(raw+rate)，随后同步getCharge()+rate，静态上客户端显示多一份rate；超cap直接return不归一。每种装备/Curios槽位不另计。',
 'Dynasty可借鉴显式列出永久资格与可再生资源/选择器各自的持久边界，Clone只复制审定永久字段，绝不整体copy capability/ForgeData以带入免疫姿态计时器。旧ID映射应写清唯一受支持别名及版本，不能把未使用字符串推定为兼容键。迁移先读取并保留Count/tag/未知payload，再验证目标成功后提交；工作队列尝试数不等于成功回执，应以实际写入/伤害结果确认后一次消费。源值double与消费者int、同步值与真值不一致时先定义不变式，不能靠客户端显示认定持久化成功。',
 '实际BreakHandler仅当marker等于事件pos且手持不在VEIN_BLACKLIST时启动；applyVein按int charge/cost和客户端给定上限构造形状，各位置在调用原生gameMode.destroyAndAck之前累加cost，循环后以原先int charge-cost覆盖原double，因此扣费依据尝试而非破坏成功，且使用会舍弃小数；未运行证明丢资源。shape列表去掉起点，原生游戏模式仍负责各块最终权限/结果，本批不声称能绕过。服务端target/limit/shape包用ctx.sender UUID，target无独立维度/range字段、limit未显式非负校验，实际起点仍需BreakEvent命中；客户端预览不是权威状态。原生Clone/NBT类型读取、GameMode结果、客户端HUD、Curios本体未审查/未启动，不保证错误DoubleTag全部兜底。',
 '与029世界UUID XP真值/030区块放置者归属是不同真实资源对象；共有Core/BreakHandler/Networking为支持，重复摘录credit0。与既有能量缓冲、饥饿/冷却研究有广义相似，主责可因任务适用性合并或排除；只提交一条，charge getter/setter、三个形状、每条packet、client显示、装备字段、cap ID拼写都不拆候选。无旧别名/Clone已验证兼容信用，credit0待Kepler裁定。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix,needles in [('/features/veinmining/capability/VeinProvider.java',None),('/features/veinmining/capability/VeinHandler.java',None),('/features/veinmining/VeinMiningLogic.java',None),('/client/utils/VeinTracker.java',None),('/core/Core.java',['markers']),('/config/codecs/VeinData.java',None)]:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
def generate():
    rows=[]
    for spec in SPECS:
        evidence=[]
        for selector in spec['selectors']:
            suffix,name=selector[:2]
            matches=[r for r in INDEX if r['path'].endswith(suffix) and r['name']==name and (len(selector)<3 or r['start']==selector[2])]
            if not matches:
                raise ValueError(('No complete source method for evidence',selector))
            for r in matches:
                evidence.append(dict(r,revision=r['commit'],private_file=r['source'],start_line=r['start'],end_line=r['end'],method=r['name'],file_sha256=r['sourceSha256'],method_sha256=r['excerptSha256'],structural_fingerprint=r['normalizedSha256'],context=r['text'],source_url_or_coordinate='https://github.com/'+r['repo']+'/blob/'+r['commit']+'/'+r['path']+'#L'+str(r['start'])+'-L'+str(r['end'])))
        evidence=list({e['candidate_id']:e for e in evidence}.values())
        primary=evidence[0]
        row={k:v for k,v in spec.items() if k!='selectors'}
        row.update(primary)
        row.update(status='helper_reviewed_pending_coordinator',credit=0,accepted=False,evidence=evidence,preservation=spec['observation'],application_limit=spec['limits'],url=primary['source_url_or_coordinate'],excerpt=primary['text'],source_local=primary['source'],source_sha256=primary['sourceSha256'],line=primary['start'],end_line=primary['end'],runtime_validation='not_run_static_research_scope')
        attach_declarations(row)
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-031.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
