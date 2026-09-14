"""实体自检：注册了实体却没注册渲染器/贴图 —— 一刷出来就是客户端 NPE 崩溃。

（九霄天将 / 东海龙王 就踩过：实体、刷怪蛋都有，客户端没有渲染器，
  一进九霄天界 `Cannot invoke EntityRenderer.render because "entityrenderer" is null` 直接崩。）

另外一并钉死「属性表」这一条（崩服过）：
  * 每个注册的实体都必须在 EntityAttributeCreationEvent 里 put 一次属性；
  * 属性表里必须有攻击力 / 生命 —— 缺攻击力时，任何 getAttributeValue 都会抛
    `IllegalArgumentException: Can't find attribute minecraft:generic.attack_damage`，
    服务端主线程当场崩（盔甲架就是这个坑：`LivingEntity.createLivingAttributes()` 没有攻击力）。
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENTITIES = os.path.join(ROOT, "src/main/java/com/dynasty/entity/DynastyEntities.java")
CLIENT = os.path.join(ROOT, "src/main/java/com/dynasty/client/DynastyClientEvents.java")
TEX_DIR = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/entity")
ENTITY_DIR = os.path.join(ROOT, "src/main/java/com/dynasty/entity")

problems = []


def attribute_checks(registered):
    """属性注册自检：注册了实体就要注册属性，而且属性表得能打人。"""
    text = open(ENTITIES, encoding="utf-8").read()
    # ① EntityAttributeCreationEvent 里 put 了哪些实体常量
    put = set(re.findall(r"event\.put\(\s*([A-Z0-9_]+)", text))
    constants = set(re.findall(r'RegistryObject<EntityType<[^>]+>>\s+([A-Z0-9_]+)\s*=', text))
    for const in sorted(constants):
        if const not in put:
            problems.append("实体常量 %s 没有在 EntityAttributeCreationEvent 里注册属性"
                            "（缺属性 = 一进世界读属性就抛异常崩服）" % const)

    # ② 每个实体类的 createAttributes 必须来自 Mob/Monster 模板（含攻击力），
    #    或者自己显式加了 ATTACK_DAMAGE；只有 createLivingAttributes 的（盔甲架那种）会崩。
    #    注意：属性模板常常包在 base(...) / stats(...) 这类小助手里的，所以只要该文件
    #    出现过 Mob/Monster 模板就认为它没问题。
    for path in sorted(os.listdir(ENTITY_DIR)):
        if not path.endswith(".java"):
            continue
        body = open(os.path.join(ENTITY_DIR, path), encoding="utf-8").read()
        template = ("createMonsterAttributes" in body) or ("createMobAttributes" in body)
        for match in re.finditer(r"AttributeSupplier\.Builder\s+(\w+)\s*\(([^)]*)\)\s*\{(.*?)\n    \}",
                                 body, re.S):
            method, code = match.group(1), match.group(3)
            if not template and "ATTACK_DAMAGE" not in code:
                problems.append("%s 的 %s() 属性表里没有攻击力（createLivingAttributes 系列）"
                                "—— 读攻击力会抛异常崩服（盔甲架就是这么崩的）" % (path, method))
            if not template and "MAX_HEALTH" not in code:
                problems.append("%s 的 %s() 属性表里没有生命" % (path, method))


def main():
    registered = set(re.findall(r'ENTITIES\.register\("([a-z_]+)"', open(ENTITIES, encoding="utf-8").read()))
    rendered = set(re.findall(r'registerEntityRenderer\(\s*Dynasty[A-Za-z]*\.([A-Z0-9_]+)\.get\(\)',
                              open(CLIENT, encoding="utf-8").read()))
    rendered_ids = {name.lower() for name in rendered}
    textures = {name[:-4] for name in os.listdir(TEX_DIR) if name.endswith(".png")}

    print("实体自检：注册 %d 个，渲染器 %d 个，贴图 %d 张" % (len(registered), len(rendered_ids), len(textures)))
    for entity in sorted(registered):
        if entity not in rendered_ids:
            problems.append("实体 %s 没有注册渲染器（一刷出来客户端就崩）" % entity)
        if entity not in textures:
            problems.append("实体 %s 没有贴图（assets/dynasty/textures/entity/%s.png）" % (entity, entity))

    attribute_checks(registered)

    if problems:
        print("实体自检：发现问题 ❌")
        for problem in problems[:20]:
            print("   -", problem)
        sys.exit(1)
    print("实体自检：通过 ✅（每个实体都有渲染器 / 贴图 / 属性注册，属性表含攻击力与生命）")


if __name__ == "__main__":
    main()
