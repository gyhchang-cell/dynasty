package com.dynasty.blueprint.boss;
import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;

/** Separate catalog Boss1 registry; existing final sovereign and earlier bosses are untouched. */
public final class CauldronPitContent {
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<MobEffect> EFFECTS=DeferredRegister.create(ForgeRegistries.MOB_EFFECTS,Dynasty.MODID);
    public static final DeferredRegister<StructureType<?>> STRUCTURES=DeferredRegister.create(Registries.STRUCTURE_TYPE,Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,Dynasty.MODID);
    public static final RegistryObject<EntityType<TaoyanCauldron>> CAULDRON=ENTITIES.register(TaoyanCauldron.ID,()->EntityType.Builder.<TaoyanCauldron>of(TaoyanCauldron::new,MobCategory.MONSTER).sized(4.8F,4.5F).fireImmune().clientTrackingRange(14).updateInterval(1).build(TaoyanCauldron.ID));
    public static final RegistryObject<EntityType<CauldronGroundSpell>> OIL_POOL=ENTITIES.register(CauldronGroundSpell.OIL_ID,()->EntityType.Builder.<CauldronGroundSpell>of(CauldronGroundSpell::new,MobCategory.MISC).sized(.1F,.1F).fireImmune().clientTrackingRange(12).updateInterval(2).build(CauldronGroundSpell.OIL_ID));
    public static final RegistryObject<EntityType<CauldronGroundSpell>> FIRE_CRACK=ENTITIES.register(CauldronGroundSpell.CRACK_ID,()->EntityType.Builder.<CauldronGroundSpell>of(CauldronGroundSpell::new,MobCategory.MISC).sized(.1F,.1F).fireImmune().clientTrackingRange(12).updateInterval(2).build(CauldronGroundSpell.CRACK_ID));
    public static final RegistryObject<Item> EGG=ITEMS.register(TaoyanCauldron.ID+"_spawn_egg",()->new ForgeSpawnEggItem(CAULDRON,0x293331,0x8C6B45,new Item.Properties()));
    public static final RegistryObject<Item> EAR=ITEMS.register("taoyan_bronze_cauldron_ear",()->new Item(new Item.Properties()));
    public static final RegistryObject<Item> STAKE=ITEMS.register("taoyan_quenched_siege_stake",()->new Item(new Item.Properties()));
    public static final RegistryObject<Item> CRYSTAL=ITEMS.register("taoyan_army_soul_crystal",()->new Item(new Item.Properties()));
    public static final RegistryObject<MobEffect> BLEED=EFFECTS.register("taoyan_bone_bleeding",()->new MobEffect(MobEffectCategory.HARMFUL,0x293331){
        @Override public boolean isDurationEffectTick(int ticks,int amp){return ticks%20==0;}
        @Override public void applyEffectTick(LivingEntity e,int amp){if(!e.level().isClientSide&&e.isAlive()&&!(e instanceof net.minecraft.world.entity.player.Player p&&p.isCreative()))e.hurt(e.damageSources().magic(),1);}
    });
    public static final RegistryObject<Block> SOUL_OIL=BLOCKS.register("cauldron_abyss_oil",()->new Block(BlockBehaviour.Properties.of().strength(-1,3600000).noCollission().noOcclusion()){
        @Override public void entityInside(net.minecraft.world.level.block.state.BlockState state,net.minecraft.world.level.Level level,net.minecraft.core.BlockPos pos,Entity e){if(!level.isClientSide&&!e.fireImmune()&&!e.isSpectator()&&!(e instanceof net.minecraft.world.entity.player.Player p&&p.isCreative())&&e.tickCount%20==0&&e.hurt(level.damageSources().lava(),8))e.setSecondsOnFire(3);}
    });
    public static final RegistryObject<Block> RITUAL=BLOCKS.register("cauldron_bone_ritual",()->new Block(BlockBehaviour.Properties.of().strength(-1,3600000)));
    public static final RegistryObject<Item> RITUAL_ITEM=ITEMS.register("cauldron_bone_ritual",()->new BlockItem(RITUAL.get(),new Item.Properties()));
    public static final RegistryObject<StructureType<CauldronPitStructure>> PIT_TYPE=STRUCTURES.register("cauldron_pit",()->()->CauldronPitStructure.CODEC);
    public static final RegistryObject<StructurePieceType> PIT_PIECE=PIECES.register("cauldron_pit",()->CauldronPitPiece::new);
    public static void register(IEventBus bus){ENTITIES.register(bus);ITEMS.register(bus);BLOCKS.register(bus);EFFECTS.register(bus);STRUCTURES.register(bus);PIECES.register(bus);bus.addListener(CauldronPitContent::attributes);}
    private static void attributes(EntityAttributeCreationEvent e){e.put(CAULDRON.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,2400).add(Attributes.ATTACK_DAMAGE,18).add(Attributes.ARMOR,18).add(Attributes.MOVEMENT_SPEED,.18).add(Attributes.KNOCKBACK_RESISTANCE,1).add(Attributes.FOLLOW_RANGE,40).build());}
    private CauldronPitContent(){}
}
