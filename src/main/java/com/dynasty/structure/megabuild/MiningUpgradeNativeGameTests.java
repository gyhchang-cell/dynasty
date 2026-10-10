package com.dynasty.structure.megabuild;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class MiningUpgradeNativeGameTests {
    private static int sequence;
    private record Fixture(ServerPlayer player,MegabuildPiece piece,StructureStart start,Structure structure,ChunkPos owner,Vec3 entrance){}
    private static Fixture fixture(GameTestHelper h,int version,int rotation)throws Exception{
        // Independent remote cells, not offsets from the full-suite template grid: different
        // batches can otherwise put two 96-block fixtures on top of one another.
        var level=h.getLevel();var owner=new ChunkPos(4096+(++sequence)*16,4096);var origin=new BlockPos(owner.getMinBlockX(),160,owner.getMinBlockZ());
        var context=StructurePieceSerializationContext.fromLevel(level);var initial=new MegabuildPiece(MegabuildStructures.MINING_PIECE.get(),0,origin,MegabuildStructures::mining,71,rotation,96,36);
        var tag=initial.createTag(context);tag.putInt("MegabuildLayout",version);var old=(MegabuildPiece)MegabuildStructures.MINING_PIECE.get().load(context,tag);
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty","tiangong_mining_estate"));
        var start=StructureStart.loadStaticStart(context,new StructureStart(structure,owner,0,new PiecesContainer(List.of(old))).createTag(context,owner),level.getSeed());var piece=(MegabuildPiece)start.getPieces().get(0);
        for(int x=owner.x-1;x<=owner.x+6;x++)for(int z=owner.z-1;z<=owner.z+6;z++){var chunk=level.getChunk(x,z);chunk.setAllReferences(Map.of(structure,new it.unimi.dsi.fastutil.longs.LongOpenHashSet(new long[]{owner.toLong()})));}
        level.getChunk(owner.x,owner.z).setStartForStructure(structure,start);
        piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,piece.getBoundingBox(),owner,origin);
        int x=47,z=5;for(int r=0;r<rotation;r++){int previous=x;x=95-z;z=previous;}var entrance=Vec3.atBottomCenterOf(piece.miningWorld(x,1,z));
        var p=new ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),"mine-upgrade-native"));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(entrance);return new Fixture(p,piece,start,structure,owner,entrance);
    }
    private static int command(ServerPlayer p,String action,int permission){return p.server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(permission).withSuppressedOutput(),"dynasty upgrade_mine "+action);}
    private static MiningUpgrade.Survey legal(GameTestHelper h,Fixture f){var s=MiningUpgrade.survey(f.player);var b=f.piece.getBoundingBox();var entities=s.refusal().isEmpty()?"":h.getLevel().getEntities((net.minecraft.world.entity.Entity)null,new net.minecraft.world.phys.AABB(b.minX(),b.minY(),b.minZ(),b.maxX()+1,b.maxY()+1,b.maxZ()+1),e->!e.isRemoved()).stream().map(e->net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(e.getType())+"@"+e.blockPosition()+" "+(e instanceof net.minecraft.world.entity.item.ItemEntity item?item.getItem():"")).toList().toString();h.assertTrue(s.refusal().isEmpty()&&!s.changes().isEmpty(),"Actual saved native legacy instance is eligible: "+s.refusal()+"; fixtureEntities="+entities);return s;}
    private static void untouched(GameTestHelper h,Fixture f,MiningUpgrade.Survey s){s.changes().forEach((pos,c)->h.assertTrue(h.getLevel().getBlockState(pos).equals(c.before()),"Rejected transaction never changes "+pos));s.containers().forEach((pos,nbt)->h.assertTrue(h.getLevel().getBlockEntity(pos).saveWithFullMetadata().equals(nbt),"Native original container unchanged at "+pos));h.assertTrue(f.piece.legacyMine(),"Rejected operation never advances one-time native version");}
    private static void close(Fixture f){MiningUpgrade.logout(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(f.player));f.player.discard();}
    public static final class Drops {
        final BoundingBox bounds;int count;Drops(BoundingBox bounds){this.bounds=bounds;}
        @net.minecraftforge.eventbus.api.SubscribeEvent public void joined(net.minecraftforge.event.entity.EntityJoinLevelEvent e){if(e.getEntity() instanceof net.minecraft.world.entity.item.ItemEntity item&&bounds.isInside(item.blockPosition()))count++;}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_mine_upgrade_native_receipt",setupTicks=20,timeoutTicks=200)
    public static void actualRotatedV4UpgradePreservesPlayerAndUnopenedContainersAndNativeDiskVersionRejectsRefillAfterReload(GameTestHelper h)throws Exception{
        var f=fixture(h,4,1);try{
            var initial=legal(h,f);var entries=initial.containers().keySet().stream().filter(pos->h.getLevel().getBlockEntity(pos) instanceof ChestBlockEntity).toList();h.assertTrue(entries.size()>=2,"Native original generation really placed multiple old chests");
            var first=(ChestBlockEntity)h.getLevel().getBlockEntity(entries.get(0));var second=(ChestBlockEntity)h.getLevel().getBlockEntity(entries.get(1));first.clearContent();var diamonds=new ItemStack(Items.DIAMOND,17);diamonds.getOrCreateTag().putString("ForeignPlayerData","native-save-preserve");first.setItem(2,diamonds);second.clearContent();second.setLootTable(new ResourceLocation("dynasty","chests/tiangong_common"),73);
            var s=legal(h,f);h.assertTrue(command(f.player,"preview",0)==0&&command(f.player,"confirm",0)==0,"Actual command permissions reject non-operator preview/confirmation");
            h.assertTrue(command(f.player,"preview",2)==s.changes().size(),"Readonly command lists precise original candidate count");untouched(h,f,s);
            var drops=new Drops(f.piece.getBoundingBox());var bus=net.minecraftforge.common.MinecraftForge.EVENT_BUS;bus.register(drops);try{h.assertTrue(command(f.player,"confirm",2)==s.changes().size(),"Actual native confirmation changes this selected instance once");h.assertTrue(drops.count==0,"Native migration emits no incidental lantern/support item drops or duplicated original furniture loot");}finally{bus.unregister(drops);}
            s.changes().forEach((pos,c)->h.assertTrue(h.getLevel().getBlockState(pos).is(c.after().getBlock()),"Real final ore/gallery/new chest matches actual target source at "+pos));s.containers().forEach((pos,nbt)->h.assertTrue(h.getLevel().getBlockEntity(pos).saveWithFullMetadata().equals(nbt),"Original player17diamonds/foreignNBT and unopened loot table/seed stay exact at original coordinates"));
            h.assertTrue(!f.piece.legacyMine()&&command(f.player,"confirm",2)==0&&command(f.player,"preview",2)==0,"Piece one-time revision rejects repeat rewards and world writes");h.assertTrue(s.changes().values().stream().filter(MiningUpgrade.Change::newChest).count()==4,"Intact native rotated mine creates all four original new mine chests");
            for(var e:s.changes().entrySet())if(e.getValue().newChest()){var chest=(ChestBlockEntity)h.getLevel().getBlockEntity(e.getKey());int occupied=0,core=0;for(int slot=0;slot<27;slot++){var stack=chest.getItem(slot);if(!stack.isEmpty())occupied++;if(stack.is(com.dynasty.DynastyItems.JADE.get()))core+=stack.getCount();}h.assertTrue(occupied==9&&core==1,"Migration uses original exact9slot/one-jade new-placement reward; never refills old containers");}
            f.player.server.overworld().getDataStorage().save();var root=f.player.server.getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT);var saved=NbtIo.readCompressed(root.resolve("data/"+MiningUpgrade.History.KEY+".dat").toFile());var receipt=MiningUpgrade.History.load(saved.getCompound("data")).receipts.get(f.player.getUUID());h.assertTrue(receipt!=null&&receipt.originalPiece().getInt("MegabuildLayout")==4&&receipt.changes().equals(s.changes())&&receipt.containers().equals(s.containers()),"Actual compressed SavedData disk reload preserves original states/piece and exact old-container NBT receipt");
            var context=StructurePieceSerializationContext.fromLevel(h.getLevel());var disk=root.resolve("data/mine-selected-native-"+f.player.getUUID()+".nbt");NbtIo.writeCompressed(f.start.createTag(context,f.owner),disk.toFile());var reloaded=StructureStart.loadStaticStart(context,NbtIo.readCompressed(disk.toFile()),h.getLevel().getSeed());var loaded=(MegabuildPiece)reloaded.getPieces().get(0);h.assertTrue(!loaded.legacyMine()&&loaded.miningLayout()==4,"Native compressed structure-start reload retains original seed/version and one-time upgrade without rewriting all legacy layouts");
            h.getLevel().getChunk(f.owner.x,f.owner.z).setStartForStructure(f.structure,reloaded);h.assertTrue(command(f.player,"preview",2)==0,"Command resolves actual reloaded instance and refuses a new transaction");var pos=entries.get(0);var nbt=h.getLevel().getBlockEntity(pos).saveWithFullMetadata();loaded.postProcess(h.getLevel(),h.getLevel().structureManager(),h.getLevel().getChunkSource().getGenerator(),h.getLevel().random,new BoundingBox(pos),new ChunkPos(pos),pos);h.assertTrue(h.getLevel().getBlockEntity(pos).saveWithFullMetadata().equals(nbt),"Upgraded native placement replay preserves old container NBT too");h.succeed();
        }finally{close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_mine_upgrade_native_stale",setupTicks=20,timeoutTicks=200)
    public static void actualV2RotatedNativePlayerEditAfterPreviewInvalidatesWholeTransactionAndNewSelectionOrMovementCannotReusePlan(GameTestHelper h)throws Exception{
        var f=fixture(h,2,2);try{
            var s=legal(h,f);var changed=s.changes().keySet().stream().filter(pos->!s.changes().get(pos).before().isAir()).findFirst().orElseThrow();
            h.assertTrue(command(f.player,"preview",2)>0,"Native v2 source including its original mirror/rotation supports exact preview");h.getLevel().setBlock(changed,Blocks.DIAMOND_BLOCK.defaultBlockState(),2);
            h.assertTrue(command(f.player,"confirm",2)==0&&h.getLevel().getBlockState(changed).is(Blocks.DIAMOND_BLOCK),"Native changed player block after preview refuses all writes, never overwrites edit");
            s.changes().forEach((pos,c)->{if(!pos.equals(changed))h.assertTrue(h.getLevel().getBlockState(pos).equals(c.before()),"Other original source cells stay untouched after rejected stale operation");});
            h.assertTrue(command(f.player,"preview",2)==0&&f.piece.legacyMine(),"Ambiguous remodel reserves the ENTIRE selected instance and one-time version remains unclaimed");h.getLevel().setBlock(changed,s.changes().get(changed).before(),2);
            h.assertTrue(command(f.player,"preview",2)>0,"Explicit original state restoration permits a fresh preview");f.player.setPos(f.entrance.add(160,0,0));h.assertTrue(command(f.player,"preview",2)==0,"An empty preview outside the actual saved instance invalidates old selection");f.player.setPos(f.entrance);h.assertTrue(command(f.player,"confirm",2)==0,"Returning cannot resurrect a previously invalidated preview");
            command(f.player,"preview",2);f.player.setPos(f.entrance.add(12,0,0));h.assertTrue(command(f.player,"confirm",2)==0,"Actual12block movement exceeds original eight-block confirmation bound");f.player.setPos(f.entrance);untouched(h,f,s);
            command(f.player,"preview",2);var container=s.containers().keySet().iterator().next();var be=(net.minecraft.world.Container)h.getLevel().getBlockEntity(container);be.setItem(0,new ItemStack(Items.DIAMOND,17));h.assertTrue(command(f.player,"confirm",2)==0&&be.getItem(0).is(Items.DIAMOND)&&be.getItem(0).getCount()==17,"Changing native chest OR barrel inventory after a preview also rejects transaction without consuming or replacing content");h.succeed();
        }finally{close(f);}
    }
    public static final class Protection {
        final BlockPos cell;int called;Protection(BlockPos cell){this.cell=cell;}
        @net.minecraftforge.eventbus.api.SubscribeEvent public void block(net.minecraftforge.event.level.BlockEvent.BreakEvent e){if(e.getPos().equals(cell)){called++;e.setCanceled(true);}}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_mine_upgrade_native_protection",setupTicks=20,timeoutTicks=200)
    public static void actualV3NativeForgeProtectionVetoPrecedesEveryWriteAndFreshConsentIsRequiredAfterVetoRemoved(GameTestHelper h)throws Exception{
        var f=fixture(h,3,3);var s=legal(h,f);var guard=new Protection(s.changes().keySet().iterator().next());var bus=net.minecraftforge.common.MinecraftForge.EVENT_BUS;boolean registered=false;
        try{
            h.assertTrue(command(f.player,"preview",2)>0,"Actual v3 saved mirror/rotation supports native preview");bus.register(guard);registered=true;
            h.assertTrue(command(f.player,"confirm",2)==0&&guard.called==1&&!MiningUpgrade.History.get(f.player.server).receipts.containsKey(f.player.getUUID()),"Authentic Forge protection veto occurs before ANY write, upgrade flag or success receipt");untouched(h,f,s);bus.unregister(guard);registered=false;
            h.assertTrue(command(f.player,"confirm",2)==0,"Canceled preview cannot remain latent");h.assertTrue(command(f.player,"preview",2)>0&&command(f.player,"confirm",2)==s.changes().size(),"Removed protection still requires a fresh actual preview and explicit transaction");h.assertTrue(!f.piece.legacyMine(),"Actual oldest mirror source can finish new native upgrade without changing registry ID");h.succeed();
        }finally{if(registered)bus.unregister(guard);close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_mine_upgrade_native_missing",setupTicks=20,timeoutTicks=200)
    public static void actualV5UnloadedForeignReferenceNeverLoadsAndPlayerInsideProposedSolidCellPreventsBuryingOrConsumingUpgrade(GameTestHelper h)throws Exception{
        var f=fixture(h,5,0);try{
            var s=legal(h,f);var far=new ChunkPos(f.owner.x+1000,f.owner.z+1000);var nativeChunk=h.getLevel().getChunk(f.owner.x,f.owner.z);
            h.assertTrue(h.getLevel().getChunkSource().getChunkNow(far.x,far.z)==null,"Actual native foreign start really begins unloaded");nativeChunk.addReferenceForStructure(f.structure,far.toLong());
            h.assertTrue(command(f.player,"preview",2)==0&&h.getLevel().getChunkSource().getChunkNow(far.x,far.z)==null,"Readonly whole-instance integrity check refuses unverifiable references without forcing native chunk loads");nativeChunk.getReferencesForStructure(f.structure).remove(far.toLong());untouched(h,f,s);
            var obstructed=s.changes().entrySet().stream().filter(e->e.getValue().before().isAir()&&!e.getValue().after().isAir()).findFirst().orElseThrow().getKey();f.player.setPos(Vec3.atBottomCenterOf(obstructed));
            var refused=MiningUpgrade.survey(f.player);h.assertTrue(refused.refusal().contains("阻挡现有")&&command(f.player,"preview",2)==0&&f.piece.legacyMine(),"Actual native player collision box in newly solid gallery refuses entire upgrade instead of burying player: "+refused.refusal());f.player.setPos(f.entrance);untouched(h,f,s);
            h.assertTrue(command(f.player,"preview",2)==s.changes().size()&&command(f.player,"confirm",2)==s.changes().size(),"Leaving real target volume permits a fresh native v5-to6 gallery-only upgrade");h.assertTrue(s.changes().values().stream().noneMatch(MiningUpgrade.Change::newChest),"Already existing v5 original new mine chests never get paid or refilled again");s.containers().forEach((pos,nbt)->h.assertTrue(h.getLevel().getBlockEntity(pos).saveWithFullMetadata().equals(nbt),"Actual v5 existing native inventory survives exact"));h.succeed();
        }finally{close(f);}
    }
    @GameTest(template="bow_ritual_test",batch="cod6_mine_native_harvest_safety",setupTicks=20,timeoutTicks=200)
    public static void actualCurrentFullMineSurvivalHarvestChestUseAndTickingNonFireproofDropHaveNoGeneratedBurnHazard(GameTestHelper h)throws Exception{
        var f=fixture(h,6,0);var level=h.getLevel();var p=f.player;var box=f.piece.getBoundingBox();
        ChunkPos ticket=null;net.minecraft.world.entity.item.ItemEntity dropped=null;
        try{
            for(var pos:BlockPos.betweenClosed(box.minX()-1,box.minY()-1,box.minZ()-1,box.maxX()+1,box.maxY()+1,box.maxZ()+1)){
                var state=level.getBlockState(pos);
                h.assertTrue(!state.is(Blocks.FIRE)&&!state.is(Blocks.SOUL_FIRE)&&!state.is(Blocks.MAGMA_BLOCK)&&!state.is(Blocks.CAMPFIRE)&&!state.is(Blocks.SOUL_CAMPFIRE)&&!state.getFluidState().is(net.minecraft.tags.FluidTags.LAVA),"Entire actually placed new native mine plus boundary has no burning reward decoration at "+pos);
            }
            p.gameMode.changeGameModeForPlayer(net.minecraft.world.level.GameType.SURVIVAL);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.NETHERITE_PICKAXE));
            var source=f.piece.miningSource();BlockPos ore=null;
            for(int x=10;x<=38&&ore==null;x++)if(source.at(x,1,14)==Blueprint.Kind.ORE_COAL)ore=f.piece.miningWorld(x,1,14);
            h.assertTrue(ore!=null,"Original seeded native ore bench includes reachable coal ore");p.setPos(Vec3.atBottomCenterOf(ore.north()));
            var before=level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(ore).inflate(2)).stream().map(net.minecraft.world.entity.Entity::getUUID).collect(java.util.stream.Collectors.toSet());
            h.assertTrue(!p.isCreative()&&p.gameMode.destroyBlock(ore)&&level.getBlockState(ore).isAir(),"Native survival harvest really mines original ore, without creative or a substitute loot function");
            h.assertTrue(level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(ore).inflate(2)).stream().anyMatch(e->!before.contains(e.getUUID())&&e.getItem().is(Items.COAL)),"Actual native block harvesting creates its real unburned coal drop");
            var at=f.piece.miningWorld(39,1,29);p.setPos(Vec3.atBottomCenterOf(at.north()));
            p.gameMode.useItemOn(p,level,p.getMainHandItem(),net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.phys.BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));
            h.assertTrue(p.containerMenu instanceof net.minecraft.world.inventory.ChestMenu,"Native survival right-click opens the actual newly generated mining chest");var menu=(net.minecraft.world.inventory.ChestMenu)p.containerMenu;
            int slot=-1;for(int i=0;i<27;i++)if(menu.getSlot(i).getItem().is(com.dynasty.DynastyItems.JADE.get()))slot=i;
            h.assertTrue(slot>=0&&menu.getSlot(slot).getItem().getCount()==1,"Actual opened chest retains original one-jade core");var moved=menu.quickMoveStack(p,slot);h.assertTrue(moved.is(com.dynasty.DynastyItems.JADE.get())&&menu.getSlot(slot).getItem().isEmpty()&&p.getInventory().countItem(com.dynasty.DynastyItems.JADE.get())==1,"Native container transfer retrieves exactly one real reward");p.closeContainer();
            ItemStack jade=ItemStack.EMPTY;for(int i=0;i<p.getInventory().getContainerSize();i++)if(p.getInventory().getItem(i).is(com.dynasty.DynastyItems.JADE.get()))jade=p.getInventory().removeItem(i,1);
            h.assertTrue(!jade.isEmpty()&&!jade.getItem().isFireResistant(),"The observed reward has original normal fire vulnerability, no global immunity workaround");dropped=p.drop(jade,false);h.assertTrue(dropped!=null,"Native survival drop creates real reward item entity");dropped.setDeltaMovement(Vec3.ZERO);ticket=new ChunkPos(dropped.blockPosition());level.getChunkSource().addRegionTicket(net.minecraft.server.level.TicketType.FORCED,ticket,2,ticket);
            var observed=dropped;int age=observed.getAge();var heldTicket=ticket;
            h.runAfterDelay(40,()->{try{h.assertTrue(!observed.isRemoved()&&observed.isAlive()&&observed.getAge()>=age+20&&!observed.isOnFire()&&observed.getItem().is(com.dynasty.DynastyItems.JADE.get())&&observed.getItem().getCount()==1,"Real native world ticking keeps normally vulnerable mining reward intact after retrieval/drop; this is not a static source fixture");h.succeed();}finally{observed.discard();level.getChunkSource().removeRegionTicket(net.minecraft.server.level.TicketType.FORCED,heldTicket,2,heldTicket);close(f);}});
        }catch(Exception|AssertionError failure){if(dropped!=null)dropped.discard();if(ticket!=null)level.getChunkSource().removeRegionTicket(net.minecraft.server.level.TicketType.FORCED,ticket,2,ticket);close(f);throw failure;}
    }
}
