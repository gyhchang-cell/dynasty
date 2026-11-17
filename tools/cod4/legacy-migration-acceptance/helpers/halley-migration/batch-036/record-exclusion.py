# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parent;r=Path('/Users/a15356015027/Desktop/dynasty');d=r/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-036'
sys.path.insert(0,str(b.parent))
from extract import PARSER,walk,norm,sha
idx=json.loads((b/'method-index.json').read_text())
e=[]
for x in idx:
 if x['path'].endswith('/entities/EntityMoverMinecart.java') or (x['path'].endswith('/blocks/BlockDimensionRail.java') and x['name'] in ['BlockDimensionRail','canUseHere','onMinecartPass','placeEntity','getGoalCoords']) or x['path'].endswith('/items/ItemMoverMinecart.java'):
  raw=(r/x['source']).read_bytes();assert sha(raw)==x['sourceSha256']
  nodes=[n for n in walk(PARSER.parse(raw).root_node) if n.type in ['method_declaration','constructor_declaration'] and n.start_point.row+1==x['start'] and n.end_point.row+1==x['end']]
  assert len(nodes)==1 and not nodes[0].has_error
  n=nodes[0];assert raw[n.start_byte:n.end_byte].decode()==x['text'] and sha(x['text'].encode())==x['excerptSha256'] and norm(n,raw)==x['normalizedSha256']
  e.append(dict(x,url='https://github.com/'+x['repo']+'/blob/'+x['commit']+'/'+x['path']+'#L'+str(x['start'])+'-L'+str(x['end'])))
p=next(x for x in e if x['name']=='deserializeNBT')
row=dict(p,family='naturesaura-aura-mover-minecart-native-persistence-wiring-unproven',status='reviewed_exclusion_pending_native_callback_proof',credit=0,accepted=False,observation='固定官方源码表明矿车记录active/last_pos/offsets并搬运灵气，而非收纳实体。serializeNBT/deserializeNBT覆写存在，但本仓库未见将扩展字段接入addAdditionalSaveData/readAdditionalSaveData或自定义常规实体存储的调用；常规chunk实体保存与restoreFrom是否调用这些覆写须固定对应原生版本再读，当前不能声称真实重载保持offsets。',application='研究中严格核对实际序列化触发，不以有read/write方法推定生命周期接线。若参考实体跨维度状态，必须核对真正native save/load/restoreFrom边界，永久Clone只拷审定资格，不整体ForgeData。',limits='未下载/运行对应原生版本，不声称确定不保存，仅未证实。不把三种维度rail/七个getters或class下载计数。moveAura先drain再store且故意丢ceil(drained/250)是运输成本，非玩家死亡惩罚；destroy新空cart ItemStack不带扩展NBT。源码完整读完但不升级已研究有效参考。',semantic_duplicate_risk='033 aura资源消费者同链风险高；仅自定义serializable wrapper与changeDimension→native restoreFrom不是新完整实现信用。候选完整证据留Kepler，可排除或在展开native后再审核。',evidence=e,text=p['text'],sourceSha256=p['sourceSha256'],excerptSha256=p['excerptSha256'],normalizedSha256=p['normalizedSha256'])
(d/'excluded-candidates.json').write_text(json.dumps({'credit':0,'accepted_reference_suggestions':0,'excluded_or_pending_chains':1,'records':[row]},ensure_ascii=False,indent=2)+'\n')
(d/'batch-036.json').write_text(json.dumps({'credit':0,'reviewed_chains':0,'records':[],'excluded_records':[row],'reason':'Native persistence/copy trigger unproven. Do not merge as accepted; static review of exclusion only.'},ensure_ascii=False,indent=2)+'\n')
(d/'reviewed-suggestions.jsonl').write_text('')
(d/'exclusion-document-integrity.json').write_text(json.dumps({'credit':0,'accepted_reference_suggestions':0,'complete_methods_support_not_credit':len(e),'selected_ast_hash_errors':0,'selected_files':len(set(x['source'] for x in e)),'reason':'Hash verification is document integrity only, not native wiring proof; full source Git tree/blob audit separate.'},ensure_ascii=False,indent=2)+'\n')
print('Excluded/pending1 chain; accepted suggestions0; static source methods',len(e),'not credit')
