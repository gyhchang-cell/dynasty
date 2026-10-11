package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.GeoReplacedEntity;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.GeoReplacedEntityRenderer;
import software.bernie.geckolib.renderer.layer.BlockAndItemGeoLayer;

/** Original large creature rigs; existing entities retain their animation/skill clocks. */
public final class BossFormsRenderer {
    private BossFormsRenderer() {}

    private static final class Model<T extends GeoAnimatable> extends GeoModel<T> {
        private final String id;
        Model(String id) { this.id=id; }
        private ResourceLocation resource(String folder,String suffix) {
            return new ResourceLocation("dynasty",folder+"/boss_forms/"+id+suffix);
        }
        @Override public ResourceLocation getModelResource(T actor) { return resource("geo",".geo.json"); }
        @Override public ResourceLocation getTextureResource(T actor) { return resource("textures/entity",".png"); }
        @Override public ResourceLocation getAnimationResource(T actor) { return resource("animations",".animation.json"); }
        @Override public void setCustomAnimations(T actor,long instanceId,AnimationState<T> state) {
            super.setCustomAnimations(actor,instanceId,state);
            if(id.equals("rebel_general") && state.getData(DataTickets.ENTITY) instanceof Mob mob)
                getBone("war_glaive").ifPresent(bone -> {
                    boolean equipped=!mob.getMainHandItem().isEmpty();
                    bone.setHidden(equipped);bone.setChildrenHidden(equipped);
                });
        }
    }

    public static final class Elite<T extends Entity & GeoEntity> extends GeoEntityRenderer<T> {
        public Elite(EntityRendererProvider.Context context,String id,float shadow) {
            super(context,new Model<>(id)); shadowRadius=shadow;
        }
        @Override protected float getDeathMaxRotation(T actor) { return 0; }
        @Override public boolean shouldRender(T actor,Frustum frustum,double x,double y,double z) {
            return actor.shouldRender(x,y,z) && (actor.noCulling || frustum.isVisible(actor.getBoundingBox().inflate(5,3,5)));
        }
    }

    public static final class Chain extends GeoEntityRenderer<com.dynasty.blueprint.elite.HammerChain> {
        public Chain(EntityRendererProvider.Context context) { super(context,new Model<>("hammer_chain")); shadowRadius=.65f; }
        @Override public void render(com.dynasty.blueprint.elite.HammerChain actor,float yaw,float partial,PoseStack pose,MultiBufferSource buffers,int light) {
            super.render(actor,yaw,partial,pose,buffers,light);
            if(!(actor.level().getEntity(actor.ownerEntityId()) instanceof com.dynasty.blueprint.elite.HammerGuardian caster)||!caster.isAlive())return;
            double age=caster.level().getGameTime()-caster.skillStart()+partial;
            double angle=age<36?-30:age<48?-30*(48-age)/12:0;
            Vec3 endpoint=com.dynasty.entity.BossFormSockets.hand(caster,caster.getPosition(partial),angle);
            Vec3 to=endpoint.subtract(actor.getPosition(partial));
            if(to.lengthSqr()>32*32)return;
            pose.pushPose();
            try {
                var entry=pose.last();var vertices=buffers.getBuffer(net.minecraft.client.renderer.RenderType.lines());
                for(int i=0;i<8;i++) {
                    double a=i/8.0,b=(i+1)/8.0;
                    Vec3 from=to.scale(a).add(0,-.15*Math.sin(Math.PI*a),0),end=to.scale(b).add(0,-.15*Math.sin(Math.PI*b),0),normal=end.subtract(from).normalize();
                    vertices.vertex(entry.pose(),(float)from.x,(float)from.y,(float)from.z).color(112,108,93,255).normal(entry.normal(),(float)normal.x,(float)normal.y,(float)normal.z).endVertex();
                    vertices.vertex(entry.pose(),(float)end.x,(float)end.y,(float)end.z).color(112,108,93,255).normal(entry.normal(),(float)normal.x,(float)normal.y,(float)normal.z).endVertex();
                }
            } finally { pose.popPose(); }
        }
    }

