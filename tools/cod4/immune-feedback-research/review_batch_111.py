"""Native spawn-provenance final control refusal, one credit for complete trap policy."""
from ledger import B,O,record,verify
import json
r='TeamPneumatic/pnc-repressurized';p='src/main/java/me/desht/pneumaticcraft/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='pnc-native-spawn-provenance-rechecked-at-final-capture-after-type-whitelist'
record(k,r,[f('PneumaticCraftRepressurized.java',70,102),f('common/event/MiscEventHandler.java',286,307),f('common/registry/ModBlocks.java',247,250),f('common/registry/ModBlockEntityTypes.java',180,181),w('common/block/VacuumTrapBlock.java'),w('common/block/PneumaticCraftEntityBlock.java'),w('common/block/entity/spawning/VacuumTrapBlockEntity.java'),w('common/item/SpawnerCoreItem.java')],
 '固定已核Git树。原生mod ctor注册MiscEventHandler，FinalizeSpawn LOWEST仅vanilla spawner block/minecart标DEFENDER_TAG，注释明确不含PressurizedSpawner。实际trap注册方块/BE、shift交互或红石OPEN；native ticker分服务端tickServer。开门/装core/容量>0/负压<=-.5才每16世界tick扫描；isApplicable类型白名单优先于Boss/Drone/Warden/已驯服/黑名单排除。每tick对缓存targets再次查alive与DEFENDER_TAG，故白名单不能覆盖此最终来源免捕获。近距absorb，否则导航吸引。',
 '计1：来源事件生成的实例防御标签在最终控制执行前再验，区别纯类型Boss黑名单/白名单政策和Ars bubble释放UUID。扫描时未查defender，最终不吸不导航；Boss类型白名单可越过扫描Boss排除，但仍不能越过实例defender。absorb按core addAmount返回同一对象与否决定是否discard/扣XP/改core/播放PORTAL_TRIGGER和目标CLOUD粒子；缓存targets不因中途core满重新停止，随后addAmount无变化就不discard，但调用者仍addAir按e.getHealth。problem枚举只报告core/open，不报告目标免控；无immune灰字。',
 'Boss最终拒控应在原生执行点显式判定，不只在候选扫描过滤；白名单/实例Boss身份优先级需固定。灰字从明确拒控结果生产，成功吸收粒子及problem OK都不能推断拒控。节流回执不改变持续拒控。',
 '全文trap/block/ticker/core和完整onMobSpawn、mod ctor已读；注册仅具体字段范围。框架父tick/DescSynced通用编码未逐层读，拒控不依赖其可见UI；不声称网络/像素/自然获取已验。不按Boss/Warden/Drone或成功粒子包装拆数，守卫旧账0。','native_spawn_provenance_final_control_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch111-native-spawn-provenance-final-control-gate','credited_chains':[k],'rationale':'Instance-level defender provenance stamped on native spawn, rechecked on cached targets after type-whitelist scan. One final control-refusal policy, not another boss blacklist constant or capture wrapper. Core admission/receipt context not additional credits.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
