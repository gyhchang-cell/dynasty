"""Render handwritten static research notes; never builds, tests or runs upstream code."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib, datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-013'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))





add('akashictome-morphtool-shared-family-nested-carrier-stack-restoration',[
 ('akashictome/MorphingHandler.java','makeMorphedStack'),('akashictome/MorphingHandler.java','getShiftStackForMod'),('akashictome/MorphingHandler.java','getModFromStack'),('akashictome/MorphingHandler.java','getModFromState'),('akashictome/MorphingHandler.java','getModOrAlias'),('akashictome/MorphingHandler.java','isAkashicTome'),('akashictome/MorphingHandler.java','onItemDropped'),('akashictome/MorphingHandler.java','onPlayerLeftClick'),
 ('akashictome/AttachementRecipe.java','matches'),('akashictome/AttachementRecipe.java','assemble'),('akashictome/AttachementRecipe.java','isTarget'),('akashictome/AttachementRecipe.java','getRemainingItems'),('akashictome/NBTUtils.java','getNBT'),('akashictome/NBTUtils.java','verifyExistence'),('akashictome/NBTUtils.java','getString'),('akashictome/NBTUtils.java','setString'),('akashictome/NBTUtils.java','getCompound'),('akashictome/TomeItem.java','useOn'),('akashictome/TomeItem.java','use'),('akashictome/client/TomeScreen.java','render'),('akashictome/client/TomeScreen.java','mouseClicked'),('akashictome/network/MessageMorphTome.java','handle'),('akashictome/network/MessageUnmorphTome.java','handle'),('akashictome/network/NetworkHandler.java','register'),('akashictome/AkashicTome.java','AkashicTome'),('akashictome/AkashicTome.java','commonSetup'),('akashictome/proxy/CommonProxy.java','preInit'),('akashictome/proxy/ClientProxy.java','openTomeGUI'),
 ('morphtool/MorphingHandler.java','makeMorphedStack'),('morphtool/MorphingHandler.java','getShiftStackForMod'),('morphtool/MorphingHandler.java','getModFromStack'),('morphtool/MorphingHandler.java','getModFromState'),('morphtool/MorphingHandler.java','getModOrAlias'),('morphtool/MorphingHandler.java','isMorphTool'),('morphtool/MorphingHandler.java','onItemDropped'),('morphtool/MorphingHandler.java','onItemBroken'),('morphtool/MorphingHandler.java','removeItemFromTool'),('morphtool/MorphingHandler.java','raycast'),('morphtool/AttachementRecipe.java','matches'),('morphtool/AttachementRecipe.java','assemble'),('morphtool/AttachementRecipe.java','isTarget'),('morphtool/AttachementRecipe.java','getRemainingItems'),('morphtool/ClientHandler.java','onTick'),('morphtool/ClientHandler.java','onMouseEvent'),('morphtool/ClientHandler.java','nextMod'),('morphtool/ClientHandler.java','previousMod'),('morphtool/network/MessageMorphTool.java','handle'),('morphtool/network/MessageMorphTool.java','serialize'),('morphtool/network/MessageMorphTool.java','deserialize'),('morphtool/network/NetworkHandler.java','register'),('morphtool/MorphTool.java','MorphTool'),('morphtool/MorphTool.java','commonSetup'),('morphtool/proxy/CommonProxy.java','preInit'),('morphtool/proxy/ClientProxy.java','preInit')],
 '实际合成把文档书/工具存进单件载体；玩家选择书籍、潜行用在方块或自动注视/滚轮选择时恢复目标真实ItemStack；变回基础物品或丢出/损坏时保留其余已附着载荷。两个官方项目共享核心，只提一条家族。',
 '物品tag下akashictome:data或morphtool:data按模组用途键保存完整ItemStack.save compound，含id/Count/tag；当前形态不在集合中，而是手中真实ItemStack。各自is_morphing、原显示名compound；Tome额外definedMod用于同模组多本书。',
 'makeMorphedStack先save当前形态、拷贝compound并移除其中嵌套data防递归，将非minecraft/自身的当前形态放回集合；取目标compound并先remove目标键，再ItemStack.of。解析为空则回基础书/工具，剩余集合继续附着，最后强制Count1。变回基础载体不丢其余有效项；但目标记录在解析前已移除，空结果不能保证保留不可识别原始载荷。',
 '两个项目alias方法是同源模式，映射方块/物品creator mod到用途键，不重写ItemStack.id，也不遍历旧保存键迁移；不能以配置别名表当真实旧注册ID修复。Tome同mod多书靠definedMod+_0.._98存储，while达到99次后不再检查最终键冲突，超限可覆盖，且assemble直接给原target加definedMod，合成预览不是纯只读。Morph重复用途键直接返回EMPTY。Tome服务端用modid重算，Morph客户端直接发整个目标栈/slot，服务端只粗查当前为MorphTool及不同item后写入，不重新构造源载荷或核对slot归属。',
 'Dynasty任务册兼容在调用原生ItemStack.of前保留原id/Count/tag并验证映射/目标注册存在，成功构造且持久写入后才替换或消费旧记录；缺FTB/缺物品时保留原始载荷并明确fallback，而不是默默清空。用途别名、保存集合键、真正注册ID三者要区分。普通任务册迁移保持原Count，不能照搬载体固定单件策略；原显示名只在结构有效时转换。',
 '本批只证明本mod的if(empty)路径与先删除顺序，未重验原生ItemStack.of对每种未知ID/ForgeCaps的完整解析，不声称任意坏档必为空。两边displayName无类型检查直接cast，fromJson返回null后的fallback只改displayName变量、不重建rawComp，随后rawComp.setStyle仍可NPE；非法JSON也无catch。getShift读取现有compound引用并原位修改，调用方即使拒收结果仍可能改原栈；TomeItem.useOn只比较item不比tag。拆出外来书/工具时会删除整个display compound，原自定义名字/染色等未保证还原，definedMod可能留存。Tome unmorph包仅主手，Morph损坏后余集恢复与拆出同链，不是Clone永久进度。未启动客户端GUI、游戏、网络或执行上游代码。',
 '两官方仓库makeMorphedStack绝大多数控制流只改名称/标签，归同家族一条；多书碰撞、工具损坏/拆出和网络权威差别作为同链限制，不按两个repo/附件键/alias条目/书籍种类另加信用。与原生ItemStack及其他物品集合家族需Kepler再审；本批credit0，支持方法/下载数零额外。')
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
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-013.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'exam_test_ban_lifted':True,'scope':'Research only; no upstream execution, master ledger, production or original save changes; no local game/GUI/TCP','records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')
if __name__=='__main__':generate()
