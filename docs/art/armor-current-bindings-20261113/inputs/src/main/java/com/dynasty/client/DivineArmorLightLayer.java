package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraftforge.registries.ForgeRegistries;

/** Depth-tested, unlit cyan gems that follow equipped legendary armor; no shaders required. */
public final class DivineArmorLightLayer extends RenderLayer<AbstractClientPlayer,PlayerModel<AbstractClientPlayer>> {
    public DivineArmorLightLayer(PlayerRenderer renderer) {super(renderer);}
    private boolean worn(AbstractClientPlayer p,EquipmentSlot slot) {
        var id=ForgeRegistries.ITEMS.getKey(p.getItemBySlot(slot).getItem());
        return id!=null&&id.getNamespace().equals("dynasty")&&id.getPath().startsWith("xuantian_");
    }
    @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,AbstractClientPlayer player,
            float swing,float amount,float partial,float age,float yaw,float pitch) {
        if(player.isInvisible())return;
        float pulse=.7f+.3f*(float)Math.sin(age*.085f);
        var m=getParentModel();
        if(worn(player,EquipmentSlot.HEAD))gem(pose,buffers,m.head,0,-.37f,-.319f,.055f,pulse);
        if(worn(player,EquipmentSlot.CHEST))gem(pose,buffers,m.body,0,.25f,-.19f,.072f,pulse);
        if(worn(player,EquipmentSlot.LEGS)) {
            gem(pose,buffers,m.leftLeg,0,.35f,-.166f,.04f,pulse);
            gem(pose,buffers,m.rightLeg,0,.35f,-.166f,.04f,pulse);
        }
        if(worn(player,EquipmentSlot.FEET)) {
            gem(pose,buffers,m.leftLeg,0,.65f,-.19f,.032f,pulse);
            gem(pose,buffers,m.rightLeg,0,.65f,-.19f,.032f,pulse);
        }
    }
    private void gem(PoseStack pose,MultiBufferSource buffers,ModelPart part,float x,float y,float z,float r,float pulse) {
        pose.pushPose();part.translateAndRotate(pose);
        var sink=buffers.getBuffer(RenderType.debugQuads());var mat=pose.last().pose();
        int green=(int)(180+70*pulse),blue=(int)(210+45*pulse);
        sink.vertex(mat,x,y-r,z).color(90,green,blue,255).endVertex();
        sink.vertex(mat,x-r,y,z).color(90,green,blue,255).endVertex();
        sink.vertex(mat,x,y+r,z).color(90,green,blue,255).endVertex();
        sink.vertex(mat,x+r,y,z).color(90,green,blue,255).endVertex();
        pose.popPose();
    }
}
