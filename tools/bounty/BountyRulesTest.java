import com.dynasty.bounty.BountyModel;
import com.dynasty.bounty.BountyRules;
import com.dynasty.bounty.BountyStateMachine;

import java.util.ArrayList;
import java.util.List;

/**
 * 悬赏委托核心状态与奖励约束的可运行测试（不需要 JUnit、不需要 Minecraft 运行时）。
 *
 * 运行：
 *   ./gradlew compileJava --offline
 *   javac -cp build/classes/java/main -d /tmp/bounty_test tools/bounty/BountyRulesTest.java
 *   java -cp build/classes/java/main:/tmp/bounty_test BountyRulesTest
 *
 * 只测纯逻辑（BountyModel / BountyStateMachine / BountyRules）。
 * 界面交互、网络与多人真机行为不在本测试范围。
 */
public final class BountyRulesTest {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    public static void main(String[] args) {
        acceptLimit();
        killsBeforeAcceptDoNotCount();
        wrongTargetDoesNotCount();
        abandonThenReaccept();
        crossDayKeepsAcceptedOffer();
        timeRollbackDoesNotRepublish();
        duplicateClaimRejected();
        duplicateSubmitRejected();
        insufficientItemsConsumeNothing();
        rewardSpaceRejectedThenKept();
        twoPlayersIsolated();
        saveAndReload();
        datapackReloadKeepsSnapshot();
        exploreCompletion();
        publishedListIsDeterministic();

        System.out.println();
        System.out.println("通过 " + passed + " 项，失败 " + failures.size() + " 项");
        for (String failure : failures) {
            System.out.println("  ❌ " + failure);
        }
        if (!failures.isEmpty()) {
            System.exit(1);
        }
        System.out.println("✅ 悬赏委托核心逻辑测试全部通过");
    }

    // ------------------------------------------------------------------ 用例

