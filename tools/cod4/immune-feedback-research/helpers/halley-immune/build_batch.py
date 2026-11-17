"""Build a local-only research batch. Reads source text; never executes upstream code.

Writes exclusively to the two Halley helper directories. No network, build, game,
server, upstream import, master-ledger mutation, or checklist backup is performed.
"""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from inspect_methods import end_method

ROOT = Path(__file__).resolve().parents[5]
TOOLS = ROOT / 'tools/cod4/immune-feedback-research/helpers/halley-immune'
DOCS = ROOT / 'docs/cod4/audit-20261022/immune-feedback-research/helpers/halley-immune'
SOURCES = ROOT / 'tools/cod4/immune-feedback-research/sources'
MASTER = ROOT / 'docs/cod4/audit-20261022/immune-feedback-research'
U, L, V, D = ('AssortedMods__AssortedUtil', 'AssortedMods__AssortedLib',
               'luavixen__damagenumbers', 'Modrinth__kubdoMLE__LVErYFzu')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def master_hashes():
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in MASTER.iterdir()
            if p.is_file()}

before = master_hashes()
reviewed_bytes = (MASTER / 'reviewed.json').read_bytes()
reviewed = json.loads(reviewed_bytes)
assert any(x['id'] == 'dnp-health-delta-worldtext' for x in reviewed)
meta = {r: json.loads((SOURCES / r / 'source.json').read_text()) for r in (U, L, V, D)}
verified = {}

def exact(repo, filename):
    paths = list((SOURCES / repo).rglob(filename))
    assert len(paths) == 1, (repo, filename, paths)
    return paths[0].relative_to(SOURCES / repo).as_posix()

def evidence(repo, path, line, observation, application, limits, end=None, unit='complete_method'):
    p = SOURCES / repo / path
    data = p.read_bytes()
    lines = data.decode('utf-8').splitlines(keepends=True)
    if end is None:
        end = end_method(lines, line) if unit == 'complete_method' else len(lines)
    assert 1 <= line <= end <= len(lines), (path, line, end)
    pin = meta[repo]
    item = next(x for x in pin['files'] if x['path'] == path)
    digest = sha(data)
    assert digest == item['sha256'], (path, digest, item['sha256'])
    revision = pin.get('commit', pin.get('version_id'))
    git_blob = None
    if 'commit' in pin:
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert git_blob == item['git_blob_sha1'], path
        tree = json.loads((SOURCES / repo / 'tree.json').read_text())
        assert next(x['sha'] for x in tree['tree'] if x['path'] == path) == git_blob
        url = f"https://github.com/{pin['repo']}/blob/{revision}/{path}#L{line}-L{end}"
    else:
        url = f"https://modrinth.com/datapack/{pin['repo'].split('/')[-1]}/version/{revision}"
    local = str(p.resolve())
    verified[local] = {'repo': pin['repo'], 'revision': revision, 'path': path,
                       'source_local': local, 'source_sha256': digest,
                       'git_blob_sha1': git_blob, 'metadata_hash_match': True}
    return dict(repo=pin['repo'], revision=revision, path=path, source_local=local,
                source_sha256=digest, line=line, end_line=end,
                excerpt=''.join(lines[line-1:end]), observation=observation,
                application=application, limits=limits, url=url, unit=unit,
                research_credit=0, source_url=pin.get('source_url'),
                archive_member=path if repo == D else None)

def java(repo, filename, start, obs, app, limits):
    return evidence(repo, exact(repo, filename), start, obs, app, limits)

def whole(repo, path, obs, app, limits):
    return evidence(repo, path, 1, obs, app, limits, unit='complete_file')

u = []
def uj(name, start, obs, app, limits):
    u.append(java(U, name + '.java', start, obs, app, limits))

uj('AssortedDamageNumbersFabricClient', 9,
   'Fabric客户端入口仅调用DamageNumbersClient.init。', '定位注册入口。',
   'fabric.mod.json未缓存，不能证明该入口在发行物中被声明；不另计。')
uj('AssortedDamageNumbersNeoForgeClient', 16,
   'NeoForge构造器调用同一个init；类上有客户端Mod注解。', '两平台合并成一个玩法链。',
   'mods.toml未缓存，版本声明不可核实；不是独立实现。')
uj('DamageNumbersClient', 15,
   'init设置family图标/排序，并注册客户端tick END和level submit。',
   '先明确状态推进与逐帧提交的生命周期入口。', '调用依赖AssortedLib服务装载，发行版依赖声明缺失。')
