package com.dynasty;

import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * 王朝稀有材料与帝兵信物。
 *
 * 这些是「进化链的条件」：后半段的武器/护甲都必须加入 Boss 掉落物或图纸才能合成，
 * 所以想拿到神兵，就必须先科举升官、进天朝与地府、击败对应 Boss。
 *
 * Relics: the rare materials and imperial tokens that gate the late-game progression.
 */
@SuppressWarnings("null")
public final class DynastyRelics {

    private DynastyRelics() {
    }

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static RegistryObject<Item> basic(String name) {
        return ITEMS.register(name, () -> new Item(new Item.Properties()));
    }

    /** 兵器图纸：合成/升级武器与护甲的必要条件（可自制，也需要科举功名） */
    public static final RegistryObject<Item> BLUEPRINT = basic("blueprint");

    /** 精钢：铁锭精炼而成，青铜期以后的材料 */
    public static final RegistryObject<Item> REFINED_STEEL = basic("refined_steel");

    /** 叛将首级：击败「叛将」掉落 */
    public static final RegistryObject<Item> REBEL_HEAD = basic("rebel_head");

    /** 内廷令牌：击败「宦官首脑」掉落 */
    public static final RegistryObject<Item> EUNUCH_TOKEN = basic("eunuch_token");

    /** 帝骸骨：击败「不死始皇」掉落 */
    public static final RegistryObject<Item> EMPEROR_BONE = basic("emperor_bone");

    /** 龙帝玉玺：击败「龙帝」掉落，终盘装备的唯一凭据 */
    public static final RegistryObject<Item> DRAGON_EMPEROR_SEAL = basic("dragon_emperor_seal");

    /** 玄天玉：玄天套装的强化材料（用帝骸骨 + 龙晶 + 玉合成） */
    public static final RegistryObject<Item> XUANTIAN_JADE = basic("xuantian_jade");
}
