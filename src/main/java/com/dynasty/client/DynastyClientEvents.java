package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.entity.DynastyEntities;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Dynasty 客户端注册：模型层 + 实体渲染器。
 * Dynasty client registration: model layers + entity renderers.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
@SuppressWarnings({"null", "removal"})
public class DynastyClientEvents {

    /** 与原版弓相同的拉弓属性：仅为后羿弓注册，贴图按蓄力阶段切换。 */
    @SubscribeEvent
    public static void onClientSetup(net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            net.minecraft.world.item.Item bow = com.dynasty.DynastyWeapons.HOUYI_BOW.get();
            net.minecraft.client.renderer.item.ItemProperties.register(
                    bow, new ResourceLocation(Dynasty.MODID, "pulling"),
                    (stack, level, living, seed) ->
                            living != null && living.isUsingItem() && living.getUseItem() == stack ? 1.0F : 0.0F);
            net.minecraft.client.renderer.item.ItemProperties.register(
                    bow, new ResourceLocation(Dynasty.MODID, "pull"),
                    (stack, level, living, seed) ->
                            living != null && living.getUseItem() == stack
                                    ? Math.min(1.0F, (stack.getUseDuration() - living.getUseItemRemainingTicks()) / 20.0F)
                                    : 0.0F);
        });
    }

    private static ModelLayerLocation layer(String name) {
        return new ModelLayerLocation(new ResourceLocation(Dynasty.MODID, name), "main");
    }

    public static final ModelLayerLocation WARRIOR_LAYER = layer("terracotta_warrior");
    public static final ModelLayerLocation SOLDIER_LAYER = layer("imperial_soldier");
    public static final ModelLayerLocation EMPEROR_LAYER = layer("undead_first_emperor");
    public static final ModelLayerLocation MINISTER_LAYER = layer("minister");
    public static final ModelLayerLocation ASSASSIN_LAYER = layer("assassin");
    public static final ModelLayerLocation ARCHER_LAYER = layer("archer");
    public static final ModelLayerLocation ROYAL_GUARD_LAYER = layer("royal_guard");
    public static final ModelLayerLocation REBEL_SOLDIER_LAYER = layer("rebel_soldier");
    public static final ModelLayerLocation NIAN_BEAST_LAYER = layer("nian_beast");
    public static final ModelLayerLocation DRAGON_EMPEROR_LAYER = layer("dragon_emperor");
    public static final ModelLayerLocation REBEL_GENERAL_LAYER = layer("rebel_general");
    public static final ModelLayerLocation EUNUCH_MASTERMIND_LAYER = layer("eunuch_mastermind");
    public static final ModelLayerLocation QILIN_LAYER = layer("qilin");
    public static final ModelLayerLocation NINE_TAILED_FOX_LAYER = layer("nine_tailed_fox");
    public static final ModelLayerLocation NINE_HEAVEN_GENERAL_LAYER = layer("nine_heaven_general");
    public static final ModelLayerLocation DRAGON_KING_LAYER = layer("dragon_king");
    public static final ModelLayerLocation JADE_GUARD_LAYER = layer("jade_guard");
    public static final ModelLayerLocation SOUL_SOLDIER_LAYER = layer("soul_soldier");
    public static final ModelLayerLocation THUNDER_ENVOY_LAYER = layer("thunder_envoy");
    public static final ModelLayerLocation MERFOLK_LAYER = layer("merfolk");
    public static final ModelLayerLocation PHOENIX_LAYER = layer("phoenix");

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Dynasty.MODID, "textures/entity/" + name + ".png");
    }

    private static final ResourceLocation TEX_WARRIOR = tex("terracotta_warrior");
    private static final ResourceLocation TEX_SOLDIER = tex("imperial_soldier");
    private static final ResourceLocation TEX_EMPEROR = tex("undead_first_emperor");
    private static final ResourceLocation TEX_MINISTER = tex("minister");
    private static final ResourceLocation TEX_ASSASSIN = tex("assassin");
    private static final ResourceLocation TEX_ARCHER = tex("archer");
    private static final ResourceLocation TEX_ROYAL_GUARD = tex("royal_guard");
    private static final ResourceLocation TEX_REBEL_SOLDIER = tex("rebel_soldier");
    private static final ResourceLocation TEX_NIAN_BEAST = tex("nian_beast");
    private static final ResourceLocation TEX_DRAGON_EMPEROR = tex("dragon_emperor");
    private static final ResourceLocation TEX_REBEL_GENERAL = tex("rebel_general");
    private static final ResourceLocation TEX_EUNUCH_MASTERMIND = tex("eunuch_mastermind");
    private static final ResourceLocation TEX_QILIN = tex("qilin");
    private static final ResourceLocation TEX_NINE_TAILED_FOX = tex("nine_tailed_fox");
    private static final ResourceLocation TEX_NINE_HEAVEN_GENERAL = tex("nine_heaven_general");
    private static final ResourceLocation TEX_DRAGON_KING = tex("dragon_king");
    private static final ResourceLocation TEX_JADE_GUARD = tex("jade_guard");
    private static final ResourceLocation TEX_SOUL_SOLDIER = tex("soul_soldier");
    private static final ResourceLocation TEX_THUNDER_ENVOY = tex("thunder_envoy");
    private static final ResourceLocation TEX_MERFOLK = tex("merfolk");
    private static final ResourceLocation TEX_PHOENIX = tex("phoenix");

    @SubscribeEvent
    public static void onRegisterLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(WARRIOR_LAYER, DynastyHumanoidModel::createBodyLayer);
        event.registerLayerDefinition(SOLDIER_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.0F));
        event.registerLayerDefinition(EMPEROR_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.25F));
        event.registerLayerDefinition(MINISTER_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.0F));
        event.registerLayerDefinition(ASSASSIN_LAYER, () -> DynastyHumanoidModel.createBodyLayer(-0.05F));
        event.registerLayerDefinition(ARCHER_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.0F));
        event.registerLayerDefinition(ROYAL_GUARD_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.1F));
        event.registerLayerDefinition(REBEL_SOLDIER_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.0F));
        event.registerLayerDefinition(NIAN_BEAST_LAYER,
                () -> DetailedBeastModel.createLayer(DetailedBeastModel.Kind.NIAN));
        event.registerLayerDefinition(DRAGON_EMPEROR_LAYER, () -> DynastyHumanoidModel.decoratedLayer(1));
        event.registerLayerDefinition(REBEL_GENERAL_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.25F));
        event.registerLayerDefinition(EUNUCH_MASTERMIND_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.2F));
        event.registerLayerDefinition(NINE_HEAVEN_GENERAL_LAYER, () -> DynastyHumanoidModel.decoratedLayer(2));
        event.registerLayerDefinition(DRAGON_KING_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.3F));
        event.registerLayerDefinition(JADE_GUARD_LAYER, () -> DynastyHumanoidModel.decoratedLayer(3));
        event.registerLayerDefinition(SOUL_SOLDIER_LAYER, () -> DynastyHumanoidModel.decoratedLayer(4));
        event.registerLayerDefinition(THUNDER_ENVOY_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.0F));
        event.registerLayerDefinition(MERFOLK_LAYER, () -> DynastyHumanoidModel.createBodyLayer(0.0F));
        event.registerLayerDefinition(QILIN_LAYER,
                () -> DetailedBeastModel.createLayer(DetailedBeastModel.Kind.QILIN));
        event.registerLayerDefinition(NINE_TAILED_FOX_LAYER,
                () -> DetailedBeastModel.createLayer(DetailedBeastModel.Kind.FOX));
        event.registerLayerDefinition(PHOENIX_LAYER,
                () -> DetailedBeastModel.createLayer(DetailedBeastModel.Kind.PHOENIX));
    }

    @SubscribeEvent
    public static void onAddLayers(EntityRenderersEvent.AddLayers event) {
        // 所有模型层注册完成后统一烘焙一次：模型定义有误会立刻暴露，而不是等实体出现才崩
        // Bake every layer once, after all layer definitions are registered.
        net.minecraft.client.model.geom.EntityModelSet modelSet = event.getEntityModels();
        ModelLayerLocation[] layers = {
                WARRIOR_LAYER, SOLDIER_LAYER, EMPEROR_LAYER, MINISTER_LAYER, ASSASSIN_LAYER, ARCHER_LAYER,
                ROYAL_GUARD_LAYER, REBEL_SOLDIER_LAYER, NIAN_BEAST_LAYER, DRAGON_EMPEROR_LAYER,
                REBEL_GENERAL_LAYER, EUNUCH_MASTERMIND_LAYER, QILIN_LAYER, NINE_TAILED_FOX_LAYER,
                PHOENIX_LAYER,
                NINE_HEAVEN_GENERAL_LAYER,
                DRAGON_KING_LAYER,
                JADE_GUARD_LAYER,
                SOUL_SOLDIER_LAYER,
                THUNDER_ENVOY_LAYER,
                MERFOLK_LAYER,
        };
        for (ModelLayerLocation layer : layers) {
            modelSet.bakeLayer(layer);
        }
        com.dynasty.Dynasty.LOGGER.info("[Dynasty] baked {} entity model layers", layers.length);
    }

    @SubscribeEvent
    public static void onItemColors(net.minecraftforge.client.event.RegisterColorHandlersEvent.Item event) {
        event.register((stack, tintIndex) -> tintIndex == 0
                        ? net.minecraft.world.item.alchemy.PotionUtils.getColor(stack) : -1,
                com.dynasty.DynastyItems.DYNASTY_POTION.get(),
                com.dynasty.DynastyItems.DYNASTY_SPLASH_POTION.get(),
                com.dynasty.DynastyItems.DYNASTY_LINGERING_POTION.get());
        // 刷怪蛋染色 / spawn egg tinting
        // 注意：必须延迟到注册完成后才取 RegistryObject，否则会在类初始化阶段崩溃
        // NOTE: resolve the RegistryObjects lazily, never in a static initializer.
        event.register((stack, tintIndex) -> stack.getItem() instanceof net.minecraftforge.common.ForgeSpawnEggItem egg
                        ? egg.getColor(tintIndex) : -1,
                spawnEggs());
    }

    /** 全部刷怪蛋 / all Dynasty spawn eggs（注册完成后再调用） */
    private static net.minecraft.world.item.Item[] spawnEggs() {
        return new net.minecraft.world.item.Item[]{
                com.dynasty.DynastyItems.JADE_GUARD_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.SOUL_SOLDIER_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.THUNDER_ENVOY_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.MERFOLK_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.TERRACOTTA_WARRIOR_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.IMPERIAL_SOLDIER_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.UNDEAD_FIRST_EMPEROR_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.MINISTER_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.ASSASSIN_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.ARCHER_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.ROYAL_GUARD_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.REBEL_SOLDIER_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.NIAN_BEAST_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.QILIN_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.PHOENIX_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.NINE_TAILED_FOX_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.DRAGON_EMPEROR_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.REBEL_GENERAL_SPAWN_EGG.get(),
                com.dynasty.DynastyItems.EUNUCH_MASTERMIND_SPAWN_EGG.get(),
        };
    }

    @SubscribeEvent
    public static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(DynastyEntities.TERRACOTTA_WARRIOR.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, WARRIOR_LAYER, TEX_WARRIOR, 0.5F));
        event.registerEntityRenderer(DynastyEntities.IMPERIAL_SOLDIER.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, SOLDIER_LAYER, TEX_SOLDIER, 0.5F));
        event.registerEntityRenderer(DynastyEntities.UNDEAD_FIRST_EMPEROR.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, EMPEROR_LAYER, TEX_EMPEROR, 0.7F));
        event.registerEntityRenderer(DynastyEntities.MINISTER.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, MINISTER_LAYER, TEX_MINISTER, 0.5F));
        event.registerEntityRenderer(DynastyEntities.ASSASSIN.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, ASSASSIN_LAYER, TEX_ASSASSIN, 0.5F));
        event.registerEntityRenderer(DynastyEntities.ARCHER.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, ARCHER_LAYER, TEX_ARCHER, 0.5F));
        event.registerEntityRenderer(DynastyEntities.ROYAL_GUARD.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, ROYAL_GUARD_LAYER, TEX_ROYAL_GUARD, 0.5F));
        event.registerEntityRenderer(DynastyEntities.REBEL_SOLDIER.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, REBEL_SOLDIER_LAYER, TEX_REBEL_SOLDIER, 0.5F));
        event.registerEntityRenderer(DynastyEntities.NIAN_BEAST.get(),
                ctx -> new DynastyDetailedBeastRenderer<>(ctx, NIAN_BEAST_LAYER, TEX_NIAN_BEAST, 0.9F,
                        DetailedBeastModel.Kind.NIAN));
        event.registerEntityRenderer(DynastyEntities.DRAGON_EMPEROR.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, DRAGON_EMPEROR_LAYER, TEX_DRAGON_EMPEROR, 0.9F,1));
        event.registerEntityRenderer(DynastyEntities.REBEL_GENERAL.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, REBEL_GENERAL_LAYER, TEX_REBEL_GENERAL, 0.7F));
        event.registerEntityRenderer(DynastyEntities.EUNUCH_MASTERMIND.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, EUNUCH_MASTERMIND_LAYER, TEX_EUNUCH_MASTERMIND, 0.7F));
        event.registerEntityRenderer(DynastyEntities.QILIN.get(),
                ctx -> new DynastyDetailedBeastRenderer<>(ctx, QILIN_LAYER, TEX_QILIN, 0.9F,
                        DetailedBeastModel.Kind.QILIN));
        event.registerEntityRenderer(DynastyEntities.NINE_TAILED_FOX.get(),
                ctx -> new DynastyDetailedBeastRenderer<>(ctx, NINE_TAILED_FOX_LAYER, TEX_NINE_TAILED_FOX, 0.7F,
                        DetailedBeastModel.Kind.FOX));
        event.registerEntityRenderer(DynastyEntities.PHOENIX.get(),
                ctx -> new DynastyDetailedBeastRenderer<>(ctx, PHOENIX_LAYER, TEX_PHOENIX, 0.7F,
                        DetailedBeastModel.Kind.PHOENIX));
        event.registerEntityRenderer(DynastyEntities.JADE_GUARD.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, JADE_GUARD_LAYER, TEX_JADE_GUARD, 0.5F,3));
        event.registerEntityRenderer(DynastyEntities.SOUL_SOLDIER.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, SOUL_SOLDIER_LAYER, TEX_SOUL_SOLDIER, 0.5F,4));
        event.registerEntityRenderer(DynastyEntities.THUNDER_ENVOY.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, THUNDER_ENVOY_LAYER, TEX_THUNDER_ENVOY, 0.5F));
        event.registerEntityRenderer(DynastyEntities.MERFOLK.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, MERFOLK_LAYER, TEX_MERFOLK, 0.5F));
        event.registerEntityRenderer(DynastyEntities.NINE_HEAVEN_GENERAL.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, NINE_HEAVEN_GENERAL_LAYER, TEX_NINE_HEAVEN_GENERAL, 0.9F,2));
        event.registerEntityRenderer(DynastyEntities.DRAGON_KING.get(),
                ctx -> new DynastyHumanoidRenderer<>(ctx, DRAGON_KING_LAYER, TEX_DRAGON_KING, 0.9F));
    }

    /** 精细化神兽渲染器（麒麟 / 九尾狐 / 凤凰）/ renderer for the detailed beast models */
    private static class DynastyDetailedBeastRenderer<T extends Mob>
            extends net.minecraft.client.renderer.entity.MobRenderer<T, DetailedBeastModel<T>> {

        private final ResourceLocation texture;

        DynastyDetailedBeastRenderer(EntityRendererProvider.Context ctx, ModelLayerLocation layer,
                                     ResourceLocation texture, float shadow, DetailedBeastModel.Kind kind) {
            super(ctx, new DetailedBeastModel<>(ctx.bakeLayer(layer), kind), shadow);
            this.texture = texture;
        }

        @Override
        public ResourceLocation getTextureLocation(T entity) {
            return this.texture;
        }
    }

    /** 四足神兽渲染器 / renderer for quadruped beasts */
    private static class DynastyBeastRenderer<T extends Mob> extends net.minecraft.client.renderer.entity.MobRenderer<T, DynastyBeastModel<T>> {

        private final ResourceLocation texture;

        DynastyBeastRenderer(EntityRendererProvider.Context ctx, ModelLayerLocation layer,
                             ResourceLocation texture, float shadow) {
            super(ctx, new DynastyBeastModel<>(ctx.bakeLayer(layer)), shadow);
            this.texture = texture;
        }

        @Override
        public ResourceLocation getTextureLocation(T entity) {
            return this.texture;
        }
    }

    /** 飞行神兽渲染器 / renderer for winged beasts */
    private static class DynastyWingedRenderer<T extends Mob> extends net.minecraft.client.renderer.entity.MobRenderer<T, DynastyWingedModel<T>> {

        private final ResourceLocation texture;

        DynastyWingedRenderer(EntityRendererProvider.Context ctx, ModelLayerLocation layer,
                              ResourceLocation texture, float shadow) {
            super(ctx, new DynastyWingedModel<>(ctx.bakeLayer(layer)), shadow);
            this.texture = texture;
        }

        @Override
        public ResourceLocation getTextureLocation(T entity) {
            return this.texture;
        }
    }

    /** 通用人形渲染器 / generic humanoid renderer for Dynasty mobs */
    private static class DynastyHumanoidRenderer<T extends Mob> extends HumanoidMobRenderer<T, DynastyHumanoidModel<T>> {

        private final ResourceLocation texture;
        private final float visualScale;

        DynastyHumanoidRenderer(EntityRendererProvider.Context ctx, ModelLayerLocation layer,
                                ResourceLocation texture, float shadow) {
            this(ctx,layer,texture,shadow,0);
        }
        DynastyHumanoidRenderer(EntityRendererProvider.Context ctx,ModelLayerLocation layer,
                                ResourceLocation texture,float shadow,int style) {
            super(ctx, new DynastyHumanoidModel<>(ctx.bakeLayer(layer)), shadow);
            this.texture = texture;
            this.visualScale=switch(style){case 1->1.35F;case 2->1.28F;case 3->1.08F;case 4->1.05F;default->1F;};
            if(style>0)addLayer(new DynastyAuraLayer<>(this,style));
        }

        @Override protected void scale(T entity,com.mojang.blaze3d.vertex.PoseStack pose,float partial) {
            pose.scale(visualScale,visualScale,visualScale);
        }

        @Override
        public ResourceLocation getTextureLocation(T entity) {
            return this.texture;
        }
    }
}