uj('LivingEntityDamageEventMixin', 16,
   'handleDamageEvent的HEAD注入把原生DamageSource交给onDamageEvent；只记来源而不直接出生文字。',
   '来源事件与HP同步可分开到达，必须审查关联窗口。',
   '注入注解在第15行，mixin配置内容未缓存，不能证明实际启用。')
uj('DamageNumbers', 53,
   '仅客户端level记录entity整数ID→最新DamageSource及gameTime；新来源覆盖旧来源。',
   '短窗口来源关联可供比较；Boss免疫仍应由权威拒绝点给出语义。',
   '无target UUID、攻击序号、单次消费标记；不是成功或免疫回执。')
uj('DamageNumbers', 65,
   'level对象变更、level/player为空、功能关闭均清四张状态/弹窗集合并返回。正常tick先移除寿终弹窗；遍历范围内可渲染活体，以前次HP为基线。绝对变化<0.05、不对玩家可见、第一人称自身不产字。负HP差用年龄<=5的来源分类，正差可配置治疗字；最后换新基线并清>5tick来源。',
   '可借鉴world对象epoch清表和有限来源寿命；同tick一个目标只看到净HP变化，不能把它等同于按攻击/免疫原因合并。',
   '5tick不是提示节流；年龄无>=0下界；来源未消费，窗口内可被再次关联。伤害与治疗可抵消，未计吸收；没有弹窗总量上限。只查整数ID，死亡/离开渲染集合可能漏尾击。HP先到则不会在来源后到时回填标签。')
uj('DamageNumbers', 118,
   '金额和可选类型Component拼接后居中；以实体高度0.8和朝玩家XZ方向的宽度偏移确定出生点，存入DamagePopup。',
   '免疫字可借鉴按实体体型约束初始位置、让多字词整体居中。',
   '出生后保存世界坐标而不继续绑定target；没有去重键或同目标合并。')
uj('DamageNumbers', 134,
   '近战玩家标签读取消费时主手物品名，其他近战读取攻击者名，弹射物读取直接实体名；否则由类型给标签。',
   '提醒区分来源快照和事后可变状态，免疫原因不宜从当前持物猜测。',
   '来源记忆窗口内切换武器会改变标签语义；非拒绝原因。')
uj('DamageNumbers', 148,
   '逐弹窗插值世界坐标减相机位置，乘相机旋转后缩放0.025；NORMAL深度/FULL_BRIGHT提交文本，alpha<=0不提交。',
   '可比较世界锚点、相机朝向及淡出的文字呈现链。',
   '无目标实时追踪、无帧提交总量限制、无声音；这些绘制方法只属于本链辅助。')
uj('DamagePopup', 33,
   '构造器保存字形、偏移、颜色、寿命、地板与出生/前帧坐标，随机水平和向上速度。',
   '将文字内容和运动状态放进一个寿命对象便于清理。', '不是新免疫生产点或独立粒子玩法。')
uj('DamagePopup', 52,
   '每tick先存旧坐标，推进速度和重力、0.98阻尼；低于floor时弹跳并减速；++age<lifetime决定保留。',
   '寿终必须从容器移除而不只停止绘制。', '地板是出生时值；没有重查地形/实体/维度。')
uj('DamagePopup', 74,
   'alpha=clamp((1-(age+partial)/lifetime)*2)*255；前半程近似不透明，后半程淡出。',
   '可比较可读时间与寿命的区别。', '依赖正寿命配置；没有声音节流语义。')
uj('DamagePopup', 80,
   '金额距整数<0.05时取整，否则Locale.ROOT保留一位小数。',
   '固定locale避免数值显示因系统区域而变化。', '金额格式不构成额外参考家族；免疫词不是金额。')
uj('DamageKind', 86,
   '按DamageType标签、原版类型、NeoForge magic标签和modded命名空间归类；未知source为GENERIC。枚举中的GENERIC灰色只是伤害类别。',
   '必须把Boss拒绝原因与普通灰色类别分开研究。',
   '没有免疫/抵抗判定；modded一律MAGIC是启发式，不能作为真实原因。')
for start, obs, app, lim in [
    (49, '泛型modded来源走colorOf，否则取枚举颜色。', '分类色与语义消息必须分离。', '仅配色辅助，不计。'),
    (55, '标识符hash经murmur及HSV生成稳定颜色。', '可比较来源色稳定性。', '颜色不证明免疫，不计。'),
    (64, '只返回非minecraft命名空间的DamageType key。', '核实modded分类边界。', '缺key返回空；不是玩法新链。'),
    (69, '枚举名小写构建翻译键。', '多语言文案应有明确键。', '语言资源未缓存，不能声称已核对成品译文。'),
    (74, 'GENERIC的modded来源用damage type翻译键和nameOf回退，其他用枚举标签。', '缺译文时应有明确回退。', '这里不是Immune文字入口。'),
    (80, '取path最后一段、按下划线拆词并首字母大写。', '检查未翻译来源如何呈现。', '仅名称回退，不计。')]:
    uj('DamageKind', start, obs, app, lim)
