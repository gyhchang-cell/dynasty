package com.dynasty.structure.megabuild;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class SculptureStoryGameTests {
    @GameTest(template="bow_ritual_test",batch="sculpture_story",timeoutTicks=40)
    public static void onlyActualVisitorsReceiveIndependentProgress(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(2,2,2));
        var data=SculptureStorySites.load(new SculptureStorySites().save(new CompoundTag()));
        data.register("yunqi_manor",origin,2,3,2);
        // Forge intentionally refuses advancement grants to FakePlayer. Exercise
        // the real ServerPlayer path with an inert network connection instead.
        var visitor=player(level,"story-visitor");
        var outside=player(level,"story-outside");
        var adv=level.getServer().getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","story_visit_yunqi_manor"));
        var dragon=level.getServer().getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","story_visit_longque_sanctuary"));
        try {
            visitor.moveTo(origin.getX()+.5,origin.getY()+1,origin.getZ()+.5);
            outside.moveTo(origin.getX()+4,origin.getY()+1,origin.getZ()+.5);
            data.checkPlayer(visitor);data.checkPlayer(outside);
            h.assertTrue(visitor.getAdvancements().getOrStartProgress(adv).isDone(),"Actual visitor did not complete");
            h.assertTrue(!outside.getAdvancements().getOrStartProgress(adv).isDone(),"Nearby non-visitor completed");
            h.assertTrue(!visitor.getAdvancements().getOrStartProgress(dragon).isDone(),"Manor falsely completed dragon visit");
            visitor.getAdvancements().revoke(adv,"placed");
            visitor.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);data.checkPlayer(visitor);
            h.assertTrue(!visitor.getAdvancements().getOrStartProgress(adv).isDone(),"Spectator completed exploration");
            outside.moveTo(origin.getX()+.5,origin.getY()+1,origin.getZ()+.5);
            SculptureStorySites.load(data.save(new CompoundTag())).checkPlayer(outside);
            h.assertTrue(outside.getAdvancements().getOrStartProgress(adv).isDone(),"Second player could not use reloaded site");
        } finally {
            visitor.getAdvancements().stopListening();outside.getAdvancements().stopListening();
            visitor.discard();outside.discard();
        }
        h.succeed();
    }
    private static net.minecraft.server.level.ServerPlayer player(net.minecraft.server.level.ServerLevel level,String name) {
        var player=new net.minecraft.server.level.ServerPlayer(level.getServer(),level,
                new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),name));
        player.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),
                new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),player) {
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet) {}
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet,net.minecraft.network.PacketSendListener listener) {}
        };
        return player;
    }
    @GameTest(template="bow_ritual_test",batch="sculpture_story",timeoutTicks=40)
    public static void storySitesPersistAndDoNotDuplicate(GameTestHelper h) {
        var data=new SculptureStorySites();var origin=new BlockPos(-20,-60,30);
        data.register("yunqi_manor",origin,101,80,111);
        data.register("yunqi_manor",origin,101,80,111);
        var nbt=data.save(new CompoundTag());
        h.assertTrue(nbt.getList("Sites",10).size()==1,"Duplicate placement receipt");
        var loaded=SculptureStorySites.load(nbt);
        h.assertTrue(loaded.contains("yunqi_manor",new Vec3(-19.5,-59,30.5)),"Lost saved visit bounds");
        h.assertTrue(!loaded.contains("longque_sanctuary",new Vec3(-19.5,-59,30.5)),"Wrong structure completed");
        h.assertTrue(!loaded.contains("yunqi_manor",new Vec3(81,0,31)),"Outside upper X counted");
        h.assertTrue(!loaded.contains("yunqi_manor",new Vec3(0,21,31)),"Outside height counted");
        h.assertTrue(!loaded.contains("yunqi_manor",new Vec3(0,0,141)),"Outside upper Z counted");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="sculpture_story",timeoutTicks=40)
    public static void storyAdvancementsAreLoadedAndIndependent(GameTestHelper h) {
        var manager=h.getLevel().getServer().getAdvancements();
        for(String mob:new String[]{"zuwu_daoshou","ludun_jiashi","fufa_jijiu","shanjing_shanxiao"}) {
            var adv=manager.getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","story_slay_"+mob));
            h.assertTrue(adv!=null&&adv.getCriteria().containsKey("slay"),"Kill receipt missing: "+mob);
        }
        for(String site:SculptureBlueprint.IDS) {
            var adv=manager.getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","story_visit_"+site));
            h.assertTrue(adv!=null&&adv.getRequirements().length==1&&adv.getRequirements()[0].length==2,"Natural OR placed receipt invalid");
        }
        h.succeed();
    }
}
