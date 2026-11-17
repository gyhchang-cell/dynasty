package com.yellowbrossproductions.illageandspillage.events;

import com.yellowbrossproductions.illageandspillage.client.model.*;
import com.yellowbrossproductions.illageandspillage.client.render.*;
import com.yellowbrossproductions.illageandspillage.client.render.layer.HayArmorLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.WebbedLayer;
import com.yellowbrossproductions.illageandspillage.gui.overlay.JumpscareOverlay;
import com.yellowbrossproductions.illageandspillage.gui.overlay.WebbedOverlay;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.particle.ParticleRegisterer;
import com.yellowbrossproductions.illageandspillage.particle.custom.BloodParticles;
import com.yellowbrossproductions.illageandspillage.particle.custom.MutationDripParticles;
import com.yellowbrossproductions.illageandspillage.particle.custom.MutationParticles;
import com.yellowbrossproductions.illageandspillage.particle.custom.MutationParticles2;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod.EventBusSubscriber;
import net.minecraftforge.fml.common.Mod.EventBusSubscriber.Bus;

@OnlyIn(Dist.CLIENT)
@EventBusSubscriber(modid = "illageandspillage", bus = Bus.MOD, value = Dist.CLIENT)
public class ClientModEventBusSubscriber {
    @SubscribeEvent
    public static void registerEntityRenders(EntityRenderersEvent.AddLayers event) {
        event.getContext().getEntityRenderDispatcher().getSkinMap().forEach((model, renderer) -> {
            RenderLayerParent<Player, EntityModel<Player>> layerParent = (RenderLayerParent<Player, EntityModel<Player>>) event.getSkin(model);
            if (layerParent != null) {
                ((LivingEntityRenderer<Player, EntityModel<Player>>) renderer).addLayer(new WebbedLayer<>(layerParent));
                ((LivingEntityRenderer<Player, EntityModel<Player>>) renderer).addLayer(new HayArmorLayer<>(layerParent));
            }
        });

        Minecraft.getInstance().getEntityRenderDispatcher().renderers.values().forEach(r -> {
            if (r instanceof LivingEntityRenderer) {
                ((LivingEntityRenderer<?, ?>) r).addLayer(new WebbedLayer<>((RenderLayerParent<?, ?>) r));
                ((LivingEntityRenderer<?, ?>) r).addLayer(new HayArmorLayer<>((RenderLayerParent<?, ?>) r));
            }
        });
    }

    @SubscribeEvent
    public static void registerGuiOverlays(RegisterGuiOverlaysEvent event) {
        event.registerBelowAll("webbed", WebbedOverlay.WEBBED_OVERLAY);
        event.registerAbove(VanillaGuiOverlay.PORTAL.id(), "jumpscare", (forgeGui, guiGraphics, partialTicks, screenWidth, screenHeight) -> JumpscareOverlay.JUMPSCARE_OVERLAY.render(guiGraphics, partialTicks, screenWidth, screenHeight));
    }

    @SubscribeEvent
    public static void registerParticleFactories(final RegisterParticleProvidersEvent event) {
        Minecraft.getInstance().particleEngine.register(ParticleRegisterer.MUTATION_PARTICLES.get(), MutationParticles.Provider::new);
        Minecraft.getInstance().particleEngine.register(ParticleRegisterer.MUTATION_PARTICLES2.get(), MutationParticles2.Provider::new);
        Minecraft.getInstance().particleEngine.register(ParticleRegisterer.MUTATION_DRIP_PARTICLES.get(), MutationDripParticles.Provider::new);
        Minecraft.getInstance().particleEngine.register(ParticleRegisterer.BLOOD_PARTICLES.get(), BloodParticles.Provider::new);
    }

