package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import software.bernie.geckolib.animatable.GeoReplacedEntity;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoReplacedEntityRenderer;
import software.bernie.geckolib.renderer.layer.BlockAndItemGeoLayer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.RenderType;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Client-only rig replacement; existing mobs, saves, AI, hitboxes and skills stay authoritative. */
public final class BossCuboidRenderer<E extends Mob> extends GeoReplacedEntityRenderer<E,BossCuboidRenderer.Visual> {
    public BossCuboidRenderer(EntityRendererProvider.Context context,EntityType<E> type,String id){
        super(context,new Model(id),new Visual(type,id));
        // The three human bosses author their real size in Cuboid units, without a species scale.
        shadowRadius=id.equals("dragon_emperor")?.85f:id.equals("dragon_king")?.7f:id.equals("nine_heaven_general")?.8f:.5f;
        if(id.equals("nine_heaven_general")||id.equals("dragon_king")||id.equals("dragon_emperor"))addRenderLayer(new GeoRenderLayer<Visual>(this){
            @Override public void render(PoseStack pose,Visual visual,BakedGeoModel model,RenderType type,MultiBufferSource buffers,VertexConsumer vertex,float partial,int light,int overlay){
                var mob=getCurrentEntity();
                var controller=visual.getAnimatableInstanceCache().getManagerForId(mob.getId()).getAnimationControllers().get("body");
                boolean casting=controller!=null&&controller.getCurrentAnimation()!=null&&controller.getCurrentAnimation().animation().name().equals("cast");
                BossHumanAura.draw(pose,buffers,mob,id,partial,casting);
                if(id.equals("nine_heaven_general")){
                    float alpha=TianjiangAura.glowAlpha(mob,partial,casting);
                    if(alpha>0){
                        var glow=RenderType.entityTranslucentEmissive(TianjiangAura.GLOW);
                        BossCuboidRenderer.this.reRender(model,pose,buffers,visual,glow,buffers.getBuffer(glow),partial,
                                15728880,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY,1,1,1,alpha);
                    }
                }
            }
        });
        // Preserve actual main/offhand equipment at articulated grip bones.
        addRenderLayer(new BlockAndItemGeoLayer<Visual>(this){
            @Override protected ItemStack getStackForBone(GeoBone bone,Visual visual){
                boolean left=bone.getName().equals("left_grip");
                if(!left&&!bone.getName().equals("right_grip"))return null;
                E mob=getCurrentEntity();
                return left==(mob.getMainArm()==HumanoidArm.LEFT)?mob.getMainHandItem():mob.getOffhandItem();
            }
            @Override protected void renderStackForBone(PoseStack pose,GeoBone bone,ItemStack item,Visual visual,MultiBufferSource buffers,float partial,int light,int overlay){
                if(item.isEmpty())return;
                boolean left=bone.getName().equals("left_grip");
                // This rig is already Y-up in Gecko's bone space. Vanilla's
                // humanoid inversion would turn upright blades into flat ones.
                if(item.is(Items.TRIDENT)){
                    // The built-in shaft runs from Y=2 to Y=27 before its
                    // renderer flips Y. Center that shaft on the actual palm;
                    // the vanilla humanoid display transform assumes another basis.
                    pose.translate(0,14.0/16.0,0);
                    net.minecraftforge.client.extensions.common.IClientItemExtensions.of(item).getCustomRenderer()
                            .renderByItem(item,ItemDisplayContext.NONE,pose,buffers,light,overlay);
                    return;
                }
                context.getItemInHandRenderer().renderItem(getCurrentEntity(),item,left?ItemDisplayContext.THIRD_PERSON_LEFT_HAND:ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,left,pose,buffers,light);
            }
        });
    }
    @Override protected float getDeathMaxRotation(Visual visual){
        // Every species now authors its grounded fall; avoid a second feet-pivot flip.
        return 0;
    }

