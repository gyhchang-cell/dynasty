package com.dynasty.structure.megabuild;

import com.dynasty.Dynasty;
import com.dynasty.ritual.*;
import com.mojang.serialization.Codec;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.*;
import net.minecraft.core.registries.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.packs.resources.*;
import net.minecraft.util.RandomSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.*;
import java.util.*;

/** Huge original models, generated ONLY within the current chunk by vanilla structure scheduling.
 * Vanilla references search just 8 chunks: one 517-block-wide StructureStart would lose its edges.
 * Each tile therefore has its own durable start, sharing a deterministic rare site and datum.
 * No ChunkEvent scanner, forced loads, placement tick jobs, or repeated whole-model decompression.
 */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class NaturalSculptures {
    public static final DeferredRegister<StructureType<?>> TYPES=DeferredRegister.create(Registries.STRUCTURE_TYPE,Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,Dynasty.MODID);
    public static final DeferredRegister<net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType<?>> PLACEMENTS=DeferredRegister.create(Registries.STRUCTURE_PLACEMENT,Dynasty.MODID);
    public static final RegistryObject<net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType<Placement>> PLACEMENT=PLACEMENTS.register("rare_sculpture_tiles",()->()->Placement.CODEC);
    public static final RegistryObject<StructureType<Tiled>> DRAGON=TYPES.register("longque_sanctuary",()->()->Tiled.DRAGON_CODEC);
    public static final RegistryObject<StructureType<Tiled>> MANOR=TYPES.register("yunqi_manor",()->()->Tiled.MANOR_CODEC);
    public static final RegistryObject<StructurePieceType> TILE=PIECES.register("sculpture_tile",()->(context,tag)->new Tile(tag));
    private record Resource(SculptureBlueprint blueprint,BlockState[] palette){}
    private static volatile Map<String,Resource> resources=Map.of();
    static int cachedCount(){return resources.size();}
    private record TerrainKey(long seed,int x,int z,String id,ChunkGenerator generator){}
    private static final Map<TerrainKey,Integer> datums=Collections.synchronizedMap(new LinkedHashMap<>(){
        @Override protected boolean removeEldestEntry(Map.Entry<TerrainKey,Integer> e){return size()>512;}
    });
    @SubscribeEvent public static void reload(AddReloadListenerEvent event){
        event.addListener(new SimplePreparableReloadListener<Map<String,Resource>>(){
            @Override protected Map<String,Resource> prepare(ResourceManager manager,ProfilerFiller profiler){
                Map<String,Resource> loaded=new HashMap<>();
                for(String id:SculptureBlueprint.IDS)try{
                    var b=SculptureBlueprint.load(manager,id);BlockState[] palette=new BlockState[b.palette.size()];
                    for(int i=0;i<palette.length;i++)palette[i]=BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(),b.palette.get(i),false).blockState();
                    loaded.put(id,new Resource(b,palette));
                }catch(Exception e){throw new IllegalStateException("Invalid natural sculpture "+id,e);}
                return Map.copyOf(loaded);
            }
            @Override protected void apply(Map<String,Resource> loaded,ResourceManager manager,ProfilerFiller profiler){resources=loaded;datums.clear();}
        });
    }
    /** Read-only, local roof preview. Requires a saved structure start and its authored roof still in place. */
    static Map<BlockPos,BlockState> roofPreview(net.minecraft.server.level.ServerPlayer player) {
        ServerLevel level=player.serverLevel();var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        for(String id:SculptureBlueprint.IDS) {
            var structure=registry.get(new net.minecraft.resources.ResourceLocation("dynasty",id));if(structure==null)continue;
            var start=level.structureManager().getStructureAt(player.blockPosition(),structure);if(!start.isValid())continue;
            Tile selected=null;for(var piece:start.getPieces())if(piece instanceof Tile tile){selected=tile;break;}
            if(selected==null)continue;var r=resources.get(selected.id);if(r==null)continue;
            var plan=new LinkedHashMap<BlockPos,BlockState>();var b=r.blueprint;
            for(int x=player.getBlockX()-24;x<=player.getBlockX()+24;x++)for(int z=player.getBlockZ()-24;z<=player.getBlockZ()+24;z++) {
                int lx=x-selected.origin.getX(),lz=z-selected.origin.getZ();if(lx<0||lz<0||lx>=b.width||lz>=b.length)continue;
                int top=b.columnTop(lx,lz);if(top<4)continue;
                BlockPos roof=new BlockPos(x,selected.origin.getY()+top,z);
                if(!level.hasChunkAt(roof)||!level.getBlockState(roof).equals(r.palette[b.at(lx,top,lz)]))continue;
                for(int y=top+1;y<=b.clearTop(lx,lz);y++) {
                    var pos=new BlockPos(x,selected.origin.getY()+y,z);var state=level.getBlockState(pos);
                    if(level.getBlockEntity(pos)==null&&RoofRepair.terrain(state)&&plan.size()<8192)plan.put(pos,state);
                }
            }
            return plan;
        }
        return Map.of();
    }

    public record Site(int x,int z,String id){}
    /** One candidate (either building) per 10,000 x 10,000 blocks, before terrain rejection. */
    public static Site site(long seed,int chunkX,int chunkZ){
        int rx=Math.floorDiv(chunkX,625),rz=Math.floorDiv(chunkZ,625);
        var random=RandomSource.create(seed^((long)rx*341873128712L)^((long)rz*132897987541L)^0x4C4F4E47515545L);
        return new Site((rx*625+40+random.nextInt(545))*16,(rz*625+40+random.nextInt(545))*16,
            random.nextBoolean()?"longque_sanctuary":"yunqi_manor");
    }
    /** RandomSpread subclass preserves vanilla /locate's coarse cell search, but schedules all tiles. */
    public static final class Placement extends net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement {
        static final Codec<Placement> CODEC=Codec.unit(Placement::new);
        Placement(){super(625,80,net.minecraft.world.level.levelgen.structure.placement.RandomSpreadType.LINEAR,1279739205);}
        @Override public ChunkPos getPotentialStructureChunk(long seed,int x,int z){var s=site(seed,x,z);return new ChunkPos(s.x>>4,s.z>>4);}
        @Override protected boolean isPlacementChunk(net.minecraft.world.level.chunk.ChunkGeneratorStructureState state,int x,int z){
            var s=site(state.getLevelSeed(),x,z);var r=resources.get(s.id);if(r==null)return false;
            var b=r.blueprint;int ox=s.x-b.width/2,oz=s.z-b.length/2;
            return x>=Math.floorDiv(ox,16)&&x<=Math.floorDiv(ox+b.width-1,16)&&z>=Math.floorDiv(oz,16)&&z<=Math.floorDiv(oz+b.length-1,16);
        }
        @Override public net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType<?> type(){return PLACEMENT.get();}
    }
    public static final class Tiled extends Structure {
        static final Codec<Tiled> DRAGON_CODEC=simpleCodec(s->new Tiled(s,"longque_sanctuary"));
        static final Codec<Tiled> MANOR_CODEC=simpleCodec(s->new Tiled(s,"yunqi_manor"));
        private final String id;
        Tiled(StructureSettings settings,String id){super(settings);this.id=id;}
        @Override public StructureType<?> type(){return id.equals("yunqi_manor")?MANOR.get():DRAGON.get();}
        @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){
            Site site=site(ctx.seed(),ctx.chunkPos().x,ctx.chunkPos().z);
            if(!id.equals(site.id)||((long)site.x*site.x+(long)site.z*site.z)<2500L*2500)return Optional.empty();
            Resource r=resources.get(id);if(r==null)return Optional.empty();var b=r.blueprint;
            int ox=site.x-b.width/2,oz=site.z-b.length/2;
            int x0=Math.max(ox,ctx.chunkPos().getMinBlockX()),z0=Math.max(oz,ctx.chunkPos().getMinBlockZ());
            int x1=Math.min(ox+b.width-1,ctx.chunkPos().getMaxBlockX()),z1=Math.min(oz+b.length-1,ctx.chunkPos().getMaxBlockZ());
            if(x0>x1||z0>z1)return Optional.empty();
            TerrainKey key=new TerrainKey(ctx.seed(),site.x,site.z,id,ctx.chunkGenerator());
            int datum=datums.computeIfAbsent(key,k->terrain(ctx,site,b));
            if(datum==Integer.MIN_VALUE)return Optional.empty();
            BlockPos origin=new BlockPos(ox,datum-4,oz);
            BoundingBox box=new BoundingBox(x0,origin.getY(),z0,x1,origin.getY()+b.height+4,z1);
            return Optional.of(new GenerationStub(new BlockPos(x0,datum,z0),builder->builder.addPiece(new Tile(id,origin,box))));
        }
        private int terrain(GenerationContext ctx,Site site,SculptureBlueprint b){
            // Reject an entire site, never individual tiles, near candidate surface structures.
            // Checking deterministic candidates avoids loading neighbors or allowing chopped buildings.
            for(var set:ctx.registryAccess().registryOrThrow(Registries.STRUCTURE_SET)){
                // Bundled Dynasty/vanilla surface sets reserve this footprint through
                // exclusion_zone. Only third-party sets need conservative candidate avoidance.
                if(set.structures().stream().allMatch(e->e.structure().unwrapKey().map(k->java.util.Set.of("dynasty","minecraft").contains(k.location().getNamespace())&&!k.location().getPath().equals("pillager_outpost")).orElse(false)))continue;
                if(!(set.placement() instanceof net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement spread)||spread instanceof Placement||spread.spacing()<8)continue;
                if(set.structures().stream().noneMatch(e->e.structure().value().step()==net.minecraft.world.level.levelgen.GenerationStep.Decoration.SURFACE_STRUCTURES
                        && !(e.structure().value() instanceof Tiled)))continue;
                int minX=Math.floorDiv(site.x-b.width/2-96,16),maxX=Math.floorDiv(site.x+b.width/2+96,16);
                int minZ=Math.floorDiv(site.z-b.length/2-96,16),maxZ=Math.floorDiv(site.z+b.length/2+96,16);
                for(int x=Math.floorDiv(minX,spread.spacing());x<=Math.floorDiv(maxX,spread.spacing());x++)
                    for(int z=Math.floorDiv(minZ,spread.spacing());z<=Math.floorDiv(maxZ,spread.spacing());z++){
                        var candidate=spread.getPotentialStructureChunk(ctx.seed(),x*spread.spacing(),z*spread.spacing());
                        if(candidate.x>=minX&&candidate.x<=maxX&&candidate.z>=minZ&&candidate.z<=maxZ){
                            // Vanilla outposts use LEGACY_TYPE_1 at frequency .2, not every grid candidate.
                            boolean outpost=set.structures().stream().anyMatch(e->e.structure().unwrapKey().map(k->k.location().toString().equals("minecraft:pillager_outpost")).orElse(false));
                            if(outpost){var chance=new net.minecraft.world.level.levelgen.WorldgenRandom(new net.minecraft.world.level.levelgen.LegacyRandomSource(0));chance.setSeed((long)((candidate.x>>4)^(candidate.z>>4)<<4)^ctx.seed());chance.nextInt();if(chance.nextInt(5)!=0)continue;}
                            var biome=ctx.biomeSource().getNoiseBiome(candidate.x*4+2,16,candidate.z*4+2,ctx.randomState().sampler());
                            if(set.structures().stream().anyMatch(e->e.structure().value().step()==net.minecraft.world.level.levelgen.GenerationStep.Decoration.SURFACE_STRUCTURES
                                    && e.structure().value().biomes().contains(biome)))return Integer.MIN_VALUE;
                        }
                    }
            }
            // Identical finite terrain samples for every tile; no neighboring chunk is loaded.
            int min=Integer.MAX_VALUE,max=Integer.MIN_VALUE;
            for(int dx:new int[]{-b.width/2,0,b.width/2})for(int dz:new int[]{-b.length/2,0,b.length/2}){
                int y=ctx.chunkGenerator().getFirstFreeHeight(site.x+dx,site.z+dz,Heightmap.Types.OCEAN_FLOOR_WG,ctx.heightAccessor(),ctx.randomState());
                min=Math.min(min,y);max=Math.max(max,y);
            }
            boolean flat=ctx.chunkGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource;
            if(max-min>18||(!flat&&min<ctx.chunkGenerator().getSeaLevel())||max+b.height+5>=ctx.heightAccessor().getMaxBuildHeight())return Integer.MIN_VALUE;
            return max;
        }
    }
    private static final class Tile extends StructurePiece {
        private final String id;private final BlockPos origin;
        Tile(String id,BlockPos origin,BoundingBox box){super(TILE.get(),0,box);this.id=id;this.origin=origin;}
        Tile(CompoundTag tag){super(TILE.get(),tag);id=tag.getString("Sculpture");origin=BlockPos.of(tag.getLong("Origin"));}
        @Override protected void addAdditionalSaveData(StructurePieceSerializationContext context,CompoundTag tag){tag.putString("Sculpture",id);tag.putLong("Origin",origin.asLong());}
        @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos pivot){
            var r=resources.get(id);if(r==null)throw new IllegalStateException("Sculpture cache not loaded");var b=r.blueprint;
            BlockPos.MutableBlockPos p=new BlockPos.MutableBlockPos();
            int x0=Math.max(boundingBox.minX(),clip.minX()),x1=Math.min(boundingBox.maxX(),clip.maxX());
            int z0=Math.max(boundingBox.minZ(),clip.minZ()),z1=Math.min(boundingBox.maxZ(),clip.maxZ());
            for(int x=x0;x<=x1;x++)for(int z=z0;z<=z1;z++){
                // Short foundation ties low terrain to the courtyard/dragon base, never a giant pillar.
                int ground=level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG,x,z);
                for(int y=Math.max(ground,origin.getY()-18);y<origin.getY();y++)level.setBlock(p.set(x,y,z),net.minecraft.world.level.block.Blocks.STONE_BRICKS.defaultBlockState(),2);
                int localX=x-origin.getX(),localZ=z-origin.getZ();
                int clearTop=b.clearTop(localX,localZ);
                for(int y=0;y<=Math.max(b.height-1,clearTop);y++){
                    if(origin.getY()+y<clip.minY()||origin.getY()+y>clip.maxY())continue;
                    int index=y<b.height?b.at(localX,y,localZ):0;
                    if(index==0){
                        // Clear natural terrain only above the model's local base, inside its silhouette.
                        // Do not cut an enormous rectangular air box through the landscape.
                        if(y>=4&&y<=clearTop)
                            level.setBlock(p.set(x,origin.getY()+y,z),net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(),2);
                        continue;
                    }
                    p.set(x,origin.getY()+y,z);level.setBlock(p,r.palette[index],2);
                    if(r.palette[index].is(ZhenyuanRitualContent.NODE.get())){
                        BlockEntity entity=level.getBlockEntity(p);
                        if(entity instanceof ZhenyuanNodeBlockEntity node){
                            var tag=node.saveWithoutMetadata();tag.putLong("NaturalOrigin",origin.asLong());
                            tag.putLong("Core",origin.offset(b.ritualCore[0],b.ritualCore[1],b.ritualCore[2]).asLong());node.load(tag);node.setChanged();
                        }
                    }
                }
            }
        }
    }
    /** Called only on an actual altar interaction, on the server thread. No chunk forcing. */
    public static void bindIfNatural(ServerLevel level,ZhenyuanNodeBlockEntity node){
        BlockPos origin=node.naturalOrigin();if(origin==null||ZhenyuanRitualSavedData.get(level).at(level,node.getCorePos())!=null)return;
        var r=resources.get("longque_sanctuary");if(r==null)return;
        Map<BlockPos,BlockState> owned=new LinkedHashMap<>();Map<Integer,BlockPos> nodes=new LinkedHashMap<>();
        for(var c:r.blueprint.ritualOwned){var p=origin.offset(c.x(),c.y(),c.z());if(!level.hasChunkAt(p))return;owned.put(p,r.palette[r.blueprint.at(c.x(),c.y(),c.z())]);}
        for(var n:r.blueprint.ritualNodes)nodes.put(n.slot(),origin.offset(n.x(),n.y(),n.z()));
        if(ZhenyuanRitualService.bindImportedAltar(level,node.getCorePos(),owned,nodes))ZhenyuanSceneLighting.mouth(level,node.getCorePos(),nodes.values());
    }
    private NaturalSculptures(){}
}
