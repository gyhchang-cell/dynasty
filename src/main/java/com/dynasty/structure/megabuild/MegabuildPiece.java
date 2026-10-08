package com.dynasty.structure.megabuild;

import com.dynasty.Dynasty;
import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

import java.util.function.Function;

/**
 * 大型建筑通用部件：把 {@link Blueprint} 的 Kind 映射成方块，逐格 {@code placeBlock}
 * （内部按 chunk box 裁剪，不加载周围区块）。种子与朝向序列化进 NBT，重载后形状不变。
 */
class MegabuildPiece extends DynastyStructurePiece {

    static final ResourceLocation CHEST_TABLE =
            new ResourceLocation(Dynasty.MODID, "chests/tiangong_common");

    private final Function<Long, Blueprint> factory;
    private final int size;
    private final int height;
    private long seed;
    private int rot;
    private Blueprint cached;
    private int layoutVersion=4;

    MegabuildPiece(StructurePieceType type, int depth, BlockPos corner,
                   Function<Long, Blueprint> factory, long seed, int rot, int size, int height) {
        super(type, depth, new BoundingBox(corner.getX(),corner.getY(),corner.getZ(),
                corner.getX()+size-1,corner.getY()+height-1,corner.getZ()+size-1));
        this.setOrientation(Direction.SOUTH);
        this.factory = factory;
        this.seed = seed;
        this.rot = rot;
        this.size = size;
        this.height = height;
    }

    MegabuildPiece(StructurePieceType type, CompoundTag tag, Function<Long, Blueprint> factory,
                   int size, int height) {
        super(type, tag);
        this.layoutVersion = tag.contains("MegabuildLayout") ? tag.getInt("MegabuildLayout") : 2;
        this.factory = size==176 && layoutVersion<=3 ?
            (layoutVersion<=2 ? seed -> new LegacyCitadelV2(seed).blueprint() : seed -> new LegacyCitadelV3(seed).blueprint()) : factory;
        this.size = size;
        this.height = height;
        this.seed = tag.getLong("MegabuildSeed");
        this.rot = tag.getInt("MegabuildRot");
    }

    @Override
    protected void addAdditionalSaveData(
            net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
            CompoundTag tag) {
        tag.putLong("MegabuildSeed", seed);
        tag.putInt("MegabuildRot", rot);
        tag.putInt("MegabuildLayout", layoutVersion);
    }

    @Override
    protected void placeBlock(WorldGenLevel level,BlockState state,int x,int y,int z,BoundingBox box){
        // SOUTH keeps additive coordinates but vanilla also mirrors block states.
        // Blueprint already owns rotation: cancel that second transform for v4.
        if(layoutVersion>=4)state=state.mirror(getMirror());
        super.placeBlock(level,state,x,y,z,box);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        Blueprint blueprint = blueprint();
        int x0=Math.max(0,box.minX()-boundingBox.minX()),x1=Math.min(size-1,box.maxX()-boundingBox.minX());
        int z0=Math.max(0,box.minZ()-boundingBox.minZ()),z1=Math.min(size-1,box.maxZ()-boundingBox.minZ());
        for (int x = x0; x <= x1; x++) {
            for (int y = 0; y < height; y++) {
                for (int z = z0; z <= z1; z++) {
                    Blueprint.Kind kind = blueprint.at(x, y, z);
                    if(kind==Blueprint.Kind.SPAWNER_ZOMBIE||kind==Blueprint.Kind.SPAWNER_SKELETON){
                        placeBlock(level,Blocks.SPAWNER.defaultBlockState(),x,y,z,box);
                        var p=world(x,y,z);
                        if(level!=null && level.getBlockEntity(p) instanceof net.minecraft.world.level.block.entity.SpawnerBlockEntity spawner)
                            spawner.load(CityEncounters.spawnerTag(kind));
                        continue;
                    }
                    if (kind == Blueprint.Kind.CHEST || kind == Blueprint.Kind.RICH_CHEST) {
                        createChest(level, box, random, x, y, z, kind==Blueprint.Kind.RICH_CHEST
                            ? new ResourceLocation(Dynasty.MODID,"chests/tiangong_rich") : CHEST_TABLE);
                        continue;
                    }
                    placeBlock(level, blockState(kind), x, y, z, box);
                }
            }
        }
    }

