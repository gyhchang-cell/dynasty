"""A learned damage-source armor gate, not one credit per gem or armor slot."""
from ledger import B,O,record,verify
import json
r='DaedalusGame/EmbersRekindled';p='src/main/java/teamroots/embers/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='embers-native-attuned-source-full-set-socket-aggregate-final-refusal'
record(k,r,[f('Embers.java',64,73),f('RegistryManager.java',394,398),f('recipe/RecipeRegistry.java',1146,1147),w('item/ItemInflictorGem.java'),w('api/item/IInflictorGem.java'),w('api/item/IInflictorGemHolder.java'),w('recipe/AshenCloakSocketRecipe.java'),f('item/ItemAshenCloak.java',61,150),f('EventManager.java',283,336)],
 '已注册EventManager的原生LivingHurt→若受击者Player则先对主副手gem调用attuneSource，再对四装备各applyInflictorGemResistance。gem必须已有NBT，来源damageType不为mob/generic/player/arrow就写type并把metadata设1、播attune声；原生inventory onUpdate初始化NBT。已注册socket recipe把gem完整NBT复制入cloak的gem1..7；cloak只有全身四件都为未broken AshenCloak才累加同damageType各gem的.35。每件armor gate取max(0,1-totalResistance)，等于0 cancel，随后仍setAmount(当前伤害*mult)。',
 '一个由实际历史受击学习的来源签名+全套未坏装备资格+持久socket预算决定最终拒伤位点1，非逐damageType/七槽/四件/metadata换壳。不是按名字免疫：没有同源训练的gem或缺任何有效套件，累计为0；三颗同源gem可使该件mult归零，分布在不同件的两颗各.35则串行乘而非跨件简单相加。attune不检查当前gem已满，符合来源每次仍覆写与播声；手持训练音在防护取消之前，不证明这次拒伤。事件没有cancel后return，后续四件/装备heat和攻击者held heat仍继续；既有伤害被否决也可能推进附属进度。本条不是取消造成Boss免控，也没有免疫灰字/拒控嗡鸣。',
 'Boss灰字必须区分来源不支持、部分减伤、最终完全拒控以及装备/资源训练提示。先后副作用和重复通知需独立审计；同事件出现sound并不证明对应免疫语义。全套资格/目标实际状态应由服务端判定，客户端不从浮字反推免疫。',
 '固定版本，关键native处理、attune/read/resistance/装备完整gate与socket方法全文已读；大型物品/配方注册容器仅直接接入行作支持0，不声称全部配方方法已研究。未运行游戏/装备耐久实际集成/编译，不证明三颗gem实机确免疫所有相关来源。材质模型未制作未覆盖；普通体质不扩灰字。','native_learned_damage_signature_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'embers-batch80-learned-source-socket-gate','credited_chains':[k],'rationale':'完整原生来源训练→持久镶嵌→全套资格→按每件聚合最终拒伤合并1；NBT包装/来源名/四槽/七gem/训练音0额外，不与世界爆炸事件取消重复。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