    public static final class Visual implements GeoReplacedEntity {
        private final EntityType<?> type;
        private final boolean humanBoss;
        private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
        private static final RawAnimation IDLE=RawAnimation.begin().thenLoop("idle"),WALK=RawAnimation.begin().thenLoop("walk"),
                ATTACK=RawAnimation.begin().thenPlay("attack"),HURT=RawAnimation.begin().thenPlay("hurt"),DEATH=RawAnimation.begin().thenPlayAndHold("death");
        Visual(EntityType<?> type,String id){this.type=type;this.humanBoss=id.equals("nine_heaven_general")||id.equals("dragon_king")||id.equals("dragon_emperor");}
        @Override public EntityType<?> getReplacingEntityType(){return type;}
        @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
        @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers){
            var controller=new AnimationController<Visual>(this,"body",2,state->{
                if(!(state.getData(DataTickets.ENTITY) instanceof Mob mob))return PlayState.STOP;
                // A six-tick strike must not spend its first two ticks blending away
                // its tell/contact. This only changes visual transitions for the three
                // approved human bosses; server swing and damage timing stay intact.
                if(humanBoss)state.getController().setTransitionLength(mob.swinging||mob.isDeadOrDying()||mob.hurtTime>0?0:2);
                if(mob.isDeadOrDying())return state.setAndContinue(DEATH);
                if(mob.hurtTime>0)return state.setAndContinue(HURT);
                if(mob.swinging)return state.setAndContinue(ATTACK);
                var playing=state.getController().getCurrentAnimation();
                if(playing!=null&&(playing.animation().name().equals("attack")||playing.animation().name().equals("hurt"))&&!state.getController().hasAnimationFinished())return PlayState.CONTINUE;
                return state.setAndContinue(state.isMoving()?WALK:IDLE);
            });
            // Local resource-QA triggers; never invoked by production gameplay.
            for(String clip:new String[]{"idle","walk","attack","cast","hurt","death"})
                controller.triggerableAnim("art_check_"+clip,RawAnimation.begin().then(clip,Animation.LoopType.HOLD_ON_LAST_FRAME));
            controllers.add(controller);
        }
    }

    private static final class Model extends GeoModel<Visual>{
        private final ResourceLocation geo,texture,animation;
        private final boolean humanBoss;
        Model(String id){humanBoss=id.equals("nine_heaven_general")||id.equals("dragon_king")||id.equals("dragon_emperor");geo=new ResourceLocation("dynasty","geo/boss_cuboid/"+id+".geo.json");texture=new ResourceLocation("dynasty","textures/entity/boss_cuboid/"+id+".png");animation=new ResourceLocation("dynasty","animations/boss_cuboid/"+id+".animation.json");}
        @Override public ResourceLocation getModelResource(Visual visual){return geo;}
        @Override public ResourceLocation getTextureResource(Visual visual){return texture;}
        @Override public ResourceLocation getAnimationResource(Visual visual){return animation;}
        @Override public void setCustomAnimations(Visual visual,long instanceId,AnimationState<Visual> state){
            // The authored spear/trident is a visual carrier for existing skills. Actual
            // equipped main-hand items use the grip layer instead, never two overlapping weapons.
            if(humanBoss&&state.getData(DataTickets.ENTITY) instanceof Mob equipped)
                getBone("weapon").ifPresent(weapon->weapon.setHidden(!equipped.getMainHandItem().isEmpty()));
            if(state.getData(DataTickets.ENTITY) instanceof Mob mob&&mob.isDeadOrDying())return;
            var data=state.getData(DataTickets.ENTITY_MODEL_DATA);
            if(data==null)return;
            getBone("head").ifPresent(head->{
                head.setRotY(head.getRotY()+Mth.clamp(data.netHeadYaw()*Mth.DEG_TO_RAD,-.6f,.6f));
                head.setRotX(head.getRotX()+Mth.clamp(data.headPitch()*Mth.DEG_TO_RAD,-.35f,.35f));
            });
        }
    }
}