uj('DamageNumbersClientConfig', 18,
   '客户端配置默认来源/治疗开启，range=24范围4..64，lifetime=40范围10..200，最后setup。',
   '用户可调寿命与扫描距离应分别约束。', '配置注册库实现/依赖版本未齐；不能声称配置已在游戏加载。')

for filename, ranges in [('FabricClientHelper.java', [(174, 'Fabric END_CLIENT_TICK将handler::handle注册为末端tick回调。'),
                                                     (184, 'Fabric COLLECT_SUBMITS把poseStack、collector、cameraRenderState交给handler。')]),
                         ('ForgeClientHelper.java', [(179, 'NeoForge ClientTickEvent.Post调用handler.handle(Minecraft.getInstance())。'),
                                                    (189, 'NeoForge SubmitCustomGeometryEvent把同类pose/collector/camera传给handler。')])]:
    for start, obs in ranges:
        u.append(java(L, filename, start, obs, '仅验证两端Java回调参数与Util注册点在静态文本上吻合，随主链合并。',
                      'AssortedLib独立固定提交不等于Util发行版实际依赖版本；服务资源/版本文件缺失，库0计数。'))
for filename, obs in [('ClientServices.java', '静态CLIENT=Services.load(IClientHelper.class)，服务装载仍是外部边界。'),
                      ('ClientTickHandler.java', '函数接口接收Minecraft客户端。'),
                      ('LevelSubmitHandler.java', '函数接口接收PoseStack、SubmitNodeCollector、CameraRenderState。'),
                      ('IClientHelper.java', '接口含registerClientTickEnd和registerLevelSubmit声明，契合Util调用和平台实现。')]:
    u.append(whole(L, exact(L, filename), obs, '补足Java接口与装载点，保持同链0计数。',
                   'Services.load实现和META-INF/services实际内容未缓存；接口声明不是已激活证据。'))

v = []
def vj(name, start, obs, app, limits, path=None):
    v.append(evidence(V, path, start, obs, app, limits) if path else java(V, name+'.java', start, obs, app, limits))
vj('DamageNumbersInitializer', 9, 'Fabric客户端入口以configDir构造DamageNumbers。', '标定入口与配置路径。', '入口声明资源未缓存；与其他平台同链。')
for platform, starts in [('forge', [13,21]), ('neoforge',[13,18])]:
    path = f'{platform}/src/main/java/dev/foxgirl/damagenumbers/DamageNumbersMod.java'
    for start in starts:
        vj('', start, '构造器注册client setup及配置界面；client setup构造同一DamageNumbers。' if start==13 else 'client setup以FMLPaths.CONFIGDIR构造同一DamageNumbers。',
           '平台入口合并核对。', '不因平台移植增加家族；发行元数据未缓存。', path=path)
vj('DamageNumbers', 25, '先设全局INSTANCE，再反射构造客户端DamageNumbersImpl；反射失败转RuntimeException。',
   '辨别客户端装载边界。', '仅静态读到反射目标；未执行/构建。')
vj('DamageNumbers', 16, 'getHandler要求INSTANCE非空，返回实例handler。', '核查mixin到handler的调用路径。', '初始化顺序依赖入口实际激活；不另计。')
vj('MixinLivingEntity', 18,
   'LivingEntity.tick TAIL仅在client world读取getHealth，变化时更新previousHealth并调用handler。初始基线0，第一次正HP变化随后被damage<=0过滤。',
   '零血差不会生成Immune；首次基线不是一次伤害。',
   'mixin配置缺失，不能验证启用；与主账dnp-health-delta-worldtext同属HP差生产家族。')
vj('DamageNumbersImpl', 32, '保存configDir并readConfig。', '追到实际使用的enabled/颜色配置。', '不执行配置读写；配置方法不是独立玩法。')
vj('DamageNumbersImpl', 59,
   'enabled→damage=old-new且>0→可配置排除自身→同client world→48格距离→按粒子档位256/64/16限制deque。追加前while>=limit剔除并markDead；按伤害2/8/16区间插值颜色，构造TextParticle再交particleManager。',
   '总存活粒子预算可与每目标提示频率分开；追加前>=能约束所持队列长度。',
   '不是抗刷屏冷却/同原因合并，无来源/免疫判定。队列未见自然死亡主动清理及world切换清表；可能持有过期引用。读取player距离前未显式判空。数值用默认locale后只剥离字面“.0”。')
