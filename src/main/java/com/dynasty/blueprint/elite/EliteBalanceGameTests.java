package com.dynasty.blueprint.elite;

import com.dynasty.Dynasty;
import com.dynasty.DynastyGear;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Native equipment/damage-pipeline calibration at the existing bronze and silver entry tiers. */
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class EliteBalanceGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="elite_balance")
    public static void actualEntryWeaponsPreserveEliteDurabilityAndUpgradeProgression(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<10;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var types=List.of(EliteContent.HEADLESS.get(),EliteContent.BIRD.get(),EliteContent.MECHANIST.get(),EliteContent.JINWU.get(),EliteContent.FOX.get(),EliteContent.HAMMER.get(),EliteContent.SPIDER_WOMAN.get(),EliteContent.ALCHEMIST.get());
        var mobs=new ArrayList<Monster>();
        for(int i=0;i<types.size();i++){
            var m=(Monster)h.spawn(types.get(i),new BlockPos(3+(i%3)*5,2,3+(i/3)*8));m.setNoAi(true);m.setNoGravity(true);m.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);mobs.add(m);
        }
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"elite-tier-qa"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(GameType.SURVIVAL);p.setNoGravity(true);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyGear.SWORD_BRONZE.get()));h.getLevel().addNewPlayer(p);
        h.onEachTick(()->{if(!p.isRemoved())p.doTick();});
        var bronze=new HashMap<EntityType<?>,Float>();
        h.runAfterDelay(25,()->{
            for(var m:mobs){
                p.moveTo(m.position().add(0,0,-1));p.resetAttackStrengthTicker();for(int i=0;i<22;i++)p.doTick();
                float before=m.getHealth();p.attack(m);float damage=before-m.getHealth();bronze.put(m.getType(),damage);
                int hits=damage<=0?Integer.MAX_VALUE:(int)Math.ceil(m.getMaxHealth()/damage);
                h.assertTrue(damage>0&&hits>=5&&hits<=20,"Bronze entry weapon must require five to twenty fully charged elite contacts: "+m.getType()+" damage="+damage+" hits="+hits);
                Dynasty.LOGGER.info("ELITE_TIER_SAMPLE weapon=bronze entity={} hp={} armor={} damage={} fullHitEstimate={}",m.getType(),m.getMaxHealth(),m.getArmorValue(),damage,hits);
                m.setHealth(m.getMaxHealth());m.invulnerableTime=0;
            }
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyGear.SWORD_SILVER.get()));
        });
        h.runAfterDelay(52,()->{
            try{for(var m:mobs){
                p.moveTo(m.position().add(0,0,-1));p.resetAttackStrengthTicker();for(int i=0;i<22;i++)p.doTick();
                float before=m.getHealth();p.attack(m);float damage=before-m.getHealth();int hits=damage<=0?Integer.MAX_VALUE:(int)Math.ceil(m.getMaxHealth()/damage);
                h.assertTrue(damage>=bronze.get(m.getType())*1.8&&hits>=2&&hits<=6,"Silver upgrade improves actual damage while preserving at least two contacts: "+m.getType()+" damage="+damage+" hits="+hits);
                Dynasty.LOGGER.info("ELITE_TIER_SAMPLE weapon=silver entity={} hp={} armor={} damage={} fullHitEstimate={}",m.getType(),m.getMaxHealth(),m.getArmorValue(),damage,hits);
            }h.succeed();}finally{p.discard();for(var m:mobs)if(!m.isRemoved())m.discard();}
        });
    }
}
