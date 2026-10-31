package artifacts.world;

import artifacts.Artifacts;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.RandomizableContainer;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.BarrelBlock;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FurnaceBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class CampsiteFeature extends AbstractCampsiteFeature<CampsiteFeatureConfiguration> {

    public static final ResourceKey<LootTable> BARREL_LOOT = Artifacts.key(Registries.LOOT_TABLE, "chests/campsite_barrel");

    public CampsiteFeature() {
        super(CampsiteFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<CampsiteFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        CampsiteFeatureConfiguration config = context.config();

        BlockPos.betweenClosedStream(origin.offset(-2, 0, -2), origin.offset(2, 2, 2))
                .filter(pos -> Math.abs(pos.getX() - origin.getX()) < 2 ||  Math.abs(pos.getZ() - origin.getZ()) < 2)
                .filter(pos -> !level.getBlockState(pos).isAir())
                .forEach(pos -> setBlock(level, pos, Blocks.CAVE_AIR.defaultBlockState()));

        placeFloor(config, level, origin, random);
        placeCampfire(config, level, origin, random);

        Direction direction = Direction.Plane.HORIZONTAL.getRandomDirection(random);
        BlockPos pos = origin.relative(direction, 2);

        if (random.nextInt(3) == 0) {
            BlockPos.betweenClosedStream(
                    pos.relative(direction.getClockWise()),
                    pos.relative(direction.getCounterClockWise())
            ).forEach(barrelPos -> {
                placeBarrel(level, barrelPos, random);
                if (random.nextInt(3) == 0) {
                    placeBarrel(level, barrelPos.above(), random);
                }
            });
        } else {
            Direction bedDirection = random.nextBoolean() ? direction.getClockWise() : direction.getCounterClockWise();
            BlockState bedBlock = config.beds().getState(level, random, pos).setValue(BedBlock.FACING, bedDirection);
            setBlock(level, pos, bedBlock.setValue(BedBlock.PART, BedPart.HEAD));
            setBlock(level, pos.relative(bedDirection.getOpposite()), bedBlock.setValue(BedBlock.PART, BedPart.FOOT));
            placeBarrel(level, pos.relative(bedDirection), random);
            placeLightSource(config, level, pos.relative(bedDirection).above(), random);
        }

        direction = random.nextBoolean() ? direction.getClockWise() : direction.getCounterClockWise();
        pos = origin.relative(direction, 2);

        List<BlockPos> positions = BlockPos.betweenClosedStream(
                pos.relative(direction.getClockWise()),
                pos.relative(direction.getCounterClockWise())
        ).map(BlockPos::immutable).collect(Collectors.toCollection(ArrayList::new));

        Collections.shuffle(positions);

        placeCraftingStation(config, level, positions.removeFirst(), random, direction.getOpposite());
        placeFurnace(config, level, positions.removeFirst(), random, direction.getOpposite());
        placeChest(level, positions.removeFirst(), random, direction.getOpposite(), config.chestConfig());

        return true;
    }

    private void placeFloor(CampsiteFeatureConfiguration config, WorldGenLevel level, BlockPos origin, RandomSource random) {
        BlockPos.betweenClosedStream(origin.offset(-2, -1, -2), origin.offset(2, -1, 2))
                .filter(pos -> Math.abs(pos.getX() - origin.getX()) < 2 ||  Math.abs(pos.getZ() - origin.getZ()) < 2)
                .forEach(pos -> {
                    if (!level.getBlockState(pos).isFaceSturdy(level, pos, Direction.UP)) {
                        setBlock(level, pos, config.floor().getState(level, random, pos));
                    } else if (random.nextBoolean()) {
                        if (level.getBlockState(pos).is(Blocks.DEEPSLATE)) {
                            setBlock(level, pos, Blocks.COBBLED_DEEPSLATE.defaultBlockState());
                        } else if (level.getBlockState(pos).is(Blocks.STONE)) {
                            setBlock(level, pos, Blocks.COBBLESTONE.defaultBlockState());
                        }
                    }
                });
    }

    private void placeCampfire(CampsiteFeatureConfiguration config, WorldGenLevel level, BlockPos origin, RandomSource random) {
        BlockState campfire = config.unlitCampfires().getState(level, random, origin);
        if (Artifacts.CONFIG.general.campsite.allowLightSources.get() && random.nextFloat() < 0.10) {
            campfire = config.litCampfires().getState(level, random, origin);
        }
        setBlock(level, origin, campfire);
    }

    private void placeLightSource(CampsiteFeatureConfiguration config, WorldGenLevel level, BlockPos pos, RandomSource random) {
        if (random.nextFloat() < 0.5) {
            BlockState lightSource = config.unlitLightSources().getState(level, random, pos);
            if (Artifacts.CONFIG.general.campsite.allowLightSources.get() && random.nextFloat() < 0.30) {
                lightSource = config.lightSources().getState(level, random, pos);
            }
            setBlock(level, pos, lightSource);
        }
    }

    private void placeCraftingStation(CampsiteFeatureConfiguration config, WorldGenLevel level, BlockPos pos, RandomSource random, Direction facing) {
        BlockState craftingStation = config.craftingStations().getState(level, random, pos);
        if (craftingStation.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
            craftingStation = craftingStation.setValue(BlockStateProperties.HORIZONTAL_FACING, facing);
        }
        setBlock(level, pos, craftingStation);
        if (random.nextInt(3) == 0) {
            setBlock(level, pos.above(), config.decorations().getState(level, random, pos));
        }
    }

    private void placeFurnace(CampsiteFeatureConfiguration config, WorldGenLevel level, BlockPos pos, RandomSource random, Direction facing) {
        BlockState furnace = config.furnaces().getState(level, random, pos);
        furnace = furnace.setValue(FurnaceBlock.FACING, facing);
        setBlock(level, pos, furnace);
        if (random.nextBoolean()) {
            setBlock(level, pos.above(), config.furnaceChimneys().getState(level, random, pos));
        }
    }

    private void placeBarrel(WorldGenLevel level, BlockPos pos, RandomSource random) {
        BlockState barrel = Blocks.BARREL.defaultBlockState();
        if (random.nextBoolean()) {
            barrel = barrel.setValue(BarrelBlock.FACING, Direction.UP);
        } else {
            barrel = barrel.setValue(BarrelBlock.FACING, Direction.Plane.HORIZONTAL.getRandomDirection(random));
        }
        setBlock(level, pos, barrel);
        RandomizableContainer.setBlockEntityLootTable(level, random, pos, BARREL_LOOT);
    }
}