    @SubscribeEvent
    public static void registerLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(IgniterModel.LAYER_LOCATION, IgniterModel::createBodyLayer);
        event.registerLayerDefinition(EngineerModel.LAYER_LOCATION, EngineerModel::createBodyLayer);
        event.registerLayerDefinition(ChagrinSentryModel.LAYER_LOCATION, ChagrinSentryModel::createBodyLayer);
        event.registerLayerDefinition(HinderModel.LAYER_LOCATION, HinderModel::createBodyLayer);
        event.registerLayerDefinition(FactoryModel.LAYER_LOCATION, FactoryModel::createBodyLayer);
        event.registerLayerDefinition(BeeperModel.LAYER_LOCATION, BeeperModel::createBodyLayer);
        event.registerLayerDefinition(SniperModel.LAYER_LOCATION, SniperModel::createBodyLayer);
        event.registerLayerDefinition(PokerModel.LAYER_LOCATION, PokerModel::createBodyLayer);
        event.registerLayerDefinition(MagispellerModel.LAYER_LOCATION, MagispellerModel::createBodyLayer);
        event.registerLayerDefinition(FakerModel.LAYER_LOCATION, FakerModel::createBodyLayer);
        event.registerLayerDefinition(DispenserModel.LAYER_LOCATION, DispenserModel::createBodyLayer);
        event.registerLayerDefinition(IllashooterModel.LAYER_LOCATION, IllashooterModel::createBodyLayer);
        event.registerLayerDefinition(CrashagerModel.LAYER_LOCATION, CrashagerModel::createBodyLayer);
        event.registerLayerDefinition(BossRandomizerModel.LAYER_LOCATION, BossRandomizerModel::createBodyLayer);
        event.registerLayerDefinition(TwittollagerModel.LAYER_LOCATION, TwittollagerModel::createBodyLayer);
        event.registerLayerDefinition(SpiritcallerModel.LAYER_LOCATION, SpiritcallerModel::createBodyLayer);
        event.registerLayerDefinition(MobSpiritModel.LAYER_LOCATION, MobSpiritModel::createBodyLayer);
        event.registerLayerDefinition(IllagerSoulModel.LAYER_LOCATION, IllagerSoulModel::createBodyLayer);
        event.registerLayerDefinition(ImpModel.LAYER_LOCATION, ImpModel::createBodyLayer);
        event.registerLayerDefinition(SpiritHandModel.LAYER_LOCATION, SpiritHandModel::createBodyLayer);
        event.registerLayerDefinition(CrocofangModel.LAYER_LOCATION, CrocofangModel::createBodyLayer);
//        event.registerLayerDefinition(DevastatorModel.LAYER_LOCATION, DevastatorModel::createBodyLayer);
        event.registerLayerDefinition(AbsorberModel.LAYER_LOCATION, AbsorberModel::createBodyLayer);
        event.registerLayerDefinition(PreserverModel.LAYER_LOCATION, PreserverModel::createBodyLayer);
        event.registerLayerDefinition(HayArmorModel.LAYER_LOCATION, HayArmorModel::createBodyLayer);
        event.registerLayerDefinition(FreakagerModel.LAYER_LOCATION, FreakagerModel::createBodyLayer);
        event.registerLayerDefinition(RagnoModel.LAYER_LOCATION, RagnoModel::createBodyLayer);
        event.registerLayerDefinition(EyesoreModel.LAYER_LOCATION, EyesoreModel::createBodyLayer);
        event.registerLayerDefinition(FunnyboneModel.LAYER_LOCATION, FunnyboneModel::createBodyLayer);
        event.registerLayerDefinition(BoneModel.LAYER_LOCATION, BoneModel::createBodyLayer);
        event.registerLayerDefinition(SkullBombModel.LAYER_LOCATION, SkullBombModel::createBodyLayer);
        event.registerLayerDefinition(OldFreakagerModel.LAYER_LOCATION, OldFreakagerModel::createBodyLayer);
        event.registerLayerDefinition(OldRagnoModel.LAYER_LOCATION, OldRagnoModel::createBodyLayer);
        event.registerLayerDefinition(OldMagispellerModel.LAYER_LOCATION, OldMagispellerModel::createBodyLayer);
        event.registerLayerDefinition(MagiHealModel.LAYER_LOCATION, MagiHealModel::createBodyLayer);
        event.registerLayerDefinition(KaboomerModel.LAYER_LOCATION, KaboomerModel::createBodyLayer);
        event.registerLayerDefinition(PumpkinBombModel.LAYER_LOCATION, PumpkinBombModel::createBodyLayer);
        event.registerLayerDefinition(AxeModel.LAYER_LOCATION, AxeModel::createBodyLayer);
        event.registerLayerDefinition(ScytheModel.LAYER_LOCATION, ScytheModel::createBodyLayer);
        event.registerLayerDefinition(OldScytheModel.LAYER_LOCATION, OldScytheModel::createBodyLayer);
        event.registerLayerDefinition(TrickOrTreatModel.LAYER_LOCATION, TrickOrTreatModel::createBodyLayer);
        event.registerLayerDefinition(WebNetModel.LAYER_LOCATION, WebNetModel::createBodyLayer);
        event.registerLayerDefinition(VillagerSoulModel.LAYER_LOCATION, VillagerSoulModel::createBodyLayer);
    }

    @SubscribeEvent
    public static void onClientSetup(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntityTypes.Igniter.get(), IgniterRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Engineer.get(), EngineerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.ChagrinSentry.get(), ChagrinSentryRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Hinder.get(), HinderRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Factory.get(), FactoryRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Beeper.get(), BeeperRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Sniper.get(), SniperRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Poker.get(), PokerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Magispeller.get(), MagispellerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Faker.get(), FakeMagispellerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Dispenser.get(), DispenserRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Illashooter.get(), IllashooterRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Crashager.get(), CrashagerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.BossRandomizer.get(), BossRandomizerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Twittollager.get(), TwittollagerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Spiritcaller.get(), SpiritcallerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.MobSpirit.get(), MobSpiritRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.IllagerSoul.get(), IllagerSoulRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Imp.get(), ImpRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.SpiritHand.get(), SpiritHandRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.SoulBeam.get(), SoulBeamRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Crocofang.get(), CrocofangRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.IgniterFireball.get(), (p_174064_) -> new ThrownItemRenderer<>(p_174064_, 0.75F, true));
        event.registerEntityRenderer(ModEntityTypes.CameraShake.get(), NothingRenderer::new);
