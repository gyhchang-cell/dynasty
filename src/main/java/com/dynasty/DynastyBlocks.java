package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 方块 / Dynasty blocks.
 */
@SuppressWarnings("null")
public class DynastyBlocks {

    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, Dynasty.MODID);
    public static final DeferredRegister<Item> BLOCK_ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static RegistryObject<Block> simple(String name, BlockBehaviour.Properties props) {
        RegistryObject<Block> block = BLOCKS.register(name, () -> new Block(props));
        BLOCK_ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
        return block;
    }

    private static RegistryObject<Block> custom(String name, java.util.function.Supplier<Block> factory) {
        RegistryObject<Block> block = BLOCKS.register(name, factory);
        BLOCK_ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
        return block;
    }

    private static BlockBehaviour.Properties stone(float strength) {
        return BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(strength).sound(SoundType.STONE);
    }

    /** 玉矿 / Jade Ore */
    public static final RegistryObject<Block> JADE_ORE =
            simple("jade_ore", stone(3.0F).requiresCorrectToolForDrops());

    /** 深层玉矿 / Deepslate Jade Ore */
    public static final RegistryObject<Block> DEEPSLATE_JADE_ORE =
            simple("deepslate_jade_ore", BlockBehaviour.Properties.of().mapColor(MapColor.DEEPSLATE)
                    .strength(4.5F).sound(SoundType.DEEPSLATE).requiresCorrectToolForDrops());

    /** 龙晶矿 / Dragon Crystal Ore */
    public static final RegistryObject<Block> DRAGON_CRYSTAL_ORE =
            simple("dragon_crystal_ore", stone(5.5F).requiresCorrectToolForDrops());

    /** 玉块 / Jade Block */
    public static final RegistryObject<Block> JADE_BLOCK =
            simple("jade_block", stone(5.0F));

    /** 青铜块 / Bronze Block */
    public static final RegistryObject<Block> BRONZE_BLOCK =
            simple("bronze_block", BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_ORANGE)
                    .strength(5.0F).sound(SoundType.METAL));

    /** 宫廷砖 / Palace Bricks */
    public static final RegistryObject<Block> PALACE_BRICKS =
            simple("palace_bricks", stone(2.5F));

    /** 汉白玉 / Marble */
    public static final RegistryObject<Block> MARBLE_BLOCK =
            simple("marble_block", stone(2.5F));

    /** 朱红柱 / Crimson Pillar */
    public static final RegistryObject<Block> CRIMSON_PILLAR = BLOCKS.register("crimson_pillar",
            () -> new RotatedPillarBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED)
                    .strength(2.5F).sound(SoundType.WOOD)));
    static {
        BLOCK_ITEMS.register("crimson_pillar",
                () -> new BlockItem(CRIMSON_PILLAR.get(), new Item.Properties()));
    }

    /** 宫灯 / Imperial Lantern */
    public static final RegistryObject<Block> IMPERIAL_LANTERN =
            simple("imperial_lantern", BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED)
                    .strength(1.0F).sound(SoundType.WOOD).lightLevel(state -> 15));

    private static BlockBehaviour.Properties portalProps() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_LIGHT_GREEN)
                .strength(-1.0F, 3600000.0F).noCollission().lightLevel(state -> 15)
                .sound(SoundType.GLASS);
    }

    /** 天朝传送门 / Celestial Dynasty portal */
    public static final RegistryObject<Block> JADE_PORTAL = BLOCKS.register("jade_portal",
            () -> new com.dynasty.block.DynastyPortalBlock(portalProps(),
                    com.dynasty.block.DynastyPortalBlock.CELESTIAL_DYNASTY));
    static {
        BLOCK_ITEMS.register("jade_portal", () -> new BlockItem(JADE_PORTAL.get(), new Item.Properties()));
    }

    /** 云门：通往九霄天界 / Cloud Gate to the nine-heaven realm */
    public static final RegistryObject<Block> CLOUD_PORTAL = BLOCKS.register("cloud_portal",
            () -> new com.dynasty.block.DynastyPortalBlock(portalProps(),
                    com.dynasty.block.DynastyPortalBlock.JIUXIAO));
    static {
        BLOCK_ITEMS.register("cloud_portal", () -> new BlockItem(CLOUD_PORTAL.get(), new Item.Properties()));
    }

    /** 龙门：通往东海龙宫 / Dragon Gate to the Dragon Palace */
    public static final RegistryObject<Block> DRAGON_GATE = BLOCKS.register("dragon_gate",
            () -> new com.dynasty.block.DynastyPortalBlock(portalProps(),
                    com.dynasty.block.DynastyPortalBlock.DRAGON_PALACE));
    static {
        BLOCK_ITEMS.register("dragon_gate", () -> new BlockItem(DRAGON_GATE.get(), new Item.Properties()));
    }

    /** 地府传送门 / Underworld portal */
    public static final RegistryObject<Block> UNDERWORLD_PORTAL = BLOCKS.register("underworld_portal",
            () -> new com.dynasty.block.DynastyPortalBlock(
                    portalProps().mapColor(MapColor.COLOR_PURPLE).sound(SoundType.GLASS),
                    com.dynasty.block.DynastyPortalBlock.UNDERWORLD));
    static {
        BLOCK_ITEMS.register("underworld_portal", () -> new BlockItem(UNDERWORLD_PORTAL.get(), new Item.Properties()));
    }

    // ---- 宫廷装饰 / palace decoration ----
    /** 龙椅 / Dragon Throne */
    public static final RegistryObject<Block> DRAGON_THRONE = simple("dragon_throne", stone(3.5F));
    /** 祭坛 / Altar */
    public static final RegistryObject<Block> ALTAR = simple("altar", stone(3.0F).lightLevel(s -> 7));
    /** 法阵·祭坛：用 Boss 信物召唤 Boss / ritual altar for summoning bosses */
    public static final RegistryObject<Block> RITUAL_ALTAR =
            custom("ritual_altar", () -> new com.dynasty.block.RitualAltarBlock(
                    stone(4.0F).lightLevel(s -> 11)));
    /** 编钟 / Chime Bell */
    public static final RegistryObject<Block> CHIME_BELL =
            custom("chime_bell", () -> new com.dynasty.block.DynastyInstrumentBlock(
                    BlockBehaviour.Properties.of().mapColor(MapColor.GOLD)
                            .strength(2.0F).sound(SoundType.METAL), true));
    /** 太鼓 / Taiko Drum */
    public static final RegistryObject<Block> TAIKO_DRUM =
            custom("taiko_drum", () -> new com.dynasty.block.DynastyInstrumentBlock(
                    BlockBehaviour.Properties.of().mapColor(MapColor.WOOD)
                            .strength(2.0F).sound(SoundType.WOOD), false));
    /** 香炉 / Incense Burner */
    public static final RegistryObject<Block> INCENSE_BURNER =
            simple("incense_burner", BlockBehaviour.Properties.of().mapColor(MapColor.GOLD)
                    .strength(2.0F).sound(SoundType.METAL).lightLevel(s -> 5));
    /** 屏风 / Screen */
    public static final RegistryObject<Block> SCREEN =
            simple("screen", BlockBehaviour.Properties.of().mapColor(MapColor.WOOD)
                    .strength(1.5F).sound(SoundType.WOOD));
    /** 匾额 / Plaque */
    public static final RegistryObject<Block> PLAQUE =
            simple("plaque", BlockBehaviour.Properties.of().mapColor(MapColor.WOOD)
                    .strength(1.5F).sound(SoundType.WOOD));
}
