package com.dynasty.expansion;

import net.minecraft.world.item.*;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;

public final class ExpansionSupplies extends Item {
    public static final int GUIDE_TICKS=1200;
    private static final String GUIDE="cod4Guide";
    private final String kind;
    ExpansionSupplies(String kind) {
        super(new Properties().stacksTo(16).food(new FoodProperties.Builder().nutrition(kind.equals("army_ration")?10:0).saturationMod(kind.equals("army_ration")?1.2F:0).alwaysEat().build()));
        this.kind=kind;
    }
    @Override public UseAnim getUseAnimation(ItemStack s) { return kind.endsWith("wine")?UseAnim.DRINK:UseAnim.EAT; }
    @Override public ItemStack finishUsingItem(ItemStack s,Level level,LivingEntity user) {
        if(!level.isClientSide && user instanceof ServerPlayer p) {
            switch(kind) {
                case "regen_pill" -> { p.heal(p.getMaxHealth()*.12F);p.addEffect(new MobEffectInstance(MobEffects.REGENERATION,100,1)); }
                case "qi_pill" -> {
                    p.getPersistentData().putLong("cod4QiUntil",level.getGameTime()+200);
                    p.getPersistentData().putInt("cod4Rage",Math.min(5,p.getPersistentData().getInt("cod4Rage")+2));
                    ExpansionEffects.apply(p,ExpansionEffects.YANG,100);
                }
                case "antidote_pill" -> { p.removeEffect(MobEffects.POISON);p.getPersistentData().putLong("cod4Antidote",level.getGameTime()+600); }
                case "zhuangyuan_wine" -> p.getPersistentData().putLong("cod4ExamWine",level.getGameTime()+1200);
                case "marching_wine" -> { ExpansionEffects.apply(p,ExpansionEffects.YANG,100);p.addEffect(new MobEffectInstance(MobEffects.CONFUSION,80,0)); }
                case "soul_incense" -> {
                    p.removeEffect(ExpansionEffects.YIN.get());p.removeEffect(ExpansionEffects.SOUL.get());
                    for(var mob:level.getEntitiesOfClass(Mob.class,p.getBoundingBox().inflate(6),m->m.getMobType()==net.minecraft.world.entity.MobType.UNDEAD)) {
                        mob.setTarget(null);mob.getNavigation().moveTo(mob.getX()+(mob.getX()-p.getX()),mob.getY(),mob.getZ()+(mob.getZ()-p.getZ()),1.1);
                    }
                }
                case "guide_incense" -> locate(p);
                case "army_ration" -> p.addEffect(new MobEffectInstance(MobEffects.SATURATION,200,0));
                default -> { }
            }
            p.getCooldowns().addCooldown(this,kind.equals("guide_incense")?1200:200);
            CombatFeedback.send(p,CombatFeedback.HEAL);
        }
        return super.finishUsingItem(s,level,user);
    }
    public static void locate(ServerPlayer p) {
        var tag=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/ritual_sites"));
        var pos=p.serverLevel().findNearestMapStructure(tag,p.blockPosition(),32,false);
        if(pos==null) p.displayClientMessage(Component.translatable("message.dynasty.cod4.no_ruin"),false);
        else mark(p,pos);
    }
    public static void mark(ServerPlayer p,net.minecraft.core.BlockPos pos){
        var data=new net.minecraft.nbt.CompoundTag();data.putLong("Target",pos.asLong());
        data.putString("Dimension",p.level().dimension().location().toString());data.putLong("Until",p.level().getGameTime()+GUIDE_TICKS);
        p.getPersistentData().put(GUIDE,data);updateGuide(p);
    }
    public static void updateGuide(ServerPlayer p){
        if(!p.getPersistentData().contains(GUIDE))return;
        var data=p.getPersistentData().getCompound(GUIDE);
        if(!data.getString("Dimension").equals(p.level().dimension().location().toString()) || p.level().getGameTime()>=data.getLong("Until")){
            p.getPersistentData().remove(GUIDE);p.displayClientMessage(Component.translatable("message.dynasty.cod4.guide_expired"),true);return;
        }
        var pos=net.minecraft.core.BlockPos.of(data.getLong("Target"));double dx=pos.getX()-p.getX(),dz=pos.getZ()-p.getZ();
        String[] compass={"south","southwest","west","northwest","north","northeast","east","southeast"};
        int direction=Math.floorMod((int)Math.round(Math.atan2(-dx,dz)/(Math.PI/4)),8);
        int seconds=(int)((data.getLong("Until")-p.level().getGameTime()+19)/20);
        p.displayClientMessage(Component.translatable("message.dynasty.cod4.guide",Component.translatable("direction.dynasty."+compass[direction]),(int)Math.hypot(dx,dz),seconds),true);
        if(p.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(pos))<=1024)
            com.dynasty.cod3.Cod3Vfx.send(p.serverLevel(),15,net.minecraft.world.phys.Vec3.atCenterOf(pos),p.getLookAngle(),20,.15,0xE7C866);
    }
    @net.minecraftforge.fml.common.Mod.EventBusSubscriber(modid="dynasty")
    public static final class Guidance {
        @net.minecraftforge.eventbus.api.SubscribeEvent public static void tick(net.minecraftforge.event.TickEvent.PlayerTickEvent e){
            if(e.phase==net.minecraftforge.event.TickEvent.Phase.END && e.player instanceof ServerPlayer p && p.tickCount%20==0)updateGuide(p);
        }
        @net.minecraftforge.eventbus.api.SubscribeEvent public static void dimension(net.minecraftforge.event.entity.player.PlayerEvent.PlayerChangedDimensionEvent e){e.getEntity().getPersistentData().remove(GUIDE);}
        @net.minecraftforge.eventbus.api.SubscribeEvent public static void clone(net.minecraftforge.event.entity.player.PlayerEvent.Clone e){e.getEntity().getPersistentData().remove(GUIDE);}
    }
}