    java.util.List<BlockPos> miningSpiderPositions(){
        return size==MiningEstate.SIZE?rotateMechanical(new int[][]{{17,4,44},{31,4,45}}):java.util.List.of();
    }
    java.util.List<BlockPos> bronzeSnakePositions(){return mechanicalPositions(new int[][]{{35,1,52},{66,1,36}});}
    java.util.List<BlockPos> clockworkPatrols(){return mechanicalPositions(new int[][]{{84,1,20},{91,1,28}});}
    private java.util.List<BlockPos> mechanicalPositions(int[][] authored){
        if(size!=TiangongCitadel.SIZE||layoutVersion<4)return java.util.List.of();
        return rotateMechanical(authored);
    }
    private java.util.List<BlockPos> rotateMechanical(int[][] authored){
        var points=new java.util.ArrayList<BlockPos>();
        for(int[] p:authored){
            int x=p[0],z=p[2];for(int i=0;i<Math.floorMod(rot,4);i++){int old=x;x=size-1-z;z=old;}
            points.add(world(x,p[1],z).immutable());
        }return java.util.List.copyOf(points);
    }
    private synchronized Blueprint blueprint() {
        if(cached==null) cached=factory.apply(seed).rotate(rot);
        return cached;
    }

    static BlockState blockState(Blueprint.Kind kind) {
        return switch (kind) {
            case PLATFORM -> Blocks.DEEPSLATE_BRICKS.defaultBlockState();
            case WALL -> Blocks.STONE_BRICKS.defaultBlockState();
            case FLOOR -> Blocks.SMOOTH_STONE.defaultBlockState();
            case WOOD -> Blocks.OAK_PLANKS.defaultBlockState();
            case DARK_WOOD -> Blocks.DARK_OAK_PLANKS.defaultBlockState();
            case ROOF -> Blocks.DARK_PRISMARINE.defaultBlockState();
            case COPPER -> Blocks.CUT_COPPER.defaultBlockState();
            case LANTERN -> Blocks.LANTERN.defaultBlockState();
            case STAIR_N -> Blocks.OAK_STAIRS.defaultBlockState().setValue(StairBlock.FACING, Direction.NORTH);
            case STAIR_E -> Blocks.OAK_STAIRS.defaultBlockState().setValue(StairBlock.FACING, Direction.EAST);
            case STAIR_S -> Blocks.OAK_STAIRS.defaultBlockState().setValue(StairBlock.FACING, Direction.SOUTH);
            case STAIR_W -> Blocks.OAK_STAIRS.defaultBlockState().setValue(StairBlock.FACING, Direction.WEST);
            case FURNACE -> Blocks.FURNACE.defaultBlockState();
            case BOOKSHELF -> Blocks.BOOKSHELF.defaultBlockState();
            case CROP -> Blocks.OAK_LEAVES.defaultBlockState().setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT,true);
            case ORE_IRON -> Blocks.IRON_ORE.defaultBlockState();
            case ORE_COPPER -> Blocks.COPPER_ORE.defaultBlockState();
            case ORE_COAL -> Blocks.COAL_ORE.defaultBlockState();
            case BARREL -> Blocks.BARREL.defaultBlockState();
            case GATE -> Blocks.IRON_BARS.defaultBlockState();
            case WATER -> Blocks.WATER.defaultBlockState();
            case LOG -> Blocks.OAK_LOG.defaultBlockState();
            case ANVIL -> Blocks.ANVIL.defaultBlockState();
            case CRAFTING -> Blocks.CRAFTING_TABLE.defaultBlockState();
            case BREWING -> Blocks.BREWING_STAND.defaultBlockState();
            case HAY -> Blocks.HAY_BLOCK.defaultBlockState();
            case LIGHT -> Blocks.LIGHT.defaultBlockState().setValue(net.minecraft.world.level.block.LightBlock.LEVEL,15);
            case SPAWNER_ZOMBIE, SPAWNER_SKELETON -> Blocks.SPAWNER.defaultBlockState();
            case TINTED_GLASS -> Blocks.TINTED_GLASS.defaultBlockState();
            case CHISELED -> Blocks.CHISELED_STONE_BRICKS.defaultBlockState();
            case RED_WOOD -> Blocks.STRIPPED_MANGROVE_LOG.defaultBlockState();
            default -> Blocks.AIR.defaultBlockState();
        };
    }
}
