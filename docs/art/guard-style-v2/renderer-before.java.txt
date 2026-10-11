package com.dynasty.client.character;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.Items;

/** One textured pass per character; original mesh palette over vanilla's neutral pixel grain. */
public final class DynastyCharacterRenderer<T extends Mob> extends MobRenderer<T,DynastyCharacterModel<T>> {
    private static final ResourceLocation SURFACE=new ResourceLocation("minecraft","textures/block/white_concrete.png");
    public DynastyCharacterRenderer(EntityRendererProvider.Context context,DynastyCharacterModel.Role role) {
        super(context,new DynastyCharacterModel<>(role),role==DynastyCharacterModel.Role.GENERAL?.48f:.35f);
        addLayer(new RenderLayer<T,DynastyCharacterModel<T>>(this) {
            @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,T mob,float a,float b,float partial,float age,float yaw,float pitch) {
                for(boolean left:new boolean[]{false,true}) {
                    var item=left?mob.getOffhandItem():mob.getMainHandItem();
                    if(item.isEmpty()||role==DynastyCharacterModel.Role.ARCHER&&item.is(Items.BOW))continue;
                    pose.pushPose();getParentModel().handTransform(pose,left);
                    pose.mulPose(Axis.XP.rotationDegrees(-90));pose.mulPose(Axis.YP.rotationDegrees(180));
                    context.getItemInHandRenderer().renderItem(mob,item,left?ItemDisplayContext.THIRD_PERSON_LEFT_HAND:ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,left,pose,buffers,light);
                    pose.popPose();
                }
            }
        });
    }
    @Override public ResourceLocation getTextureLocation(T mob){return SURFACE;}
}
