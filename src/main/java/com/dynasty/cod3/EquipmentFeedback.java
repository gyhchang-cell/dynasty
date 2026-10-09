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
    @SubscribeEvent public static void damage(LivingDamageEvent e){
        if(e.getAmount()>0&&e.getEntity() instanceof ServerPlayer victim){
            var armor=DynastySetBonus.wornArmorIds(victim);
            if(armor.stream().anyMatch(x->x.startsWith("bronze_")||x.startsWith("silver_")||x.startsWith("general_")))Cod3Vfx.send(victim.serverLevel(),12,victim.position().add(0,1,0),victim.getLookAngle(),6,.08);
            if(e.getAmount()>=6&&armor.stream().anyMatch(x->x.startsWith("dark_iron_")||x.startsWith("xuanwu_")))Cod3Vfx.send(victim.serverLevel(),27,victim.position(),victim.getLookAngle(),8,.12);
        }
        if(e.getAmount()<=0||!(e.getSource().getEntity() instanceof ServerPlayer p)||!(p.level() instanceof ServerLevel l))return;
        if(DynastyTrinketOnHit.isSyntheticDamage()||QinglongDescent.isDragonDamage(e.getSource())||DynastyBowRitual.isSolarDamage(e.getSource()))return;
        var stack=p.getMainHandItem();var id=ForgeRegistries.ITEMS.getKey(stack.getItem());if(id==null||!id.getNamespace().equals(Dynasty.MODID)||!(stack.getItem() instanceof SwordItem||stack.getItem() instanceof AxeItem))return;
        // Imperial weapons already own their mesh/phantom presentation.
        if(id.getPath().equals("qinglong_dao")||id.getPath().equals("houyi_bow"))return;
        var n=p.getPersistentData();long now=l.getGameTime();if(n.getLong("cod3_hit_at")==now)return;
        int combo=now-n.getLong("cod3_hit_at")<=40?n.getInt("cod3_combo")%3+1:1;n.putInt("cod3_combo",combo);n.putLong("cod3_hit_at",now);
        boolean critical=p.fallDistance>0&&!p.onGround();int vfx=template(id.getPath(),combo,critical);
        Cod3Vfx.send(l,vfx,e.getEntity().position(),p.getLookAngle(),Cod3Catalog.vfx(vfx).duration(),.2+combo*.035,tint(id.getPath()));
        if(critical)Cod3Vfx.send(l,12,e.getEntity().position().add(0,.8,0),p.getLookAngle(),8,.15);
    }
    @SubscribeEvent public static void arrow(EntityJoinLevelEvent e){
        if(!(e.getLevel() instanceof ServerLevel l)||!(e.getEntity() instanceof AbstractArrow arrow)||!(arrow.getOwner() instanceof ServerPlayer p))return;
        ItemStack bow=firingWeapon(arrow,p);
        var id=ForgeRegistries.ITEMS.getKey(bow.getItem());if(id==null||!id.getNamespace().equals(Dynasty.MODID)||!ranged(bow))return;
        arrow.getPersistentData().putLong("cod3_trail_start",l.getGameTime());arrow.getPersistentData().putLong("cod3_trail_seed",l.random.nextLong());
        arrow.getPersistentData().putInt("cod3_trail_tint",tint(id.getPath()));
        arrow.getPersistentData().putString("cod3_trail_weapon",id.toString());
        var packet=arrowPacket(l,arrow);
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(p.getX(),p.getY(),p.getZ(),32,l.dimension())),packet);
    }
    private static boolean ranged(ItemStack stack){return stack.getItem() instanceof BowItem||stack.getItem() instanceof CrossbowItem;}
    public static ItemStack firingWeapon(AbstractArrow arrow,Player p){
        var data=arrow.getPersistentData();
        if(data.contains("cod4FiringWeapon"))return ItemStack.of(data.getCompound("cod4FiringWeapon"));
        if(data.contains(DynastySchoolCombat.FIRING_WEAPON))return ItemStack.of(data.getCompound(DynastySchoolCombat.FIRING_WEAPON));
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
    public static void proc(Player attacker,LivingEntity target,int code){
        if(attacker.level() instanceof ServerLevel l){
            var n=attacker.getPersistentData();String key="cod3_proc_at_"+code;if(n.contains(key)&&n.getLong(key)==l.getGameTime())return;n.putLong(key,l.getGameTime());
            Cod3Vfx.send(l,switch(code){case 1->37;case 2->34;case 3,4->12;case 5->29;case 6->31;default->14;},target.position().add(0,.5,0),attacker.getLookAngle(),10,.12);
        }
    }
}
