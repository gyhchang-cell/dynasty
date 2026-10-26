package net.sam.simple_combat_indicators.render;

import com.mojang.blaze3d.platform.Window;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.sam.simple_combat_indicators.SimpleCombatIndicators;
import net.sam.simple_combat_indicators.config.ClientConfig;
import net.sam.simple_combat_indicators.util.ConfigUtils;
import net.sam.simple_combat_indicators.util.DamageDealtIndicator;
import net.sam.simple_combat_indicators.util.DamageTakenIndicator;

import java.util.ArrayList;
import java.util.List;

@Mod.EventBusSubscriber(modid = SimpleCombatIndicators.MOD_ID, value = Dist.CLIENT)
public class DamageIndicatorRenderer {

    public static boolean shouldSpray;

    public static List<DamageTakenIndicator> damageTakenIndicators = new ArrayList<>();
    public static List<DamageDealtIndicator> damageDealtIndicators = new ArrayList<>();
    private static final ResourceLocation DAMAGE_TAKEN_INDICATOR = new ResourceLocation(SimpleCombatIndicators.MOD_ID, "textures/client/damage_taken_indicator.png");
    @SubscribeEvent
    public static void onRenderGui(RenderGuiEvent.Post event) {
        renderDamageTakenIndicators(event.getPartialTick());
        renderDamageDealtIndicators(event.getPartialTick(), event.getGuiGraphics());
    }


    public static void renderDamageTakenIndicators(float partialTick){


        Window window = Minecraft.getInstance().getWindow();
        float screenWidth = window.getWidth();
        float screenHeight = window.getHeight();
        List<DamageTakenIndicator> temp1 = new ArrayList<>();
        for (DamageTakenIndicator dmg : damageTakenIndicators){
            dmg.tick(partialTick);
            float x = (float) (screenWidth/2 + (Math.sin(dmg.rotation * (Math.PI/180)) * dmg.centerDistPx * dmg.distScale));
            float y = (float) (screenHeight/2 - (Math.cos(dmg.rotation * (Math.PI/180)) * dmg.centerDistPx * dmg.distScale));
            float width = 15 * dmg.scale;
            float height = 11 * dmg.scale;
            CustomHudRenderer.renderCustomHudObject(DAMAGE_TAKEN_INDICATOR, x,y,width,height, dmg.rotation, dmg.r, dmg.g, dmg.b, dmg.a);
            if (dmg.age < dmg.lifetime){
                temp1.add(dmg);
            }
        }
        damageTakenIndicators = temp1;

    }


    public static void renderDamageDealtIndicators(float partialTick, GuiGraphics guiGraphics){
        List<DamageDealtIndicator> temp2 = new ArrayList<>();
        for (DamageDealtIndicator dmg : damageDealtIndicators){

            dmg.tick(partialTick);
            Camera camera = Minecraft.getInstance().gameRenderer.getMainCamera();
            Vec3 up = new Vec3 (camera.getUpVector().x(),camera.getUpVector().y(),camera.getUpVector().z());
            Vec3 left = new Vec3 (camera.getLeftVector().x(),camera.getLeftVector().y(),camera.getLeftVector().z());

            double offsetY = 0.75;
            double offsetX = 0.35;

            Vec3 pos = dmg.targetPos;
            //if spray numbers is off then spawn at top left, otherwise spawn in center of mob
            if(!shouldSpray){
                pos = pos.add(up.scale(offsetY * (CustomHudRenderer.currentFov / 110) * dmg.sqrtDistToEntity));
                pos = pos.add(left.scale(offsetX * (CustomHudRenderer.currentFov / 110) * dmg.sqrtDistToEntity));
            }
            Vec2 screenRenderPos = CustomHudRenderer.worldToScreen(pos);
            if(screenRenderPos != null){

                String text = String.format("%.0f", dmg.totalDamage);
                CustomHudRenderer.renderText(guiGraphics, text, screenRenderPos.x + dmg.xOffset, screenRenderPos.y + dmg.yOffset, dmg.r, dmg.g, dmg.b, dmg.a , dmg.scale, dmg.rotation);
            }

            if (dmg.age < dmg.lifetime){
                temp2.add(dmg);
            }
        }
        damageDealtIndicators = temp2;
    }

    //called in ConfigUtils when config is read
    public static void initFromConfig() {
        shouldSpray = ConfigUtils.getOrDefault(ClientConfig.SPRAY_NUMBERS);
    }
}
