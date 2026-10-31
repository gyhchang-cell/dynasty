/*
 * Decompiled with CFR 0.2.2 (FabricMC 7c48b8c4).
 */
package floffy.toffys_hooks.render.entity;

import floffy.toffys_hooks.ToffysHooks;
import floffy.toffys_hooks.entity.HookEntity;
import floffy.toffys_hooks.register.ModItems;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.render.LightmapTextureManager;
import net.minecraft.client.render.OverlayTexture;
import net.minecraft.client.render.RenderLayer;
import net.minecraft.client.render.VertexConsumer;
import net.minecraft.client.render.VertexConsumerProvider;
import net.minecraft.client.render.entity.*;
import net.minecraft.client.render.item.ItemRenderer;
import net.minecraft.client.render.model.json.ModelTransformationMode;
import net.minecraft.client.texture.SpriteAtlasTexture;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.entity.Entity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemConvertible;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.util.Arm;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.MathHelper;
import net.minecraft.util.math.RotationAxis;
import net.minecraft.util.math.Vec3d;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

@Environment(value=EnvType.CLIENT)
public class HookRenderer
        extends EntityRenderer<HookEntity> {
    private final ItemRenderer itemRenderer;

    public HookRenderer(EntityRendererFactory.Context context) {
        super(context);
        this.itemRenderer = context.getItemRenderer();
    }

    @Override
    public void render(HookEntity lashingPotatoHookEntity, float f, float g, MatrixStack matrixStack, VertexConsumerProvider vertexConsumerProvider, int i) {
        PlayerEntity playerEntity = lashingPotatoHookEntity.getPlayer();
        if (playerEntity == null) {
            return;
        }
        matrixStack.push();
        Vec3d vec3d = getHandPos(playerEntity, g, ModItems.GRAPPLE_HOOK, this.dispatcher);
        Vec3d vec3d2 = new Vec3d(MathHelper.lerp((double)g, (double)lashingPotatoHookEntity.prevX, (double)lashingPotatoHookEntity.getX()), MathHelper.lerp((double)g, (double)lashingPotatoHookEntity.prevY, (double)lashingPotatoHookEntity.getY()) + (double)lashingPotatoHookEntity.getStandingEyeHeight(), MathHelper.lerp((double)g, (double)lashingPotatoHookEntity.prevZ, (double)lashingPotatoHookEntity.getZ()));

        Vec3d vec3d3 = vec3d.subtract(vec3d2);
        float k = (float)(vec3d3.length() + 0.1);
        vec3d3 = vec3d3.normalize();
        float l = (float)Math.acos(vec3d3.y);
        float m = (float)Math.atan2(vec3d3.z, vec3d3.x);
        matrixStack.multiply(RotationAxis.POSITIVE_Y.rotationDegrees((1.5707964f - m) * 57.295776f));
        matrixStack.multiply(RotationAxis.POSITIVE_X.rotationDegrees(l * 57.295776f));
        this.itemRenderer.renderItem(new ItemStack((ItemConvertible)ModItems.HOOK), ModelTransformationMode.GROUND, i, OverlayTexture.DEFAULT_UV, matrixStack, vertexConsumerProvider, lashingPotatoHookEntity.getWorld(), lashingPotatoHookEntity.getId());
        float o = 0.2f;
        float p = MathHelper.cos((float)((float)Math.PI)) * 0.1f;
        float q = MathHelper.sin((float)((float)Math.PI)) * 0.1f;
        float r = MathHelper.cos((float)(0.0f)) * 0.1f;
        float s = MathHelper.sin((float)(0.0f)) * 0.1f;
        float t = MathHelper.cos((float)(1.5707964f)) * 0.1f;
        float u = MathHelper.sin((float)(1.5707964f)) * 0.1f;
        float v = MathHelper.cos((float)(4.712389f)) * 0.1f;
        float w = MathHelper.sin((float)(4.712389f)) * 0.1f;
        float x = k;
        float y = 0.0f;
        float z = 0.4999f;
        float aa = -1.0f;
        float ab = k * 2.5f + aa;
        VertexConsumer vertexConsumer = vertexConsumerProvider.getBuffer(RenderLayer.getEntityCutoutNoCull(Identifier.of(ToffysHooks.MOD_ID,"textures/entity/hook_rope.png")));
        MatrixStack.Entry entry = matrixStack.peek();
        Matrix4f matrix4f = entry.getPositionMatrix();
        Matrix3f matrix3f = entry.getNormalMatrix();
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, p, x, q, 0.4999f, ab, i );
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, p, 0.0f, q, 0.4999f, aa, i );
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, r, 0.0f, s, 0.0f, aa, i );
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, r, x, s, 0.0f, ab, i );

        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, t, x, u, 1, ab, i );
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, t, 0.0f, u, 1, aa, i );
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, v, 0.0f, w, 0.4999f, aa, i );
        HookRenderer.vertex(matrix4f,matrix3f, vertexConsumer, v, x, w, 0.4999f, ab, i );
        matrixStack.pop();
        super.render(lashingPotatoHookEntity, f, g, matrixStack, vertexConsumerProvider, i);
    }

    private static void vertex(Matrix4f positionMatrix, Matrix3f normalMatrix, VertexConsumer vertexConsumer, float x, float y, float z, float u, float v, int i) {
        vertexConsumer.vertex(positionMatrix, x, y, z).color(255, 255, 255, 255).texture(u, v).overlay(OverlayTexture.DEFAULT_UV).light(i).normal(normalMatrix,0.0f, 1.0f, 0.0f).next();
    }

    public static Vec3d getHandPos(PlayerEntity player, float tickDelta, Item item, EntityRenderDispatcher dispatcher) {
        int i = player.getMainArm() == Arm.RIGHT ? 1 : -1;
        ItemStack itemStack = player.getMainHandStack();
        if (!itemStack.isOf(item)) {
            i = -i;
        }
        float f = player.getHandSwingProgress(tickDelta);
        float g = MathHelper.sin((float)(MathHelper.sqrt((float)f) * (float)Math.PI));
        float h = MathHelper.lerp((float)tickDelta, (float)player.prevBodyYaw, (float)player.bodyYaw) * ((float)Math.PI / 180);
        double d = MathHelper.sin((float)h);
        double e = MathHelper.cos((float)h);
        double j = (double)i * 0.35;
        double k = 0.8;
        if (dispatcher.gameOptions != null && !dispatcher.gameOptions.getPerspective().isFirstPerson() || player != MinecraftClient.getInstance().player) {
            float l = player.isInSneakingPose() ? -0.1875f : 0.0f;
            return new Vec3d(MathHelper.lerp((double)tickDelta, (double)player.prevX, (double)player.getX()) - e * j - d * 0.4, player.prevY + (double)player.getStandingEyeHeight() + (player.getY() - player.prevY) * (double)tickDelta - 0.55 + (double)l, MathHelper.lerp((double)tickDelta, (double)player.prevZ, (double)player.getZ()) - d * j + e * 0.4);
        }
        double m = 960.0 / (double)dispatcher.gameOptions.getFov().getValue().intValue();
        Vec3d vec3d = dispatcher.camera.getProjection().getPosition((float)i * 0.525f, -0.1f);
        vec3d = vec3d.multiply(m);
        vec3d = vec3d.rotateY(g * 0.5f);
        vec3d = vec3d.rotateX(-g * 0.7f);
        return new Vec3d(MathHelper.lerp((double)tickDelta, (double)player.prevX, (double)player.getX()) + vec3d.x, MathHelper.lerp((double)tickDelta, (double)player.prevY, (double)player.getY()) + vec3d.y + (double)player.getStandingEyeHeight(), MathHelper.lerp((double)tickDelta, (double)player.prevZ, (double)player.getZ()) + vec3d.z);
    }

    @Override
    public Identifier getTexture(HookEntity hookEntity) {
        return SpriteAtlasTexture.BLOCK_ATLAS_TEXTURE;
    }
}

