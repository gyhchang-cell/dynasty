package com.dynasty.dungeon;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class ChenshaShortcutGameTests {
    private record Fixture(BlockPos origin,UUID instance){}
    private static Fixture generate(GameTestHelper h){
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(-16,80,-16));var id=UUID.randomUUID();
        for(int x=1;x<=2;x++)for(int z=0;z<=1;z++){
            var piece=new ChenshaPiece(origin,x,z,id);var bounds=piece.getBoundingBox();
            // GameTest grid origins need not align with world chunks. A sixteen-block column
            // may intersect four native chunks; execute the production clipping path for all of them.
            for(int cx=bounds.minX()>>4;cx<=bounds.maxX()>>4;cx++)for(int cz=bounds.minZ()>>4;cz<=bounds.maxZ()>>4;cz++){
                var chunk=new ChunkPos(cx,cz);level.getChunk(cx,cz);
                var clip=new BoundingBox(chunk.getMinBlockX(),level.getMinBuildHeight(),chunk.getMinBlockZ(),chunk.getMaxBlockX(),level.getMaxBuildHeight()-1,chunk.getMaxBlockZ());
                piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),RandomSource.create(59),clip,chunk,origin);
            }
        }
        return new Fixture(origin,id);
    }
    private static FakePlayer player(GameTestHelper h,BlockPos pos){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"lift-native"));p.setGameMode(GameType.SURVIVAL);
        p.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+.5);return p;
    }
    private static void strike(FakePlayer p,BlockPos pos,int sequence){
        p.gameMode.handleBlockBreakAction(pos,ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK,Direction.NORTH,p.level().getMaxBuildHeight(),sequence);
        p.gameMode.handleBlockBreakAction(pos,ServerboundPlayerActionPacket.Action.ABORT_DESTROY_BLOCK,Direction.NORTH,p.level().getMaxBuildHeight(),sequence+1);
    }
    private static net.minecraft.server.level.ServerPlayer nativePlayer(GameTestHelper h,BlockPos pos){
        var level=h.getLevel();var p=new net.minecraft.server.level.ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),"lift-position"));
        // Keep the real packet-listener teleport logic; Forge FakePlayer deliberately disables it.
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(GameType.SURVIVAL);p.setPos(Vec3.atBottomCenterOf(pos));return p;
    }
    private static void use(GameTestHelper h,net.minecraft.server.level.ServerPlayer p,BlockPos pos){
        var state=h.getLevel().getBlockState(pos);state.getBlock().use(state,h.getLevel(),pos,p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(pos),Direction.NORTH,pos,false));
    }
    @GameTest(template="bow_ritual_test",batch="cod2_lift_authored")
    public static void fourAuthoredStelesHaveIndependentBreakageAndSharedPermanentRoute(GameTestHelper h){
        var f=generate(h);var level=h.getLevel();var room=DungeonStateStore.get(level).room(f.instance(),"imperial_vault");
        var steles=ChenshaPiece.returnSteleOffsets();h.assertTrue(steles.size()==4,"Four authored corners exist");
        for(var offset:steles){var pos=f.origin().offset(offset);
            h.assertTrue(level.getBlockState(pos).is(DungeonContent.SHORTCUT_STELE.get()),"Production column places every corner stele");
            h.assertTrue(level.getBlockState(pos.above()).isAir()&&!ChenshaVaultLayout.moatCell(offset.getX(),offset.getZ()),"Each corner has dry ground and headroom");
        }
        var pos=f.origin().offset(steles.get(2));var p=player(h,pos.south(2));strike(p,pos,1);
        h.assertTrue(!room.shortcutOpen("return_lift"),"A bare-handed native mining action cannot open the shortcut");
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_PICKAXE));strike(p,pos,3);
        h.assertTrue(room.shortcutOpen("return_lift")&&room.shortcutOpen("return_lift_corner_2"),"Pickaxe strike opens selected stone and shared lift");
        for(int n=0;n<4;n++){
            var be=(DungeonMechanismBlockEntity)level.getBlockEntity(f.origin().offset(steles.get(n)));be.syncVisual(room);
            h.assertTrue(be.getBlockState().getValue(DungeonMechanismBlock.OPEN)==(n==2),"Unstruck stones keep their independent collision and visual state");
        }
        var copy=DungeonStateStore.load(DungeonStateStore.get(level).save(new net.minecraft.nbt.CompoundTag())).room(f.instance(),"imperial_vault");
        copy.reset();h.assertTrue(copy.shortcutOpen("return_lift")&&copy.shortcutOpen("return_lift_corner_2"),"Saved progress and selected stone survive room reset");
        strike(p,pos,5);h.assertTrue(!room.unlockShortcut("return_lift"),"Repeated strike cannot duplicate unlock");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_lift_authored")
    public static void actualReturnLiftRequiresUnlockAlivePlayerAndSafeLanding(GameTestHelper h){
        var f=generate(h);var level=h.getLevel();var lift=f.origin().offset(41,1,8);var landing=f.origin().offset(41,73,8);
        var p=nativePlayer(h,lift.east());use(h,p,lift);h.assertTrue(p.getY()<landing.getY(),"Locked lift cannot carry a player");
        h.assertTrue(level.getBlockState(landing).isAir()&&level.getBlockState(landing.above()).isAir(),"Authored arrival has two-block headroom");
        var room=DungeonStateStore.get(level).room(f.instance(),"imperial_vault");room.unlockShortcut("return_lift");
        var be=(DungeonMechanismBlockEntity)level.getBlockEntity(lift);be.syncVisual(room);
        level.setBlockAndUpdate(landing,Blocks.STONE.defaultBlockState());use(h,p,lift);
        h.assertTrue(p.getY()<landing.getY(),"A blocked arrival cannot place a player inside stone");
        level.setBlockAndUpdate(landing,Blocks.AIR.defaultBlockState());p.setHealth(0);use(h,p,lift);
        h.assertTrue(p.getY()<landing.getY(),"A dead player cannot activate the route");p.setHealth(20);use(h,p,lift);
        h.assertTrue(p.position().distanceToSqr(Vec3.atBottomCenterOf(landing))<.01&&p.fallDistance==0,"Native lift carries the living player to its authored entrance landing");
        var other=nativePlayer(h,lift.east());use(h,other,lift);
        h.assertTrue(other.position().distanceToSqr(Vec3.atBottomCenterOf(landing))<.01,"Second player shares the permanent route");h.succeed();
    }
    private ChenshaShortcutGameTests(){}
}
