package com.dynasty.cod3;

import com.dynasty.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Feedback observes successful attacks and set changes; it never re-applies attack damage. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class EquipmentFeedback {
    public static int tint(String id){
        if(id.matches(".*(thunder|leiting|leifu|beichen|beidou).*"))return 0xAACDFF;
        if(id.matches(".*(phoenix|zhuque|chiling).*"))return 0xFF8050;
        if(id.matches(".*(jade|longyuan|qinggang|qinglong|liuyun|chengying|fengling).*"))return 0x75DBBF;
        if(id.matches(".*(tianzi|supreme|bawang|gilded|gold|dragon_spear|qilin).*"))return 0xEBC370;
        if(id.matches(".*(sea|xuanwu).*"))return 0x70BEDA;
        if(id.matches(".*(seven_star|ziwei|taiyi|zhuxing).*"))return 0xDDD9FF;
        if(id.matches(".*(mu_mao|chang_gong|stone|shi_ge|tong_dao).*"))return 0xB59C79;
        return 0xDAE2E2;
    }
    public static int template(String id,int combo,boolean critical){
        return switch(id){
            case "mu_mao","dragon_spear","bawang_spear","thunder_spear","beichen_spear"->critical?12:3;
            case "longyuan_sword","dragon_slayer"->17;
            case "seven_star_saber","ziwei_saber","zhuxing_bow"->21;
            case "halberd_fangtian"->2;
            case "sea_trident"->7;
            case "leiting_hammer","leifu_staff","thunder_sword"->6;
            case "juling_axe","pojun_axe"->combo==3?27:26;
            case "xuantian_axe","hunyuan_staff"->25;
            case "qilin_war_axe","baihu_glaive"->18;
            case "tianzi_sword","supreme_sword"->12;
            case "taiyi_whisk","chiling_brush"->15;
            case "zhuque_fan"->19;
            case "yu_di"->26;
            case "tang_dao"->1;
            case "huan_shou_dao"->combo==3?34:29;
            case "zhenyue_blade"->20;
            case "liuyun_sword","chengying_sword"->23;
            default->critical?2:29;
        };
    }
    private static final String FIRING_SNAPSHOT="cod3_firing_weapon";
    /** Direct source only: a held replacement or an indirect spell is never the original hit item. */
    public static ItemStack sourceWeapon(LivingDamageEvent e){
        if(e.getAmount()<=0||DynastyTrinketOnHit.isSyntheticDamage()||QinglongDescent.isDragonDamage(e.getSource())
                ||DynastyBowRitual.isSolarDamage(e.getSource())||com.dynasty.EdictSpells.isSpell(e.getSource()))return ItemStack.EMPTY;
        if(e.getSource().getDirectEntity() instanceof AbstractArrow arrow&&e.getSource().getEntity() instanceof Player p&&arrow.getOwner()==p)return firingWeapon(arrow,p).copy();
        if(e.getSource().getEntity() instanceof Player p&&e.getSource().getDirectEntity()==p&&e.getSource().is(net.minecraft.world.damagesource.DamageTypes.PLAYER_ATTACK))return DynastySchoolCombat.primaryStack(p,e.getEntity());
        if(e.getSource().getEntity() instanceof LivingEntity mob&&!(mob instanceof Player)&&e.getSource().getDirectEntity()==mob&&e.getSource().is(net.minecraft.world.damagesource.DamageTypes.MOB_ATTACK))return mob.getMainHandItem().copy();
        return ItemStack.EMPTY;
    }
    @SubscribeEvent public static void damage(LivingDamageEvent e){
        if(e.getAmount()>0&&e.getEntity() instanceof ServerPlayer victim){
            var armor=DynastySetBonus.wornArmorIds(victim);
            if(armor.stream().anyMatch(x->x.startsWith("bronze_")||x.startsWith("silver_")||x.startsWith("general_")))Cod3Vfx.send(victim.serverLevel(),12,victim.position().add(0,1,0),victim.getLookAngle(),6,.08);
            if(e.getAmount()>=6&&armor.stream().anyMatch(x->x.startsWith("dark_iron_")||x.startsWith("xuanwu_")))Cod3Vfx.send(victim.serverLevel(),27,victim.position(),victim.getLookAngle(),8,.12);
        }
        if(e.getAmount()<=0||!(e.getSource().getEntity() instanceof ServerPlayer p)||!(p.level() instanceof ServerLevel l))return;
        if(DynastyTrinketOnHit.isSyntheticDamage()||QinglongDescent.isDragonDamage(e.getSource())||DynastyBowRitual.isSolarDamage(e.getSource()))return;
        var stack=sourceWeapon(e);var id=ForgeRegistries.ITEMS.getKey(stack.getItem());if(id==null||!id.getNamespace().equals(Dynasty.MODID))return;
        if(e.getSource().getDirectEntity() instanceof AbstractArrow arrow){
            if(!ranged(stack))return;var data=e.getEntity().getPersistentData();long now=l.getGameTime();
            if(data.contains("cod3_arrow_impact_at")&&now-data.getLong("cod3_arrow_impact_at")<3)return;
            data.putLong("cod3_arrow_impact_at",now);var direction=arrow.getDeltaMovement().lengthSqr()>.0001?arrow.getDeltaMovement().normalize():p.getLookAngle();
            Cod3Vfx.send(l,arrow.isCritArrow()?12:3,e.getEntity().position().add(0,.6,0),direction,8,.16,tint(id.getPath()));return;
        }
        if(!(stack.getItem() instanceof SwordItem||stack.getItem() instanceof AxeItem))return;
        // Imperial weapons already own their mesh/phantom presentation.
        if(id.getPath().equals("qinglong_dao")||id.getPath().equals("houyi_bow"))return;
        var n=p.getPersistentData();long now=l.getGameTime();if(n.getLong("cod3_hit_at")==now)return;
        int combo=now-n.getLong("cod3_hit_at")<=40?n.getInt("cod3_combo")%3+1:1;n.putInt("cod3_combo",combo);n.putLong("cod3_hit_at",now);
        boolean critical=DynastySchoolCombat.primaryCritical(p,e.getEntity());int vfx=template(id.getPath(),combo,critical);
        Cod3Vfx.send(l,vfx,e.getEntity().position(),p.getLookAngle(),Cod3Catalog.vfx(vfx).duration(),.2+combo*.035,tint(id.getPath()));
        if(critical)Cod3Vfx.send(l,12,e.getEntity().position().add(0,.8,0),p.getLookAngle(),8,.15);
    }
    @SubscribeEvent public static void arrow(EntityJoinLevelEvent e){
        if(!(e.getLevel() instanceof ServerLevel l)||!(e.getEntity() instanceof AbstractArrow arrow)||!(arrow.getOwner() instanceof ServerPlayer p))return;
        ItemStack bow=firingWeapon(arrow,p);
        var id=ForgeRegistries.ITEMS.getKey(bow.getItem());if(id==null||!id.getNamespace().equals(Dynasty.MODID)||!ranged(bow))return;
        arrow.getPersistentData().put(FIRING_SNAPSHOT,bow.copy().save(new net.minecraft.nbt.CompoundTag()));
        var data=arrow.getPersistentData();
        if(!data.contains("cod3_trail_start")){
            data.putLong("cod3_trail_start",l.getGameTime());data.putLong("cod3_trail_seed",l.random.nextLong());
            data.putInt("cod3_trail_tint",tint(id.getPath()));data.putString("cod3_trail_weapon",id.toString());
        }
        if(l.getGameTime()-data.getLong("cod3_trail_start")>=1200)return;
        var packet=arrowPacket(l,arrow);
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(p.getX(),p.getY(),p.getZ(),32,l.dimension())),packet);
    }
    private static boolean ranged(ItemStack stack){return stack.getItem() instanceof BowItem||stack.getItem() instanceof CrossbowItem;}
    public static ItemStack firingWeapon(AbstractArrow arrow,Player p){
        var data=arrow.getPersistentData();
        if(data.contains("cod4FiringWeapon"))return ItemStack.of(data.getCompound("cod4FiringWeapon"));
        if(data.contains(DynastySchoolCombat.FIRING_WEAPON))return ItemStack.of(data.getCompound(DynastySchoolCombat.FIRING_WEAPON));
        if(data.contains(FIRING_SNAPSHOT))return ItemStack.of(data.getCompound(FIRING_SNAPSHOT));
        // Already flying old arrows saved only the trail's registry identity.
        if(data.contains("cod3_trail_weapon")){
            var id=ResourceLocation.tryParse(data.getString("cod3_trail_weapon"));var item=id==null?null:ForgeRegistries.ITEMS.getValue(id);
            if(item!=null){var old=new ItemStack(item);if(ranged(old))return old;}
        }
        if(ranged(p.getUseItem()))return p.getUseItem();
        return ranged(p.getMainHandItem())?p.getMainHandItem():p.getOffhandItem();
    }
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
    public static void siegeImpact(net.minecraftforge.event.entity.ProjectileImpactEvent e){
        if(e.isCanceled()||!(e.getEntity() instanceof AbstractArrow arrow)||!(arrow.level() instanceof ServerLevel level)
                ||!arrow.getPersistentData().getBoolean("cod4Siege")||e.getRayTraceResult().getType()==net.minecraft.world.phys.HitResult.Type.MISS)return;
        Cod3Vfx.send(level,3,e.getRayTraceResult().getLocation(),arrow.getDeltaMovement().normalize(),8,.18,tint("siege_crossbow"));
    }
    private static Cod3VisualPacket arrowPacket(ServerLevel l,AbstractArrow arrow){return new Cod3VisualPacket(l.dimension().location().toString(),4,arrow.getId(),arrow.getPersistentData().getLong("cod3_trail_seed"),arrow.getPersistentData().getLong("cod3_trail_start"),1200,1,arrow.position(),arrow.getDeltaMovement().normalize(),"",0,arrow.getPersistentData().getInt("cod3_trail_tint"));}
    @SubscribeEvent public static void tracking(net.minecraftforge.event.entity.player.PlayerEvent.StartTracking e){
        if(e.getEntity() instanceof ServerPlayer p&&e.getTarget() instanceof AbstractArrow arrow&&arrow.getPersistentData().contains("cod3_trail_start")&&arrow.getDeltaMovement().lengthSqr()>.0025&&p.serverLevel().getGameTime()-arrow.getPersistentData().getLong("cod3_trail_start")<1200)
            com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->p),arrowPacket(p.serverLevel(),arrow));
    }
    @SubscribeEvent public static void set(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;
        if(p.tickCount%60==0)passiveAccessories(p);
        var worn=DynastySetBonus.wornArmorIds(p);String matched="";for(String armor:worn){String base=armor.replaceFirst("_(helmet|chestplate|leggings|boots)$","");if(worn.stream().filter(x->x.startsWith(base+"_")).count()==4){matched=base;break;}}
        var flags=p.getPersistentData();boolean fire=p.isOnFire(),water=p.isUnderWater(),low=p.getHealth()<p.getMaxHealth()*.4;
        if(!fire&&flags.getBoolean("cod3_was_fire")&&worn.stream().anyMatch(x->x.startsWith("phoenix_")||x.startsWith("zhuque_")))Cod3Vfx.send(p.serverLevel(),19,p.position(),p.getLookAngle(),12,.12);
        if(low&&!flags.getBoolean("cod3_was_low")&&worn.stream().anyMatch(x->x.startsWith("jade_")))Cod3Vfx.send(p.serverLevel(),14,p.position(),p.getLookAngle(),12,.12);
        if(water&&!flags.getBoolean("cod3_was_water")&&(worn.stream().anyMatch(x->x.startsWith("dragon_scale_")||x.startsWith("sea_silk_"))||DynastyTrinkets.has(p,"sea_pearl")||DynastyTrinkets.has(p,"jade_tortoise")||DynastyTrinkets.has(p,"sea_conch")))Cod3Vfx.send(p.serverLevel(),7,p.position(),p.getLookAngle(),12,.12);
        flags.putBoolean("cod3_was_fire",fire);flags.putBoolean("cod3_was_low",low);flags.putBoolean("cod3_was_water",water);
        String last=p.getPersistentData().getString("cod3_visual_set");p.getPersistentData().putString("cod3_visual_set",matched);
        if(matched.isEmpty()||matched.equals(last)||java.util.Set.of("cloth","bamboo","leather","brocade").contains(matched))return;
        Cod3Vfx.send(p.serverLevel(),matched.matches(".*(beidou|sky|taiyi|ziwei|hunyuan).*")?21:40,p.position(),p.getLookAngle(),20,.15);
        p.displayClientMessage(net.minecraft.network.chat.Component.translatable("cod3.dynasty.set.complete",p.getItemBySlot(EquipmentSlot.CHEST).getHoverName()),true);
    }
    /** Item-specific cue on the original actor wire; this never applies gameplay effects. */
    public static void accessory(Player p,String id){
        int tint=switch(id){
            case "jade_pendant"->0x75DBBF;case "jade_bi_disc"->0xB7E6DC;case "gold_seal_charm"->0xEBC370;
            case "dragon_scale_charm"->0x63BEB5;case "phoenix_feather_charm"->0xFF8050;case "qilin_horn_charm"->0xE1CB87;
            case "fox_tail_charm"->0xA6A3F5;case "silk_pouch"->0xC591BD;case "moon_pendant"->0xDDD9FF;case "jade_cicada"->0x99E5C5;
            default->0;
        };
        if(tint==0||!(p.level() instanceof ServerLevel l)||!p.isAlive()||!DynastyTrinkets.activeIds(p).contains(id))return;
        var n=p.getPersistentData();String key="cod3_accessory_at_"+id;long now=l.getGameTime(),elapsed=now-n.getLong(key);
        if(n.contains(key)&&elapsed>=0&&elapsed<20)return;n.putLong(key,now);
        Cod3Vfx.actor(p,"accessory_"+id,16,.8,tint);
    }
    private static void passiveAccessories(ServerPlayer p){
        var ids=DynastyTrinkets.activeIds(p);
        if(!p.level().isDay()){
            if(ids.contains("jade_bi_disc")&&!ids.contains("moon_pendant"))accessory(p,"jade_bi_disc");
            if(ids.contains("moon_pendant"))accessory(p,"moon_pendant");
        }
        if(ids.contains("qilin_horn_charm"))accessory(p,"qilin_horn_charm");
        if(ids.contains("silk_pouch"))accessory(p,"silk_pouch");
    }
    public static void proc(Player attacker,LivingEntity target,int code){
        if(attacker.level() instanceof ServerLevel l){
            var n=attacker.getPersistentData();String key="cod3_proc_at_"+code;if(n.contains(key)&&n.getLong(key)==l.getGameTime())return;n.putLong(key,l.getGameTime());
            Cod3Vfx.send(l,switch(code){case 1->37;case 2->34;case 3,4->12;case 5->29;case 6->31;default->14;},target.position().add(0,.5,0),attacker.getLookAngle(),10,.12);
            if(code<1||code>6)return;
            LivingEntity owner=code==1?attacker:target;
            int tint=switch(code){case 1->0xCF4A69;case 2->0xB76476;case 3,4->0xF2D178;case 6->0xAACDFF;default->0x75DBBF;};
            var packet=new Cod3VisualPacket(l.dimension().location().toString(),14,code==2?-1:owner.getId(),
                    code==2?l.random.nextLong():owner.getUUID().getLeastSignificantBits(),l.getGameTime(),10,.6,
                    owner.position(),target.position().subtract(attacker.position()),"accessory_proc_"+code,0,tint);
            com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(owner.getX(),owner.getY(),owner.getZ(),32,l.dimension())),packet);
        }
    }
}
