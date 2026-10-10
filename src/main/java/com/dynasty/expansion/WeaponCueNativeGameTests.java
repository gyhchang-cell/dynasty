package com.dynasty.expansion;
import com.dynasty.*;
import com.dynasty.cod3.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class WeaponCueNativeGameTests {
    private static int sequence;
    private static ServerPlayer player(GameTestHelper h,Item item){
        var level=h.getLevel();var base=h.absolutePos(new BlockPos(4,2,4)).offset(4096+(++sequence)*32,150,4096);
        level.getChunkAt(base);level.getChunkAt(base.south(16));
        for(var cell:BlockPos.betweenClosed(base.offset(-2,0,-2),base.offset(2,4,16)))level.setBlock(cell,Blocks.AIR.defaultBlockState(),2);
        var p=new ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),"weapon-cue-native"));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(base));p.setNoGravity(true);p.setYRot(0);p.setXRot(0);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(item));p.getFoodData().setFoodLevel(17);
        var festival=DynastyFestivals.today();if(festival!=null)p.getPersistentData().putString("dynasty_festival_day",festival+":"+java.time.LocalDate.now());
        level.addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    private static void close(ServerPlayer p){p.stopUsingItem();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    private static void crossbow(GameTestHelper h,boolean siege){
        var p=player(h,siege?ExpansionContent.SIEGE.get():ExpansionContent.REPEATING.get());var weapon=p.getMainHandItem();int count=siege?1:3;String id=siege?"siege_crossbow":"repeating_crossbow";
        p.getInventory().setItem(10,new ItemStack(ExpansionContent.AMMO.get(siege?"heavy_bolt":"repeating_bolt").get(),count));
        // Actual physical native collision keeps shot entities in this loaded test corridor.
        var wall=p.blockPosition().south(12);for(var cell:BlockPos.betweenClosed(wall.offset(-3,0,0),wall.offset(3,4,0)))h.getLevel().setBlockAndUpdate(cell,Blocks.STONE.defaultBlockState());
        p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);
        h.runAfterDelay(32,()->{try{
            p.releaseUsingItem();h.assertTrue(CrossbowItem.isCharged(weapon)&&weapon.getOrCreateTag().getList("cod4Magazine",10).size()==count&&p.getInventory().getItem(10).isEmpty(),"Real native charging consumes original ammo once and stores original loaded magazine");
            p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);
            h.runAfterDelay(24,()->{try{
                var arrows=h.getLevel().getEntitiesOfClass(AbstractArrow.class,p.getBoundingBox().inflate(100),a->a.getOwner()==p);
                h.assertTrue(arrows.size()==count&&!CrossbowItem.isCharged(weapon)&&weapon.getOrCreateTag().getList("cod4Magazine",10).isEmpty()&&weapon.getDamageValue()==count,"Actual native ticks fire only original finite projectiles/magazine/durability, cosmetic recoil creates none: arrows="+arrows.size()+", charged="+CrossbowItem.isCharged(weapon)+", magazine="+weapon.getOrCreateTag().getList("cod4Magazine",10).size()+", damage="+weapon.getDamageValue()+", current="+p.getMainHandItem()+", arrowDetails="+arrows.stream().map(a->a.position()+":"+a.isRemoved()+":"+a.getDeltaMovement()+":"+a.getOwner()).toList());
                h.assertTrue(p.getPersistentData().contains("cod3_weapon_at_"+id),"Actual native shot owns finite actor recoil cue");
                for(var arrow:arrows)h.assertTrue(EquipmentFeedback.firingWeapon(arrow,p).is(weapon.getItem())&&arrow.getPierceLevel()==(siege?2:0),"Every real arrow keeps original firing identity and original pierce count");
                var packet=EquipmentFeedback.weaponPacket(p,id,null);h.assertTrue(packet.valid()&&packet.duration()==8&&packet.entityId()==p.getId()&&packet.seed()==p.getUUID().getLeastSignificantBits(),"Original visual wire uses native actor identity/dimension and finite8tick lifetime; real client display pending");
                arrows.forEach(Entity::discard);h.succeed();
            }finally{close(p);}});
        }catch(Throwable fail){close(p);throw fail;}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_native_repeating_cue",setupTicks=20,timeoutTicks=100)
    public static void actualRepeatingNativeChargeFireKeepsThreeProjectilesAndOriginalWeaponSnapshot(GameTestHelper h){crossbow(h,false);}
    @GameTest(template="bow_ritual_test",batch="cod4_native_siege_cue",setupTicks=20,timeoutTicks=100)
    public static void actualSiegeNativeChargeFireKeepsOnePiercingProjectileAndFiniteOwnerRecoil(GameTestHelper h){crossbow(h,true);}
    @GameTest(template="bow_ritual_test",batch="cod4_native_tether_cue",setupTicks=20,timeoutTicks=100)
    public static void actualNativeRopeAndClawContactKeepOnePullWallCollisionCooldownAndNoMissCue(GameTestHelper h){
        var players=new ArrayList<ServerPlayer>();var targets=new ArrayList<net.minecraft.world.entity.monster.Zombie>();
        for(Item item:new Item[]{ExpansionContent.ROPE.get(),ExpansionContent.CLAW.get()}){
            var p=player(h,item);players.add(p);var z=new net.minecraft.world.entity.monster.Zombie(h.getLevel());z.setPos(p.position().add(0,0,6));z.setNoAi(true);z.setNoGravity(true);z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(10000);z.setHealth(10000);h.getLevel().addFreshEntity(z);targets.add(z);
        }
        // Register all native per-tick fixtures before callbacks run; GameTest's schedule is not mutation-safe.
        var wall=player(h,ExpansionContent.CLAW.get());var miss=player(h,ExpansionContent.ROPE.get());
        h.runAfterDelay(3,()->{try{
            for(int i=0;i<players.size();i++){
                var p=players.get(i);var z=targets.get(i);String id=i==0?"rope_dart":"flying_claw";float hp=z.getHealth();
                p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);
                h.assertTrue(p.getPersistentData().contains("cod3_weapon_at_"+id)&&z.getDeltaMovement().z<-.5&&z.hasEffect(ExpansionEffects.STAGGER.get())&&z.getHealth()==hp&&p.getMainHandItem().getDamageValue()==1&&p.getCooldowns().isOnCooldown(p.getMainHandItem().getItem()),"Real native input keeps original one pull/finite stagger/durability/cooldown and adds only geometric dart/claw cue");
                var packet=EquipmentFeedback.weaponPacket(p,id,z.getEyePosition());h.assertTrue(packet.valid()&&packet.duration()==24&&packet.origin().add(packet.direction()).distanceTo(z.getEyePosition())<.00001&&packet.entityId()==p.getId()&&packet.seed()==p.getUUID().getLeastSignificantBits(),"Original native actor wire preserves bounded actual endpoint/owner and finite24tick life");
                long at=p.getPersistentData().getLong("cod3_weapon_at_"+id);p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getDamageValue()==1&&p.getPersistentData().getLong("cod3_weapon_at_"+id)==at,"Native cooldown rejects repeated input without a second charge or cue");
            }
            var anchor=wall.blockPosition().south(6).above();h.getLevel().setBlockAndUpdate(anchor,Blocks.STONE.defaultBlockState());
            wall.gameMode.useItem(wall,h.getLevel(),wall.getMainHandItem(),InteractionHand.MAIN_HAND);h.assertTrue(wall.getPersistentData().contains("cod3_weapon_at_flying_claw")&&wall.getDeltaMovement().z>.7&&!wall.noPhysics&&wall.getMainHandItem().getDamageValue()==1,"Real original wall hook uses collision-respecting velocity, not a new teleport/projectile");
            miss.gameMode.useItem(miss,h.getLevel(),miss.getMainHandItem(),InteractionHand.MAIN_HAND);h.assertTrue(!miss.getPersistentData().contains("cod3_weapon_at_rope_dart")&&miss.getMainHandItem().getDamageValue()==0,"Actual empty ray neither consumes original durability nor starts contact-only cue");
            h.assertTrue(EquipmentFeedback.weaponPacket(miss,"rope_dart",miss.getEyePosition().add(100,0,0))==null&&EquipmentFeedback.weaponPacket(miss,"unknown",null)==null,"Unknown/unbounded trace cannot create cosmetic wire entry");h.succeed();
        }finally{targets.forEach(Entity::discard);players.forEach(WeaponCueNativeGameTests::close);close(wall);close(miss);}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_native_hammer_cue",setupTicks=20,timeoutTicks=100)
    public static void actualNativeHammerChargeAndReleasePreserveOriginalAreaDamageAndSingleDurabilityPayment(GameTestHelper h){
        var full=player(h,ExpansionContent.HAMMER.get());var shortUse=player(h,ExpansionContent.HAMMER.get());
        var targets=new ArrayList<net.minecraft.world.entity.animal.Cow>();
        for(var p:new ServerPlayer[]{full,shortUse}){var cow=new net.minecraft.world.entity.animal.Cow(net.minecraft.world.entity.EntityType.COW,h.getLevel());cow.setPos(p.position().add(2,0,1));cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(10000);cow.setHealth(10000);h.getLevel().addFreshEntity(cow);targets.add(cow);p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);}
        h.runAfterDelay(10,()->{h.assertTrue(shortUse.getPersistentData().contains("cod3_weapon_at_meteor_charge"),"Actual native use ticks own only finite geometric winding, no charge damage");shortUse.releaseUsingItem();h.assertTrue(targets.get(1).getHealth()==10000&&shortUse.getMainHandItem().getDamageValue()==0&&!shortUse.getPersistentData().contains("cod3_weapon_at_meteor_hammer"),"Actual native short charge has no original damage/payment or new cosmetic sweep");});
        h.runAfterDelay(24,()->{try{
            h.assertTrue(DynastyBalance.weaponBonus("meteor_hammer")==110,"Canonical original central weapon bonus remains110");double original=full.getAttributeValue(Attributes.ATTACK_DAMAGE)*.6+110;full.releaseUsingItem();
            h.assertTrue(Math.abs(10000-targets.get(0).getHealth()-original)<.5&&full.getMainHandItem().getDamageValue()==3&&full.getCooldowns().isOnCooldown(ExpansionContent.HAMMER.get())&&full.getPersistentData().contains("cod3_weapon_at_meteor_hammer"),"Actual full native release preserves original0.6 area damage, one3durability payment,80tick cooldown and finite geometric chain cue: lost="+(10000-targets.get(0).getHealth())+", expected="+original);
            h.assertTrue(EquipmentFeedback.weaponPacket(full,"meteor_hammer",null).duration()==12,"Chain sweep lifetime stays bounded to original short impact presentation");h.succeed();
        }finally{targets.forEach(Entity::discard);close(full);close(shortUse);}});
    }
}
