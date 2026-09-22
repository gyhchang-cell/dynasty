package com.dynasty.bounty;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 服务端权威的委托服务：打开会话、每日发布、接取/放弃/提交/领奖、击杀与考察进度。
 *
 * 安全模型（客户端只说意图）：
 *   * 只有**右键告示板**才会建立会话，会话记录方块坐标 + 维度 + 到期时间；
 *   * 每次操作都重新校验：会话有效、方块还在、玩家在交互距离内、实例与状态合法；
 *   * 数量、进度、奖励一律服务端计算，客户端发来的数量/奖励**从不采信**；
 *   * 提交「先算后扣」、领奖「先查背包空间再发放」，重复包/重复点击只会得到「已完成/已领取」。
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class BountyService {

    public static final int SESSION_TICKS = 20 * 60;
    public static final double REACH = 6.0D;
    /** 考察检查间隔（tick）：低频玩家检查，不每 tick 扫世界 */
    public static final int EXPLORE_CHECK_TICKS = 40;

    private static final Map<UUID, Session> SESSIONS = new HashMap<>();

    private record Session(ResourceLocation dimension, BlockPos pos, long expiresAt) {
    }

    private BountyService() {
    }

    // ------------------------------------------------------------------ 事件钩子

    @SubscribeEvent
    public static void onAddReloadListener(AddReloadListenerEvent event) {
        event.addListener(new BountyOffers());
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        MinecraftServer server = event.getServer();
        if (server.getTickCount() % EXPLORE_CHECK_TICKS != 0) {
            return;
        }
        for (ServerPlayer player : server.getPlayerList().getPlayers()) {
            checkExplore(player);
        }
    }

    /**
     * 击杀归属：只认「玩家本人」或「可追溯到该玩家的投射物」。
     * 环境死亡、其他玩家、来源不明、以及**宠物 / 驯服生物**的击杀都不计入（说明与实现一致）。
     */
    @SubscribeEvent
    public static void onLivingDeath(LivingDeathEvent event) {
        if (!(event.getEntity().level() instanceof ServerLevel level)) {
            return;
        }
        ServerPlayer player = creditPlayer(event);
        if (player == null) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(event.getEntity().getType());
        if (id == null) {
            return;
        }
        BountyStateMachine state = stateFor(player);
        if (state.addHuntProgress(id.toString(), 1) > 0) {
            BountyBoardData.get(level).setDirty();
            sendBoard(player, "dynasty.bounty.msg.progress");
        }
    }

    /** 解析击杀归属；null 表示「不算玩家击杀」。 */
    private static ServerPlayer creditPlayer(LivingDeathEvent event) {
        if (event.getEntity().getKillCredit() instanceof ServerPlayer killer) {
            return killer;
        }
        if (event.getSource().getEntity() instanceof ServerPlayer shooter) {
            return shooter;
        }
        if (event.getSource().getEntity() instanceof net.minecraft.world.entity.projectile.Projectile projectile
                && projectile.getOwner() instanceof ServerPlayer owner) {
            return owner;
        }
        return null;
    }

    // ------------------------------------------------------------------ 会话

    public static void openSession(ServerPlayer player, BlockPos pos) {
        if (!(player.level() instanceof ServerLevel level)) {
            return;
        }
        if (!(level.getBlockState(pos).getBlock() instanceof BountyBoardBlock)) {
            return;
        }
        SESSIONS.put(player.getUUID(), new Session(level.dimension().location(), pos.immutable(),
                level.getGameTime() + SESSION_TICKS));
        sendBoard(player, null);
    }

    public static void closeSession(ServerPlayer player) {
        SESSIONS.remove(player.getUUID());
    }

    /** 每次操作前重新校验：会话有效 + 方块还在 + 距离够。 */
    private static boolean sessionValid(ServerPlayer player) {
        Session session = SESSIONS.get(player.getUUID());
        if (session == null || !(player.level() instanceof ServerLevel level)) {
            return false;
        }
        if (level.getGameTime() > session.expiresAt()) {
            SESSIONS.remove(player.getUUID());
            return false;
        }
        if (!level.dimension().location().equals(session.dimension())) {
            return false;
        }
        if (!(level.getBlockState(session.pos()).getBlock() instanceof BountyBoardBlock)) {
            return false;
        }
        return player.position().distanceToSqr(Vec3.atCenterOf(session.pos())) <= REACH * REACH;
    }

    // ------------------------------------------------------------------ 发布

    public static BountyStateMachine stateFor(ServerPlayer player) {
        ServerLevel overworld = player.server.overworld();
        BountyBoardData data = BountyBoardData.get(overworld);
        BountyStateMachine state = data.stateOf(player.getUUID());
        long effectiveDay = state.effectiveDay(BountyRules.dayOf(overworld.getDayTime()));
        if (state.needsPublication(effectiveDay)) {
            state.publish(effectiveDay, publishFor(effectiveDay));
            data.setDirty();
        }
        return state;
    }

    /** 某一天的发布列表：同一世界同一天完全一致，重启后也一致。 */
    public static List<BountyModel.Instance> publishFor(long day) {
        List<BountyModel.Offer> picked = BountyRules.pickDaily(BountyOffers.all(), BountyRules.DAILY_PUBLISH, day);
        List<BountyModel.Instance> instances = new ArrayList<>();
        for (int slot = 0; slot < picked.size(); slot++) {
            BountyModel.Offer offer = picked.get(slot);
            instances.add(new BountyModel.Instance(day, slot, offer, offer.reward));
        }
        return instances;
    }

    // ------------------------------------------------------------------ 行动入口（全部服务端校验）

    public static void handleAction(ServerPlayer player, String action, String instanceId) {
        if (!sessionValid(player)) {
            player.sendSystemMessage(net.minecraft.network.chat.Component.translatable(
                    "dynasty.bounty.msg.no_session"));
            return;
        }
        BountyStateMachine state = stateFor(player);
        String status;
        switch (action) {
            case "ACCEPT" -> status = doAccept(player, state, instanceId);
            case "ABANDON" -> status = doAbandon(state, instanceId);
            case "SUBMIT" -> status = doSubmit(player, state, instanceId);
            case "CLAIM" -> status = doClaim(player, state, instanceId);
            default -> status = "dynasty.bounty.msg.bad_action";
        }
        BountyBoardData.get(player.server.overworld()).setDirty();
        sendBoard(player, status);
    }

    private static String doAccept(ServerPlayer player, BountyStateMachine state, String instanceId) {
        BountyModel.Instance instance = state.publishedById(instanceId);
        if (instance == null) {
            return "dynasty.bounty.msg.not_published";
        }
        String locked = prerequisiteMissing(player, instance);
        if (locked != null) {
            return locked;
        }
        return switch (state.accept(instance)) {
            case OK -> "dynasty.bounty.msg.accepted";
            case FULL -> "dynasty.bounty.msg.full";
            case ALREADY_ACCEPTED -> "dynasty.bounty.msg.already_accepted";
            case ALREADY_CLAIMED -> "dynasty.bounty.msg.already_claimed";
            case NOT_PUBLISHED -> "dynasty.bounty.msg.not_published";
        };
    }

    private static String doAbandon(BountyStateMachine state, String instanceId) {
        return state.abandon(instanceId) ? "dynasty.bounty.msg.abandoned" : "dynasty.bounty.msg.not_accepted";
    }

    private static String doSubmit(ServerPlayer player, BountyStateMachine state, String instanceId) {
        BountyStateMachine.Accepted record = state.acceptedById(instanceId);
        if (record == null) {
            return "dynasty.bounty.msg.not_accepted";
        }
        if (record.instance.type != BountyModel.Type.ACQUIRE) {
            return "dynasty.bounty.msg.wrong_type";
        }
        // 进度以「当前主背包 + 快捷栏」里可提交的数量为准（曾经拿过不算）
        int available = countInMainInventory(player, record.instance.target);
        BountyStateMachine.Submit result = state.submit(instanceId, available);
        if (result != BountyStateMachine.Submit.OK) {
            return switch (result) {
                case INSUFFICIENT -> "dynasty.bounty.msg.insufficient";
                case ALREADY_DONE -> "dynasty.bounty.msg.already_done";
                case ALREADY_CLAIMED -> "dynasty.bounty.msg.already_claimed";
                case WRONG_TYPE -> "dynasty.bounty.msg.wrong_type";
                default -> "dynasty.bounty.msg.not_accepted";
            };
        }
        int consumed = state.consumedOnSubmit(instanceId);
        int leftover = consumeFromMainInventory(player, record.instance.target, consumed);
        if (leftover > 0) {
            // 理论上不会发生（刚数过），真发生就回滚状态，绝不让玩家白交
            record.submitted = false;
            record.done = false;
            record.progress = 0;
            return "dynasty.bounty.msg.submit_failed";
        }
        return "dynasty.bounty.msg.submitted";
    }

    private static String doClaim(ServerPlayer player, BountyStateMachine state, String instanceId) {
        BountyStateMachine.Accepted record = state.acceptedById(instanceId);
        if (record == null) {
            return "dynasty.bounty.msg.not_accepted";
        }
        if (!record.done) {
            return "dynasty.bounty.msg.not_done";
        }
        BountyModel.Reward reward = record.instance.reward;
        int neededSlots = reward.allItems().size();
        if (!BountyRules.rewardFits(freeSlots(player), neededSlots)) {
            return "dynasty.bounty.msg.no_space";
        }
        BountyStateMachine.Claim result = state.claim(instanceId, true);
        if (result != BountyStateMachine.Claim.OK) {
            return switch (result) {
                case ALREADY_CLAIMED -> "dynasty.bounty.msg.already_claimed";
                case NOT_DONE -> "dynasty.bounty.msg.not_done";
                default -> "dynasty.bounty.msg.not_accepted";
            };
        }
        for (BountyModel.Stack stack : reward.allItems()) {
            net.minecraft.world.item.Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(stack.item));
            if (item != null) {
                player.getInventory().add(new net.minecraft.world.item.ItemStack(item, stack.count));
            }
        }
        if (reward.experience > 0) {
            player.giveExperiencePoints(reward.experience);
        }
        return "dynasty.bounty.msg.claimed";
    }

    /** 前置条件（例如「已进入某维度」的成就）；不满足时返回提示键。 */
    private static String prerequisiteMissing(ServerPlayer player, BountyModel.Instance instance) {
        String prerequisite = instance.offer.prerequisite;
        if (prerequisite == null || prerequisite.isBlank()) {
            return null;
        }
        var advancement = player.server.getAdvancements()
                .getAdvancement(new ResourceLocation(prerequisite));
        if (advancement == null) {
            return null;                       // 条件本身不存在 → 不当作锁定，避免卡住玩家
        }
        boolean done = player.getAdvancements().getOrStartProgress(advancement).isDone();
        return done ? null : "dynasty.bounty.msg.locked";
    }

    // ------------------------------------------------------------------ 主背包（不含盔甲/副手/饰品/外部容器）

    /**
     * 只数**主背包 + 快捷栏**（`Inventory.items` 的 36 格）；盔甲、副手、Curios 饰品、外部容器都不动。
     */
    public static int countInMainInventory(ServerPlayer player, String target) {
        int total = 0;
        for (int slot = 0; slot < player.getInventory().items.size(); slot++) {
            net.minecraft.world.item.ItemStack stack = player.getInventory().items.get(slot);
            if (matches(stack, target)) {
                total += stack.getCount();
            }
        }
        return total;
    }

    /** 从主背包消耗指定数量；返回**没有消耗掉的数量**（0 = 全部消耗成功）。 */
    public static int consumeFromMainInventory(ServerPlayer player, String target, int amount) {
        int remaining = amount;
        for (int slot = 0; slot < player.getInventory().items.size() && remaining > 0; slot++) {
            net.minecraft.world.item.ItemStack stack = player.getInventory().items.get(slot);
            if (!matches(stack, target)) {
                continue;
            }
            int take = Math.min(remaining, stack.getCount());
            stack.shrink(take);
            remaining -= take;
            if (stack.isEmpty()) {
                player.getInventory().items.set(slot, net.minecraft.world.item.ItemStack.EMPTY);
            }
        }
        player.getInventory().setChanged();
        return remaining;
    }

    /** 目标匹配：支持具体物品 ID 与 `#命名空间:标签`。 */
    public static boolean matches(net.minecraft.world.item.ItemStack stack, String target) {
        if (stack.isEmpty() || target == null) {
            return false;
        }
        if (target.startsWith("#")) {
            net.minecraft.tags.TagKey<net.minecraft.world.item.Item> tag = net.minecraft.tags.TagKey.create(
                    net.minecraft.core.registries.Registries.ITEM, new ResourceLocation(target.substring(1)));
            return stack.is(tag);
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        return id != null && id.toString().equals(target);
    }

    private static int freeSlots(ServerPlayer player) {
        int free = 0;
        for (int slot = 0; slot < player.getInventory().items.size(); slot++) {
            if (player.getInventory().items.get(slot).isEmpty()) {
                free++;
            }
        }
        return free;
    }

    // ------------------------------------------------------------------ 考察检查（低频）

    /** 只遍历在线玩家，且只处理有考察委托的玩家；不扫世界。 */
    public static void checkExplore(ServerPlayer player) {
        BountyStateMachine state = stateFor(player);
        if (state.accepted().isEmpty()) {
            return;
        }
        String dimension = player.level().dimension().location().toString();
        if (state.markExplore(dimension) > 0) {
            BountyBoardData.get(player.server.overworld()).setDirty();
            sendBoard(player, "dynasty.bounty.msg.explore_done");
        }
    }

    // ------------------------------------------------------------------ 界面数据

    public static void sendBoard(ServerPlayer player, String statusKey) {
        BountyStateMachine state = stateFor(player);
        List<BountyView.Entry> entries = new ArrayList<>();
        for (BountyModel.Instance instance : state.published()) {
            BountyStateMachine.Accepted record = state.acceptedById(instance.instanceId());
            BountyView.State viewState;
            int progress = 0;
            if (state.isClaimed(instance.instanceId())) {
                viewState = BountyView.State.CLAIMED;
            } else if (record != null) {
                progress = record.progress;
                viewState = record.done ? BountyView.State.READY : BountyView.State.ACCEPTED;
            } else if (prerequisiteMissing(player, instance) != null) {
                viewState = BountyView.State.LOCKED;
            } else {
                viewState = BountyView.State.AVAILABLE;
            }
            BountyModel.Reward reward = instance.reward;
            entries.add(new BountyView.Entry(instance.instanceId(), instance.titleKey(), instance.descKey(),
                    instance.type, targetKey(instance), instance.amount, progress, viewState,
                    reward.emeralds, reward.experience, reward.supplies));
        }
        BountyView view = new BountyView(state.publicationDay(), state.accepted().size(),
                BountyStateMachine.MAX_ACTIVE, statusKey, entries);
        com.dynasty.network.DynastyNetwork.CHANNEL.sendTo(
                new com.dynasty.network.BountyBoardPacket(view),
                player.connection.connection,
                net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT);
    }

    /** 目标在客户端的翻译键：物品/实体用原版 descriptionId，维度用已有的 dimension.dynasty.* 键。 */
    private static String targetKey(BountyModel.Instance instance) {
        if (instance.targetKind == BountyModel.TargetKind.ITEM) {
            net.minecraft.world.item.Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(instance.target));
            return item == null ? instance.target : new net.minecraft.world.item.ItemStack(item).getDescriptionId();
        }
        if (instance.targetKind == BountyModel.TargetKind.ENTITY) {
            net.minecraft.world.entity.EntityType<?> type =
                    ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(instance.target));
            return type == null ? instance.target : type.getDescriptionId();
        }
        ResourceLocation dimension = new ResourceLocation(instance.target);
        return "dimension." + dimension.getNamespace() + "." + dimension.getPath();
    }
}
