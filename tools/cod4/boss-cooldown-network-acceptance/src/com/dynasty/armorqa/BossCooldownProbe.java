package com.dynasty.armorqa;

import com.dynasty.expansion.EquipmentBehaviors;
import com.dynasty.expansion.ExpansionEffects;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** Native AI generates damage. QA supplies gear, positions and initial low health only. */
public final class BossCooldownProbe {
    static Mob boss;
    static long deadline,firstTick;
    static UUID victim;
    static final List<Map<String,Object>> hits=new ArrayList<>(),deaths=new ArrayList<>();
    static void engage(ServerPlayer player)throws Exception {
        victim=player.getUUID();
        if(boss==null) {
            boss=(Mob)Objects.requireNonNull(ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty:dragon_emperor"))).create(server.overworld());
            require(boss!=null&&ExpansionEffects.boss(boss),"Registered entity must satisfy production Boss classification");
            boss.moveTo(player.getX()+1,player.getY(),player.getZ(),90,0);
            server.overworld().addFreshEntity(boss);
        } else boss.teleportTo(player.getX()+1,player.getY(),player.getZ());
        boss.setNoAi(false);
        write("boss-fixture.json",obj("uuid",boss.getUUID().toString(),"entity",boss.getId(),"type",ForgeRegistries.ENTITY_TYPES.getKey(boss.getType()).toString(),"isProductionBoss",ExpansionEffects.boss(boss),"nativeAI",!boss.isNoAi(),"manualAttackOrDamageCall",false,"fixture","Registered Boss spawned next to low-health equipped player; native goals choose target and attack; freeze only after observed hit"));
    }
    static void freeze(){if(boss!=null)boss.setNoAi(true);}
    static void firstSave(ServerPlayer player)throws Exception {
        deadline=EquipmentBehaviors.saved(player).getLong("lastStand");firstTick=server.overworld().getGameTime();
        require(deadline>firstTick&&deadline<=firstTick+6000,"Original 6000tick deadline must come from production save proc");
        require(hits.stream().anyMatch(h->((Number)h.get("stage")).intValue()==10),"Actual Boss damage must precede first save");
        write("boss-first-save.json",obj("deadline",deadline,"tick",firstTick,"alive",player.isAlive(),"health",player.getHealth(),"boss",boss.getUUID().toString(),"manualCooldownAssignment",false));
    }
    static boolean fromBoss(net.minecraft.world.damagesource.DamageSource source) {
        return boss!=null&&source.getEntity()==boss;
    }
    @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true)
    public static void damage(LivingDamageEvent event) {
        if(event.getEntity().level().isClientSide||!fromBoss(event.getSource()))return;
        hits.add(obj("victim",event.getEntity().getUUID().toString(),"source",boss.getUUID().toString(),"stage",DeathQa.stage,"tick",event.getEntity().level().getGameTime(),"amountAfterProductionHandlers",event.getAmount(),"canceled",event.isCanceled(),"bossNativeAI",!boss.isNoAi(),"damageType",event.getSource().type().msgId()));
        try{write("boss-native-damage.json",hits);}catch(Exception x){throw new RuntimeException(x);}
    }
    @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true)
    public static void death(LivingDeathEvent event) {
        if(event.getEntity().level().isClientSide||!fromBoss(event.getSource()))return;
        deaths.add(obj("victim",event.getEntity().getUUID().toString(),"source",boss.getUUID().toString(),"stage",DeathQa.stage,"tick",event.getEntity().level().getGameTime(),"canceled",event.isCanceled()));
        try{write("boss-native-deaths.json",deaths);}catch(Exception x){throw new RuntimeException(x);}
    }
    static boolean finish()throws Exception {
        var player=server.getPlayerList().getPlayer(victim);
        long currentDeadline=EquipmentBehaviors.saved(player).getLong("lastStand");
        var checks=List.of(
            obj("name","native Boss AI caused first save","passed",hits.stream().anyMatch(h->((Number)h.get("stage")).intValue()==10&&Boolean.TRUE.equals(h.get("bossNativeAI")))),
            obj("name","native Boss killed re-equipped player before original deadline","passed",deaths.stream().anyMatch(d->((Number)d.get("stage")).intValue()==11&&!Boolean.TRUE.equals(d.get("canceled"))&&((Number)d.get("tick")).longValue()<deadline&&d.get("victim").equals(victim.toString()))),
            obj("name","same cooldown survives actual C2S unequip death respawn and re-equip","passed",deadline==currentDeadline&&deadline>firstTick,"deadline",deadline,"after",currentDeadline));
        boolean pass=checks.stream().allMatch(c->Boolean.TRUE.equals(c.get("passed")));
        write("boss-cooldown-result.json",obj("passed",pass,"checks",checks,"nativeDamage",hits,"nativeDeaths",deaths,"fullBossKillOrNaturalAcquisition",false,"clockModified",false));
        if(boss!=null)boss.discard();return pass;
    }
}
