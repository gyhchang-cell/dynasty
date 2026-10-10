package com.dynasty.structure.megabuild;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class RoofRepairNativeGameTests {
    private static int fixtureSequence;
    private record Fixture(ServerPlayer player,BlockPos roof,BlockPos terrain,BlockPos chest,BlockPos sentinel,BlockState authored){}
    private static Fixture fixture(GameTestHelper h)throws Exception{
        var level=h.getLevel();var b=SculptureBlueprint.load(level.getServer().getResourceManager(),"yunqi_manor");
        int bx=-1,bz=-1;search:for(int x=0;x<b.width-1;x++)for(int z=0;z<b.length;z++)if(b.columnTop(x,z)>=4&&b.columnTop(x+1,z)>=4){bx=x;bz=z;break search;}h.assertTrue(bx>=0,"Existing source has adjacent authored roof columns");
        // Own temporary native chunks, outside adjacent large templates and separate for each fixture.
        var base=new ChunkPos(h.absolutePos(new BlockPos(6,2,6)));var chunk=new ChunkPos(base.x+64+(++fixtureSequence)*8,base.z+64);BlockPos roof=new BlockPos(chunk.getMinBlockX()+8,160,chunk.getMinBlockZ()+8);
        int top=b.columnTop(bx,bz);var origin=new BlockPos(roof.getX()-bx,roof.getY()-top,roof.getZ()-bz);
        var tag=new CompoundTag();tag.putString("id","dynasty:sculpture_tile");tag.putIntArray("BB",new int[]{chunk.getMinBlockX(),origin.getY(),chunk.getMinBlockZ(),chunk.getMaxBlockX(),Math.max(roof.getY()+6,origin.getY()+b.height+4),chunk.getMaxBlockZ()});tag.putInt("O",-1);tag.putInt("GD",0);tag.putString("Sculpture","yunqi_manor");tag.putLong("Origin",origin.asLong());
        var context=StructurePieceSerializationContext.fromLevel(level);var piece=NaturalSculptures.TILE.get().load(context,tag);
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty","yunqi_manor"));
        var start=new StructureStart(structure,chunk,0,new PiecesContainer(List.of(piece)));
        // Native save/read of an existing authored instance, then the real manager references.
        var reloaded=StructureStart.loadStaticStart(context,start.createTag(context,chunk),level.getSeed());h.assertTrue(reloaded!=null&&reloaded.isValid(),"Native saved selected instance reloads");
        var nativeChunk=level.getChunk(chunk.x,chunk.z);
        // A controlled saved-instance fixture. Other-reference safety is authored explicitly below.
        nativeChunk.setAllReferences(Map.of(structure,new it.unimi.dsi.fastutil.longs.LongOpenHashSet(new long[]{chunk.toLong()})));
        nativeChunk.setStartForStructure(structure,reloaded);
        h.assertTrue(level.getChunkSource().getChunkNow(chunk.x,chunk.z)==nativeChunk,"Native selected-instance fixture chunk is genuinely available without a survey load");
        var authored=net.minecraft.commands.arguments.blocks.BlockStateParser.parseForBlock(net.minecraft.core.registries.BuiltInRegistries.BLOCK.asLookup(),b.palette.get(b.at(bx,top,bz)),false).blockState();level.setBlockAndUpdate(roof,authored);
        var otherRoof=origin.offset(bx+1,b.columnTop(bx+1,bz),bz);var otherState=net.minecraft.commands.arguments.blocks.BlockStateParser.parseForBlock(net.minecraft.core.registries.BuiltInRegistries.BLOCK.asLookup(),b.palette.get(b.at(bx+1,b.columnTop(bx+1,bz),bz)),false).blockState();level.setBlockAndUpdate(otherRoof,otherState);
        var terrain=roof.above();level.setBlockAndUpdate(terrain,Blocks.STONE.defaultBlockState());var chest=otherRoof.above();level.setBlockAndUpdate(chest,Blocks.CHEST.defaultBlockState());var container=(net.minecraft.world.level.block.entity.ChestBlockEntity)level.getBlockEntity(chest);container.setItem(0,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.DIAMOND,17));
        var sentinel=roof.east(3).above();level.setBlockAndUpdate(sentinel,Blocks.DIAMOND_BLOCK.defaultBlockState());
        var p=new ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),"roof-native"));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(roof.below(2)));
        return new Fixture(p,roof,terrain,chest,sentinel,authored);
    }
    private static int command(ServerPlayer p,String action,int permission){return p.server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(permission).withSuppressedOutput(),"dynasty repair_roof "+action);}
    private static void close(Fixture f){RoofRepair.logout(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(f.player));f.player.discard();}
    @GameTest(template="bow_ritual_test",batch="cod6_roof_native_receipt",setupTicks=20,timeoutTicks=100)
    public static void actualAdminPreviewAndConfirmOnlyRepairSelectedSavedInstanceAndNativeDiskReceiptPreservesOriginalStates(GameTestHelper h)throws Exception{
        var f=fixture(h);try{
            var before=h.getLevel().getBlockState(f.terrain);var chest=(net.minecraft.world.level.block.entity.ChestBlockEntity)h.getLevel().getBlockEntity(f.chest);var inventory=chest.saveWithFullMetadata();
            h.assertTrue(command(f.player,"preview",0)==0&&command(f.player,"confirm",0)==0,"Real command permission tree rejects non-operator preview and confirmation");
            var survey=NaturalSculptures.roofSurvey(f.player);h.assertTrue(survey.cells().size()==1&&survey.containers()>=1&&survey.alteredRoofs()>0,"Native saved source survey lists one uncertain terrain cell, protected real chest and unconfirmed/edited roof columns: cells="+survey.cells()+", containers="+survey.containers()+", altered="+survey.alteredRoofs()+", reserved="+survey.reserved());
            int entities=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(f.terrain).inflate(5)).size();
            h.assertTrue(command(f.player,"preview",2)==1&&h.getLevel().getBlockState(f.terrain).equals(before)&&chest.saveWithFullMetadata().equals(inventory),"Actual administrator read-only preview changes neither terrain nor inventory");
            h.assertTrue(command(f.player,"confirm",2)==1&&h.getLevel().isEmptyBlock(f.terrain)&&h.getLevel().getBlockState(f.roof).equals(f.authored)&&h.getLevel().getBlockState(f.sentinel).is(Blocks.DIAMOND_BLOCK)&&chest.saveWithFullMetadata().equals(inventory),"Real explicit confirmation removes only selected terrain, preserves source roof, foreign block and17diamond container NBT");
            h.assertTrue(command(f.player,"confirm",2)==0&&command(f.player,"preview",2)==0&&h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(f.terrain).inflate(5)).size()==entities,"Repeat is idempotent and native replacement creates no dropped items");
            h.getLevel().getServer().overworld().getDataStorage().save();var disk=h.getLevel().getServer().getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT).resolve("data/"+RoofRepair.History.KEY+".dat");
            var stored=NbtIo.readCompressed(disk.toFile());var data=stored.getCompound("data");h.assertTrue(data.getInt("Version")==1,"Native SavedData file contains explicit receipt version");var restored=RoofRepair.History.load(data).receipts.get(f.player.getUUID());
            h.assertTrue(restored!=null&&restored.dimension().equals(h.getLevel().dimension().location().toString())&&restored.anchor().equals(f.player.blockPosition())&&restored.cells().size()==1&&restored.cells().get(f.terrain).equals(before),"Actual compressed disk/NBT read preserves bounded original position/state/dimension/operator receipt for recovery, not a live old-world claim");h.succeed();
        }finally{close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_roof_native_supported_decoration",setupTicks=20,timeoutTicks=100)
    public static void actualSupportedTorchAndElevatedChestReserveEntireColumnAndPostPreviewChangeCannotPopPlayerDecoration(GameTestHelper h)throws Exception{
        var f=fixture(h);try{
            var level=h.getLevel();var ornament=f.terrain.above();level.setBlockAndUpdate(ornament,Blocks.TORCH.defaultBlockState());
            var survey=NaturalSculptures.roofSurvey(f.player);h.assertTrue(level.getBlockState(ornament).is(Blocks.TORCH)&&survey.cells().isEmpty()&&survey.reserved()>0,"Real supported torch reserves its original supporting stone, not merely the decoration itself");
            int drops=level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(f.terrain).inflate(4)).size();
            h.assertTrue(command(f.player,"preview",2)==0&&command(f.player,"confirm",2)==0&&level.getBlockState(f.terrain).is(Blocks.STONE)&&level.getBlockState(ornament).is(Blocks.TORCH)&&level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(f.terrain).inflate(4)).size()==drops,"Actual admin no-op preserves supported native decoration and creates no neighbor-update item drops");
            level.setBlockAndUpdate(ornament,Blocks.AIR.defaultBlockState());h.assertTrue(command(f.player,"preview",2)==1,"Only explicitly empty column becomes an original legal terrain preview");
            level.setBlockAndUpdate(ornament,Blocks.CHEST.defaultBlockState());var chest=(net.minecraft.world.level.block.entity.ChestBlockEntity)level.getBlockEntity(ornament);chest.setItem(0,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.DIAMOND,17));var saved=chest.saveWithFullMetadata();
            h.assertTrue(command(f.player,"confirm",2)==0&&level.getBlockState(f.terrain).is(Blocks.STONE)&&chest.saveWithFullMetadata().equals(saved),"Actual elevated player chest after preview invalidates confirmation, preserves its support and exact17diamond native NBT");h.succeed();
        }finally{close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_roof_native_side_attachment",setupTicks=20,timeoutTicks=100)
    public static void actualWallTorchAttachedBesideCandidateKeepsItsStoneSupportAndNativeDecorationWithoutNeighborDrops(GameTestHelper h)throws Exception{
        var f=fixture(h);try{
            var level=h.getLevel();var side=f.terrain.west();level.setBlockAndUpdate(side,Blocks.WALL_TORCH.defaultBlockState().setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.HORIZONTAL_FACING,Direction.WEST));
            h.assertTrue(level.getBlockState(side).is(Blocks.WALL_TORCH)&&level.getBlockState(side).canSurvive(level,side),"Actual native side decoration really depends on candidate stone support");
            int before=level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(f.terrain).inflate(4)).size();
            var survey=NaturalSculptures.roofSurvey(f.player);h.assertTrue(survey.cells().isEmpty()&&survey.reserved()>0&&command(f.player,"preview",2)==0&&command(f.player,"confirm",2)==0&&level.getBlockState(f.terrain).is(Blocks.STONE)&&level.getBlockState(side).is(Blocks.WALL_TORCH)&&level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(f.terrain).inflate(4)).size()==before,"Real readonly preview preserves nearby attached native torch, supporting terrain and item-entity count");h.succeed();
        }finally{close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_roof_native_stale",setupTicks=20,timeoutTicks=100)
    public static void actualEmptyPreviewMovementAndEditedRoofInvalidateOldPlanWithoutDeletingAnyTerrain(GameTestHelper h)throws Exception{
        var f=fixture(h);try{
            h.assertTrue(command(f.player,"preview",2)==1,"Real initial preview selects actual stored instance: survey="+NaturalSculptures.roofSurvey(f.player)+", refs="+h.getLevel().getChunkAt(f.roof).getAllReferences());var feet=f.player.position();f.player.setPos(feet.add(64,0,0));h.assertTrue(command(f.player,"preview",2)==0,"Actual preview outside stored instance invalidates prior plan");f.player.setPos(feet);
            h.assertTrue(command(f.player,"confirm",2)==0&&h.getLevel().getBlockState(f.terrain).is(Blocks.STONE),"Returning cannot confirm stale plan left by an empty preview");
            command(f.player,"preview",2);h.getLevel().setBlockAndUpdate(f.roof,Blocks.DIAMOND_BLOCK.defaultBlockState());h.assertTrue(command(f.player,"confirm",2)==0&&h.getLevel().getBlockState(f.terrain).is(Blocks.STONE)&&h.getLevel().getBlockState(f.roof).is(Blocks.DIAMOND_BLOCK),"Roof changed after preview invalidates whole real confirmation instead of clearing above player extension");
            h.getLevel().setBlockAndUpdate(f.roof,f.authored);command(f.player,"preview",2);f.player.setPos(feet.add(12,0,0));h.assertTrue(command(f.player,"confirm",2)==0&&h.getLevel().getBlockState(f.terrain).is(Blocks.STONE),"Actual operator moving beyond eight-block selected range cannot confirm elsewhere");h.succeed();
        }finally{close(f);}
    }
    public static final class Protection {
        final BlockPos cell;int called;Protection(BlockPos cell){this.cell=cell;}
        @net.minecraftforge.eventbus.api.SubscribeEvent public void breakBlock(net.minecraftforge.event.level.BlockEvent.BreakEvent e){if(e.getPos().equals(cell)){called++;e.setCanceled(true);}}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_roof_native_protection",setupTicks=20,timeoutTicks=100)
    public static void actualForgeProtectionVetoRunsBeforeAnyRepairWriteAndAllowsFreshUnprotectedConfirmation(GameTestHelper h)throws Exception{
        var f=fixture(h);var guard=new Protection(f.terrain);var bus=net.minecraftforge.common.MinecraftForge.EVENT_BUS;boolean registered=false;
        try{
            command(f.player,"preview",2);bus.register(guard);registered=true;h.assertTrue(command(f.player,"confirm",2)==0&&guard.called==1&&h.getLevel().getBlockState(f.terrain).is(Blocks.STONE)&&!RoofRepair.History.get(f.player.server).receipts.containsKey(f.player.getUUID()),"Authentic Forge claim/protection veto prevents all writes and receipt, independent of operator permission");bus.unregister(guard);registered=false;
            h.assertTrue(command(f.player,"confirm",2)==0,"Veto consumes old plan; no latent confirmation");h.assertTrue(command(f.player,"preview",2)==1&&command(f.player,"confirm",2)==1,"Removing veto still needs fresh actual preview before legal confirmation");h.succeed();
        }finally{if(registered)bus.unregister(guard);close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_roof_native_neighbor",setupTicks=20,timeoutTicks=100)
    public static void actualOtherSavedPieceAndUnloadedReferenceRemainReservedWithoutLoadingOrDeletingThem(GameTestHelper h)throws Exception{
        var f=fixture(h);var level=h.getLevel();var chunk=new ChunkPos(f.roof);var nativeChunk=level.getChunk(chunk.x,chunk.z);
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty","yunqi_manor"));
        var neighbor=new ChunkPos(chunk.x+1,chunk.z);var far=new ChunkPos(chunk.x+200,chunk.z+200);
        try{
            var context=StructurePieceSerializationContext.fromLevel(level);var own=nativeChunk.getStartForStructure(structure);var tag=own.getPieces().get(0).createTag(context);
            tag.putLong("Origin",BlockPos.of(tag.getLong("Origin")).east().asLong());tag.putIntArray("BB",new int[]{f.terrain.getX(),f.terrain.getY(),f.terrain.getZ(),f.terrain.getX(),f.terrain.getY(),f.terrain.getZ()});
            var other=NaturalSculptures.TILE.get().load(context,tag);var foreign=new StructureStart(structure,neighbor,0,new PiecesContainer(List.of(other)));
            level.getChunk(neighbor.x,neighbor.z).setStartForStructure(structure,foreign);nativeChunk.addReferenceForStructure(structure,neighbor.toLong());
            var survey=NaturalSculptures.roofSurvey(f.player);h.assertTrue(survey.cells().isEmpty()&&survey.reserved()>0&&command(f.player,"preview",2)==0&&level.getBlockState(f.terrain).is(Blocks.STONE),"Actual foreign saved piece reserves the otherwise eligible terrain cell; matching material is never enough to delete neighboring structure");
            nativeChunk.getReferencesForStructure(structure).remove(neighbor.toLong());h.assertTrue(level.getChunkSource().getChunkNow(far.x,far.z)==null,"Native unloaded reference fixture really starts unloaded");nativeChunk.addReferenceForStructure(structure,far.toLong());
            survey=NaturalSculptures.roofSurvey(f.player);h.assertTrue(survey.cells().isEmpty()&&survey.reserved()>0&&level.getChunkSource().getChunkNow(far.x,far.z)==null&&level.getBlockState(f.terrain).is(Blocks.STONE),"Unverifiable foreign reference conservatively reserves loaded chunk; actual survey never forces its missing start chunk");h.succeed();
        }finally{nativeChunk.getReferencesForStructure(structure).remove(neighbor.toLong());nativeChunk.getReferencesForStructure(structure).remove(far.toLong());close(f);}
    }
}
