package com.dynasty;

import java.util.*;
import java.lang.reflect.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.gametest.*;

/** Opt-in QA against the exact installed FTB jars and a copied quest tree in a fresh world. */
@GameTestHolder("dynasty_ftb_qa") @PrefixGameTestTemplate(false)
public final class FtbRewardGameTests {
    /** Detached vanilla ServerPlayer fixtures bypass the normal FTB Teams login hook. */
    @net.minecraftforge.fml.common.Mod.EventBusSubscriber(modid=Dynasty.MODID)
    public static final class FixtureTeams {
        private static final Set<UUID> registered=new HashSet<>();
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.HIGHEST)
        public static void tick(net.minecraftforge.event.TickEvent.PlayerTickEvent e){ensure(e.player);}
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.HIGHEST)
        public static void player(net.minecraftforge.event.entity.player.PlayerEvent e){ensure(e.getEntity());}
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.HIGHEST)
        public static void death(net.minecraftforge.event.entity.living.LivingDeathEvent e){
            if(e.getSource().getEntity() instanceof net.minecraft.world.entity.player.Player p)ensure(p);
        }
        private static void ensure(net.minecraft.world.entity.player.Player player){
            if(!Boolean.getBoolean("dynasty.ftbRewardQa")||!net.minecraftforge.gametest.ForgeGameTestHooks.isGametestServer()
                    ||!(player instanceof ServerPlayer p)
                    ||p instanceof net.minecraftforge.common.util.FakePlayer||registered.contains(p.getUUID()))return;
            try{
                Object api=Class.forName("dev.ftb.mods.ftbteams.api.FTBTeamsAPI").getMethod("api").invoke(null);
                Object manager=Class.forName("dev.ftb.mods.ftbteams.api.FTBTeamsAPI$API").getMethod("getManager").invoke(api);
                var managerType=Class.forName("dev.ftb.mods.ftbteams.api.TeamManager");
                if(((Optional<?>)managerType.getMethod("getTeamForPlayerID",UUID.class).invoke(manager,p.getUUID())).isEmpty()){
                    // Native offline registration supports a null player. Avoid replaying login
                    // rewards or pretending these detached QA fixtures are real network clients.
                    Class.forName("dev.ftb.mods.ftbteams.data.TeamManagerImpl").getMethod("playerLoggedIn",ServerPlayer.class,UUID.class,String.class)
                            .invoke(manager,null,p.getUUID(),p.getGameProfile().getName());
                }
                Object file=Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile").getField("INSTANCE").get(null);
                Object data=file.getClass().getMethod("getOrCreateTeamData",net.minecraft.world.entity.Entity.class).invoke(file,p);
                if(data==null)throw new IllegalStateException("Native QA team data missing after registration");registered.add(p.getUUID());
            }catch(ReflectiveOperationException ex){throw new IllegalStateException("Native FTB fixture team setup",ex);}
        }
        @net.minecraftforge.eventbus.api.SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){registered.clear();}
    }
    @GameTestGenerator public static Collection<TestFunction> nativeRewards(){
        if(!Boolean.getBoolean("dynasty.ftbRewardQa"))return List.of();
        return List.of(new TestFunction("ftb_native_rewards","dynasty_ftb_qa.native_rewards","dynasty_ftb_qa:bow_ritual_test",100,20,true,FtbRewardGameTests::run));
    }
    private static void run(GameTestHelper h){
        try{
            Class<?> sidebarType=Class.forName("dev.ftb.mods.ftblibrary.sidebar.SidebarButtonCreatedEvent");
            Field sidebarField=sidebarType.getField("EVENT");Object sidebar=sidebarField.get(null);
            h.assertTrue((Boolean)sidebarField.getType().getMethod("isRegistered",Object.class).invoke(sidebar,DynastyFtbSetup.SIDEBAR_HANDLER),"Existing native sidebar handler attaches through the public Architectury Event interface");
            Class<?> fileType=Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile"),questType=Class.forName("dev.ftb.mods.ftbquests.quest.Quest"),xpType=Class.forName("dev.ftb.mods.ftbquests.quest.reward.XPReward");
            Object file=fileType.getField("INSTANCE").get(null);h.assertTrue(file!=null,"Native server quest file is actually loaded");
            Collection<?> objects=(Collection<?>)fileType.getMethod("getAllObjects").invoke(file);
            long quests=objects.stream().filter(questType::isInstance).count();h.assertTrue(quests==808,"Copied existing quest tree loads all 808 original nodes: "+quests);
            var rewardData=xpType.getMethod("writeData",CompoundTag.class);int rewards=0;
            for(Object object:objects)if(xpType.isInstance(object)){
                var data=new CompoundTag();rewardData.invoke(object,data);
                h.assertTrue(data.getInt("xp")>0,"Every original positive XP reward remains nonzero in the actual FTB loader: "+object);rewards++;
            }
            h.assertTrue(rewards==693,"All original 693 XP reward objects retain their IDs and definitions: "+rewards);
            // Verify native read/payout on a detached QA object, without mutating real claim flags.
            Object quest=fileType.getMethod("getQuest",long.class).invoke(file,Long.parseUnsignedLong("1000000000010005",16));
            h.assertTrue(quest!=null,"Original early-game quest identity remains available");
            Object sample=xpType.getConstructor(long.class,questType).newInstance(0x7F1234567890ABCDL,quest);
            var old=new CompoundTag();old.putInt("value",6);xpType.getMethod("readData",CompoundTag.class).invoke(sample,old);
            var written=new CompoundTag();rewardData.invoke(sample,written);h.assertTrue(written.getInt("xp")==0,"Installed native reader reproduces the legacy value-field bug");
            var fixed=new CompoundTag();fixed.putInt("xp",6);xpType.getMethod("readData",CompoundTag.class).invoke(sample,fixed);
            var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"ftb-xp-qa"));
            p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
            xpType.getMethod("claim",ServerPlayer.class,boolean.class).invoke(sample,p,false);
            h.assertTrue(p.totalExperience==6,"Actual native reward pays the original six experience points");
            Class<?> teamType=Class.forName("dev.ftb.mods.ftbquests.quest.TeamData"),baseFileType=Class.forName("dev.ftb.mods.ftbquests.quest.BaseQuestFile"),rewardType=Class.forName("dev.ftb.mods.ftbquests.quest.reward.Reward");
            Object loaded=objects.stream().filter(xpType::isInstance).findFirst().orElseThrow();
            var original=new CompoundTag();rewardData.invoke(loaded,original);int expected=original.getInt("xp");
            UUID teamId=UUID.randomUUID();Object team=teamType.getConstructor(UUID.class,baseFileType).newInstance(teamId,file);
            var claim=teamType.getMethod("claimReward",ServerPlayer.class,rewardType,boolean.class);
            var legacy=original.copy();legacy.remove("xp");legacy.putInt("value",expected);
            int before=p.totalExperience;
            try{
                xpType.getMethod("readData",CompoundTag.class).invoke(loaded,legacy);claim.invoke(team,p,loaded,false);
                h.assertTrue(p.totalExperience==before,"Legacy zero reward can be claimed without paying XP, reproducing old completion flags");
            }finally{xpType.getMethod("readData",CompoundTag.class).invoke(loaded,original);}
            Object saved=teamType.getMethod("serializeNBT").invoke(team),restored=teamType.getConstructor(UUID.class,baseFileType).newInstance(teamId,file);
            teamType.getMethod("deserializeNBT",saved.getClass()).invoke(restored,saved);
            h.assertTrue((Boolean)teamType.getMethod("isRewardClaimed",UUID.class,rewardType).invoke(restored,p.getUUID(),loaded),"Native persisted claim identity survives corrected reward definition");
            claim.invoke(restored,p,loaded,false);h.assertTrue(p.totalExperience==before,"Corrected reward does not repay the old claimant after native claim-state reload");
            var other=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"ftb-other-qa"));
            other.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),other);
            claim.invoke(restored,other,loaded,false);h.assertTrue(other.totalExperience==expected,"Existing personal XP reward still pays a different player exactly once");
            claim.invoke(restored,other,loaded,false);h.assertTrue(other.totalExperience==expected,"Native duplicate reward claim is rejected");
            System.out.println("FTB NATIVE QA: nodes="+quests+", XP rewards="+rewards+", legacy value=0, corrected native claim=6; native persisted old-claim replay rejected; distinct QA-player claim once; real multiplayer/client acceptance pending");h.succeed();
        }catch(ReflectiveOperationException e){h.fail("Native FTB QA reflection: "+e+(e instanceof InvocationTargetException target?" cause="+target.getCause():""));}
    }
}
