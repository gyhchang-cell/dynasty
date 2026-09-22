package com.dynasty.puzzle;

import com.dynasty.Dynasty;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * 遗迹机关服务端逻辑：交互校验、三类机关、演示调度、开门、一次性奖励。
 *
 * 安全模型：客户端只说"我右键了这个方块"；服务端自己校验
 *   * 玩家与方块的距离、所在维度；
 *   * 方块身份（必须是控制器/机关部件/线索石板/封印石）；
 *   * 房间归属：在部件周围**有限范围**内找最近的控制器，房间身份 = 控制器坐标；
 *   * 机关类型与布局取自控制器方块状态（不信客户端）。
 * 所有答案、完成状态、奖励都由服务端计算；客户端无法注入坐标或奖励。
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class PuzzleService {

    /** 交互距离 / interaction reach */
    public static final double REACH = 6.0D;
    /** 从部件找控制器的搜索半径（有限范围，不做世界扫描）*/
    public static final int CONTROLLER_RADIUS = 12;
    /** 音效与提示的广播半径（不广播到全服）*/
    public static final double BROADCAST = 12.0D;
    /** 演示每个音符的间隔（tick）*/
    public static final int DEMO_INTERVAL = 16;
    /** 默认奖励战利品表 / reward loot table */
    public static final ResourceLocation REWARD_TABLE = new ResourceLocation(Dynasty.MODID, "puzzles/ruin_reward");

    /** 正在演示的房间：只保留活动演示，不随存档保存（重载后自然回到"等待演示"）*/
    private static final Map<String, Demo> DEMOS = new HashMap<>();

    private PuzzleService() {
    }

    private static final class Demo {
        final net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> dimension;
        final BlockPos controller;
        final int[] sequence;
        int index;
        int delay;

        Demo(net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> dimension,
             BlockPos controller, int[] sequence) {
            this.dimension = dimension;
            this.controller = controller;
            this.sequence = sequence;
            this.delay = DEMO_INTERVAL;
        }
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || DEMOS.isEmpty()) {
            return;
        }
        List<String> finished = new ArrayList<>();
        for (Map.Entry<String, Demo> entry : DEMOS.entrySet()) {
            Demo demo = entry.getValue();
            if (demo.delay-- > 0) {
                continue;
            }
            ServerLevel level = event.getServer().getLevel(demo.dimension);
            if (level == null || demo.index >= demo.sequence.length) {
                finished.add(entry.getKey());
                continue;
            }
            int tone = demo.sequence[demo.index++];
            playTone(level, demo.controller, tone);
            broadcast(level, demo.controller, Component.translatable("dynasty.puzzle.demo.tone",
                    demo.index, demo.sequence.length, toneName(tone)).withStyle(ChatFormatting.AQUA));
            demo.delay = DEMO_INTERVAL;
            if (demo.index >= demo.sequence.length) {
                finished.add(entry.getKey());
            }
        }
        for (String key : finished) {
            Demo demo = DEMOS.remove(key);
            if (demo != null) {
                ServerLevel level = event.getServer().getLevel(demo.dimension);
                if (level != null) {
                    broadcast(level, demo.controller, Component.translatable("dynasty.puzzle.demo.done"));
                }
            }
        }
    }

    // ------------------------------------------------------------------ 交互入口

    /** 右键控制器：查看状态 / 领取奖励 / 潜行右键重置 / 编钟请求演示 */
    public static void onControllerUse(ServerPlayer player, BlockPos pos, BlockState state) {
        if (!(player.level() instanceof ServerLevel level) || !withinReach(player, pos)) {
            return;
        }
        PuzzleRules.Kind kind = PuzzleBlocks.kindOf(state);
        int layout = state.getValue(PuzzleBlocks.VARIANT);
        String roomKey = roomKey(level, pos);
        PuzzleSavedData data = PuzzleSavedData.get(level);
        PuzzleRoomState room = data.state(roomKey, kind, layout);

        if (player.isShiftKeyDown()) {
            if (room.reset()) {
                data.setDirty();
                resetParts(level, pos, kind, layout);
                feedback(player, "dynasty.puzzle.msg.reset");
            } else {
                feedback(player, "dynasty.puzzle.msg.reset_locked");
            }
            return;
        }
        if (room.solved()) {
            if (room.rewardClaimed()) {
                feedback(player, "dynasty.puzzle.msg.already_claimed");
            } else {
                claim(player, level, room, data);
            }
            return;
        }
        if (kind == PuzzleRules.Kind.BELL) {
            if (DEMOS.containsKey(roomKey)) {
                feedback(player, "dynasty.puzzle.msg.demo_running");
                return;
            }
            DEMOS.put(roomKey, new Demo(level.dimension(), pos.immutable(),
                    PuzzleRules.bellSequence(room.layout())));
            feedback(player, "dynasty.puzzle.msg.demo_start");
            return;
        }
        feedback(player, switch (kind) {
            case STAR -> "dynasty.puzzle.msg.star_status";
            case ELEMENTS -> "dynasty.puzzle.msg.lamp_rules";
            case BELL -> "dynasty.puzzle.msg.bell_rules";
        });
    }

    /** 右键机关部件 / 线索石板 */
    public static void onPartUse(ServerPlayer player, BlockPos pos, BlockState state) {
        if (!(player.level() instanceof ServerLevel level) || !withinReach(player, pos)) {
            return;
        }
        if (state.is(PuzzleBlocks.CLUE_TABLET.get())) {
            readClue(player, level, pos);
            return;
        }
        BlockPos controllerPos = findController(level, pos);
        if (controllerPos == null) {
            feedback(player, "dynasty.puzzle.msg.no_controller");
            return;
        }
        BlockState controllerState = level.getBlockState(controllerPos);
        PuzzleRules.Kind kind = PuzzleBlocks.kindOf(controllerState);
        int layout = controllerState.getValue(PuzzleBlocks.VARIANT);
        if (!matchesPart(kind, state)) {
            feedback(player, "dynasty.puzzle.msg.wrong_part");
            return;
        }
        String roomKey = roomKey(level, controllerPos);
        PuzzleSavedData data = PuzzleSavedData.get(level);
        PuzzleRoomState room = data.state(roomKey, kind, layout);
        if (room.solved()) {
            feedback(player, room.rewardClaimed() ? "dynasty.puzzle.msg.already_claimed"
                    : "dynasty.puzzle.msg.solved_claim");
            return;
        }
        List<BlockPos> parts = discoverParts(level, controllerPos, kind);
        int index = parts.indexOf(pos);
        if (index < 0) {
            feedback(player, "dynasty.puzzle.msg.wrong_part");
            return;
        }
        String partKey = offsetKey(pos, controllerPos);
        switch (kind) {
            case STAR -> {
                int next = room.rotateDial(partKey, index);
                level.setBlock(pos, state.setValue(PuzzleBlocks.FACING, facingOf(next)), 3);
                feedback(player, "dynasty.puzzle.msg.star_turn", facingName(next));
                checkSolved(player, level, room, data, controllerPos, kind);
            }
            case ELEMENTS -> {
                int[] ring = ringOrder(controllerPos, parts);
                int position = indexOf(ring, index);
                int neighbourIndex = ring[(position + 1) % ring.length];
                BlockPos neighbour = parts.get(neighbourIndex);
                String neighbourKey = offsetKey(neighbour, controllerPos);
                int self = room.toggleLamp(partKey, index, neighbourKey, neighbourIndex);
                level.setBlock(pos, state.setValue(PuzzleBlocks.LIT, self == 1), 3);
                BlockState neighbourState = level.getBlockState(neighbour);
                if (neighbourState.is(PuzzleBlocks.ELEMENT_LAMP.get())) {
                    level.setBlock(neighbour, neighbourState.setValue(PuzzleBlocks.LIT,
                            room.lampState(neighbourKey, neighbourIndex) == 1), 3);
                }
                feedback(player, "dynasty.puzzle.msg.lamp_toggle", symbolName(index));
                checkSolved(player, level, room, data, controllerPos, kind);
            }
            case BELL -> {
                if (DEMOS.containsKey(roomKey)) {
                    feedback(player, "dynasty.puzzle.msg.demo_running");
                    return;
                }
                room.bellPress(index);
                playTone(level, pos, index);
                broadcast(level, pos, Component.translatable("dynasty.puzzle.msg.bell_press",
                        toneName(index)).withStyle(ChatFormatting.YELLOW));
                if (room.bellInputWrong()) {
                    room.clearBellInput();
                    data.setDirty();
                    feedback(player, "dynasty.puzzle.msg.bell_wrong");
                    return;
                }
                if (!room.bellInputCorrect()) {
                    feedback(player, "dynasty.puzzle.msg.bell_progress",
                            room.bellInput().size(), PuzzleRules.bellSequenceLength(room.layout()));
                    return;
                }
                checkSolved(player, level, room, data, controllerPos, kind);
            }
        }
    }

    /** 完成检查：满足则开自己的门、抽一次奖励并存下来、通知附近玩家 */
    private static void checkSolved(ServerPlayer player, ServerLevel level, PuzzleRoomState room,
                                    PuzzleSavedData data, BlockPos controllerPos, PuzzleRules.Kind kind) {
        if (!room.satisfied()) {
            data.setDirty();
            return;
        }
        room.solve(rollReward(level, controllerPos, room));
        data.setDirty();
        openGates(level, controllerPos);
        broadcast(level, controllerPos, Component.translatable("dynasty.puzzle.msg.solved")
                .withStyle(ChatFormatting.GOLD));
        feedback(player, "dynasty.puzzle.msg.solved_claim");
    }

    // ------------------------------------------------------------------ 奖励（一次性公共奖励）

    /** 抽奖：结果**编码成一行存进房间状态**（背包满重试不会重新抽奖）*/
    private static String rollReward(ServerLevel level, BlockPos controllerPos, PuzzleRoomState room) {
        Random random = new Random(PuzzleRules.roomKey(level.dimension().location().toString(),
                controllerPos.getX(), controllerPos.getY(), controllerPos.getZ()).hashCode() * 31L
                + room.layout());
        LootTable table = level.getServer().getLootData().getLootTable(REWARD_TABLE);
        LootParams params = new LootParams.Builder(level)
                .withParameter(LootContextParams.ORIGIN, Vec3.atCenterOf(controllerPos))
                .create(LootContextParamSets.CHEST);
        return encode(table.getRandomItems(params, random.nextLong()));
    }

    private static String encode(List<ItemStack> stacks) {
        StringBuilder builder = new StringBuilder();
        for (ItemStack stack : stacks) {
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
            if (id == null || stack.isEmpty()) {
                continue;
            }
            if (builder.length() > 0) {
                builder.append(',');
            }
            builder.append(id).append('=').append(stack.getCount());
        }
        return builder.toString();
    }

    private static List<ItemStack> decode(String roll) {
        List<ItemStack> stacks = new ArrayList<>();
        if (roll == null || roll.isEmpty()) {
            return stacks;
        }
        for (String pair : roll.split(",")) {
            String[] parts = pair.split("=");
            if (parts.length != 2) {
                continue;
            }
            Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(parts[0]));
            if (item != null) {
                try {
                    stacks.add(new ItemStack(item, Integer.parseInt(parts[1])));
                } catch (NumberFormatException ignored) {
                    // 坏数字跳过，不影响其它奖励
                }
            }
        }
        return stacks;
    }

    /**
     * 领奖：**公共奖励只发一次**——两名玩家同时点也只会有一个成功
     * （服务端串行 + 状态里只有一次可领）。背包空间不足 → 拒绝并保留可领取状态。
     */
    private static void claim(ServerPlayer player, ServerLevel level, PuzzleRoomState room, PuzzleSavedData data) {
        List<ItemStack> stacks = decode(room.rewardRoll());
        if (stacks.isEmpty()) {
            feedback(player, "dynasty.puzzle.msg.claimed");
            return;
        }
        if (countEmptySlots(player) < stacks.size()) {
            feedback(player, "dynasty.puzzle.msg.no_space");
            return;
        }
        if (!room.claim(player.getUUID().toString())) {
            feedback(player, "dynasty.puzzle.msg.already_claimed");
            return;
        }
        data.setDirty();
        for (ItemStack stack : stacks) {
            player.getInventory().add(stack.copy());
        }
        feedback(player, "dynasty.puzzle.msg.claimed");
        broadcast(level, player.blockPosition(), Component.translatable("dynasty.puzzle.msg.claimed_by",
                player.getDisplayName()).withStyle(ChatFormatting.GREEN));
    }

    private static int countEmptySlots(ServerPlayer player) {
        int free = 0;
        for (int slot = 0; slot < player.getInventory().items.size(); slot++) {
            if (player.getInventory().items.get(slot).isEmpty()) {
                free++;
            }
        }
        return free;
    }

    // ------------------------------------------------------------------ 部件发现 / 开门 / 线索 / 提示

    /** 在控制器有限范围内按 (y,x,z) 排序找出该类型的所有部件（同房间下标稳定）*/
    public static List<BlockPos> discoverParts(ServerLevel level, BlockPos controllerPos, PuzzleRules.Kind kind) {
        Block part = PuzzleBlocks.partFor(kind);
        List<BlockPos> found = new ArrayList<>();
        for (BlockPos pos : BlockPos.betweenClosed(
                controllerPos.offset(-CONTROLLER_RADIUS, -8, -CONTROLLER_RADIUS),
                controllerPos.offset(CONTROLLER_RADIUS, 8, CONTROLLER_RADIUS))) {
            if (level.getBlockState(pos).is(part)) {
                found.add(pos.immutable());
            }
        }
        found.sort(Comparator.<BlockPos>comparingInt(BlockPos::getY)
                .thenComparingInt(BlockPos::getX).thenComparingInt(BlockPos::getZ));
        return found;
    }

    /** 从部件找最近的控制器（有限范围；不依赖客户端提供的房间身份）*/
    public static BlockPos findController(ServerLevel level, BlockPos partPos) {
        BlockPos best = null;
        double bestDistance = Double.MAX_VALUE;
        for (BlockPos pos : BlockPos.betweenClosed(
                partPos.offset(-CONTROLLER_RADIUS, -8, -CONTROLLER_RADIUS),
                partPos.offset(CONTROLLER_RADIUS, 8, CONTROLLER_RADIUS))) {
            if (!level.getBlockState(pos).is(PuzzleBlocks.RUIN_CONTROLLER.get())) {
                continue;
            }
            double distance = pos.distSqr(partPos);
            if (distance < bestDistance) {
                bestDistance = distance;
                best = pos.immutable();
            }
        }
        return best;
    }

    /** 开门：只移除**这个房间范围内**的封印石，不动其它方块 */
    private static void openGates(ServerLevel level, BlockPos controllerPos) {
        for (BlockPos pos : BlockPos.betweenClosed(
                controllerPos.offset(-CONTROLLER_RADIUS, -8, -CONTROLLER_RADIUS),
                controllerPos.offset(CONTROLLER_RADIUS, 8, CONTROLLER_RADIUS))) {
            if (level.getBlockState(pos).is(PuzzleBlocks.RUIN_GATE.get())) {
                level.removeBlock(pos.immutable(), false);
            }
        }
    }

    /** 重置：把未解开的星盘/灯阵恢复成初始布局的方块状态 */
    private static void resetParts(ServerLevel level, BlockPos controllerPos, PuzzleRules.Kind kind, int layout) {
        if (kind == PuzzleRules.Kind.STAR) {
            List<BlockPos> parts = discoverParts(level, controllerPos, kind);
            for (int i = 0; i < parts.size(); i++) {
                BlockState state = level.getBlockState(parts.get(i));
                if (state.is(PuzzleBlocks.STAR_DIAL.get())) {
                    level.setBlock(parts.get(i), state.setValue(PuzzleBlocks.FACING,
                            facingOf(PuzzleRules.starInitial(layout)[Math.floorMod(i, 4)])), 3);
                }
            }
        } else if (kind == PuzzleRules.Kind.ELEMENTS) {
            List<BlockPos> parts = discoverParts(level, controllerPos, kind);
            for (int i = 0; i < parts.size(); i++) {
                BlockState state = level.getBlockState(parts.get(i));
                if (state.is(PuzzleBlocks.ELEMENT_LAMP.get())) {
                    level.setBlock(parts.get(i), state.setValue(PuzzleBlocks.LIT,
                            PuzzleRules.lampInitial(layout)[Math.floorMod(i, 4)] == 1), 3);
                }
            }
        }
    }

    // ------------------------------------------------------------------ 小工具

    private static boolean matchesPart(PuzzleRules.Kind kind, BlockState state) {
        return switch (kind) {
            case STAR -> state.is(PuzzleBlocks.STAR_DIAL.get());
            case BELL -> state.is(PuzzleBlocks.ECHO_BELL.get());
            case ELEMENTS -> state.is(PuzzleBlocks.ELEMENT_LAMP.get());
        };
    }

    private static String roomKey(ServerLevel level, BlockPos pos) {
        return PuzzleRules.roomKey(level.dimension().location().toString(),
                pos.getX(), pos.getY(), pos.getZ());
    }

    /** 部件相对控制器的偏移（可验证的相对坐标，落盘用）*/
    private static String offsetKey(BlockPos part, BlockPos controller) {
        return (part.getX() - controller.getX()) + "," + (part.getY() - controller.getY())
                + "," + (part.getZ() - controller.getZ());
    }

    /** 四象灯的顺时针环序（用部件的相对坐标算，纯几何，不依赖排序下标）*/
    private static int[] ringOrder(BlockPos controllerPos, List<BlockPos> parts) {
        int[] dx = new int[parts.size()];
        int[] dz = new int[parts.size()];
        for (int i = 0; i < parts.size(); i++) {
            dx[i] = parts.get(i).getX() - controllerPos.getX();
            dz[i] = parts.get(i).getZ() - controllerPos.getZ();
        }
        return PuzzleRules.ringOrder(dx, dz);
    }

    private static int indexOf(int[] values, int target) {
        for (int i = 0; i < values.length; i++) {
            if (values[i] == target) {
                return i;
            }
        }
        return 0;
    }

    private static Direction facingOf(int orientation) {
        return switch (PuzzleRules.wrap(orientation)) {
            case 0 -> Direction.NORTH;
            case 1 -> Direction.EAST;
            case 2 -> Direction.SOUTH;
            default -> Direction.WEST;
        };
    }

    private static String facingName(int orientation) {
        return "dynasty.puzzle.facing." + PuzzleRules.FACING_KEYS[PuzzleRules.wrap(orientation)];
    }

    private static String symbolName(int index) {
        return "dynasty.puzzle.symbol." + PuzzleRules.SYMBOL_KEYS[Math.floorMod(index, 4)];
    }

    private static String toneName(int index) {
        return "dynasty.puzzle.tone." + PuzzleRules.TONE_KEYS[Math.floorMod(index, 5)];
    }

    private static void playTone(ServerLevel level, BlockPos pos, int tone) {
        level.playSound(null, pos, SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.BLOCKS,
                1.0F, PuzzleRules.TONE_PITCH[Math.floorMod(tone, 5)]);
    }

    /** 只发给附近玩家（不广播到整个服务器）*/
    private static void broadcast(ServerLevel level, BlockPos pos, Component message) {
        for (ServerPlayer nearby : level.getEntitiesOfClass(ServerPlayer.class,
                new net.minecraft.world.phys.AABB(pos).inflate(BROADCAST))) {
            nearby.displayClientMessage(message, true);
        }
    }

    private static void feedback(ServerPlayer player, String key, Object... args) {
        player.displayClientMessage(Component.translatable(key, args).withStyle(ChatFormatting.YELLOW), true);
    }

    private static boolean withinReach(ServerPlayer player, BlockPos pos) {
        return player.position().distanceToSqr(Vec3.atCenterOf(pos)) <= REACH * REACH;
    }

    /** 读线索：可以反复读；星盘逐盘给出目标朝向，其它类型给出规则。 */
    private static void readClue(ServerPlayer player, ServerLevel level, BlockPos pos) {
        BlockPos controllerPos = findController(level, pos);
        if (controllerPos == null) {
            feedback(player, "dynasty.puzzle.msg.no_controller");
            return;
        }
        BlockState state = level.getBlockState(controllerPos);
        PuzzleRules.Kind kind = PuzzleBlocks.kindOf(state);
        int layout = state.getValue(PuzzleBlocks.VARIANT);
        if (kind == PuzzleRules.Kind.STAR) {
            List<BlockPos> dials = discoverParts(level, controllerPos, kind);
            int index = dials.indexOf(pos);
            int dialIndex = index >= 0 ? index % 4 : Math.floorMod(pos.getX() + pos.getZ(), 4);
            player.displayClientMessage(Component.translatable("dynasty.puzzle.clue.star",
                    dialIndex + 1, Component.translatable(facingName(PuzzleRules.starTarget(layout, dialIndex)))),
                    false);
            return;
        }
        player.displayClientMessage(Component.translatable(kind == PuzzleRules.Kind.BELL
                ? "dynasty.puzzle.clue.bell" : "dynasty.puzzle.clue.lamp"), false);
    }
}
