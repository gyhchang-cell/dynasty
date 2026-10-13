package com.dynasty.blueprint.artifact;
import com.dynasty.Dynasty;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;

public final class ArtifactContent {
    public static final String ID="longyin_zhanma_duanyue_dao";
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<Item> LONGYIN=ITEMS.register(ID,()->new ArtifactItem(Tiers.NETHERITE,8,-3.2F,new LongyinAbility(),new Item.Properties().stacksTo(1).durability(2031).fireResistant().rarity(Rarity.EPIC)));
    public static final String ZHANLU_ID="zhanlu_rendao_bamian_jian";
    public static final RegistryObject<Item> ZHANLU=ITEMS.register(ZHANLU_ID,()->new ArtifactItem(Tiers.NETHERITE,5,-2.9F,new ZhanluAbility(),new Item.Properties().stacksTo(1).durability(2031).fireResistant().rarity(Rarity.EPIC)));
    public static final RegistryObject<EntityType<ZhanluField>> ZHANLU_FIELD=ENTITIES.register("zhanlu_ceasefire_field",()->EntityType.Builder.<ZhanluField>of(ZhanluField::new,MobCategory.MISC).sized(10F,.25F).clientTrackingRange(8).updateInterval(2).build("zhanlu_ceasefire_field"));
    public static final RegistryObject<EntityType<ArtifactWave>> WAVE=ENTITIES.register("longyin_finite_ground_wave",()->EntityType.Builder.<ArtifactWave>of(ArtifactWave::new,MobCategory.MISC).sized(1.6F,.75F).clientTrackingRange(8).updateInterval(1).build("longyin_finite_ground_wave"));
    public static final RegistryObject<EntityType<MarshalBladeMemorial>> MEMORIAL=ENTITIES.register("marshal_blade_memorial",()->EntityType.Builder.<MarshalBladeMemorial>of(MarshalBladeMemorial::new,MobCategory.MISC).sized(.5F,3F).clientTrackingRange(8).updateInterval(10).build("marshal_blade_memorial"));
    public static void register(IEventBus bus){ITEMS.register(bus);ENTITIES.register(bus);TaiqingContent.register(bus);}
    private ArtifactContent(){}
}