    public static final class CoreVisual implements GeoReplacedEntity {
        private final EntityType<?> type;
        private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
        private static final RawAnimation IDLE=RawAnimation.begin().thenLoop("idle"),WALK=RawAnimation.begin().thenLoop("walk"),
            ATTACK=RawAnimation.begin().thenPlay("attack"),HURT=RawAnimation.begin().thenPlay("hurt"),DEATH=RawAnimation.begin().thenPlayAndHold("death");
        CoreVisual(EntityType<?> type) { this.type=type; }
        @Override public EntityType<?> getReplacingEntityType() { return type; }
        @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
        @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
            final Mob[] active=new Mob[1];final float[] partial=new float[1];
            var controller=new AnimationController<CoreVisual>(this,"body",0,state -> {
                if(!(state.getData(DataTickets.ENTITY) instanceof Mob mob))return PlayState.STOP;
                active[0]=mob;partial[0]=state.getPartialTick();
                if(mob.isDeadOrDying())return state.setAndContinue(DEATH);
                if(mob.hurtTime>0)return state.setAndContinue(HURT);
                boolean winding=mob instanceof com.dynasty.entity.DynastyBosses.RebelGeneral rebel && rebel.characterAttackProgress(partial[0])>0;
                if(mob.swinging||winding)return state.setAndContinue(ATTACK);
                var playing=state.getController().getCurrentAnimation();
                if(playing!=null && (playing.animation().name().equals("attack")||playing.animation().name().equals("hurt")) && !state.getController().hasAnimationFinished())return PlayState.CONTINUE;
                return state.setAndContinue(state.isMoving()?WALK:IDLE);
            }) {
                @Override protected double adjustTick(double tick) {
                    double local=super.adjustTick(tick);
                    if(active[0] instanceof com.dynasty.entity.DynastyBosses.RebelGeneral rebel && getCurrentAnimation()!=null && getCurrentAnimation().animation().name().equals("attack")) {
                        float progress=rebel.characterAttackProgress(partial[0]);
                        if(progress>0)return progress*rebel.characterAttackDuration();
                    }
                    return local;
                }
            };
            for(String clip:new String[]{"idle","walk","attack","cast","hurt","death"})
                controller.triggerableAnim("art_check_"+clip,RawAnimation.begin().then(clip,Animation.LoopType.HOLD_ON_LAST_FRAME));
            controllers.add(controller);
        }
    }

    public static final class Core<E extends Mob> extends GeoReplacedEntityRenderer<E,CoreVisual> {
        public Core(EntityRendererProvider.Context context,EntityType<E> type,String id) {
            super(context,new Model<>(id),new CoreVisual(type));
            shadowRadius=id.equals("eunuch_mastermind")?1.6f:1.9f;
            if(id.equals("rebel_general"))addRenderLayer(new BlockAndItemGeoLayer<CoreVisual>(this) {
                @Override protected ItemStack getStackForBone(GeoBone bone,CoreVisual actor) {
                    return bone.getName().equals("right_grip")?getCurrentEntity().getMainHandItem():null;
                }
                @Override protected void renderStackForBone(PoseStack pose,GeoBone bone,ItemStack item,CoreVisual actor,
                        MultiBufferSource buffers,float partial,int light,int overlay) {
                    if(item.isEmpty())return;
                    pose.pushPose();
                    try {
                        pose.scale(1.8f,1.8f,1.8f);
                        context.getItemInHandRenderer().renderItem(getCurrentEntity(),item,ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,false,pose,buffers,light);
                    } finally { pose.popPose(); }
                }
            });
        }
        @Override protected float getDeathMaxRotation(CoreVisual actor) { return 0; }
        @Override public boolean shouldRender(E actor,Frustum frustum,double x,double y,double z) {
            return actor.shouldRender(x,y,z) && (actor.noCulling || frustum.isVisible(actor.getBoundingBox().inflate(5,3,5)));
        }
    }
}
