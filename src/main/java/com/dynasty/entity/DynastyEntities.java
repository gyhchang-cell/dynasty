package com.dynasty.entity;

import com.dynasty.Dynasty;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 实体注册 / Dynasty entity registry.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class DynastyEntities {

    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Dynasty.MODID);

    /** 兵马俑战士 / Terracotta Warrior */
    public static final RegistryObject<EntityType<TerracottaWarrior>> TERRACOTTA_WARRIOR =
            ENTITIES.register("terracotta_warrior", () -> EntityType.Builder
                    .of(TerracottaWarrior::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.95F).clientTrackingRange(8).build("terracotta_warrior"));

    /** 帝国士兵（友方）/ Imperial Soldier (friendly) */
    public static final RegistryObject<EntityType<ImperialSoldier>> IMPERIAL_SOLDIER =
            ENTITIES.register("imperial_soldier", () -> EntityType.Builder
                    .of(ImperialSoldier::new, MobCategory.CREATURE)
                    .sized(0.6F, 1.95F).clientTrackingRange(8).build("imperial_soldier"));

    /** 亡故始皇（Boss）/ Undead First Emperor (boss) */
    public static final RegistryObject<EntityType<UndeadFirstEmperor>> UNDEAD_FIRST_EMPEROR =
            ENTITIES.register("undead_first_emperor", () -> EntityType.Builder
                    .of(UndeadFirstEmperor::new, MobCategory.MONSTER)
                    .sized(0.7F, 2.3F).clientTrackingRange(12).fireImmune()
                    .build("undead_first_emperor"));

    // ---- 新生物 / additional mobs ----
    public static final RegistryObject<EntityType<DynastyMobs.Minister>> MINISTER =
            ENTITIES.register("minister", () -> EntityType.Builder
                    .of(DynastyMobs.Minister::new, MobCategory.CREATURE)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("minister"));

    public static final RegistryObject<EntityType<DynastyMobs.Assassin>> ASSASSIN =
            ENTITIES.register("assassin", () -> EntityType.Builder
                    .of(DynastyMobs.Assassin::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("assassin"));

    public static final RegistryObject<EntityType<DynastyMobs.Archer>> ARCHER =
            ENTITIES.register("archer", () -> EntityType.Builder
                    .of(DynastyMobs.Archer::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("archer"));

    public static final RegistryObject<EntityType<DynastyMobs.RoyalGuard>> ROYAL_GUARD =
            ENTITIES.register("royal_guard", () -> EntityType.Builder
                    .of(DynastyMobs.RoyalGuard::new, MobCategory.MONSTER)
                    .sized(0.65F, 2.0F).clientTrackingRange(10).build("royal_guard"));

    public static final RegistryObject<EntityType<DynastyMobs.RebelSoldier>> REBEL_SOLDIER =
            ENTITIES.register("rebel_soldier", () -> EntityType.Builder
                    .of(DynastyMobs.RebelSoldier::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("rebel_soldier"));

    public static final RegistryObject<EntityType<DynastyMobs.NianBeast>> NIAN_BEAST =
            ENTITIES.register("nian_beast", () -> EntityType.Builder
                    .of(DynastyMobs.NianBeast::new, MobCategory.MONSTER)
                    .sized(0.9F, 2.4F).clientTrackingRange(12).fireImmune().build("nian_beast"));

    // ---- 神兽 / mythical beasts ----
    public static final RegistryObject<EntityType<DynastyBeasts.Qilin>> QILIN =
            ENTITIES.register("qilin", () -> EntityType.Builder
                    .of(DynastyBeasts.Qilin::new, MobCategory.CREATURE)
                    .sized(1.3F, 1.4F).clientTrackingRange(10).build("qilin"));

    public static final RegistryObject<EntityType<DynastyBeasts.Phoenix>> PHOENIX =
            ENTITIES.register("phoenix", () -> EntityType.Builder
                    .of(DynastyBeasts.Phoenix::new, MobCategory.MONSTER)
                    .sized(1.0F, 1.0F).clientTrackingRange(12).fireImmune().build("phoenix"));

    public static final RegistryObject<EntityType<DynastyBeasts.NineTailedFox>> NINE_TAILED_FOX =
            ENTITIES.register("nine_tailed_fox", () -> EntityType.Builder
                    .of(DynastyBeasts.NineTailedFox::new, MobCategory.MONSTER)
                    .sized(0.8F, 0.9F).clientTrackingRange(10).build("nine_tailed_fox"));

    // ---- Boss ----
    public static final RegistryObject<EntityType<DynastyBosses.DragonEmperor>> DRAGON_EMPEROR =
            ENTITIES.register("dragon_emperor", () -> EntityType.Builder
                    .of(DynastyBosses.DragonEmperor::new, MobCategory.MONSTER)
                    .sized(0.8F, 2.6F).clientTrackingRange(16).fireImmune().build("dragon_emperor"));

    public static final RegistryObject<EntityType<DynastyBosses.RebelGeneral>> REBEL_GENERAL =
            ENTITIES.register("rebel_general", () -> EntityType.Builder
                    .of(DynastyBosses.RebelGeneral::new, MobCategory.MONSTER)
                    .sized(0.7F, 2.2F).clientTrackingRange(14).build("rebel_general"));

    public static final RegistryObject<EntityType<DynastyBosses.EunuchMastermind>> EUNUCH_MASTERMIND =
            ENTITIES.register("eunuch_mastermind", () -> EntityType.Builder
                    .of(DynastyBosses.EunuchMastermind::new, MobCategory.MONSTER)
                    .sized(0.7F, 2.1F).clientTrackingRange(14).build("eunuch_mastermind"));

    /** 九霄天将 / the Nine-Heaven General */
    public static final RegistryObject<EntityType<DynastyBosses.NineHeavenGeneral>> NINE_HEAVEN_GENERAL =
            ENTITIES.register("nine_heaven_general", () -> EntityType.Builder
                    .of(DynastyBosses.NineHeavenGeneral::new, MobCategory.MONSTER)
                    .sized(0.7F, 2.3F).clientTrackingRange(16).build("nine_heaven_general"));

    /** 东海龙王 / the Dragon King of the East Sea */
    public static final RegistryObject<EntityType<DynastyBosses.DragonKing>> DRAGON_KING =
            ENTITIES.register("dragon_king", () -> EntityType.Builder
                    .of(DynastyBosses.DragonKing::new, MobCategory.MONSTER)
                    .sized(1.2F, 2.8F).clientTrackingRange(16).build("dragon_king"));

    /** 玉甲卫 / Jade Guard */
    public static final RegistryObject<EntityType<DynastyRealmMobs.JadeGuard>> JADE_GUARD =
            ENTITIES.register("jade_guard", () -> EntityType.Builder
                    .of(DynastyRealmMobs.JadeGuard::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("jade_guard"));

    /** 冥卒 / Soul Soldier */
    public static final RegistryObject<EntityType<DynastyRealmMobs.SoulSoldier>> SOUL_SOLDIER =
            ENTITIES.register("soul_soldier", () -> EntityType.Builder
                    .of(DynastyRealmMobs.SoulSoldier::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("soul_soldier"));

    /** 雷使 / Thunder Envoy */
    public static final RegistryObject<EntityType<DynastyRealmMobs.ThunderEnvoy>> THUNDER_ENVOY =
            ENTITIES.register("thunder_envoy", () -> EntityType.Builder
                    .of(DynastyRealmMobs.ThunderEnvoy::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("thunder_envoy"));

    /** 鲛人 / Merfolk */
    public static final RegistryObject<EntityType<DynastyRealmMobs.Merfolk>> MERFOLK =
            ENTITIES.register("merfolk", () -> EntityType.Builder
                    .of(DynastyRealmMobs.Merfolk::new, MobCategory.MONSTER)
                    .sized(0.6F, 1.9F).clientTrackingRange(10).build("merfolk"));

    @SubscribeEvent
    public static void onEntityAttributeCreation(EntityAttributeCreationEvent event) {
        event.put(TERRACOTTA_WARRIOR.get(), TerracottaWarrior.createAttributes().build());
        event.put(IMPERIAL_SOLDIER.get(), ImperialSoldier.createAttributes().build());
        event.put(UNDEAD_FIRST_EMPEROR.get(), UndeadFirstEmperor.createAttributes().build());
        event.put(MINISTER.get(), DynastyMobs.Minister.createAttributes().build());
        event.put(ASSASSIN.get(), DynastyMobs.Assassin.createAttributes().build());
        event.put(ARCHER.get(), DynastyMobs.Archer.createAttributes().build());
        event.put(ROYAL_GUARD.get(), DynastyMobs.RoyalGuard.createAttributes().build());
        event.put(REBEL_SOLDIER.get(), DynastyMobs.RebelSoldier.createAttributes().build());
        event.put(NIAN_BEAST.get(), DynastyMobs.NianBeast.createAttributes().build());
        event.put(QILIN.get(), DynastyBeasts.Qilin.createAttributes().build());
        event.put(PHOENIX.get(), DynastyBeasts.Phoenix.createAttributes().build());
        event.put(NINE_TAILED_FOX.get(), DynastyBeasts.NineTailedFox.createAttributes().build());
        event.put(DRAGON_EMPEROR.get(), DynastyBosses.DragonEmperor.createAttributes().build());
        event.put(REBEL_GENERAL.get(), DynastyBosses.RebelGeneral.createAttributes().build());
        event.put(EUNUCH_MASTERMIND.get(), DynastyBosses.EunuchMastermind.createAttributes().build());
        event.put(NINE_HEAVEN_GENERAL.get(), DynastyBosses.NineHeavenGeneral.createAttributes().build());
        event.put(DRAGON_KING.get(), DynastyBosses.DragonKing.createAttributes().build());
        event.put(JADE_GUARD.get(), DynastyRealmMobs.JadeGuard.createAttributes().build());
        event.put(SOUL_SOLDIER.get(), DynastyRealmMobs.SoulSoldier.createAttributes().build());
        event.put(THUNDER_ENVOY.get(), DynastyRealmMobs.ThunderEnvoy.createAttributes().build());
        event.put(MERFOLK.get(), DynastyRealmMobs.Merfolk.createAttributes().build());
    }
}
