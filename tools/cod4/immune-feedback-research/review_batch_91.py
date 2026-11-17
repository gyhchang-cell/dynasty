"""Soul vial final capture denial with ordered authority and two distinct receipt routes, one family."""
from ledger import B,O,record,verify
import json
r='Team-EnderIO/EnderIO';p='enderio/src/main/java/com/enderio/enderio/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def rr(s):return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
k='enderio-native-capture-immutable-boss-and-serializable-gate-before-whitelist-and-contextual-refusal-text'
record(k,r,[w('content/tools/vials/SoulVialItem.java'),w('foundation/util/EntityCaptureUtils.java'),w('content/tools/ToolsLang.java'),f('init/EIOItems.java',212,212),f('init/EIOItems.java',302,319),f('EnderIO.java',76,129),rr('enderio/src/generated/resources/data/enderio/tags/entity_type/soul_vial_blacklist.json'),rr('enderio/src/generated/resources/data/enderio/tags/entity_type/soul_vial_whitelist.json')],
 '真实@Mod EnderIO构造注册EIOItems，SOUL_VIAL注册SoulVialItem；原生item interact服务器catchEntity在任何NBT/消耗/discard之前拒绝已填满、Player、dead，再getCapturableStatus：不可serialize→INCOMPATIBLE，EnderDragon→BLACKLISTED，之后才whitelist优先blacklist，最后默认可捕。实际blacklist含warden、c:capturing_not_supported和c:bosses，whitelist为空。玩家callback把status.errorMessage送displayClientMessage(actionbar=true)并returnFAIL；注册Dispenser behavior复用同一catch且callback空，继续尝试下一个，最终setSuccess(false)。',
 '一套真实“强制禁捕优先于可覆盖tag政策+按交互上下文明确拒绝理由”的最终目标控制接纳1，不按玩家/发射器包装、三种错误常量或Boss标签项拆分。注释“whitelist over all”不含早于它的canSerialize/EnderDragon硬门；ToolsLang声明ERROR_BOSS但实际status不用此常量，不把有boss文本key当活体Boss专用回执已接。玩家显示为动作栏，没有目标锚定、灰色设定或拒绝音/闪光；发射器静默为不同交互语义。getCapturableEntityTypes静态缓存枚举只给可选显示，不代替真实catch重新查tag；未看到该缓存reload失效。释放时entity create失败也vialConsumed且SUCCESS，保留为同链边界不新增credit。',
 'Boss拒控判断与反馈应从最终政策结果统一关联，数据tag可覆盖的策略不能误称所有Boss无条件免疫；声明的文本必须查实际producer，自动/非玩家控制也不能借玩家动作栏回执冒称旁观者灰字已同步。',
 '完整SoulVial/EntityCaptureUtils/ToolsLang及注册/固定生成tag已读；Soul.of数据序列化内部与其第三方实体mod未核，仅限拒绝前逻辑与真实API调用观察。无游戏/存档/正式代码/资产修改。不把捕捉政策扩展到本项目普通阴阳体质灰字。','native_target_control_denial_receipt')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'enderio-final-ordered-capture-refusal','credited_chains':[k],'rationale':'Final serializability/hard dragon/tag precedence with explicit actionbar error and silent automation =one native policy; cached listing, dispenser/player wrappers, text keys, tags not extra implementations. Not guard ledger transfer.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
