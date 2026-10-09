package com.dynasty.expansion;

import com.dynasty.cod3.*;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class MortuarySecretGameTests {
    private static BlockPos room(GameTestHelper h){
        for(int x=0;x<=8;x++)for(int z=0;z<=8;z++){h.setBlock(new BlockPos(x,1,z),Blocks.STONE);for(int y=2;y<=5;y++)h.setBlock(new BlockPos(x,y,z),Blocks.AIR);}
        var at=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("mortuary_room").get().defaultBlockState());return at;
    }
    private static ServerPlayer player(GameTestHelper h,BlockPos at){return player(h,at,new GameProfile(UUID.randomUUID(),"mortuary-real"));}
    private static ServerPlayer player(GameTestHelper h,BlockPos at,GameProfile profile){var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(at));return p;}
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static DynastyNpcEntity victim(GameTestHelper h,ServerPlayer p,BlockPos at){return (DynastyNpcEntity)h.getLevel().getEntity(SmallInteractions.mortuaryVictimId(h.getLevel(),at,p.getUUID()));}
    private static void ready(ServerPlayer p){var root=EquipmentBehaviors.saved(p);root.putLong("site_mortuary_room_start",p.level().getGameTime()-2400);root.putLong("site_mortuary_room_next",p.level().getGameTime());}
    private static ItemStack potion(Potion kind){return PotionUtils.setPotion(new ItemStack(Items.POTION),kind);}
    @GameTest(template="bow_ritual_test",batch="cod4_mortuary_native",setupTicks=20)
    public static void actualLivingPatientIsBoundedPersistentAndInspectionCannotClaim(GameTestHelper h){
        var at=room(h);var p=player(h,at);use(h,p,at);var v=victim(h,p,at);h.assertTrue(v!=null&&v.isAlive()&&v.role.equals("a_ji")&&v.getHealth()==4,"Actual registered existing refugee, not a particle marker or undead, carries the weak living patient");
        h.assertTrue(v.isNoAi()&&v.getPersistentData().getUUID("cod4_mortuary_owner").equals(p.getUUID())&&v.distanceToSqr(Vec3.atCenterOf(at))<=16,"One patient is owner-bound and bounded beside the loaded physical Site");
        long now=h.getLevel().getGameTime();h.assertTrue(EquipmentBehaviors.saved(p).getLong("site_mortuary_room_start")==now&&EquipmentBehaviors.saved(p).getLong("site_mortuary_room_next")==now+2400,"Original two-minute site duration is retained");
        for(int i=0;i<10;i++)use(h,p,at);h.assertTrue(victim(h,p,at)==v&&!SecretTracker.mortuaryClaimed(p),"Repeated inspection creates no duplicate body or reward");
        var data=v.saveWithoutId(new CompoundTag());v.discard();var restored=NpcContent.NPCS.get("a_ji").get().create(h.getLevel());restored.load(data);h.getLevel().addFreshEntity(restored);use(h,p,at);
        h.assertTrue(victim(h,p,at)==restored&&restored.getHealth()==4&&restored.getPersistentData().getBoolean("cod4_mortuary_waiting"),"Native entity NBT reload retains the same patient UUID, health and rescue state");restored.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_mortuary_native",setupTicks=20)
    public static void nativeHealingChangesPatientHealthAndPaysOnePotionBottleAndSwordOnce(GameTestHelper h){
        var at=room(h);var p=player(h,at);p.getInventory().setItem(0,potion(Potions.HEALING));p.getInventory().setItem(1,potion(Potions.HEALING));use(h,p,at);var v=victim(h,p,at);
        h.assertTrue(v.getHealth()==4&&p.getInventory().countItem(Items.POTION)==2,"Early offering never heals or consumes before the original duration");ready(p);
        p.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),1000));p.addEffect(new MobEffectInstance(ExpansionEffects.SOUL.get(),1000));use(h,p,at);
        h.assertTrue(v.getHealth()==8&&!v.isNoAi()&&!v.isInvulnerable()&&!v.getPersistentData().getBoolean("cod4_mortuary_waiting"),"Actual native instant-health effect restores four health and releases the original NPC's normal AI");
        h.assertTrue(SecretTracker.mortuaryClaimed(p)&&p.getInventory().countItem(Items.POTION)==1&&p.getInventory().countItem(Items.GLASS_BOTTLE)==1&&p.getInventory().countItem(ExpansionContent.item("longyuan_sword"))==1,"Native secret 29 owns exactly one potion payment, returned bottle and original heirloom sword");
        h.assertTrue(EquipmentBehaviors.saved(p).getBoolean("site_mortuary_room_done")&&!p.hasEffect(ExpansionEffects.YIN.get())&&!p.hasEffect(ExpansionEffects.SOUL.get()),"New rescue preserves original one-time Site completion/cleanse");
        var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_mortuary_room"));h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Actual original COD4 task advancement is awarded");
        p.getInventory().selected=1;use(h,p,at);h.assertTrue(v.getHealth()==8&&p.getInventory().countItem(Items.POTION)==1&&p.getInventory().countItem(ExpansionContent.item("longyuan_sword"))==1,"Completed use heals no further and does not consume/reward a second potion");
        var q=player(h,at,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(q,p,true));q.setItemInHand(InteractionHand.MAIN_HAND,potion(Potions.HEALING));use(h,q,at);h.assertTrue(SecretTracker.mortuaryClaimed(q)&&q.getMainHandItem().is(Items.POTION)&&q.getInventory().countItem(ExpansionContent.item("longyuan_sword"))==0,"Death clone keeps original claim without repaying the heirloom");v.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_mortuary_native",setupTicks=20)
    public static void wrongPotionRemoteFullOrUnownedPatientCannotFakeARescue(GameTestHelper h){
        var at=room(h);var p=player(h,at);use(h,p,at);var v=victim(h,p,at);ready(p);p.setItemInHand(InteractionHand.MAIN_HAND,potion(Potions.WATER));use(h,p,at);
        h.assertTrue(v.getHealth()==4&&p.getMainHandItem().is(Items.POTION)&&!SecretTracker.mortuaryClaimed(p),"An ordinary water potion changes no health, item or native claim");
        p.setItemInHand(InteractionHand.MAIN_HAND,potion(Potions.HEALING));p.setPos(p.getX()+30,p.getY(),p.getZ());h.assertTrue(!SecretTracker.rescueMortuary(p,at,v)&&v.getHealth()==4,"Remote healing adapter rejects before native health/payment");p.setPos(Vec3.atBottomCenterOf(at));
        var other=player(h,at);ready(other);other.setItemInHand(InteractionHand.MAIN_HAND,potion(Potions.HEALING));h.assertTrue(!SecretTracker.rescueMortuary(other,at,v),"Another character cannot spend a potion on someone else's pending body or steal its reward");
        v.setHealth(v.getMaxHealth());h.assertTrue(!SecretTracker.rescueMortuary(p,at,v)&&p.getMainHandItem().is(Items.POTION),"Already healthy patient cannot manufacture a paid rescue");v.setHealth(4);EquipmentBehaviors.saved(p).putInt("site_mortuary_room_count",1);h.assertTrue(!SecretTracker.get(h.getLevel()).claim(p,29,at),"Old generic count without actual healing proof cannot grant original secret reward");
        h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());h.assertTrue(!SecretTracker.rescueMortuary(p,at,v)&&v.getHealth()==4,"Removed Site cannot authorize a stale physical scene");v.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_mortuary_native",setupTicks=20)
    public static void originalMilkCleanseAndLegacyCompletionRemainWhileMissingSecretIsEarned(GameTestHelper h){
        var at=room(h);var p=player(h,at);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.MILK_BUCKET));use(h,p,at);ready(p);p.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),1000));use(h,p,at);
        h.assertTrue(EquipmentBehaviors.saved(p).getBoolean("site_mortuary_room_done")&&!p.hasEffect(ExpansionEffects.YIN.get())&&p.getMainHandItem().is(Items.MILK_BUCKET)&&!SecretTracker.mortuaryClaimed(p),"Original completed milk use/cleanse/payment semantics remain and do not fake an actual rescue");
        p.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),1000));p.setItemInHand(InteractionHand.MAIN_HAND,potion(Potions.HEALING));use(h,p,at);var v=victim(h,p,at);ready(p);use(h,p,at);
        h.assertTrue(SecretTracker.mortuaryClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("longyuan_sword"))==1&&p.hasEffect(ExpansionEffects.YIN.get()),"Legacy completed Site earns only its genuinely missing native rescue reward; old cleanse is never replayed");
        var other=player(h,at);use(h,other,at);var second=victim(h,other,at);h.assertTrue(second!=null&&second!=v&&!second.getUUID().equals(v.getUUID())&&!SecretTracker.mortuaryClaimed(other),"Detached second character uses its own persisted patient and player-scope claim; real multiplayer remains pending");v.discard();second.discard();h.succeed();
    }
}
