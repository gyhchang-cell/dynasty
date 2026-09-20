package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.DynastyBowRitual;
import com.dynasty.DynastyWeapons;
import com.dynasty.HouyiAvatarShape;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;

/** Continuous, emissive ribbon geometry: no particle sprites or external mod dependency. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, value = Dist.CLIENT)
public final class DynastyBowSigilRenderer {
    private static final BufferBuilder BUFFER = new BufferBuilder(262144);

    private DynastyBowSigilRenderer() {}

    @SubscribeEvent
    public static void render(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_PARTICLES) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) return;
        Vec3 camera = event.getCamera().getPosition();
        float partial = event.getPartialTick();
        java.util.List<Avatar> avatars = new java.util.ArrayList<>();
        ClientBowEffects.clean();
        if (ClientBowEffects.ARROWS.isEmpty() && ClientBowEffects.IMPACTS.isEmpty()
                && mc.level.players().stream().noneMatch(Player::isUsingItem)) return;
        boolean begun = true;
        RenderSystem.enableBlend();
        RenderSystem.blendFunc(GL11.GL_SRC_ALPHA, GL11.GL_ONE);
        RenderSystem.enableDepthTest();
        RenderSystem.depthMask(false);
        RenderSystem.disableCull();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BUFFER.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        for (Player player : mc.level.players()) {
            if (!player.isUsingItem() || player.distanceToSqr(camera) > 48.0D * 48.0D) continue;
            Item item = player.getUseItem().getItem();
            double score;
            if (item instanceof DynastyWeapons.HuntingBowItem bow) score = bow.visualDamageScore();
            else if (item instanceof DynastyWeapons.DragonBowItem bow) score = bow.visualDamageScore();
            else continue;
            int tier = DynastyBowRitual.tier(score);
            double ticks = player.getTicksUsingItem() + partial;
            double charge = Math.min(1.0D, ticks / 20.0D);
            if (charge < 0.03D) continue;
            Matrix4f matrix = event.getPoseStack().last().pose();
            float[] color = item == DynastyWeapons.ZHUQUE_BOW.get()
                    ? new float[]{1.0F, 0.25F, 0.30F}
                    : tier >= 3 ? new float[]{1.0F, 0.64F, 0.38F} : new float[]{0.30F, 0.85F, 1.0F};
            Vec3 look = player.getViewVector(partial).normalize();
            Vec3 right = look.cross(new Vec3(0, 1, 0));
            if (right.lengthSqr() < 0.0001D) right = new Vec3(1, 0, 0);
            right = right.normalize();
            Vec3 up = right.cross(look).normalize();
            // First-person uses the actual rendered camera so camera interpolation stays aligned.
            Vec3 eye = player == mc.player && mc.options.getCameraType().isFirstPerson()
                    ? camera : player.getEyePosition(partial);
            Vec3 center = eye.add(look.scale(2.6D)).subtract(camera);
            double radius = (0.28D + tier * 0.035D) * (0.8D + charge * 0.2D);
            double time = player.tickCount + partial;
            Sigil aim = new Sigil(matrix, center, right.scale(radius), up.scale(radius), color, charge);
            aim.draw(tier, time);
            if (tier >= 2) {
                double groundRadius = DynastyBowRitual.impactRadius(tier);
                // Keep all three airborne layers below the feet, clear of the aiming view.
                // This is only a visual offset; the ward's protection stays around the player.
                double floorOffset = player.onGround() ? 0.035D : -1.2D;
                Vec3 ground = player.getPosition(partial).add(0, floorOffset, 0).subtract(camera);
                double scale = groundRadius * (0.30D + charge * 0.70D);
                floorSeal(matrix, ground, scale, color, charge, tier, time);
            }
            if (item == DynastyWeapons.HOUYI_BOW.get()) {
                Vec3 overhead = player.getPosition(partial).add(0,2.8,0).subtract(camera);
                new Sigil(matrix, overhead, new Vec3(0.8,0,0), new Vec3(0,0,0.8), color, charge).bagua(time);
                Vec3 avatar = HouyiAvatarShape.origin(player.getPosition(partial), player.getYRot()).subtract(camera);
                double formation = Math.min(1,ticks/40.0);
                avatars.add(new Avatar(avatar,player.getYRot(),formation));
                double crownCharge = Math.max(0,Math.min(1,(ticks-24)/16.0));
                if (crownCharge > 0) {
                    new Sigil(matrix,avatar.add(0,10.35,0),new Vec3(1.6,0,0),new Vec3(0,0,1.6),
                            color,crownCharge).bagua(-time*0.75);
                    new Sigil(matrix,avatar.add(0,10.55,0),new Vec3(1.85,0,0),new Vec3(0,0,1.85),
                            color,crownCharge).bands(time*0.45);
                }
            }
        }
        Matrix4f matrix = event.getPoseStack().last().pose();
        for (ClientBowEffects.Effect effect : ClientBowEffects.ARROWS.values()) {
            var packet = effect.packet();
            var entity = mc.level.getEntity(packet.entityId());
            if (!(entity instanceof net.minecraft.world.entity.projectile.AbstractArrow arrow)
                    || !arrow.isAlive() || arrow.getDeltaMovement().lengthSqr() < 0.01) continue;
            Vec3 direction = arrow.getDeltaMovement().normalize();
            Vec3 right = direction.cross(new Vec3(0,1,0)).normalize();
            if (right.lengthSqr() < 0.01) right = new Vec3(1,0,0);
            Vec3 up = right.cross(direction).normalize();
            Vec3 p = arrow.getPosition(partial).add(direction.scale(0.35)).subtract(camera);
            float[] color = packet.phoenix() ? new float[]{1,0.25F,0.3F} : new float[]{1,0.68F,0.32F};
            double size = 0.18 + packet.tier()*0.045;
            new Sigil(matrix,p,right.scale(size),up.scale(size),color,1).draw(Math.min(2,packet.tier()),arrow.tickCount+partial);
        }
        for (ClientBowEffects.Effect effect : ClientBowEffects.IMPACTS) {
            var packet = effect.packet();
            double age = mc.level.getGameTime() - effect.born() + partial;
            double visible = Math.min(1,age/6.0) * Math.min(1,(60-age)/15.0);
            Vec3 p = new Vec3(packet.x(),packet.y()+0.06,packet.z()).subtract(camera);
            float[] color = packet.phoenix() ? new float[]{1,0.25F,0.3F} : new float[]{1,0.68F,0.32F};
            floorSeal(matrix,p,DynastyBowRitual.impactRadius(packet.tier()),color,visible,packet.tier(),age);
        }
        if (begun) {
            BufferUploader.drawWithShader(BUFFER.end());
            RenderSystem.depthMask(true);
            RenderSystem.enableCull();
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
        }
        for (Avatar avatar : avatars) {
            HouyiAvatarRenderer.draw(matrix,avatar.origin(),avatar.yaw(),avatar.formed());
        }
    }

    private record Avatar(Vec3 origin, float yaw, double formed) {}

    private static void floorSeal(Matrix4f matrix, Vec3 center, double radius, float[] color,
                                  double charge, int tier, double time) {
        new Sigil(matrix,center,new Vec3(radius,0,0),new Vec3(0,0,radius),color,charge).draw(tier,-time*0.55);
        // Additional concentric rune bands hover just above the main plane, also while airborne.
        for (int layer = 1; layer <= 2; layer++) {
            double scale = radius * (1 - layer * 0.14);
            new Sigil(matrix,center.add(0,0.16*layer,0),new Vec3(scale,0,0),new Vec3(0,0,scale),
                    color,charge).bands(time * (layer == 1 ? 0.7 : -0.8));
        }
    }

    /** All strokes are thin quads, with a soft wide pass and a bright fine core. */
    private static final class Sigil {
        private final Matrix4f matrix;
        private final Vec3 center, xAxis, yAxis;
        private final float[] color;
        private final double charge;

        Sigil(Matrix4f matrix, Vec3 center, Vec3 xAxis, Vec3 yAxis, float[] color, double charge) {
            this.matrix = matrix;
            this.center = center;
            this.xAxis = xAxis;
            this.yAxis = yAxis;
            this.color = color;
            this.charge = charge;
        }

        void draw(int tier, double time) {
            new BowSigilGeometry(charge, this::stroke).draw(tier, time);
        }
        void bagua(double time) { new BowSigilGeometry(charge, this::stroke).drawBagua(time); }
        void bands(double time) { new BowSigilGeometry(charge, this::stroke).draw(0, time); }

        private void stroke(double x1, double y1, double x2, double y2, double width) {
            double dx = x2 - x1, dy = y2 - y1, length = Math.hypot(dx, dy);
            if (length < 0.00001D) return;
            for (int pass = 0; pass < 2; pass++) {
                double w = width * (pass == 0 ? 3.5D : 1.0D);
                double nx = -dy / length * w, ny = dx / length * w;
                float alpha = (float) ((pass == 0 ? 0.11D : 0.72D) * Math.min(1, charge * 3));
                vertex(x1 + nx, y1 + ny, alpha);
                vertex(x1 - nx, y1 - ny, alpha);
                vertex(x2 - nx, y2 - ny, alpha);
                vertex(x2 + nx, y2 + ny, alpha);
            }
        }

        private void vertex(double x, double y, float alpha) {
            BUFFER.vertex(matrix, (float)(center.x + xAxis.x * x + yAxis.x * y),
                            (float)(center.y + xAxis.y * x + yAxis.y * y),
                            (float)(center.z + xAxis.z * x + yAxis.z * y))
                    .color(color[0], color[1], color[2], alpha).endVertex();
        }

    }
}
