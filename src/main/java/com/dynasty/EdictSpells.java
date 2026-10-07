package com.dynasty;

import com.dynasty.network.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.damagesource.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** The existing talisman school: one server clock, one hit per cast, no client target or damage input. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class EdictSpells {
    public static final ResourceKey<DamageType> DAMAGE=ResourceKey.create(Registries.DAMAGE_TYPE,new ResourceLocation("dynasty","edict_spell"));
    public static final String[] NAMES={"飞符","巽风","雷敕","缚灵","护身","镇岳印"};
    public static final int[] WINDUP={8,14,30,20,12,42},COOLDOWN={20,38,65,52,80,90};
    private static final float[] POWER={.9f,1.6f,2.6f,1.0f,0,3.8f};
    private record Cast(UUID id,ServerPlayer owner,int kind,long start,ItemStack weapon,Vec3 origin,Vec3 aim,Vec3 point,ResourceKey<net.minecraft.world.level.Level> dimension){}
    private static final Map<UUID,Cast> ACTIVE=new HashMap<>();
    public static boolean weapon(ItemStack stack){String id=DynastyTrinkets.idOf(stack);return id!=null&&Set.of("chiling_brush","leifu_staff","taiyi_whisk","hunyuan_staff","zhuque_fan").contains(id);}
    public static boolean isSpell(DamageSource source){return source.is(DAMAGE);}
    public static boolean cast(ServerPlayer p,int kind) {
        if(kind<0||kind>=6||!p.isAlive()||p.isSpectator()||!weapon(p.getMainHandItem())||ACTIVE.containsKey(p.getUUID()))return false;
        long now=p.server.overworld().getGameTime();
        if(now<p.getPersistentData().getLong("edictReady"))return false;
        Vec3 origin=p.getEyePosition(),aim=p.getLookAngle(),end=origin.add(aim.scale(kind==0?16:20));
        var hit=p.level().clip(new ClipContext(origin,end,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p));
        end=hit.getLocation();
        // Place an area spell at the nearest visible enemy along the aimed segment, otherwise at the wall/end.
        if(kind!=4) {
            double nearest=origin.distanceToSqr(end);
            for(var e:p.level().getEntitiesOfClass(LivingEntity.class,new AABB(origin,end).inflate(1),e->hostile(p,e))) {
                var intercept=e.getBoundingBox().inflate(.25).clip(origin,end);
                if(intercept.isPresent()&&origin.distanceToSqr(intercept.get())<nearest) {end=intercept.get();nearest=origin.distanceToSqr(end);}
            }
        } else end=p.position().add(0,1,0);
        var cast=new Cast(UUID.randomUUID(),p,kind,now,p.getMainHandItem(),origin,aim,end,p.level().dimension());
        ACTIVE.put(p.getUUID(),cast);p.getPersistentData().putLong("edictReady",now+COOLDOWN[kind]);
        visual(cast,kind);return true;
    }
    private static boolean hostile(ServerPlayer p,LivingEntity e){return e instanceof Enemy&&e.isAlive()&&!e.isAlliedTo(p)&&!p.isAlliedTo(e);}
    public static boolean visible(ServerPlayer p,LivingEntity e){return p.hasLineOfSight(e);}
    private static void visual(Cast c,int kind) {
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(c.origin.x,c.origin.y,c.origin.z,64,c.dimension)),
                new EdictVisualPacket(c.id,kind,c.start,c.origin,c.point));
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void attack(AttackEntityEvent e) {
        if(!weapon(e.getEntity().getMainHandItem()))return;e.setCanceled(true);
        if(e.getEntity() instanceof ServerPlayer p)cast(p,0);
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void right(PlayerInteractEvent.RightClickItem e) {
        if(e.getHand()!=InteractionHand.MAIN_HAND||!weapon(e.getItemStack()))return;
        e.setCanceled(true);e.setCancellationResult(InteractionResult.sidedSuccess(e.getLevel().isClientSide));
        if(e.getEntity() instanceof ServerPlayer p) {
            if(p.isShiftKeyDown()) {
                int mode=p.getPersistentData().getInt("edictMode")%5+1;p.getPersistentData().putInt("edictMode",mode);
                p.displayClientMessage(net.minecraft.network.chat.Component.literal("符令 · "+NAMES[mode]+"（右键施放，潜行右键切换）"),true);
            } else cast(p,Math.max(1,Math.min(5,p.getPersistentData().getInt("edictMode"))));
        }
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END)return;
        var iterator=ACTIVE.values().iterator();
        while(iterator.hasNext()) {
            var c=iterator.next();var p=c.owner;long age=p.server.overworld().getGameTime()-c.start;
            boolean cancel=!p.isAlive()||p.hasDisconnected()||p.level().dimension()!=c.dimension||p.getMainHandItem()!=c.weapon
                    ||p.getLookAngle().dot(c.aim)<.75||p.getEyePosition().distanceToSqr(c.origin)>9;
            if(cancel){visual(c,-1);iterator.remove();continue;}
            if(age<WINDUP[c.kind])continue;
            iterator.remove();resolve(p,c.kind,c.origin,c.point);
        }
    }
    static void resolve(ServerPlayer p,int kind,Vec3 origin,Vec3 point) {
        if(kind==4){p.addEffect(new MobEffectInstance(DynastyEffects.IRON_WALL.get(),60,0));return;}
        double radius=kind==0?.65:kind==1?3:kind==5?4:2.5;
        Vec3 center=kind==1?origin.add(point.subtract(origin).normalize().scale(Math.min(7,origin.distanceTo(point)))):point;
        var source=new DamageSource(p.level().registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(DAMAGE),p,p);
        double base=1;
        for(var modifier:p.getMainHandItem().getAttributeModifiers(net.minecraft.world.entity.EquipmentSlot.MAINHAND).get(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE))
            if(modifier.getOperation()==net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION)base+=modifier.getAmount();
        base+=DynastyBalance.weaponBonus(DynastyTrinkets.idOf(p.getMainHandItem()));
        for(var target:p.level().getEntitiesOfClass(LivingEntity.class,new AABB(center,center).inflate(radius),t->hostile(p,t))) {
            if(!visible(p,target)||target.getBoundingBox().distanceToSqr(center)>radius*radius)continue;
            if(target.hurt(source,(float)(Math.max(100,base)*POWER[kind]))) {
                if(kind==1){var push=point.subtract(origin).normalize().scale(.4);target.push(push.x,.12,push.z);}
                if(kind==3) {
                    boolean boss=target instanceof DynastyBossCombat.BarHolder||target instanceof com.dynasty.ritual.ZhenyuanSovereign||target instanceof com.dynasty.entity.UndeadFirstEmperor;
                    if(!boss)target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,3));
                    else if(com.dynasty.entity.DynastyBossMechanics.weak(target))target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,10,0));
                }
            }
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){var c=ACTIVE.remove(e.getEntity().getUUID());if(c!=null)visual(c,-1);}
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){ACTIVE.clear();}
    private EdictSpells(){}
}
