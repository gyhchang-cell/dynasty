package com.dynasty.ritual;

import com.dynasty.Dynasty;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** Dedicated ritual nodes; deliberately independent of the older single-token ritual altar. */
public final class ZhenyuanRitualContent {
    private ZhenyuanRitualContent() {}
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);
    public static final DeferredRegister<BlockEntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, Dynasty.MODID);
    public static final RegistryObject<ZhenyuanNodeBlock> NODE = BLOCKS.register("zhenyuan_node", () -> new ZhenyuanNodeBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.DEEPSLATE).sound(SoundType.DEEPSLATE)
                    .strength(-1F, 3600000F).pushReaction(PushReaction.BLOCK).noLootTable().noOcclusion()
                    .lightLevel(s -> s.getValue(ZhenyuanNodeBlock.ACTIVE) ? 10 : 3)));
    public static final RegistryObject<Item> NODE_ITEM = ITEMS.register("zhenyuan_node", () -> new BlockItem(NODE.get(), new Item.Properties()));
    public static final RegistryObject<Item> TIANMING_JADE = ITEMS.register("tianming_jade", () -> new Item(new Item.Properties().stacksTo(16).rarity(net.minecraft.world.item.Rarity.EPIC)));
    public static final RegistryObject<BlockEntityType<ZhenyuanNodeBlockEntity>> NODE_ENTITY = ENTITIES.register("zhenyuan_node",
            () -> BlockEntityType.Builder.of(ZhenyuanNodeBlockEntity::new, NODE.get()).build(null));

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        ENTITIES.register(bus);
    }
}