vj('TextParticle', 18, '交给vanilla Particle构造后设velocityMultiplier=.99、gravity=.75、maxAge=32。',
   '将TTL与运动参数集中于粒子对象。', 'vanilla Particle.tick未在本授权缓存审查；只证实maxAge赋值，不能声称运行寿终通过。')
vj('TextParticle', 25, '粒子保存整段String文本。', '单条文本作为一个显示对象。', '不构成独立来源或免疫消息。')
vj('TextParticle', 29, '保存Color并复制RGB到粒子属性。', '核实颜色进入粒子实例的路径。', '未单独写免疫色；不计颜色变体。')
vj('TextParticle', 37, '返回CUSTOM粒子sheet。', '追踪自定义文字绘制入口。', '接口返回值不是第二玩法。')
vj('TextParticle', 42,
   '插值粒子位置减相机位置；相机旋转加PI的Y旋转、负0.025缩放；按完整字宽居中，以NORMAL深度、FULL_BRIGHT画字并flush。',
   '可比较整词居中、深度关系与世界点运动。',
   '出生位置不是持续target UUID跟随；此方法没有按age淡出，颜色alpha来自配置。未做观感验证。')
for start, obs in [(23, 'RGBA夹到0..1并转ARGB整数供draw。'), (85, '线性插值RGBA用于伤害区间颜色。'),
                   (61, '解析#RRGGBB或#RRGGBBAA；未给alpha时默认FF。'),
                   (100, '分量clamp后乘255并round。')]:
    vj('Color', start, obs, '仅补绘制链中的配色数据流。', '通用配色辅助0计数，颜色差异不构成独立实现。')
for start, obs in [(80, '从JSON读enabled/showPlayerDamage及三档颜色，缺项保留默认。'),
                   (97, '配置读入Gson；文件缺失时调用writeConfig，其他错误记录日志。'),
                   (112, '配置写临时文件后ATOMIC_MOVE/REPLACE_EXISTING。')]:
    vj('Config', start, obs, '说明选项如何影响链，不把配置读写另算。', '仅阅读其源码；本研究没有调用这些配置写入方法。')

d = []
def dw(path, obs, app, lim):
    d.append(whole(D, path, obs, app, lim))
dw('pack.mcmeta', 'pack_format=71，但JSON闭括号后第8行有裸说明文字；严格JSON解析失败。',
   '应先审查资源入口格式再声称整链可加载。', '只做文本/JSON解析，没有运行数据包；因此不声称游戏加载结果。')
for kind in ['load','tick']:
    dw(f'data/minecraft/tags/function/{kind}.json', f'{kind} tag指向oszu_fd:{kind}。',
       '追踪数据包入口。', '入口文件存在不等于有效pack已加载。')
dw('data/oszu_fd/function/load.mcfunction',
   '创建寿命、伤害、开关及下一tick待处理score目标，初始化常量10和共享storage小数点。',
   '确认延迟处理状态以玩家score和共享storage组织。', '没有target UUID、维度、原因队列或事件序号；未运行命令。')
dw('data/oszu_fd/advancement/root.json', 'minecraft:tick advancement奖励initial_join，只设置触发开关。',
   '区分初始化入口与战斗生产入口。', '初始化不是免疫反馈。')
dw('data/oszu_fd/function/initial_join.mcfunction', 'enable玩家print_off/on trigger。',
   '追踪聊天开关入口。', '没有限频。')
for n in ['false','true']:
    dw(f'data/oszu_fd/function/set_print_{n}.mcfunction', f'设置玩家print score、reset并重新enable trigger；切换通知tellraw @a。',
       '用户开关与战斗反馈节流需分开。', '切换文案广播所有玩家，不等于战斗接收者仅本人。')
for name, value in [('damage_0.1','0.1'),('damage_100_plus','100_plus')]:
    dw(f'data/oszu_fd/advancement/damage/{name}.json',
       'player_hurt_entity正dealt区间奖励set_damage_value；这里只完整审查最小和100+两个边界。',
       '确认真正设置pending的入口。', '其余数千数值文件没有逐方法审查，不计独立实现；未审原版dealt与全阻挡触发时序。')
    dw(f'data/oszu_fd/function/set_damage_value/{value}.mcfunction',
       '撤销自身advancement、覆盖该玩家damage score，再调用check_modifiers。',
       '同tick多次事件是覆盖而非sum聚合。', 'pending按玩家合并而非target；金额阈值包装不另计。')