    private static void acceptLimit() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        check("接取满额：前三个成功", state.accept(state.published().get(0)) == BountyStateMachine.Accept.OK
                && state.accept(state.published().get(1)) == BountyStateMachine.Accept.OK
                && state.accept(state.published().get(2)) == BountyStateMachine.Accept.OK);
        check("接取满额：第四个被拒绝（FULL）",
                state.accept(state.published().get(3)) == BountyStateMachine.Accept.FULL
                        && state.accepted().size() == 3);
    }

    private static void killsBeforeAcceptDoNotCount() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance hunt = huntInstance(state, "minecraft:zombie");
        check("接取前击杀不计数", state.addHuntProgress("minecraft:zombie", 3) == 0);
        state.accept(hunt);
        check("接取后击杀才计数", state.addHuntProgress("minecraft:zombie", 2) == 1
                && state.acceptedById(hunt.instanceId()).progress == 2);
    }

    private static void wrongTargetDoesNotCount() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance hunt = huntInstance(state, "minecraft:zombie");
        state.accept(hunt);
        check("目标不符的击杀不计入", state.addHuntProgress("minecraft:skeleton", 5) == 0
                && state.acceptedById(hunt.instanceId()).progress == 0);
    }

    private static void abandonThenReaccept() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance hunt = huntInstance(state, "minecraft:zombie");
        state.accept(hunt);
        state.addHuntProgress("minecraft:zombie", 2);
        check("放弃成功", state.abandon(hunt.instanceId()));
        check("放弃后进度清零，重新接取从 0 开始",
                state.accept(hunt) == BountyStateMachine.Accept.OK
                        && state.acceptedById(hunt.instanceId()).progress == 0);
        check("放弃不发奖励（没有已领记录）", !state.isClaimed(hunt.instanceId()));
    }

    private static void crossDayKeepsAcceptedOffer() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        state.submit(acquire.instanceId(), acquire.amount);
        state.publish(11L, daily(11L, 6));                      // 跨日
        BountyStateMachine.Accepted kept = state.acceptedById(acquire.instanceId());
        check("跨日：已接委托、进度与奖励快照都保留",
                kept != null && kept.done && kept.instance.reward.emeralds == acquire.reward.emeralds);
        check("跨日：仍然可以领奖", state.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.OK);
    }

    private static void timeRollbackDoesNotRepublish() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        state.submit(acquire.instanceId(), acquire.amount);
        state.claim(acquire.instanceId(), true);
        long rolledBack = state.effectiveDay(3L);               // 时间倒退到第 3 天
        check("时间倒退：有效日不降（水位仍是 10）", rolledBack == 10L);
        check("时间倒退：不重新发布旧日期实例", !state.needsPublication(rolledBack)
                && state.publishedById(acquire.instanceId()) != null);
        check("时间倒退：旧日期的已领委托不能重新领奖",
                state.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.ALREADY_CLAIMED
                        && state.accept(acquire) == BountyStateMachine.Accept.ALREADY_CLAIMED);
    }

    private static void duplicateClaimRejected() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        state.submit(acquire.instanceId(), acquire.amount);
        check("首次领奖成功", state.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.OK);
        check("重复领奖被拒绝",
                state.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.ALREADY_CLAIMED);
    }

    private static void duplicateSubmitRejected() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        check("首次提交成功并消耗正确数量",
                state.submit(acquire.instanceId(), acquire.amount) == BountyStateMachine.Submit.OK
                        && state.consumedOnSubmit(acquire.instanceId()) == acquire.amount);
        check("重复提交被拒绝且不再消耗",
                state.submit(acquire.instanceId(), 64) == BountyStateMachine.Submit.ALREADY_DONE
                        && state.consumedOnSubmit(acquire.instanceId()) == 0);
    }

    private static void insufficientItemsConsumeNothing() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        check("材料不足：拒绝提交且消耗量为 0（不会扣一半）",
                state.submit(acquire.instanceId(), acquire.amount - 1) == BountyStateMachine.Submit.INSUFFICIENT
                        && state.consumedOnSubmit(acquire.instanceId()) == 0
                        && !state.acceptedById(acquire.instanceId()).done);
    }

    private static void rewardSpaceRejectedThenKept() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        state.submit(acquire.instanceId(), acquire.amount);
        check("背包空间不足：拒绝领奖但保留可领取状态",
                state.claim(acquire.instanceId(), false) == BountyStateMachine.Claim.NO_SPACE
                        && state.acceptedById(acquire.instanceId()).done
                        && !state.isClaimed(acquire.instanceId()));
        check("腾出空间后可以正常领取",
                state.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.OK);
    }

    private static void twoPlayersIsolated() {
        BountyStateMachine first = new BountyStateMachine();
        BountyStateMachine second = new BountyStateMachine();
        first.publish(10L, daily(10L, 6));
        second.publish(10L, daily(10L, 6));
        BountyModel.Instance instance = first.published().get(0);
        first.accept(instance);
        check("两名玩家隔离：A 接取不影响 B", first.accepted().size() == 1 && second.accepted().isEmpty());
        first.abandon(instance.instanceId());
        check("两名玩家隔离：A 放弃后 B 的发布列表不受影响", second.published().size() == 6);
    }

    private static void saveAndReload() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        BountyModel.Instance hunt = huntInstance(state, "minecraft:zombie");
        state.accept(acquire);
        state.accept(hunt);
        state.submit(acquire.instanceId(), acquire.amount);
        state.claim(acquire.instanceId(), true);
        state.addHuntProgress("minecraft:zombie", 2);

        BountyStateMachine loaded = BountyStateMachine.fromLines(state.toLines());
        check("存档往返：日水位与发布日一致",
                loaded.lastDay() == state.lastDay() && loaded.publicationDay() == state.publicationDay());
        check("存档往返：发布列表条数一致", loaded.published().size() == state.published().size());
        check("存档往返：已接委托与进度一致",
                loaded.acceptedById(hunt.instanceId()) != null
                        && loaded.acceptedById(hunt.instanceId()).progress == 2);
        check("存档往返：已领记录仍然阻止重复领奖",
                loaded.isClaimed(acquire.instanceId())
                        && loaded.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.ALREADY_CLAIMED);
        check("存档往返：奖励快照一致",
                loaded.acceptedById(hunt.instanceId()).instance.reward.emeralds
                        == state.acceptedById(hunt.instanceId()).instance.reward.emeralds);
    }

    private static void datapackReloadKeepsSnapshot() {
        BountyStateMachine state = new BountyStateMachine();
        state.publish(10L, daily(10L, 6));
        BountyModel.Instance acquire = acquireInstance(state, "minecraft:wheat");
        state.accept(acquire);
        // 模拟数据包重载：定义池里同名委托换成「奖励更高」的新对象
        BountyModel.Offer changed = new BountyModel.Offer(acquire.offer.id, BountyModel.Type.ACQUIRE,
                acquire.titleKey(), acquire.descKey(), BountyModel.TargetKind.ITEM, acquire.target,
                acquire.amount, 99, null, new BountyModel.Reward(16, 30, List.of()));
        check("数据包重载：已接委托仍用旧快照（奖励不被改）",
                state.acceptedById(acquire.instanceId()).instance.reward.emeralds == acquire.reward.emeralds
                        && changed.reward.emeralds == 16);
        state.submit(acquire.instanceId(), acquire.amount);
        check("数据包重载后仍按旧快照完成与领奖",
                state.claim(acquire.instanceId(), true) == BountyStateMachine.Claim.OK);
    }

    private static void exploreCompletion() {
        BountyStateMachine state = new BountyStateMachine();
        List<BountyModel.Instance> published = new ArrayList<>(daily(10L, 6));
        BountyModel.Instance explore = new BountyModel.Instance(10L, published.size(),
                new BountyModel.Offer("dynasty:explore_underworld", BountyModel.Type.EXPLORE, "t", "d",
                        BountyModel.TargetKind.DIMENSION, "dynasty:underworld", 1, 8, null,
                        new BountyModel.Reward(4, 4, List.of())),
                new BountyModel.Reward(4, 4, List.of()));
        published.add(explore);
        state.publish(11L, published);
        state.accept(explore);
        check("考察：进入错误维度不完成", state.markExplore("dynasty:celestial_dynasty") == 0);
        check("考察：进入指定维度即完成", state.markExplore("dynasty:underworld") == 1
                && state.acceptedById(explore.instanceId()).done);
    }

    private static void publishedListIsDeterministic() {
        List<BountyModel.Offer> pool = pool();
        List<BountyModel.Offer> first = BountyRules.pickDaily(pool, 6, 42L);
        List<BountyModel.Offer> second = BountyRules.pickDaily(pool, 6, 42L);
        List<BountyModel.Offer> other = BountyRules.pickDaily(pool, 6, 43L);
        check("发布决定论：同一天两次抽取完全一致",
                ids(first).equals(ids(second)) && first.size() == 6);
        check("发布决定论：不同天会变化", !ids(first).equals(ids(other)));
        check("定义校验：合法定义通过",
                BountyRules.validate(new BountyModel.Offer("dynasty:good", BountyModel.Type.ACQUIRE,
                        "dynasty.bounty.good.title", "dynasty.bounty.good.desc", BountyModel.TargetKind.ITEM,
                        "minecraft:wheat", 16, 10, null, new BountyModel.Reward(3, 2, List.of()))) == null);
        check("定义校验：数量或权重非法会被拒绝",
                BountyRules.validate(new BountyModel.Offer("dynasty:zero", BountyModel.Type.ACQUIRE,
                        "dynasty.bounty.zero.title", "dynasty.bounty.zero.desc", BountyModel.TargetKind.ITEM,
                        "minecraft:wheat", 0, 10, null, new BountyModel.Reward(3, 2, List.of()))) != null
                        && BountyRules.validate(new BountyModel.Offer("dynasty:w0", BountyModel.Type.ACQUIRE,
                        "dynasty.bounty.w0.title", "dynasty.bounty.w0.desc", BountyModel.TargetKind.ITEM,
                        "minecraft:wheat", 16, 0, null, new BountyModel.Reward(3, 2, List.of()))) != null);
        check("定义校验：把 Boss 信物当奖励会被拒绝",
                BountyRules.validate(new BountyModel.Offer("dynasty:bad", BountyModel.Type.ACQUIRE,
                        "dynasty.bounty.x", "dynasty.bounty.x.desc", BountyModel.TargetKind.ITEM,
                        "minecraft:wheat", 1, 1, null,
                        new BountyModel.Reward(1, 0, List.of(new BountyModel.Stack("dynasty:sky_token", 1))))) != null);
    }

    // ------------------------------------------------------------------ 工具

    private static BountyModel.Instance huntInstance(BountyStateMachine state, String entity) {
        for (BountyModel.Instance instance : state.published()) {
            if (instance.type == BountyModel.Type.HUNT && instance.target.equals(entity)) {
                return instance;
            }
        }
        return synthetic(state, BountyModel.Type.HUNT, BountyModel.TargetKind.ENTITY, entity, 4);
    }

    private static BountyModel.Instance acquireInstance(BountyStateMachine state, String item) {
        for (BountyModel.Instance instance : state.published()) {
            if (instance.type == BountyModel.Type.ACQUIRE && instance.target.equals(item)) {
                return instance;
            }
        }
        return synthetic(state, BountyModel.Type.ACQUIRE, BountyModel.TargetKind.ITEM, item, 16);
    }

    /** 池子里没抽到时补一条同类委托，保证用例不受当天抽取结果影响。 */
    private static BountyModel.Instance synthetic(BountyStateMachine state, BountyModel.Type type,
                                                  BountyModel.TargetKind kind, String target, int amount) {
        List<BountyModel.Instance> published = new ArrayList<>(state.published());
        BountyModel.Instance instance = new BountyModel.Instance(10L, published.size(),
                new BountyModel.Offer("dynasty:test_" + target.replace(':', '_'), type, "t", "d",
                        kind, target, amount, 10, null, new BountyModel.Reward(3, 2, List.of())),
                new BountyModel.Reward(3, 2, List.of()));
        published.add(instance);
        state.publish(state.publicationDay() + 1, published);
        return instance;
    }

    /** 与真实数据同构的一组每日发布（8 收购 / 4 讨伐 / 4 考察）。 */
    private static List<BountyModel.Instance> daily(long day, int count) {
        List<BountyModel.Offer> picked = BountyRules.pickDaily(pool(), count, day);
        List<BountyModel.Instance> instances = new ArrayList<>();
        for (int slot = 0; slot < picked.size(); slot++) {
            BountyModel.Offer offer = picked.get(slot);
            instances.add(new BountyModel.Instance(day, slot, offer, offer.reward));
        }
        return instances;
    }

    private static List<BountyModel.Offer> pool() {
        List<BountyModel.Offer> pool = new ArrayList<>();
        String[] crops = {"minecraft:wheat", "minecraft:carrot", "minecraft:potato",
                "minecraft:brown_mushroom", "minecraft:string", "minecraft:leather",
                "minecraft:paper", "minecraft:bamboo"};
        for (int i = 0; i < crops.length; i++) {
            pool.add(new BountyModel.Offer("dynasty:acquire_" + i, BountyModel.Type.ACQUIRE, "t", "d",
                    BountyModel.TargetKind.ITEM, crops[i], 16, 12, null,
                    new BountyModel.Reward(3, 2, List.of())));
        }
        String[] mobs = {"minecraft:zombie", "minecraft:skeleton", "minecraft:spider", "minecraft:creeper"};
        for (String mob : mobs) {
            pool.add(new BountyModel.Offer("dynasty:hunt_" + mob.substring(10), BountyModel.Type.HUNT, "t", "d",
                    BountyModel.TargetKind.ENTITY, mob, 8, 12, null,
                    new BountyModel.Reward(4, 4, List.of(new BountyModel.Stack("minecraft:bread", 2)))));
        }
        String[] dimensions = {"dynasty:celestial_dynasty", "dynasty:underworld",
                "dynasty:jiuxiao", "dynasty:dragon_palace"};
        for (String dimension : dimensions) {
            pool.add(new BountyModel.Offer("dynasty:explore_" + dimension.substring(8), BountyModel.Type.EXPLORE,
                    "t", "d", BountyModel.TargetKind.DIMENSION, dimension, 1, 8, null,
                    new BountyModel.Reward(5, 5, List.of())));
        }
        return pool;
    }

    private static List<String> ids(List<BountyModel.Offer> offers) {
        List<String> ids = new ArrayList<>();
        for (BountyModel.Offer offer : offers) {
            ids.add(offer.id);
        }
        return ids;
    }

    private static void check(String name, boolean condition) {
        if (condition) {
            passed++;
            System.out.println("  ✓ " + name);
        } else {
            failures.add(name);
            System.out.println("  ✗ " + name);
        }
    }
}

