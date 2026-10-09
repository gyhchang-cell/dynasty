package com.dynasty.expansion;

import com.dynasty.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.PlayerWakeUpEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
import java.nio.charset.StandardCharsets;

/** Adds conditional behavior to existing armor/trinkets; IDs, base stats, and school combat stay intact. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class EquipmentBehaviors {
    private static final Map<Player,Map<MobEffect,MobEffectInstance>> SHORTEN = new WeakHashMap<>();
    private static boolean shortening;
    private static final String KEY="dynastyCod4";
    public static int pieces(Player p,String set) {
        return (int)DynastySetBonus.wornArmorIds(p).stream().filter(id->id.equals(set+"_helmet") || id.equals(set+"_chestplate") || id.equals(set+"_leggings") || id.equals(set+"_boots")).count();
    }
    public static CompoundTag saved(Player p) {
        CompoundTag persisted=p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        if(!persisted.contains(KEY))persisted.put(KEY,new CompoundTag());
        p.getPersistentData().put(Player.PERSISTED_NBT_TAG,persisted);return persisted.getCompound(KEY);
    }
    public static long now(Player p) {return p.level().getGameTime();}
    public static boolean ready(Player p,String key,int ticks) {
        var n=saved(p);long time=now(p);if(n.contains(key) && time<n.getLong(key))return false;
        n.putLong(key,time+ticks);return true;
    }
    private static boolean has(Player p,String id) {return DynastyTrinkets.activeIds(p).contains(id);}
    private static void attribute(Player p,String key,Attribute attr,double amount,AttributeModifier.Operation op) {
        var a=p.getAttribute(attr);if(a==null)return;
        UUID id=UUID.nameUUIDFromBytes(("dynasty:cod4/"+key).getBytes(StandardCharsets.UTF_8));
        var old=a.getModifier(id);if(old!=null && old.getAmount()==amount)return;
        a.removeModifier(id);if(amount!=0)a.addTransientModifier(new AttributeModifier(id,key,amount,op));
    }
    public static void refresh(Player p) {
        boolean day=p.level().isDay(),wet=p.isInWater(),full=p.getHealth()>=p.getMaxHealth();
        var n=p.getPersistentData();boolean still=n.getInt("cod4Still")>=40;
        double speed=pieces(p,"cloth")>=2 && p.getFoodData().getFoodLevel()==20?.05:0;
        if(pieces(p,"leather")>=2 && p.isShiftKeyDown())speed+=.15;
        if(pieces(p,"bamboo")>=3 && p.isSprinting() && p.level().getBiome(p.blockPosition()).is(net.minecraft.world.level.biome.Biomes.BAMBOO_JUNGLE))speed+=.10;
        if(pieces(p,"jade")>=4 && full)speed+=.08;
        if(pieces(p,"sea_silk")>=2 && wet)speed+=.20;
        if(pieces(p,"beidou")>=2)speed+=.08;
        if(pieces(p,"phoenix")>=3 && now(p)<n.getLong("cod4PhoenixSpeed"))speed+=.15;
        attribute(p,"speed",Attributes.MOVEMENT_SPEED,speed,AttributeModifier.Operation.MULTIPLY_TOTAL);
        double armor=pieces(p,"general")>=3 && still?12:0;
        if(pieces(p,"dragon_scale")>=4 && wet)armor+=10;
        if(pieces(p,"bronze")>=3 && now(p)<n.getLong("cod4BronzeGuard"))armor+=6;
        attribute(p,"armor",Attributes.ARMOR,armor,AttributeModifier.Operation.ADDITION);
        attribute(p,"resistance",Attributes.KNOCKBACK_RESISTANCE,pieces(p,"dark_iron")>=2?1:pieces(p,"general")>=2?.2:0,AttributeModifier.Operation.ADDITION);
        double luck=pieces(p,"qilin")>=2?1:pieces(p,"ziwei")>=2?3:0;
        if(has(p,"qilin_horn_charm"))luck+=2;
        if(has(p,"jade_bi_disc") && !has(p,"moon_pendant") && !day)luck+=1;
        if(has(p,"moon_pendant") && !day && p.level().getMoonPhase()==0)luck+=2;
        attribute(p,"swim",net.minecraftforge.common.ForgeMod.SWIM_SPEED.get(),pieces(p,"sea_silk")>=3?1:0,AttributeModifier.Operation.ADDITION);
        attribute(p,"luck",Attributes.LUCK,luck,AttributeModifier.Operation.ADDITION);
        attribute(p,"school_sword_speed",Attributes.ATTACK_SPEED,Set.of("liuyun_sword","chengying_sword").contains(id(p.getMainHandItem())) && DynastySchoolProgression.equippedSynergy(p,"sword")?.08:0,AttributeModifier.Operation.MULTIPLY_TOTAL);
        double all=pieces(p,"hongmeng")>=2?.06:pieces(p,"xuantian")>=2?.05:pieces(p,"taiyi")>=2?.04:0;
        long time=p.level().getDayTime()%24000;
        if(pieces(p,"tiangang")>=4 && time>=5500 && time<=6500 || pieces(p,"disha")>=4 && time>=17500 && time<=18500)all+=.08;
        if(pieces(p,"hunyuan")>=2)all+=day?.04:.02;
        attribute(p,"all_attack",Attributes.ATTACK_DAMAGE,all,AttributeModifier.Operation.MULTIPLY_TOTAL);
        attribute(p,"all_armor",Attributes.ARMOR,all,AttributeModifier.Operation.MULTIPLY_TOTAL);
        attribute(p,"all_health",Attributes.MAX_HEALTH,all,AttributeModifier.Operation.MULTIPLY_TOTAL);
        attribute(p,"all_speed",Attributes.MOVEMENT_SPEED,all,AttributeModifier.Operation.MULTIPLY_TOTAL);
        ownedEffect(p,MobEffects.NIGHT_VISION,pieces(p,"draco_king")>=2 || pieces(p,"zhuque")>=2);
        ownedEffect(p,MobEffects.DOLPHINS_GRACE,pieces(p,"sea_silk")>=4 && wet);
        skyJump(p);
        if(pieces(p,"beidou")<4) {n.remove("cod4StarIFrame");n.remove("cod4ContinuousSteps");}
        if(pieces(p,"xuanwu")<4)n.remove("cod4Shell");
        if(pieces(p,"xuanwu")<2 && !p.getMainHandItem().is(ExpansionContent.DUCK.get()))n.remove("cod4Counter");
        if(pieces(p,"hunyuan")<3)n.remove("cod4BalanceUntil");
        if(pieces(p,"hunyuan")<4)n.remove("cod4HunyuanQiUntil");
        if(pieces(p,"qinglong")<4)n.remove("cod4QinglongQiUntil");
        if(pieces(p,"dark_iron")<3 && pieces(p,"hunyuan")<4 && now(p)>=n.getLong("cod4QiUntil"))n.remove("cod4Rage");
        if(p.getHealth()>p.getMaxHealth())p.setHealth(p.getMaxHealth());
    }
    private static void skyJump(Player p) {
        var data=p.getPersistentData();var current=p.getEffect(MobEffects.JUMP);
        boolean enabled=pieces(p,"sky")>=4;
        if(enabled && current!=null && current.getAmplifier()<1) {
            // Vanilla would hide a weaker potion under our effect; save it before upgrading so
            // unequipping can restore its remaining duration instead of removing somebody else's buff.
            var backup=new CompoundTag();current.save(backup);data.put("cod4JumpBackup",backup);
            data.putLong("cod4JumpBackupUntil",current.isInfiniteDuration()?Long.MAX_VALUE:now(p)+current.getDuration());
            p.addEffect(new MobEffectInstance(MobEffects.JUMP,30,1,true,false));
            data.putBoolean("cod4Own_minecraft:jump_boost",true);
        }
        ownedEffect(p,MobEffects.JUMP,enabled,1);
        if(!enabled && data.contains("cod4JumpBackup")) {
            var backup=MobEffectInstance.load(data.getCompound("cod4JumpBackup"));
            long remaining=data.getLong("cod4JumpBackupUntil")-now(p);
            if(backup!=null && remaining>0 && !p.hasEffect(MobEffects.JUMP))
                p.addEffect(new MobEffectInstance(MobEffects.JUMP,backup.isInfiniteDuration()?-1:(int)Math.min(Integer.MAX_VALUE,remaining),backup.getAmplifier(),backup.isAmbient(),backup.isVisible(),backup.showIcon()));
            data.remove("cod4JumpBackup");data.remove("cod4JumpBackupUntil");
        }
    }
    private static void ownedEffect(Player p,MobEffect effect,boolean enabled) {
        ownedEffect(p,effect,enabled,0);
    }
    private static void ownedEffect(Player p,MobEffect effect,boolean enabled,int amplifier) {
        String key="cod4Own_"+net.minecraftforge.registries.ForgeRegistries.MOB_EFFECTS.getKey(effect);
        var current=p.getEffect(effect);boolean ours=current!=null && current.isAmbient() && !current.isVisible() && current.getAmplifier()==amplifier && current.getDuration()<=30;
        if(enabled && (current==null || ours)) {p.addEffect(new MobEffectInstance(effect,30,amplifier,true,false));p.getPersistentData().putBoolean(key,true);}
        else if(!enabled && p.getPersistentData().getBoolean(key)) {if(ours)p.removeEffect(effect);p.getPersistentData().remove(key);}
    }
    @SubscribeEvent public static void equipment(LivingEquipmentChangeEvent e) {if(e.getEntity() instanceof ServerPlayer p)refresh(p);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END || !(e.player instanceof ServerPlayer p))return;
        var n=p.getPersistentData();double moved=p.position().distanceToSqr(new net.minecraft.world.phys.Vec3(n.getDouble("cod4X"),n.getDouble("cod4Y"),n.getDouble("cod4Z")));
        n.putInt("cod4Still",moved<.0001?Math.min(80,n.getInt("cod4Still")+1):0);
        n.putDouble("cod4X",p.getX());n.putDouble("cod4Y",p.getY());n.putDouble("cod4Z",p.getZ());
        if(moved>.16 && moved<16) {
            n.putLong("cod4Moved",now(p));
        }
        advanceStarStep(p,moved);
        if(pieces(p,"cloth")>=4 && p.isSprinting() && moved>0 && moved<4) {
            var food=p.getFoodData();food.setExhaustion(Math.max(0,food.getExhaustionLevel()-(float)Math.sqrt(moved)*.1F));
        }
        Map<MobEffect,MobEffectInstance> pending=SHORTEN.remove(p);
        if(pending!=null) {
            shortening=true;
            try {for(var entry:pending.entrySet()) {
                var current=p.getEffect(entry.getKey());var desired=entry.getValue();
                if(current!=null && current.getAmplifier()==desired.getAmplifier() && current.getDuration()>desired.getDuration()) {p.removeEffect(entry.getKey());p.addEffect(desired);}
            }} finally {shortening=false;}
        }
        if(pieces(p,"sky")>=2 && p.getDeltaMovement().y<-.15 && !p.onGround())p.setDeltaMovement(p.getDeltaMovement().multiply(1,.65,1));
        if(pieces(p,"dragon_scale")>=2 && p.isInWater() || pieces(p,"draco_king")>=2 && p.isInWater())p.setAirSupply(p.getMaxAirSupply());
        if(pieces(p,"cinnabar")>=4 || now(p)<n.getLong("cod4Antidote"))p.removeEffect(MobEffects.POISON);
        if(p.tickCount%20!=0)return;
        refresh(p);
        if(pieces(p,"brocade")>=3 && now(p)-n.getLong("cod4LastCombat")>200)p.heal(1);
        if(pieces(p,"sea_silk")>=4 && p.isInWater())p.heal(1);
        if(has(p,"jade_cicada") && p.getHealth()<p.getMaxHealth()*.3 && ready(p,"cicada",3600)){p.heal(p.getMaxHealth()*.08F);CombatFeedback.send(p,CombatFeedback.HEAL);}
        purifyCinnabar(p);
        if(pieces(p,"xuantian")>=4)for(var mob:p.level().getEntitiesOfClass(Mob.class,p.getBoundingBox().inflate(4),m->m.getTarget()==p && !ExpansionEffects.boss(m)))mob.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,30,0));
        if(pieces(p,"draco_king")>=3) SummonedGuard.maintain(p,pieces(p,"draco_king")>=4?2:1);
        taiyiGlow(p);
        releaseHunyuanQi(p);
        if(has(p,"sea_pearl") && p.isInWater() && p.tickCount%60==0)CombatFeedback.send(p,CombatFeedback.WATER);
    }
    @SubscribeEvent public static void footsteps(net.minecraftforge.event.PlayLevelSoundEvent.AtEntity e) {
        if(e.getEntity() instanceof Player p && p.isShiftKeyDown() && pieces(p,"leather")>=4 && e.getSound()!=null && e.getSound().value().getLocation().getPath().endsWith(".step"))e.setCanceled(true);
    }
    @SubscribeEvent public static void enchanting(net.minecraftforge.event.entity.player.PlayerXpEvent.LevelChange e) {
        var p=e.getEntity();if(p.level().isClientSide || e.getLevels()>=0 || pieces(p,"jade")<2 || !(p.containerMenu instanceof net.minecraft.world.inventory.EnchantmentMenu))return;
        var saved=saved(p);int credit=saved.getInt("enchantCredit")-e.getLevels();int refund=credit/10;
        saved.putInt("enchantCredit",credit%10);e.setLevels(Math.min(0,e.getLevels()+refund));
    }
    @SubscribeEvent public static void wake(PlayerWakeUpEvent e) {if(!e.getEntity().level().isClientSide && pieces(e.getEntity(),"cloth")>=3)e.getEntity().getPersistentData().putLong("cod4Rested",now(e.getEntity())+1200);}
    @SubscribeEvent public static void fall(LivingFallEvent e) {
        if(!(e.getEntity() instanceof ServerPlayer p))return;
        if(pieces(p,"sky")>=4)e.setCanceled(true);else if(pieces(p,"bamboo")>=2)e.setDistance(Math.max(0,e.getDistance()-1));
    }
    /** Ten consecutive sprint displacement ticks; teleports, stopping and unequipping reset the sequence. */
    public static void advanceStarStep(Player p,double moved) {
        var n=p.getPersistentData();
        int steps=pieces(p,"beidou")>=4 && p.isSprinting() && !p.isPassenger() && moved>.01 && moved<4
                ? Math.min(10,n.getInt("cod4ContinuousSteps")+1) : 0;
        n.putInt("cod4ContinuousSteps",steps);
        if(steps==10 && ready(p,"starStep",200)) {
            n.putInt("cod4ContinuousSteps",0);n.putLong("cod4StarIFrame",now(p)+4);
            CombatFeedback.send(p,CombatFeedback.STAR);
        }
    }
    public static boolean auspiciousGuard(Player p,float roll) {
        return pieces(p,"qilin")>=3 && roll<.15F;
    }
    public static boolean taiyiGlow(ServerPlayer p){
        if(pieces(p,"taiyi")<4||p.experienceLevel<30||!ready(p,"taiyiGlow",6000))return false;
        p.heal(p.getMaxHealth()*.05F);CombatFeedback.send(p,CombatFeedback.HEAL);
        com.dynasty.cod3.Cod3Vfx.send(p.serverLevel(),14,p.position(),p.getLookAngle(),20,.1,0xE7C866);
        return true;
    }
    public static void phoenixIgnited(Player p) {
        p.getPersistentData().putLong("cod4PhoenixAttack",now(p)+60);
        CombatFeedback.send(p,CombatFeedback.FIRE_RING);
    }
    public static boolean phoenixAttackActive(Player p) {
        return p.isOnFire() || now(p)<p.getPersistentData().getLong("cod4PhoenixAttack");
    }
    /** Balance is a recent neutralisation of the two existing effects, never merely Yang alone. */
    public static boolean balanced(Player p){
        return pieces(p,"hunyuan")>=3&&now(p)<p.getPersistentData().getLong("cod4BalanceUntil")
                &&!p.hasEffect(ExpansionEffects.YIN.get())&&!p.hasEffect(ExpansionEffects.YANG.get());
    }
    public static void neutralisedQi(Player p){
        if(pieces(p,"hunyuan")>=3)p.getPersistentData().putLong("cod4BalanceUntil",now(p)+100);
    }
    /** All three grants feed the original combo resource. Equipment grants require the equipment. */
    public static boolean qiActive(Player p){
        var n=p.getPersistentData();long time=now(p);
        return time<n.getLong("cod4QiUntil")||pieces(p,"qinglong")>=4&&time<n.getLong("cod4QinglongQiUntil")
                ||pieces(p,"hunyuan")>=4&&time<n.getLong("cod4HunyuanQiUntil");
    }
    public static boolean releaseHunyuanQi(Player p){
        var n=p.getPersistentData();
        if(pieces(p,"hunyuan")<4||n.getInt("cod4Rage")<5||!ready(p,"hunyuanQi",200))return false;
        n.putInt("cod4Rage",0);n.putLong("cod4HunyuanQiUntil",now(p)+100);
        CombatFeedback.send(p,CombatFeedback.PERFECT);return true;
    }
    public static boolean comboWave(ServerPlayer p,LivingEntity target,int combo){
        if(combo<5||!(pieces(p,"qinglong")>=3||has(p,"dragon_pearl")||strengthenedWave(p))||!ready(p,"comboWave",60))return false;
        var packet=new com.dynasty.cod3.Cod3VisualPacket(p.level().dimension().location().toString(),7,target.getId(),
                p.getRandom().nextLong(),now(p),20,strengthenedWave(p)?1.3:1,target.position(),p.getLookAngle(),"qinglong_combo_wave",0,0x54CCB8);
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(
                target.getX(),target.getY(),target.getZ(),32,p.level().dimension())),packet);
        if(strengthenedWave(p) && !ExpansionEffects.boss(target))
            target.knockback(.35,p.getX()-target.getX(),p.getZ()-target.getZ());
        if(strengthenedWave(p) && id(p.getMainHandItem()).equals("thunder_spear"))ExpansionEffects.apply(target,ExpansionEffects.THUNDER,60);
        if(pieces(p,"qinglong")>=4){p.heal(p.getMaxHealth()*.02F);p.getPersistentData().putLong("cod4QinglongQiUntil",now(p)+60);}
        return true;
    }
    public static void smallThunder(Player p,LivingEntity target) {
        if(!ExpansionWeapons.enemy(p,target))return;
        // Add to this real hit once, without a lightning entity that can burn terrain or hit bystanders.
        CombatFeedback.send(target,CombatFeedback.SMALL_THUNDER);
    }
    public static void purifyCinnabar(ServerPlayer p) {
        if(pieces(p,"cinnabar")<3 || !p.hasEffect(ExpansionEffects.SHA.get()))return;
        p.removeEffect(ExpansionEffects.SHA.get());
        for(var ally:p.level().getEntitiesOfClass(LivingEntity.class,p.getBoundingBox().inflate(3),
                e->e==p || e.isAlliedTo(p) || e instanceof net.minecraft.world.entity.TamableAnimal pet && p.getUUID().equals(pet.getOwnerUUID())))
            if(ally.distanceToSqr(p)<=9)ally.removeEffect(ExpansionEffects.SHA.get());
        CombatFeedback.send(p,CombatFeedback.CINNABAR);
    }
    @SubscribeEvent public static void effect(MobEffectEvent.Added e) {
        if(!shortening && e.getEntity() instanceof ServerPlayer p && pieces(p,"cinnabar")>=2 && !e.getEffectInstance().getEffect().isBeneficial()) {
            var effect=e.getEffectInstance();if(effect.isInfiniteDuration())return;
            SHORTEN.computeIfAbsent(p,k->new HashMap<>()).put(effect.getEffect(),new MobEffectInstance(effect.getEffect(),Math.max(1,effect.getDuration()*3/4),effect.getAmplifier(),effect.isAmbient(),effect.isVisible(),effect.showIcon()));
        }
    }
    @SubscribeEvent public static void reflect(net.minecraftforge.event.entity.ProjectileImpactEvent e) {
        if(e.getProjectile().level().isClientSide || !(e.getProjectile() instanceof net.minecraft.world.entity.projectile.AbstractArrow arrow) || !(e.getRayTraceResult() instanceof net.minecraft.world.phys.EntityHitResult hit) || !(hit.getEntity() instanceof ServerPlayer p))return;
        if(pieces(p,"bamboo")>=4 && p.getRandom().nextFloat()<.05F) {e.setCanceled(true);arrow.setOwner(p);arrow.setDeltaMovement(arrow.getDeltaMovement().scale(-.8));arrow.pickup=net.minecraft.world.entity.projectile.AbstractArrow.Pickup.DISALLOWED;arrow.hurtMarked=true;CombatFeedback.send(p,CombatFeedback.BLOCK);}
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void block(ShieldBlockEvent e) {
        if(!(e.getEntity() instanceof ServerPlayer p))return;
        var n=p.getPersistentData();n.putLong("cod4BronzeGuard",now(p)+60);
        boolean perfect=perfectGuard(p);
        String blocking=id(p.getUseItem());
        if(Set.of("zhenyue_blade","beichen_spear").contains(blocking) && DynastySchoolProgression.equippedSynergy(p,"guard"))
            e.setBlockedDamage(Math.min(e.getOriginalBlockedDamage(),e.getBlockedDamage()+e.getOriginalBlockedDamage()*.08F));
        if(blocking.equals("xuanwu_blade") && symbolEquipped(p,"xuanwu"))
            e.setBlockedDamage(Math.min(e.getOriginalBlockedDamage(),e.getBlockedDamage()+e.getOriginalBlockedDamage()*.1F));
        if(perfect && pieces(p,"xuanwu")>=2) {
            // Run after the school's partial block. Raise a 50% weapon block to 60%
            // of the original hit; an ordinary shield's full block remains full.
            e.setBlockedDamage(Math.min(e.getOriginalBlockedDamage(),Math.max(e.getBlockedDamage(),e.getOriginalBlockedDamage()*.6F)));
            p.removeEffect(ExpansionEffects.STAGGER.get());n.putLong("cod4Counter",now(p)+60);
            if(pieces(p,"xuanwu")>=4)n.putBoolean("cod4Shell",true);
        }
        if(has(p,"heart_mirror") && !has(p,"bronze_mirror") && e.getDamageSource().getEntity() instanceof LivingEntity attacker && ExpansionWeapons.enemy(p,attacker)) {
            DynastyTrinketOnHit.syntheticDamage(()->attacker.hurt(p.damageSources().thorns(p),Math.min(20,e.getBlockedDamage()*.1F)));
        }
        CombatFeedback.send(p,perfect?CombatFeedback.PERFECT:CombatFeedback.BLOCK);
    }
    /** Vanilla raises a block after five ticks; the next six active ticks are the 0.3s window. */
    public static boolean perfectGuard(Player p){return p.isBlocking()&&p.getTicksUsingItem()>=5&&p.getTicksUsingItem()<11;}
    @SubscribeEvent(priority=EventPriority.LOW) public static void attack(LivingAttackEvent e) {
        if(!(e.getEntity() instanceof ServerPlayer p) || e.getAmount()<=0)return;
        if(now(p)<p.getPersistentData().getLong("cod4StarIFrame") && !e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY))e.setCanceled(true);
        if(e.getSource().is(DamageTypeTags.IS_FIRE) && (pieces(p,"phoenix")>=2 || pieces(p,"zhuque")>=2 || has(p,"phoenix_feather_charm"))) {
            if(has(p,"phoenix_ring"))phoenixIgnited(p);
            e.setCanceled(true);p.clearFire();p.getPersistentData().putLong("cod4PhoenixSpeed",now(p)+60);
            if(pieces(p,"phoenix")>=4 && ready(p,"fireRing",80)) {
                CombatFeedback.send(p,CombatFeedback.FIRE_RING);
                for(var mob:p.level().getEntitiesOfClass(LivingEntity.class,p.getBoundingBox().inflate(3),m->ExpansionWeapons.enemy(p,m) && m.distanceToSqr(p)<=9))mob.setSecondsOnFire(3);
            }
        }
    }
    @SubscribeEvent(priority=EventPriority.LOW) public static void hurt(LivingHurtEvent e) {
        if(e.getEntity().level().isClientSide || e.getAmount()<=0 || e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY) || DynastyTrinketOnHit.isSyntheticDamage())return;
        if(e.getEntity() instanceof ServerPlayer p) {
            var n=p.getPersistentData();n.putLong("cod4LastCombat",now(p));
            if((pieces(p,"dark_iron")>=3 && n.getInt("cod4Still")>=40) || pieces(p,"hunyuan")>=4)n.putInt("cod4Rage",Math.min(5,n.getInt("cod4Rage")+1));
            if(has(p,"jade_pendant") && !has(p,"heart_mirror") && p.getHealth()<p.getMaxHealth()*.4F)e.setAmount(e.getAmount()*.88F);
            if(auspiciousGuard(p,p.getRandom().nextFloat())) {
                e.setAmount(0);e.setCanceled(true);CombatFeedback.send(p,CombatFeedback.PERFECT);return;
            }
            if(pieces(p,"bronze")>=2 && p.getRandom().nextFloat()<.1F)
                p.level().playSound(null,p.blockPosition(),net.minecraft.sounds.SoundEvents.SHIELD_BLOCK,net.minecraft.sounds.SoundSource.PLAYERS,.7F,.65F);
            if(e.getAmount()>0 && pieces(p,"qilin")>=4 && p.getHealth()<p.getMaxHealth()*.25 && ready(p,"qilinShield",6000)){e.setAmount(0);CombatFeedback.send(p,CombatFeedback.PERFECT);}
            if(pieces(p,"bronze")>=4 && e.getSource().getEntity() instanceof com.dynasty.entity.ImperialSoldier)e.setAmount(e.getAmount()*.8F);
            if(has(p,"fox_tail_charm") && p.getRandom().nextFloat()<.1 && e.getSource().getEntity() instanceof Mob mob && !ExpansionEffects.boss(mob)){mob.setTarget(null);mob.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,1));}
            if(p.isUsingItem() && p.getUseItem().is(ExpansionContent.DUCK.get()) && p.getOffhandItem().is(ExpansionContent.DUCK.get()) && !e.getSource().is(DamageTypeTags.BYPASSES_SHIELD)) {
                if(e.getSource().getSourcePosition()!=null && p.getLookAngle().dot(e.getSource().getSourcePosition().subtract(p.position()).normalize())>0) {e.setAmount(e.getAmount()*.35F);n.putLong("cod4Counter",now(p)+60);CombatFeedback.send(p,CombatFeedback.BLOCK);}
            }
        }
        if(e.getSource().getEntity() instanceof SecondaryMob mob && (mob.spec.id().equals("golden_leopard") || mob.spec.id().equals("gray_falcon")) && e.getEntity().getHealth()>=e.getEntity().getMaxHealth()*.9F)e.setAmount(e.getAmount()*1.5F);
        if(!(e.getSource().getEntity() instanceof ServerPlayer p) || !ExpansionWeapons.enemy(p,e.getEntity()))return;
        var n=p.getPersistentData();n.putLong("cod4LastCombat",now(p));float bonus=0;boolean day=p.level().isDay();
        if(pieces(p,"cloth")>=3 && now(p)<n.getLong("cod4Rested"))bonus+=.08F;
        if(pieces(p,"leather")>=3 && p.isShiftKeyDown() && ready(p,"sneak",120))bonus+=.3F;
        if(pieces(p,"general")>=4 && n.getInt("cod4Still")>=40)bonus+=.15F;
        if(pieces(p,"silver")>=2 && e.getEntity().getMobType()==MobType.UNDEAD)bonus+=.15F;
        if(pieces(p,"silver")>=3 && !day)bonus+=.1F;
        if(pieces(p,"jade")>=3 && p.getHealth()>=p.getMaxHealth())bonus+=.08F;
        if(pieces(p,"dragon_scale")>=3 && p.isInWater())bonus+=.12F;
        if(pieces(p,"sky")>=3 && !p.onGround())bonus+=.2F;
        if(pieces(p,"xuantian")>=3 && ExpansionEffects.boss(e.getEntity()))bonus+=.1F;
        if(pieces(p,"zhuque")>=3 && e.getSource().is(DamageTypeTags.IS_FIRE))bonus+=.15F;
        if(pieces(p,"tiangang")>=2 && day || pieces(p,"disha")>=2 && !day)bonus+=.1F;
        if(pieces(p,"beidou")>=3 && now(p)-n.getLong("cod4Moved")<60)bonus+=.1F;
        if(pieces(p,"hongmeng")>=3 && e.getEntity() instanceof com.dynasty.ritual.ZhenyuanSovereign)bonus+=.15F;
        if(pieces(p,"dark_iron")>=4 && n.getInt("cod4Rage")>=5){n.putInt("cod4Rage",0);bonus+=.25F;CombatFeedback.send(e.getEntity(),CombatFeedback.HEAVY);}
        if(now(p)<n.getLong("cod4Counter")){n.remove("cod4Counter");bonus+=pieces(p,"xuanwu")>=3?.2F:.1F;}
        if(pieces(p,"baihu")>=3 && p.isSprinting() && ready(p,"sprintStrike",60)){bonus+=.4F;if(pieces(p,"baihu")>=4)ExpansionEffects.apply(e.getEntity(),ExpansionEffects.STAGGER,40);}
        if(pieces(p,"baihu")>=2 && !ExpansionEffects.boss(e.getEntity()))e.getEntity().knockback(.5,p.getX()-e.getEntity().getX(),p.getZ()-e.getEntity().getZ());
        if(balanced(p))bonus+=.1F;
        if(pieces(p,"ziwei")>=3 && p.getRandom().nextFloat()<.1){bonus+=.5F;n.putLong("cod4Crit",now(p)+60);CombatFeedback.send(e.getEntity(),CombatFeedback.CRITICAL);}
        if(pieces(p,"ziwei")>=4 && now(p)<n.getLong("cod4Crit"))bonus+=.15F;
        if(has(p,"dragon_scale_charm") && net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(e.getEntity().getType()).getPath().contains("dragon"))bonus+=.15F;
        if(has(p,"phoenix_ring") && phoenixAttackActive(p))bonus+=.15F;
        float thunderDamage=0;
        if(has(p,"storm_charm") && p.level().isThundering() && p.getRandom().nextFloat()<.1F) {
            smallThunder(p,e.getEntity());thunderDamage=4;
        }
        if(e.getSource().getDirectEntity()==p && e.getSource().is(net.minecraft.world.damagesource.DamageTypes.PLAYER_ATTACK) && DynastySchoolCombat.chargedPrimary(p,e.getEntity())) {
            int combo=DynastyTrinketOnHit.advanceCombo(p,e.getEntity());
            if(pieces(p,"qinglong")>=2)bonus+=.06F*Math.min(3,combo);
            if(comboWave(p,e.getEntity(),combo))bonus+=strengthenedWave(p)?.18F:.12F;
        }
        var used=DynastySchoolCombat.firingWeapon(e.getSource(),p.getMainHandItem());
        if(e.getSource().getDirectEntity() instanceof net.minecraft.world.entity.projectile.AbstractArrow && Set.of("zhuxing_bow","fengling_bow").contains(id(used)) && DynastySchoolProgression.equippedSynergy(p,"archer")){bonus+=.08F;CombatFeedback.send(e.getEntity(),CombatFeedback.STAR);}
        e.setAmount(e.getAmount()*(1+bonus+seriesBonus(p,e.getEntity(),used))+twinBonus(p,used)+thunderDamage);
    }
    public static boolean symbolEquipped(Player p,String symbol) {
        return pieces(p,symbol)>0 || DynastyTrinkets.activeIds(p).stream().anyMatch(s->s.startsWith(symbol+"_"));
    }
    public static boolean strengthenedWave(Player p) {
        return Set.of("qinglong_dao","thunder_spear").contains(id(p.getMainHandItem())) && symbolEquipped(p,"qinglong");
    }
    private static float seriesBonus(Player p,LivingEntity target,ItemStack used) {
        String main=id(used);
        float bonus=0;
        String element=main.startsWith("xuanwu")?"xuanwu":main.startsWith("zhuque")?"zhuque":main.startsWith("qinglong")||main.equals("thunder_spear")?"qinglong":main.startsWith("baihu")?"baihu":"";
        if(!element.isEmpty() && symbolEquipped(p,element))bonus+=.1F;
        return bonus+revengeBonus(p,target,main);
    }
    /** Canonical drop/gift provenance, with no extra weapon-use gate or second reward flag. */
    public static float revengeBonus(Player p,LivingEntity target,String weapon){
        if(p.isAlliedTo(target)||target.isAlliedTo(p))return 0;
        var n=p.getPersistentData();boolean eligible=false;
        String source=switch(weapon){case "dragon_spear"->"undead_first_emperor";case "yitian_sword"->"rebel_general";
            case "qinggang_sword"->"eunuch_mastermind";case "dragon_slayer"->"dragon_emperor";default->"";};
        if(!source.isEmpty())eligible=n.getBoolean("dynasty_firstkill_"+source)&&faction(target,source);
        if(weapon.equals("sunbow"))eligible=n.getBoolean("dynasty_gift_sunbow")&&faction(target,"phoenix");
        if(weapon.equals("supreme_sword"))eligible=(DynastyStats.getRank(p)>=17||n.getBoolean("dynasty_gift_supreme_sword"))&&faction(target,"court");
        if(weapon.equals("seven_star_saber")&&n.getInt("dynasty_boss_kinds")>=5){
            var defeated=new HashSet<>(Arrays.asList(n.getString("dynasty_boss_kinds_list").split(",")));
            for(String boss:List.of("dragon_emperor","rebel_general","eunuch_mastermind","undead_first_emperor","nine_heaven_general","dragon_king"))
                if((defeated.contains(boss)||n.getBoolean("dynasty_firstkill_"+boss))&&faction(target,boss)){eligible=true;break;}
        }
        return eligible?.15F:0;
    }
    private static boolean faction(LivingEntity target,String source){
        var id=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(target.getType());if(id==null)return false;
        if(source.equals("undead_first_emperor")&&target.getMobType()==MobType.UNDEAD)return true;
        if(!id.getNamespace().equals("dynasty"))return false;String name=id.getPath();
        return switch(source){
            case "undead_first_emperor"->name.equals(source);
            case "dragon_king"->Set.of("dragon_king","merfolk","shrimp_soldier","crab_soldier","river_imp","carp_spirit").contains(name);
            case "rebel_general"->name.startsWith("rebel")||name.equals("bandit_thug");
            case "nine_heaven_general"->Set.of("thunder_envoy","nine_heaven_general").contains(name);
            case "phoenix"->name.equals("phoenix");
            case "court"->Set.of("rebel_general","rebel_soldier","bandit_thug","assassin","eunuch_mastermind").contains(name);
            default->Set.of(source,"royal_guard","jade_guard").contains(name);
        };
    }
    public static float twinBonus(Player p,ItemStack used) {
        Set<String> imperial=Set.of("qilin_war_axe","taiyi_sword","baihu_glaive","thunder_spear","ziwei_saber","zhuque_bow");
        String main=id(used),off=id(p.getOffhandItem());
        return imperial.contains(main) && imperial.contains(off) && !main.equals(off)?(float)DynastyBalance.weaponBonus(main)*.1F:0;
    }
    public static int cooldown(Player p,int base) {return pieces(p,"taiyi")>=3?Math.max(1,base*9/10):base;}
    public static String id(ItemStack s) {var id=net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(s.getItem());return id!=null && id.getNamespace().equals("dynasty")?id.getPath():"";}
    public static void symbolHit(ServerPlayer p,LivingEntity target,ItemStack used) {
        if(!ExpansionWeapons.enemy(p,target))return;
        String weapon=id(used);
        if(Set.of("zhuque_fan","zhuque_bow").contains(weapon) && symbolEquipped(p,"zhuque") && !target.fireImmune() && ready(p,"symbolFire",40)) {
            target.setSecondsOnFire(4);CombatFeedback.send(target,CombatFeedback.FIRE_RING);
        }
        if(weapon.equals("baihu_glaive") && symbolEquipped(p,"baihu") && ready(p,"symbolBreak",80)) {
            ExpansionEffects.apply(target,ExpansionEffects.BREAK,60);CombatFeedback.send(target,CombatFeedback.ARMOR);
        }
    }
    @SubscribeEvent public static void damage(LivingDamageEvent e) {
        if(e.getEntity().level().isClientSide || e.getAmount()<=0)return;
        if(e.getSource().getEntity() instanceof ServerPlayer attacker && !DynastyTrinketOnHit.isSyntheticDamage()
                && (e.getSource().getDirectEntity()==attacker || e.getSource().getDirectEntity() instanceof net.minecraft.world.entity.projectile.AbstractArrow))
            symbolHit(attacker,e.getEntity(),DynastySchoolCombat.firingWeapon(e.getSource(),attacker.getMainHandItem()));
        if(e.getSource().getEntity() instanceof ServerPlayer p && pieces(p,"silver")>=4 && !p.level().isDay() && ExpansionWeapons.enemy(p,e.getEntity()))p.heal(e.getAmount()*.05F);
        if(!(e.getEntity() instanceof ServerPlayer p) || e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY) || e.getAmount()<p.getHealth())return;
        boolean shell=pieces(p,"xuanwu")>=4 && p.getPersistentData().getBoolean("cod4Shell");
        String key=pieces(p,"hongmeng")>=4?"hongmengLife":pieces(p,"zhuque")>=4?"zhuqueLife":has(p,"phoenix_feather_charm")?"phoenixLife":shell?"xuanwuLife":"";
        if(!key.isEmpty() && ready(p,"lastStand",6000)) {e.setAmount(0);p.setHealth(Math.max(1,p.getMaxHealth()*.15F));p.getPersistentData().remove("cod4Shell");CombatFeedback.send(p,CombatFeedback.HEAL);}
    }
    @SubscribeEvent public static void kill(LivingDeathEvent e) {
        if(e.getEntity().getKillCredit() instanceof ServerPlayer p && (pieces(p,"tiangang")>=3 && p.level().isDay() || pieces(p,"disha")>=3 && !p.level().isDay()))p.heal(p.getMaxHealth()*.02F);
    }
    private EquipmentBehaviors() { }
}