for p in sorted((SOURCES / D / 'data/oszu_fd/advancement/modifiers').glob('*.json')):
    blocked = p.name == 'blocked_damage.json'
    dw(p.relative_to(SOURCES / D).as_posix(),
       ('blocked=true的player_hurt_entity判据，没有rewards/function，自己不调用check_modifiers。' if blocked else
        f'{p.stem}只设置对应advancement条件状态，无独立reward；process_data稍后检查。'),
       '把修饰状态与真正排队入口区分；颜色/目标类型变体合并一链。',
       '不能因名字blocked就认为Boss免疫；未审原版触发器，纯阻挡能否同时命中正dealt区间待核实。')
dw('data/oszu_fd/function/modifiers/check_modifiers.mcfunction',
   '只把玩家compensation score设为1。', '下一tick再读修饰状态是实在的延迟入口。',
   '不是事件队列；多击都覆盖为1，没有target或攻击来源快照。')
dw('data/oszu_fd/function/modifiers/process_data.mcfunction',
   '拆玩家damage score到共享storage小数/整数；顺序应用修饰，blocked最后将文字改Blocked。projectile分支给玩家experience_orb.pickup声音；调用文字生成后清pending并撤销全部修饰状态。',
   '可借鉴一次处理后清pending及修饰状态；需审查一次槽位丢失哪些目标/原因。',
   '一次布尔pending最多表示该玩家本tick有事，不是可靠事件合并。blocked覆盖文案不产生独立声音；投射物经验球声不是Boss免疫嗡声。共享storage不是每事件快照。')
dw('data/oszu_fd/function/modifiers/merge_damage_text.mcfunction',
   '依据整数/小数score把金额拼成文本；函数名merge是数字格式拼接。',
   '避免把merge函数名误认为同目标伤害/提示聚合。', '没有事件去重、累计或限频。')
dw('data/oszu_fd/function/modifiers/initiate_flaoting_text.mcfunction',
   '宏从storage取词色；可选tellraw给@p，世界文字在@n[HurtTime:10s]附近生成；新文字用未initiated标签选择、插值放大、位移后加initiated。',
   '显式target身份比最近HurtTime实体可靠；聊天接收者也必须绑定原玩家。',
   '选择的是最近受伤者而非事件原目标，tellraw执行上下文已改到目标附近的@p；多人多实体时可错绑。看不到免疫事件自身保证HurtTime的证据；不声称纯阻挡必定显示或必定不显示。')
dw('data/oszu_fd/function/tick.mcfunction',
   '带oszu标签的text_display每tick寿命+1，>=20杀；寿命10的每个文字又as所有text_display缩放至0；最后按pending玩家执行process_data。',
   '寿命清理与渲染动画选择器都应限制在自己拥有的实体。',
   '第5行内层选择器遗漏tag，会改其他包/玩家text_display；多个age10文字重复全选。20tick TTL不是每Boss提示/声音冷却；没有分维度全局一致性保证。')

def record(ident, refs, status, observation, application, limits, risk, chain, duplicate):
    anchor = refs[0]
    # Required evidence fields also live on the family record for simple consumers.
    out = {key: anchor[key] for key in ['repo','revision','path','source_local','source_sha256',
                                      'line','end_line','excerpt','url']}
    out.update(id=ident, status=status, observation=observation, application=application,
               limits=limits, duplicate_family_risk=risk, semantic_dedup_key=ident,
               compare_master_ids=duplicate, implementation_chain=chain, source_refs=refs,
               count_unit='one family; all supporting methods, platform ports and numeric/color wrappers merged',
               research_credit=0, suggested_credit=0, master_credit=0,
               promotion_owner='Russell / 主协调；本批不自动晋级')
    return out

