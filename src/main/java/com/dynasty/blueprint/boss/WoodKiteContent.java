package com.dynasty.blueprint.boss;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;

/** Catalog Boss3 is a separate mechanical bird; the formal final sovereign is untouched. */
public final class WoodKiteContent {
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<StructureType<?>> STRUCTURES=DeferredRegister.create(Registries.STRUCTURE_TYPE,Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,Dynasty.MODID);
    public static final RegistryObject<EntityType<WoodKite>> KITE=ENTITIES.register(WoodKite.ID,()->EntityType.Builder.<WoodKite>of(WoodKite::new,MobCategory.MONSTER).sized(3.75F,3F).fireImmune().clientTrackingRange(12).updateInterval(1).build(WoodKite.ID));
    public static final RegistryObject<EntityType<WoodKiteBomb>> BOMB=ENTITIES.register("wood_kite_thunder_bomb",()->EntityType.Builder.<WoodKiteBomb>of(WoodKiteBomb::new,MobCategory.MISC).sized(.65F,.7F).fireImmune().clientTrackingRange(10).updateInterval(1).build("wood_kite_thunder_bomb"));
    public static final RegistryObject<Block> PLANK=BLOCKS.register("stargazer_mortise_plank",()->new Block(BlockBehaviour.Properties.of().strength(3,6)));
    public static final RegistryObject<Block> CHARRED=BLOCKS.register("stargazer_charred_plank",()->new Block(BlockBehaviour.Properties.of().strength(1,3)));
    public static final RegistryObject<Block> SOCKET=BLOCKS.register("stargazer_core_socket",()->new Block(BlockBehaviour.Properties.of().strength(-1,3600000)));
    public static final RegistryObject<Block> ROPE=BLOCKS.register("stargazer_gear_rope",()->new Block(BlockBehaviour.Properties.of().strength(2,6).noCollission().noOcclusion()));
    public static final RegistryObject<Item> PLANK_ITEM=ITEMS.register("stargazer_mortise_plank",()->new BlockItem(PLANK.get(),new Item.Properties()));
    public static final RegistryObject<Item> CHARRED_ITEM=ITEMS.register("stargazer_charred_plank",()->new BlockItem(CHARRED.get(),new Item.Properties()));
    public static final RegistryObject<Item> SOCKET_ITEM=ITEMS.register("stargazer_core_socket",()->new BlockItem(SOCKET.get(),new Item.Properties()));
    public static final RegistryObject<Item> ROPE_ITEM=ITEMS.register("stargazer_gear_rope",()->new BlockItem(ROPE.get(),new Item.Properties()));
    public static final RegistryObject<Item> EGG=ITEMS.register(WoodKite.ID+"_spawn_egg",()->new ForgeSpawnEggItem(KITE,0x583E36,0x9B8354,new Item.Properties()));
    public static final RegistryObject<Item> CORE=ITEMS.register("stargazer_kite_core_mechanism",()->new Item(new Item.Properties().rarity(Rarity.RARE)){
        @Override public InteractionResultHolder<ItemStack> use(net.minecraft.world.level.Level w,net.minecraft.world.entity.player.Player p,InteractionHand hand){var actual=p.getItemInHand(hand);var other=p.getItemInHand(hand==InteractionHand.MAIN_HAND?InteractionHand.OFF_HAND:InteractionHand.MAIN_HAND);if(!other.isDamageableItem()||other.getDamageValue()==0||p.getCooldowns().isOnCooldown(this))return InteractionResultHolder.fail(actual);if(!w.isClientSide){other.setDamageValue(Math.max(0,other.getDamageValue()-180));if(!p.isCreative())actual.shrink(1);p.getCooldowns().addCooldown(this,20);}return InteractionResultHolder.sidedSuccess(actual,w.isClientSide);}
    });
    public static final RegistryObject<Item> FEATHER=ITEMS.register("stargazer_cinnabar_wood_feather",()->new Item(new Item.Properties()){
        @Override public InteractionResultHolder<ItemStack> use(net.minecraft.world.level.Level w,net.minecraft.world.entity.player.Player p,InteractionHand hand){var actual=p.getItemInHand(hand);if(p.getCooldowns().isOnCooldown(this))return InteractionResultHolder.fail(actual);if(!w.isClientSide){p.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOW_FALLING,120));p.getCooldowns().addCooldown(this,120);if(!p.isCreative())actual.shrink(1);}return InteractionResultHolder.sidedSuccess(actual,w.isClientSide);}
    });
    public static final RegistryObject<Item> PAGE=ITEMS.register("luban_clockwork_diagram_page",()->new Item(new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<StructureType<StargazerPlatformStructure>> PLATFORM_TYPE=STRUCTURES.register("stargazer_platform",()->()->StargazerPlatformStructure.CODEC);
    public static final RegistryObject<StructurePieceType> APPROACH_PIECE=PIECES.register("stargazer_approach",()->StargazerApproachPiece::new);
    public static final RegistryObject<StructurePieceType> PLATFORM_PIECE=PIECES.register("stargazer_platform",()->StargazerPlatformPiece::new);
    public static void register(IEventBus bus){ENTITIES.register(bus);ITEMS.register(bus);BLOCKS.register(bus);STRUCTURES.register(bus);PIECES.register(bus);bus.addListener(WoodKiteContent::attributes);}
    private static void attributes(EntityAttributeCreationEvent e){e.put(KITE.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,2800).add(Attributes.ATTACK_DAMAGE,20).add(Attributes.ARMOR,20).add(Attributes.MOVEMENT_SPEED,.22).add(Attributes.FLYING_SPEED,.4).add(Attributes.KNOCKBACK_RESISTANCE,1).add(Attributes.FOLLOW_RANGE,48).build());}
    private WoodKiteContent(){}
}
