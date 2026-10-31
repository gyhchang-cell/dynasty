package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Native AI regression fixtures, explicitly NOT real TCP multiplayer clients. */
@GameTestHolder("dynasty_guard_target_qa") @PrefixGameTestTemplate(false)
public final class GuardTargetAcceptance {
    private static ServerPlayer player(GameTestHelper h,String name,BlockPos at){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),name));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(at)));p.setNoGravity(true);
        p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);p.setHealth(5000);
        for(int i=0;i<61;i++)p.tick();
        h.getLevel().addNewPlayer(p);return p;
    }
    private static void suit(ServerPlayer p,int count){
        var slots=new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};
        var names=new String[]{"helmet","chestplate","leggings","boots"};
        for(int i=0;i<4;i++)p.setItemSlot(slots[i],i<count?new ItemStack(ExpansionContent.item("draco_king_"+names[i])):ItemStack.EMPTY);
    }
    private static void rejected(GameTestHelper h,SecondaryMob guard,LivingEntity target,String reason){
        float health=target.getHealth();var velocity=target.getDeltaMovement();String animation=guard.animation();
        h.assertTrue(!guard.canAttack(target),reason+": canAttack must reject");
        h.assertTrue(!guard.doHurtTarget(target),reason+": final melee boundary must reject");
        h.assertTrue(target.getHealth()==health&&target.getDeltaMovement().equals(velocity),reason+": no health/knockback mutation");
        h.assertTrue(guard.animation().equals(animation),reason+": no attack animation mutation");
        System.out.println("GUARD_TARGET_REJECT_PASS "+reason);
    }
    @GameTest(template="bow_ritual_test",batch="guard_target_regression",setupTicks=20,timeoutTicks=180)
    public static void leasedGuardSafetyAndNativeAi(GameTestHelper h){
        for(int x=1;x<=13;x++)for(int z=1;z<=13;z++){
            h.setBlock(x,1,z,Blocks.STONE);h.setBlock(x,2,z,Blocks.WATER);h.setBlock(x,3,z,Blocks.WATER);
        }
        var owner=player(h,"guard-owner",new BlockPos(6,2,6));
        var bystander=player(h,"guard-bystander",new BlockPos(7,2,6));
        suit(owner,4);owner.baseTick();h.assertTrue(owner.isInWater(),"Real lease needs water");
        SummonedGuard.maintain(owner,2);
        var guards=h.getLevel().getEntitiesOfClass(SecondaryMob.class,owner.getBoundingBox().inflate(10),
            m->m.getPersistentData().hasUUID("cod4Summoner")&&m.getPersistentData().getUUID("cod4Summoner").equals(owner.getUUID()));
        h.assertTrue(guards.size()==2,"Real maintain must lease the original shrimp/crab pair");
        var crab=guards.stream().filter(g->g.spec.id().equals("crab_soldier")).findFirst().orElseThrow();
        var shrimp=guards.stream().filter(g->g!=crab).findFirst().orElseThrow();
        var zombie=new Zombie(h.getLevel());zombie.moveTo(owner.getX()+2,owner.getY(),owner.getZ()+2,0,0);
        zombie.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);zombie.setHealth(5000);zombie.setNoAi(true);h.getLevel().addFreshEntity(zombie);
        SecondaryMob wild=SecondaryMobs.TYPES.get("crab_soldier").get().create(h.getLevel());
        h.assertTrue(wild!=null,"Original wild crab type exists");wild.moveTo(owner.getX()+4,owner.getY(),owner.getZ(),0,0);
        var scoreboard=h.getLevel().getScoreboard();var team=scoreboard.addPlayerTeam("guard-qa-"+UUID.randomUUID().toString().substring(0,8));
        try{
            rejected(h,crab,owner,"owner");rejected(h,crab,bystander,"unprovoked_bystander");rejected(h,crab,shrimp,"same_owner_guard");
            rejected(h,shrimp,bystander,"shrimp_bystander");
            h.assertTrue(crab.canAttack(zombie),"Valid Enemy still accepted");
            float before=zombie.getHealth();zombie.invulnerableTime=0;
            h.assertTrue(crab.doHurtTarget(zombie)&&zombie.getHealth()<before,"Valid Enemy receives real native damage");
            scoreboard.addPlayerToTeam(owner.getScoreboardName(),team);scoreboard.addPlayerToTeam(zombie.getScoreboardName(),team);
            rejected(h,crab,zombie,"owner_allied_enemy");scoreboard.removePlayerFromTeam(zombie.getScoreboardName(),team);scoreboard.removePlayerFromTeam(owner.getScoreboardName(),team);
            var data=crab.getPersistentData();long expires=data.getLong("cod4Expires"),generation=data.getLong("cod4GuardGeneration");
            data.putLong("cod4Expires",h.getLevel().getGameTime());rejected(h,crab,zombie,"expired_lease");data.putLong("cod4Expires",expires);
            data.putLong("cod4GuardGeneration",generation-1);rejected(h,crab,zombie,"stale_generation");data.putLong("cod4GuardGeneration",generation);
            data.putUUID("cod4Summoner",UUID.randomUUID());rejected(h,crab,zombie,"missing_owner");data.putUUID("cod4Summoner",owner.getUUID());
            float ownerHealth=owner.getHealth();owner.setHealth(0);rejected(h,crab,zombie,"dead_owner");owner.setHealth(ownerHealth);
            suit(owner,3);rejected(h,crab,zombie,"fourth_piece_removed");h.assertTrue(shrimp.canAttack(zombie),"Three-piece shrimp remains valid");suit(owner,4);
            var nether=h.getLevel().getServer().getLevel(net.minecraft.world.level.Level.NETHER);
            if(nether!=null)rejected(h,crab,new Zombie(nether),"other_dimension_enemy");
            h.assertTrue(wild.canAttack(bystander),"Wild crab can still attack ordinary players");
            bystander.invulnerableTime=0;float health=bystander.getHealth();
            h.assertTrue(wild.doHurtTarget(bystander)&&bystander.getHealth()<health,"Wild crab retains native player damage");
            zombie.discard();wild.discard();
            bystander.invulnerableTime=0;bystander.setHealth(bystander.getMaxHealth());
            float baseline=bystander.getHealth();int[] ticks={0};
            h.onEachTick(()->{
                ticks[0]++;
                // First 60 real ticks exercise unprovoked nearest-player AI. Last 20
                // deliberately inject a stale target to exercise the final damage guard.
                if(ticks[0]>60)crab.setTarget(bystander);
                h.assertTrue(bystander.getHealth()==baseline,"Leased native AI must never hurt bystander tick="+ticks[0]);
                if(ticks[0]==80){
                    suit(owner,0);rejected(h,crab,bystander,"unequipped_owner");
                    SummonedGuard.tick(crab);SummonedGuard.tick(shrimp);
                    h.assertTrue(crab.isRemoved()&&shrimp.isRemoved(),"Unequip removes leased pair normally");
                    System.out.println("GUARD_TARGET_NATIVE_AI_PASS ticks=80 unprovoked=60 forced_stale=20 realTCP=false");
                    cleanup(h,owner,bystander,guards,scoreboard,team);h.succeed();
                }
            });
        }catch(Throwable failure){
            zombie.discard();wild.discard();cleanup(h,owner,bystander,guards,scoreboard,team);throw failure;
        }
    }
    private static void cleanup(GameTestHelper h,ServerPlayer owner,ServerPlayer bystander,List<SecondaryMob> guards,
                                net.minecraft.world.scores.Scoreboard scoreboard,net.minecraft.world.scores.PlayerTeam team){
        guards.forEach(Entity::discard);scoreboard.removePlayerTeam(team);
        h.getLevel().removePlayerImmediately(owner,Entity.RemovalReason.DISCARDED);
        h.getLevel().removePlayerImmediately(bystander,Entity.RemovalReason.DISCARDED);
    }
}