# Set the main anchors to complete gameplay methods, rather than platform wrappers.
u.sort(key=lambda x: not (x['repo']=='AssortedMods/AssortedUtil' and x['path'].endswith('/DamageNumbers.java') and x['line']==65))
v.sort(key=lambda x: not (x['path'].endswith('/DamageNumbersImpl.java') and x['line']==59))
d.sort(key=lambda x: not x['path'].endswith('/modifiers/process_data.mcfunction'))
records = [
    record('halley-assortedutil-source-memory-health-text', u, 'reviewed_static_family_not_promotable',
           '完整读到客户端伤害来源记忆→HP差→分类/标签→弹窗tick/submit，以及两平台入口和AssortedLib桥接；level对象换代清表、5tick来源窗口确有实现。缺激活与依赖元数据，且没有Boss免疫语义或声音节流。',
           '仅借鉴状态epoch、来源与显示的时序边界、TTL销毁和整词居中；零HP差不能据此推断Immune。',
           ['未缓存mixin配置、mod声明、Gradle版本及服务provider资源，静态签名一致不证明发行版兼容/激活。',
            '来源年龄窗口不是消费或限频；缺UUID/攻击序号；这里只是净HP变化，非权威免疫反馈。',
            '未运行游戏/服务器/上游代码；无观感、加载或播放验证。'],
           '与dnp-health-delta-worldtext的数字生产/绘制存在重合。5tick来源记忆和world对象清理可供主协调比较，但不能拆成新credits；库/平台/颜色/金额格式均0计数。',
           ['platform entry→DamageNumbersClient.init→ClientServices.CLIENT→tick END / level submit',
            'LivingEntity.handleDamageEvent HEAD mixin→onDamageEvent(integer ID, source, time)',
            'tick→net HP delta + recent source→DamageKind/label→spawn→DamagePopup',
            'tick removeIf→DamagePopup.tick; level submit→alpha + interpolated position→submitText'],
           ['dnp-health-delta-worldtext']),
    record('halley-luavixen-health-delta-family-overlap', v, 'reviewed_duplicate_family_zero',
           '完整入口→tick TAIL HP差→过滤/颜色/总量cap→TextParticle→buildGeometry链；三平台合并一条。没有免疫分支、伤害来源、声音或每目标节流。',
           '可比较追加前>=总量上限、出生锚点与整个字符串居中；这些只是已有HP差家族的呈现差异。',
           ['与已计DNP同家族，不按32tick、颜色阈值或平台拆条。',
            '缺mixin激活元数据；vanilla Particle生命周期实现不在本次缓存审查范围。',
            '未读到world切换时清deque及自然死亡主动清引用；总量限制不等于防刷屏冷却。'],
           '高：dnp-health-delta-worldtext。仅实现参数/平台差异，不建议新增计数。',
           ['Fabric/Forge/NeoForge entry→DamageNumbers reflection→DamageNumbersImpl/config',
            'MixinLivingEntity.tick TAIL→getHandler→onEntityHealthChange',
            'damage>0 + world/distance/settings→cap deque→TextParticle→particleManager',
            'TextParticle CUSTOM buildGeometry→camera-facing NORMAL text; maxAge=32 assignment'],
           ['dnp-health-delta-worldtext']),
    record('halley-floatingdamage-blocked-counterexample', d, 'reviewed_counterexample_zero',
           '读到正dealt阈值→覆盖玩家score/pending→下一tick读advancement修饰→Blocked可覆盖文案→text_display→寿命清理。blocked本身无reward；最近HurtTime选择丢失原目标，age10动画误选全部text_display，pack.mcmeta严格JSON失败。',
           '作为反例：要在权威免疫拒绝点生成语义，携带原玩家/target身份；TTL、pending与真正限频分开，动画和清理只作用自身实体。',
           ['固定Modrinth版本LVErYFzu/1.2、目标Minecraft1.21.5；不是可虚构GitHub commit的仓库。',
            '只审查两个金额边界及其函数和全套核心/修饰文件，不声称逐一审完全部数字包装。',
            '未审原版advancement引擎，不能断言纯block必达/必不达dealt正值门；仅凭Blocked字符串不计有效免疫实现。',
            '未运行数据包或命令；pack格式诊断是严格JSON静态结果，非游戏日志。'],
           '所有阈值、伤害类型/实体类型颜色变体同一score/storage/text_display链；不得拆成数千credits。当前作为反例0计数。',
           ['load/tick tags→score objectives; positive damage advancement→set_damage_value→check_modifiers',
            'pending player tick→process_data→merge_damage_text + advancement flags',
            'blocked flag replaces text; projectile alone plays vanilla pickup sound',
            'initiate_flaoting_text macro→nearest HurtTime entity→text_display; tick lifespan/kill'],
           [])
]

missing = []
for repo in (U,L,V):
    tree = json.loads((SOURCES/repo/'tree.json').read_text())
    for entry in tree['tree']:
        path = entry['path']
        if entry.get('type') != 'blob':
            continue
        relevant = (repo != U or path.startswith('mods/damagenumbers/') or path in ['gradle.properties','build.gradle'])
        config = (path.endswith(('gradle.properties','build.gradle','fabric.mod.json','mixins.json','neoforge.mods.toml'))
                  or path.endswith('/com.grim3212.assorted.lib.platform.services.IClientHelper'))
        if relevant and config and not (SOURCES/repo/path).exists():
            missing.append(dict(repo=meta[repo]['repo'], revision=meta[repo]['commit'], path=path,
                                git_tree_blob_sha1=entry['sha'], local_contents_available=False,
                                reviewed=False, research_credit=0,
                                reason='仅固定Git树证明路径及blob ID存在；没有缓存内容，不编造激活/依赖版本。'))

