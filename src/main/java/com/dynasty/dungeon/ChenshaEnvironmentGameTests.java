package com.dynasty.dungeon;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.HashSet;
import java.util.UUID;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class ChenshaEnvironmentGameTests {
    private static net.minecraft.server.level.ServerPlayer player(GameTestHelper h,String name) {
        var level=h.getLevel();var p=new net.minecraft.server.level.ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),name));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),
            new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(GameType.SURVIVAL);
        // Advance the real player past vanilla's 60-tick login immunity; Forge
        // FakePlayer is unconditionally invulnerable and cannot test actual damage.
        for(int i=0;i<61;i++)p.tick();
        return p;
    }
    @GameTest(template="bow_ritual_test",batch="cod2_environment")
    public static void warningAndDamageArePerPlayerAndNeverCatchUpAfterRestart(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(0,-16,0));
        var first=player(h,"chensha-exposure-a");var second=player(h,"chensha-exposure-b");
        first.setPos(origin.getX()+10.5,origin.getY()+19,origin.getZ()+36.5);
        second.setPos(first.getX()+1,first.getY(),first.getZ());
        level.setBlockAndUpdate(first.blockPosition().below(),Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState());
        level.setBlockAndUpdate(second.blockPosition().below(),Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState());
        var room=new DungeonRoomController();float health=first.getHealth();
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"mercury",first).equals("mercury_channel"),"Authored channel recognises actual foot contact");
        ChenshaEnvironment.contact(level,origin,"mercury",room,first,100);
        for(long t=102;t<140;t+=2)ChenshaEnvironment.contact(level,origin,"mercury",room,first,t);
        h.assertTrue(first.getHealth()==health,"Full two-second warning precedes damage");
        ChenshaEnvironment.contact(level,origin,"mercury",room,second,138);
        ChenshaEnvironment.contact(level,origin,"mercury",room,first,140);
        ChenshaEnvironment.contact(level,origin,"mercury",room,second,140);
        h.assertTrue(first.getHealth()<health&&second.getHealth()==health,"Second entrant has an independent warning rather than inheriting the first player's damage clock");
        float after=first.getHealth();
        ChenshaEnvironment.contact(level,origin,"mercury",room,first,140);
        h.assertTrue(first.getHealth()==after,"A second core/player call in the same tick cannot repeat a pulse");
        var saved=room.save();var restored=new DungeonRoomController();restored.load(saved);
        h.assertTrue(restored.save().getCompound("Exposures").size()==2,"Both exposure records survive room serialization");
        ChenshaEnvironment.contact(level,origin,"mercury",restored,first,10000);
        for(long t=10002;t<10040;t+=2)ChenshaEnvironment.contact(level,origin,"mercury",restored,first,t);
        h.assertTrue(first.getHealth()==after,"Unloaded time restarts the warning and emits no catch-up damage");
        first.setPos(first.getX(),origin.getY()+25,first.getZ());
        ChenshaEnvironment.contact(level,origin,"mercury",restored,first,10040);
        h.assertTrue(restored.exposure(first.getUUID(),false)==null,"Returning to a platform clears exposure");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_environment")
    public static void hazardsRespectSurfaceRoomModeAndFiniteLedger(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(-30,-40,-38));
        var player=player(h,"chensha-pit");
        player.setPos(origin.getX()+31.5,origin.getY()+44,origin.getZ()+41.5);
        var floor=player.blockPosition().below();level.setBlockAndUpdate(floor,Blocks.GREEN_STAINED_GLASS.defaultBlockState());
        var state=new DungeonRoomController();
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"shendao",player).equals("poison_pit"),"Toxic pit uses only its own room and surface");
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"mercury",player).isEmpty(),"Other storey cannot apply the pit twice");
        ChenshaEnvironment.contact(level,origin,"shendao",state,player,100);
        for(long t=102;t<=140;t+=2)ChenshaEnvironment.contact(level,origin,"shendao",state,player,t);
        h.assertTrue(player.hasEffect(MobEffects.POISON),"Warned pit contact applies actual poison");
        player.setGameMode(GameType.CREATIVE);
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"shendao",player).isEmpty(),"Creative tester immune to environmental hazards");
        player.setGameMode(GameType.SPECTATOR);
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"shendao",player).isEmpty(),"Spectators do not trigger hazards");
        player.setGameMode(GameType.SURVIVAL);level.setBlockAndUpdate(floor,Blocks.STONE.defaultBlockState());
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"shendao",player).isEmpty(),"A player-built safe platform changes actual contact");
        player.setPos(origin.getX()+35.5,origin.getY()+44,origin.getZ()+41.5);
        h.assertTrue(ChenshaEnvironment.contactZone(level,origin,"shendao",player).isEmpty(),"Permanent escape ladder is outside the toxic volume");
        state=new DungeonRoomController();for(int i=0;i<100;i++)state.exposure(UUID.randomUUID(),true);
        h.assertTrue(state.save().getCompound("Exposures").size()==64,"Crowds cannot grow a room's ledger indefinitely");
        h.assertTrue(state.retainExposures(java.util.Set.of())&&state.save().getCompound("Exposures").isEmpty(),"Departed players release bounded exposure slots");
        var legacy=new DungeonRoomController();legacy.load(new CompoundTag());
        h.assertTrue(legacy.save().getCompound("Exposures").isEmpty(),"Old room saves do not acquire phantom contacts");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_environment")
    public static void onlyAuthoredCoreBindingsEnableEnvironmentAndSurviveNbt(GameTestHelper h) {
        var level=h.getLevel();var core=h.absolutePos(new BlockPos(3,2,3));
        var origin=core.subtract(ChenshaPiece.core("mercury"));
        level.setBlockAndUpdate(core,DungeonContent.CORE.get().defaultBlockState());
        var be=(DungeonMechanismBlockEntity)level.getBlockEntity(core);
        be.configure(UUID.randomUUID(),"mercury","mercury_core",core,-1,java.util.List.of());
        be.configureEnvironment(origin.east());
        h.assertTrue(!be.saveWithoutMetadata().contains("EnvironmentOrigin"),"Shifted origin cannot create an environmental controller");
        be.configureEnvironment(origin);var saved=be.saveWithoutMetadata();
        h.assertTrue(saved.getLong("EnvironmentOrigin")==origin.asLong(),"Exact authored origin is persisted");
        var restored=new DungeonMechanismBlockEntity(core,be.getBlockState());restored.load(saved);
        h.assertTrue(restored.saveWithoutMetadata().getLong("EnvironmentOrigin")==origin.asLong(),"Core reload retains its environment origin");
        saved.putString("Room","qa");restored.load(saved);
        h.assertTrue(!restored.saveWithoutMetadata().contains("EnvironmentOrigin"),"Unrelated room rejects copied environment NBT");
        saved.remove("EnvironmentOrigin");saved.putString("Room","mercury");restored.load(saved);
        h.assertTrue(!restored.saveWithoutMetadata().contains("EnvironmentOrigin"),"Existing worlds do not silently rewrite old cores");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_environment")
    public static void nineTierDaisStarsAndSecretEntranceHaveUsableGeometry(GameTestHelper h) {
        var tiers=new HashSet<Integer>();
        for(int x=22;x<=31;x++) {
            int height=ChenshaPiece.daisHeight(x,15);tiers.add(height);
            h.assertTrue(ChenshaPiece.cell(x,height,15).is(Blocks.SMOOTH_QUARTZ),"Tier has a visible quartz landing");
            for(int dy=1;dy<=3;dy++)h.assertTrue(ChenshaPiece.cell(x,height+dy,15).isAir(),"Climbable dais headroom");
        }
        h.assertTrue(tiers.size()==9&&tiers.contains(9),"Nine distinct dragon-dais risers");
        var stars=ChenshaPiece.vaultStars();
        h.assertTrue(stars.size()==28&&new HashSet<>(stars).size()==28,"Twenty-eight distinct star lamps");
        for(var p:stars)h.assertTrue(p.getY()==ChenshaPiece.vaultRoof(p.getX(),p.getZ()),"Star embeds in the authored dome, not in player headroom");
        h.assertTrue(ChenshaPiece.cell(52,24,86).is(Blocks.LIGHT_BLUE_STAINED_GLASS),"Fantasy fall has an authored receiving trough");
        for(int y=25;y<=27;y++) {
            h.assertTrue(ChenshaPiece.cell(52,y,86).isAir(),"Particle waterfall can be crossed");
            h.assertTrue(ChenshaPiece.cell(52,y,87).is(Blocks.CRACKED_STONE_BRICKS),"Hidden entrance is intentionally breakable");
            h.assertTrue(ChenshaPiece.cell(52,y,88).isAir(),"Passage behind the wall reaches the secret room");
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_environment")
    public static void expeditionDiaryUsesReadablePagesAndDoesNotRefill(GameTestHelper h) {
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(2,2,2));level.setBlockAndUpdate(pos,Blocks.CHEST.defaultBlockState());
        var chest=(net.minecraft.world.level.block.entity.ChestBlockEntity)level.getBlockEntity(pos);
        chest.setLootTable(new net.minecraft.resources.ResourceLocation("dynasty:dungeons/chensha_expedition_notes"),23L);chest.unpackLootTable(null);
        int books=0;
        for(int i=0;i<chest.getContainerSize();i++) {
            var item=chest.getItem(i);if(!item.is(net.minecraft.world.item.Items.WRITTEN_BOOK))continue;
            books+=item.getCount();var tag=item.getTag();
            h.assertTrue(net.minecraft.world.item.WrittenBookItem.makeSureTagIsValid(tag),"Book has valid title, author and pages");
            var pages=tag.getList("pages",8);h.assertTrue(pages.size()==3,"Three useful exploration clues");
            for(int p=0;p<pages.size();p++)h.assertTrue(net.minecraft.network.chat.Component.Serializer.fromJson(pages.getString(p))!=null,"Each page parses as a readable text component");
        }
        h.assertTrue(books==1,"Narrative cache contains exactly one diary");
        chest.clearContent();chest.load(chest.saveWithoutMetadata());chest.unpackLootTable(null);
        h.assertTrue(chest.isEmpty(),"Read/emptied chest reload cannot reroll the diary");h.succeed();
    }
}
