package com.dynasty.puzzle;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * 机关方块（集中在一个文件，公共注册文件只加一行）。
 * RUIN_CONTROLLER 控制器 · STAR_DIAL 星盘 · ECHO_BELL 编钟 ·
 * ELEMENT_LAMP 四象灯 · CLUE_TABLET 线索石板 · RUIN_GATE 封印石。
 * 控制器不提供物品（只能管理员命令放置），避免批量制造"可领奖的遗迹"。
 */
public final class PuzzleBlocks {

    private PuzzleBlocks() {
    }

    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    /** 机关类型用整数属性（0/1/2），避免让纯逻辑类依赖 Minecraft 的 StringRepresentable */
    public static final IntegerProperty KIND = IntegerProperty.create("kind", 0, 2);
    public static final IntegerProperty VARIANT = IntegerProperty.create("variant", 0, 2);
    public static final IntegerProperty SYMBOL = IntegerProperty.create("symbol", 0, 3);

    /** 方块状态 → 机关类型 / blockstate to kind */
    public static PuzzleRules.Kind kindOf(BlockState state) {
        return PuzzleRules.Kind.values()[Math.floorMod(state.getValue(KIND), PuzzleRules.Kind.values().length)];
    }
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final BooleanProperty LIT = BlockStateProperties.LIT;

    private static BlockBehaviour.Properties stone(float hardness) {
        return BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(hardness).sound(SoundType.STONE);
    }

    private static RegistryObject<Block> itemBlock(String name, RegistryObject<Block> block) {
        ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
        return block;
    }

    public static final RegistryObject<Block> RUIN_CONTROLLER = BLOCKS.register("ruin_controller",
            () -> new Controller(stone(3.5F).lightLevel(state -> 7)));
    // The existing star_dial ITEM is a Curios accessory; never replace its registration.
    public static final RegistryObject<Block> STAR_DIAL = itemBlock("puzzle_star_dial",
            BLOCKS.register("star_dial", () -> new DialPart(stone(2.5F))));
    public static final RegistryObject<Block> ECHO_BELL = itemBlock("echo_bell",
            BLOCKS.register("echo_bell", () -> new Part(
                    stone(2.5F).mapColor(MapColor.GOLD).sound(SoundType.METAL), false, false)));
    public static final RegistryObject<Block> ELEMENT_LAMP = itemBlock("element_lamp",
            BLOCKS.register("element_lamp", () -> new LampPart(stone(2.5F))));
    public static final RegistryObject<Block> CLUE_TABLET = itemBlock("clue_tablet",
            BLOCKS.register("clue_tablet", () -> new Part(stone(2.0F), false, false)));
    public static final RegistryObject<Block> RUIN_GATE = itemBlock("ruin_gate",
            BLOCKS.register("ruin_gate", () -> new Gate(stone(3.0F))));

    public static Block partFor(PuzzleRules.Kind kind) {
        return switch (kind) {
            case STAR -> STAR_DIAL.get();
            case BELL -> ECHO_BELL.get();
            case ELEMENTS -> ELEMENT_LAMP.get();
        };
    }

    /** 控制器：记录机关类型与布局，交互交给 PuzzleService */
    public static class Controller extends Block {

        public Controller(Properties props) {
            super(props);
            registerDefaultState(stateDefinition.any().setValue(KIND, 0).setValue(VARIANT, 0));
        }

        @Override
        protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
            builder.add(KIND, VARIANT);
        }

        @SuppressWarnings("null")
        @Override
        public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                     InteractionHand hand, BlockHitResult hit) {
            if (!level.isClientSide && player instanceof net.minecraft.server.level.ServerPlayer server) {
                PuzzleService.onControllerUse(server, pos, state);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
    }

    /** 机关部件（星盘 / 编钟 / 四象灯 / 线索石板）*/
    public static class Part extends Block {

        private final boolean dial;
        private final boolean lamp;

        public Part(Properties props, boolean dial, boolean lamp) {
            super(props);
            this.dial = dial;
            this.lamp = lamp;
            BlockState defaultState = stateDefinition.any();
            if (dial) {
                defaultState = defaultState.setValue(FACING, Direction.NORTH);
            }
            if (lamp) {
                defaultState = defaultState.setValue(LIT, false).setValue(SYMBOL, 0);
            }
            registerDefaultState(defaultState);
        }

        @Override
        protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
            // Called by Block's constructor, before Part's instance flags are assigned.
            // Specialized subclasses declare their properties without reading instance fields.
        }

        @SuppressWarnings("null")
        @Override
        public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                     InteractionHand hand, BlockHitResult hit) {
            if (!level.isClientSide && player instanceof net.minecraft.server.level.ServerPlayer server) {
                PuzzleService.onPartUse(server, pos, state);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
    }

    private static final class DialPart extends Part {
        DialPart(Properties properties) { super(properties, true, false); }
        @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
            builder.add(FACING);
        }
    }

    private static final class LampPart extends Part {
        LampPart(Properties properties) { super(properties, false, true); }
        @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
            builder.add(LIT, SYMBOL);
        }
    }

    /** 封印石：解开后由控制器移除 */
    public static class Gate extends Block {

        public Gate(Properties props) {
            super(props);
        }
    }
}