infection_refs = []
infection_provenance = []
infection_missing = []
# Latest explicit scope expansion permits these two existing local caches only.
# Copy just the two item files, after verifying their pinned Git blob identities.
for repo, item_path, helper_path, effect_path, start, obs in [
    ('TeamLapen/Werewolves',
     'src/main/java/de/teamlapen/werewolves/items/WerewolfToothItem.java',
     'src/main/java/de/teamlapen/werewolves/util/Helper.java',
     'src/main/java/de/teamlapen/werewolves/effects/LupusSanguinemEffect.java', 27,
     '服务端use先查管理员开关；允许时canBecomeWerewolf成功才加感染/毒，失败再区分已是狼人或immune_to+疾病名。管理员禁用不耗物品；允许分支无论感染成功/已是狼人/免疫都shrink(1)。displayClientMessage(...,true)给使用者overlay。'),
    ('TeamLapen/Vampirism',
     'projects/vampirism/src/main/java/de/teamlapen/vampirism/common/world/items/VampireFangItem.java',
     'projects/vampirism/src/main/java/de/teamlapen/vampirism/common/util/Helper.java',
     'projects/vampirism/src/main/java/de/teamlapen/vampirism/common/world/effects/SanguinareMobEffect.java', 22,
     '服务端use先查fangInfection开关；canBecomeVampire成功加感染/毒，否则区分already_vampire与immune_to_sanguinare。sendOverlayMessage只调用使用者；允许分支总shrink(1)，禁用分支不耗；最后SUCCESS_SERVER。')]:
    folder = ROOT / 'build/item-use-references' / repo.replace('/','__')
    provenance = json.loads((folder/'source.json').read_text())
    tree_data = (folder/'tree.json').read_bytes()
    tree = json.loads(tree_data)
    revision = provenance['sha']
    assert tree['sha'] == revision
    assert tree['url'] == f'https://api.github.com/repos/{repo}/git/trees/{revision}'
    original = folder/item_path
    data = original.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert next(x['sha'] for x in tree['tree'] if x['path']==item_path) == blob
    copy = TOOLS/'sources'/repo.replace('/','__')/item_path
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_bytes(data)
    assert original.read_bytes() == copy.read_bytes()
    lines = data.decode('utf-8').splitlines(keepends=True)
    end = end_method(lines,start)
    ref = dict(repo=repo, revision=revision, path=item_path, source_local=str(copy),
               source_original_local=str(original), source_sha256=sha(data), git_blob_sha1=blob,
               line=start,end_line=end,excerpt=''.join(lines[start-1:end]), unit='complete_method',
               observation=obs,
               application='拒绝发生在服务端且直接给发起玩家明确本地化提示；应区分配置禁用、已具身份和真正免疫，不能所有失败都写Immune。',
               limits='这里只完整取得物品use分支；Helper资格判定、感染效果实现、语言资源及vanilla overlay渲染实现未缓存，不能验证真正免疫条件/文本寿命。非伤害或Boss免疫，无自定义文字粒子/声音/限频。',
               url=f'https://github.com/{repo}/blob/{revision}/{item_path}#L{start}-L{end}',research_credit=0)
    infection_refs.append(ref)
    verified[str(copy)] = dict(repo=repo, revision=revision,path=item_path, source_local=str(copy),
                               source_original_local=str(original),source_sha256=sha(data),
                               git_blob_sha1=blob,git_tree_blob_match=True,
                               source_json_contains_file_sha256=False,
                               local_copy_matches_original=True)
    infection_provenance.append(dict(repo=repo,revision=revision,
                                      source_metadata_local=str(folder/'source.json'),
                                      source_metadata_sha256=sha((folder/'source.json').read_bytes()),
                                      tree_local=str(folder/'tree.json'),tree_sha256=sha(tree_data),
                                      tree_revision_matches_source_metadata=True))
    for path in [helper_path,effect_path]:
        entry = next(x for x in tree['tree'] if x['path']==path)
        assert not (folder/path).exists(), 'New local support source present; review before rerun'
        infection_missing.append(dict(repo=repo,revision=revision,path=path,
                                       git_tree_blob_sha1=entry['sha'],local_contents_available=False,
                                       reviewed=False,research_credit=0,
                                       reason='固定树有路径，缓存无全文；不把资格/免疫判定及感染效果声称为已审完整调用链。'))