//        event.registerEntityRenderer(ModEntityTypes.Devastator.get(), DevastatorRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Absorber.get(), AbsorberRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Preserver.get(), PreserverRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Freakager.get(), FreakagerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Ragno.get(), RagnoRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Eyesore.get(), EyesoreRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Funnybone.get(), FunnyboneRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Bone.get(), BoneRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.SkullBomb.get(), SkullBombRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.OldFreakager.get(), OldFreakagerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.OldRagno.get(), OldRagnoRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.OldMagispeller.get(), OldMagispellerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.MagiFireball.get(), MagiFireballRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.MagiArrow.get(), MagiArrowRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.MagiHeal.get(), MagiHealRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Kaboomer.get(), KaboomerRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.PumpkinBomb.get(), PumpkinBombRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Axe.get(), AxeRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.OldAxe.get(), OldAxeRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.DarkPotion.get(), (p_174064_) -> new ThrownItemRenderer<>(p_174064_, 0.75F, true));
        event.registerEntityRenderer(ModEntityTypes.Scythe.get(), ScytheRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.OldScythe.get(), OldScytheRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.TrickOrTreat.get(), TrickOrTreatRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.Web.get(), (p_174064_) -> new ThrownItemRenderer<>(p_174064_, 1.5F, true));
        event.registerEntityRenderer(ModEntityTypes.WebNet.get(), WebNetRenderer::new);
        event.registerEntityRenderer(ModEntityTypes.VillagerSoul.get(), VillagerSoulRenderer::new);
    }
}
