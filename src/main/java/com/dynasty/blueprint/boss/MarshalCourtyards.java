package com.dynasty.blueprint.boss;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** One authored yard UUID. Unloaded bosses remain reserved, and only confirmed death gives victory. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class MarshalCourtyards {
    public static boolean loaded(ServerLevel w,BlockPos centre){var b=new AABB(centre).inflate(17,1,17).expandTowards(0,16,0);if(b.minY<w.getMinBuildHeight()||b.maxY>=w.getMaxBuildHeight()||!w.getWorldBorder().isWithinBounds(b))return false;for(int x=net.minecraft.util.Mth.floor(b.minX)>>4;x<=net.minecraft.util.Mth.floor(b.maxX)>>4;x++)for(int z=net.minecraft.util.Mth.floor(b.minZ)>>4;z<=net.minecraft.util.Mth.floor(b.maxZ)>>4;z++)if(!w.hasChunkAt(new BlockPos(x<<4,0,z<<4)))return false;return true;}
    public static boolean summon(ServerLevel w,MarshalCourtyardState.Yard yard){if(w.dimension()!=Level.OVERWORLD||w.getDifficulty()==Difficulty.PEACEFUL||yard.defeated||yard.boss!=null||!loaded(w,yard.centre))return false;var type=BlindMarshalContent.MARSHAL.get();var at=Vec3.atBottomCenterOf(yard.centre);if(!w.noCollision(null,type.getDimensions().makeBoundingBox(at))||!w.getBlockState(yard.centre.below()).is(BlindMarshalContent.SOCKET.get()))return false;var mob=type.create(w);if(mob==null)return false;mob.moveTo(at.x,at.y,at.z,0,0);mob.bindArena(yard.centre);mob.finalizeSpawn(w,w.getCurrentDifficultyAt(yard.centre),MobSpawnType.EVENT,null,null);if(!w.addFreshEntity(mob))return false;yard.boss=mob.getUUID();MarshalCourtyardState.get(w).setDirty();return true;}
    @SubscribeEvent public static void rightClick(PlayerInteractEvent.RightClickBlock e){if(e.getHand()!=InteractionHand.MAIN_HAND||!(e.getEntity() instanceof ServerPlayer p)||!(e.getLevel() instanceof ServerLevel w)||p.isSpectator()||p.isCreative()||!w.getBlockState(e.getPos()).is(BlindMarshalContent.SOCKET.get())||p.distanceToSqr(Vec3.atCenterOf(e.getPos()))>6.5*6.5)return;var state=MarshalCourtyardState.get(w);var yard=state.yards.get(e.getPos().above().asLong());if(yard!=null&&summon(w,yard)){e.setCanceled(true);e.setCancellationResult(InteractionResult.SUCCESS);}}
    @SubscribeEvent public static void discover(TickEvent.PlayerTickEvent e){if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.isSpectator()||!(p.level() instanceof ServerLevel w)||w.dimension()!=Level.OVERWORLD||w.getGameTime()%80!=Math.floorMod(p.getId()+19,80))return;var registry=w.registryAccess().registryOrThrow(Registries.STRUCTURE);var wanted=new ResourceLocation("dynasty","marshal_courtyard");var starts=new LinkedHashSet<net.minecraft.world.level.levelgen.structure.StructureStart>();var origin=p.chunkPosition();int budget=64;
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){var pos=new ChunkPos(origin.x+dx,origin.z+dz);if(!w.hasChunk(pos.x,pos.z))continue;var c=w.getChunkSource().getChunk(pos.x,pos.z,net.minecraft.world.level.chunk.ChunkStatus.STRUCTURE_REFERENCES,false);if(c==null)continue;c.getAllStarts().forEach((type,start)->{if(wanted.equals(registry.getKey(type)))starts.add(start);});for(var ref:c.getAllReferences().entrySet())if(wanted.equals(registry.getKey(ref.getKey())))for(long packed:ref.getValue()){if(budget--<=0)break;var owner=new ChunkPos(packed);if(w.hasChunk(owner.x,owner.z)){var source=w.getChunkSource().getChunk(owner.x,owner.z,net.minecraft.world.level.chunk.ChunkStatus.STRUCTURE_STARTS,false);if(source!=null){var start=source.getStartForStructure(ref.getKey());if(start!=null)starts.add(start);}}}}
        var state=MarshalCourtyardState.get(w);for(var start:starts)if(start.isValid()&&start.getBoundingBox().isInside(p.blockPosition()))for(var piece:start.getPieces())if(piece instanceof MarshalCourtyardPiece yard)state.register(yard.centre());
    }
    public static void destroyed(BlindMarshal boss){if(!(boss.level() instanceof ServerLevel w)||boss.arenaCentre()==null)return;var state=MarshalCourtyardState.get(w);var yard=state.yards.get(boss.arenaCentre().asLong());if(yard!=null&&!yard.defeated&&boss.getUUID().equals(yard.boss)){yard.boss=null;state.setDirty();}}
    public static void confirmedDeath(BlindMarshal boss){if(!(boss.level() instanceof ServerLevel w)||boss.arenaCentre()==null)return;var state=MarshalCourtyardState.get(w);var yard=state.yards.get(boss.arenaCentre().asLong());if(yard==null||yard.defeated||!boss.getUUID().equals(yard.boss))return;yard.defeated=true;yard.victoryAt=w.getGameTime();yard.boss=null;state.setDirty();int count=0;for(var p:w.players())if(count<16&&!p.isSpectator()&&!p.isCreative()&&p.isAlive()&&p.distanceToSqr(Vec3.atBottomCenterOf(yard.centre))<=24*24&&state.firstRewarded.add(p.getUUID())){var stack=new ItemStack(BlindMarshalContent.OATH.get());if(!p.addItem(stack))p.drop(stack,false);count++;state.setDirty();}applyEnvironment(w,yard,16);}
    @SubscribeEvent public static void environment(TickEvent.LevelTickEvent e){if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel w)||w.dimension()!=Level.OVERWORLD||w.getGameTime()%20!=0)return;int budget=2;for(var yard:MarshalCourtyardState.get(w).yards.values())if(yard.defeated&&(yard.environmentCursor<64||yard.memorial==null)&&w.players().stream().anyMatch(p->!p.isSpectator()&&p.distanceToSqr(Vec3.atBottomCenterOf(yard.centre))<=48*48)&&loaded(w,yard.centre)){applyEnvironment(w,yard,16);placeMemorial(w,yard);if(--budget<=0)break;}}
    public static void applyEnvironment(ServerLevel w,MarshalCourtyardState.Yard yard,int budget){if(!yard.defeated||!loaded(w,yard.centre)||yard.environmentCursor>=64)return;while(budget-->0&&yard.environmentCursor<32){int i=yard.environmentCursor++;double a=i*Math.PI/16;var floor=yard.centre.offset((int)Math.round(Math.cos(a)*13),-1,(int)Math.round(Math.sin(a)*13));if(w.getBlockState(floor).is(Blocks.SANDSTONE)&&w.isEmptyBlock(floor.above())&&w.getBlockEntity(floor)==null){w.setBlock(floor,Blocks.GRASS_BLOCK.defaultBlockState(),3);w.setBlock(floor.above(),(i%2==0?Blocks.POPPY:Blocks.WHITE_TULIP).defaultBlockState(),3);}}if(yard.environmentCursor>=32)yard.environmentCursor=64;MarshalCourtyardState.get(w).setDirty();}
    public static boolean placeMemorial(ServerLevel w,MarshalCourtyardState.Yard yard){
        if(!yard.defeated||yard.memorial!=null||!loaded(w,yard.centre)||yard.victoryAt>=0&&w.getGameTime()>=yard.victoryAt&&w.getGameTime()-yard.victoryAt<240)return false;
        var at=Vec3.atBottomCenterOf(yard.centre);if(!w.noCollision(null,com.dynasty.blueprint.artifact.ArtifactContent.MEMORIAL.get().getDimensions().makeBoundingBox(at)))return false;
        var blade=com.dynasty.blueprint.artifact.ArtifactContent.MEMORIAL.get().create(w);if(blade==null)return false;blade.bind(yard.centre);if(!w.addFreshEntity(blade))return false;yard.memorial=blade.getUUID();MarshalCourtyardState.get(w).setDirty();return true;
    }
    private MarshalCourtyards(){}
}