records.append(record('halley-player-infection-item-rejection-partial-family', infection_refs,
                      'partial_candidate_not_complete_chain_zero',
                      '两份物品use方法均全文审查并核对Git blob；同属主动感染物品的服务端资格拒绝→使用者overlay模板。缺Helper全文，未完成真正免疫判定链；两仓库保守合并一候选家族。',
                      '明确拆开管理员禁用/已具身份/免疫文案；可借鉴服务端判定后只通知发起者。',
                      ['玩家主动感染而非Boss伤害/拒控；不计有效Boss免疫参考。',
                       '固定缓存未含Helper/感染效果/语言资源全文；方法名不足以证明免疫资格条件。',
                       '此处没有声音、粒子、同原因冷却或聚合，overlay刷新也不能冒充已审限频。'],
                      'WerewolfTooth/VampireFang控制结构同模板，最多一候选；不按疾病名、返回类型或平台API变化拆为两credit。',
                      ['item use server gate→admin config',
                       'Helper.canBecome*(NOT CACHED)→infection success or identity/immune message',
                       'player displayClientMessage(true) / sendOverlayMessage→vanilla overlay (not locally reviewed)',
                       'allowed-config branch shrinks item even on rejection'], []))
missing.extend(infection_missing)

archive_digest = hashlib.sha512((SOURCES/D/'source.zip').read_bytes()).hexdigest()
assert archive_digest == meta[D]['archive_sha512']
try:
    json.loads((SOURCES/D/'pack.mcmeta').read_text())
    raise AssertionError('pack.mcmeta unexpectedly parsed')
except json.JSONDecodeError as exc:
    pack_diagnostic = dict(type='JSONDecodeError', line=exc.lineno, column=exc.colno, message=exc.msg)

for row in records:
    assert row['research_credit'] == row['master_credit'] == row['suggested_credit'] == 0
    assert row['id'] not in {x['id'] for x in reviewed}
    for ref in row['source_refs']:
        p = Path(ref['source_local'])
        lines = p.read_bytes().decode('utf-8').splitlines(keepends=True)
        assert ''.join(lines[ref['line']-1:ref['end_line']]) == ref['excerpt']
        if ref['unit'] == 'complete_method':
            assert end_method(lines, ref['line']) == ref['end_line']
        assert ref['source_sha256'] == sha(p.read_bytes())

payload = dict(schema='halley-immune-family-review-v1', helper='halley-immune',
               created_utc=datetime.now(timezone.utc).isoformat(),
               scope='local source text only; no upstream execution; Russell owns promotion/dedup/master',
               master_reviewed_read=dict(path=str(MASTER/'reviewed.json'),
                                         source_sha256=sha(reviewed_bytes), count=len(reviewed)),
               requested_effective_target=30, max_suggestions_per_batch=30,
               audited_family_count=3, partial_candidate_family_count=1,
               total_family_record_count=len(records), evidence_span_count=sum(len(x['source_refs']) for x in records),
               promotable_suggestion_count=0, research_credit=0, master_credit=0,
               effective_target_gap=30,
               counting_note='3家族静态审查+1个感染提示部分候选不等于有效参考；所有方法/文件仅为同链证据，不单独计数。最多30是上限，不凑数；有效参考0。',
               records=records, supplemental_cache_provenance=infection_provenance,
               missing_activation_version_evidence=missing)

after = master_hashes()
assert before == after, 'Master files changed during build; inspect before delivering'
verification = dict(schema='halley-immune-verification-v1',
                    checked_utc=datetime.now(timezone.utc).isoformat(),
                    source_file_count=len(verified), files=list(verified.values()),
                    original_immune_cache_files_sha256_match_metadata=True,
                    original_immune_cache_java_git_blob_sha1_match_source_and_tree=True,
                    supplemental_cache_item_git_blob_sha1_match_pinned_tree=True,
                    excerpt_and_complete_method_range_validation=True,
                    archive=dict(source_local=str(SOURCES/D/'source.zip'), sha512=archive_digest,
                                 matches_source_metadata=True, version_id='LVErYFzu', version='1.2'),
                    strict_pack_mcmeta_parse=pack_diagnostic,
                    master_files_hashes_only=before, master_files_unchanged_during_build=True,
                    execution='Only authored Python static reader/assembler executed. No upstream Java, Gradle, mcfunction, game or server executed.',
                    provenance_limit='Uses existing local source.json and pinned tree/version.json including the explicitly authorized two build/item-use-references caches; no new external lookup or independent author identity check.',
                    runtime_verified=False)
DOCS.mkdir(parents=True, exist_ok=True)
for name, obj in [('batch-001.json',payload),('verification-001.json',verification)]:
    (DOCS/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
assert master_hashes() == before
print(json.dumps({key:payload[key] for key in ['audited_family_count','evidence_span_count',
                                             'promotable_suggestion_count','research_credit',
                                             'master_credit','effective_target_gap']}, ensure_ascii=False))
print(f'Verified {len(verified)} source files; wrote only {DOCS.relative_to(ROOT)}')
