package com.dynasty;

import com.dynasty.keju.KejuBankCache;
import com.dynasty.keju.KejuCooldown;
import com.dynasty.keju.KejuReloadListener;
import com.dynasty.keju.KejuRules;
import com.dynasty.keju.KejuServerState;
import com.dynasty.keju.KejuSession;
import com.dynasty.keju.KejuSessionRegistry;
import com.dynasty.network.DynastyNetwork;
import com.dynasty.network.OpenKejuPacket;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.network.PacketDistributor;

import java.util.ArrayList;
import java.util.List;

/**
 * 科举系统（服务端逻辑）：题库驱动的出题、判定与奖励。
 *
 * 题目来自数据包 `data/dynasty/keju/questions.json`：三档（县试 / 会试 / 殿试），
 * 每档带功名门槛与奖励，出题时按玩家功名自动挑档；题库由 {@code /reload} 热重载，
 * 校验失败沿用上一份有效题库，首次加载没有有效题库时回落到内置七题兜底。
 *
 * 答题走**一次性会话**：开题时把令牌、题目与档位奖励快照固定下来，
 * 判分只看快照，客户端只提交「令牌 + 1..3 选项」。先验证再消费，
 * 旧令牌 / 别人的令牌 / 非法选项都不会吃掉当前有效题目。
 *
 * 答对给三个效果与一本可书写书（不受冷却限制），档位功名带 30 秒冷却。
 *
 * Keju: datapack-driven question bank with hot reload, strict validation, a
 * one-shot session per exam, and a merit cooldown that only gates the merit.
 */
@SuppressWarnings("null")
public final class DynastyKeju {

    private DynastyKeju() {
    }

    /** 题库数据包位置 / datapack location of the bank */
    public static final ResourceLocation BANK_LOCATION = new ResourceLocation("dynasty", "keju/questions.json");

    /** 档位功名奖励冷却（毫秒），与题库契约同源：仍为 30 秒。 */
    public static final long REWARD_COOLDOWN_MS = KejuRules.REWARD_COOLDOWN_MS;

    /** 内置兜底题库（数据包缺失或整库校验失败时使用，题数下限见 KejuRules.FALLBACK_MIN_QUESTIONS）。*/
    private static final String[][] FALLBACK = {
            {"秦始皇统一六国是在公元前哪一年？", "前 221 年", "前 206 年", "前 256 年", "1"},
            {"「贞观之治」出现在哪个朝代？", "汉朝", "唐朝", "宋朝", "2"},
            {"科举制度正式创立于哪个朝代？", "隋朝", "明朝", "清朝", "1"},
            {"「文景之治」属于哪个朝代？", "秦朝", "汉朝", "唐朝", "2"},
            {"中国古代四大发明不包括？", "造纸术", "指南针", "地动仪", "3"},
            {"「开元盛世」是哪位皇帝在位时期？", "汉武帝", "唐玄宗", "宋太祖", "2"},
            {"《史记》的作者是谁？", "司马迁", "班固", "司马光", "1"},
    };

    /** 每个服务器实例各自的待答会话与奖励冷却（按实例身份隔离）。*/
    private static final KejuServerState<MinecraftServer> STATE = new KejuServerState<>(REWARD_COOLDOWN_MS);

    /** 取该服务器的会话表。/ session registry of that server instance. */
    private static KejuSessionRegistry sessions(MinecraftServer server) {
        return STATE.sessions(server);
    }

    /** 取该服务器的奖励冷却表。/ merit cooldown of that server instance. */
    private static KejuCooldown meritCooldown(MinecraftServer server) {
        return STATE.cooldown(server);
    }

    /** 打开科举界面：按功名挑档、随机出题、建立一次性会话并发给玩家。 */
    public static void openExam(ServerPlayer player) {
        MinecraftServer server = player.getServer();
        List<KejuRules.Tier> bank = bank(server);
        if (bank.isEmpty()) {
            return;
        }
        KejuRules.Tier tier = bank.get(KejuRules.tierFor(bank, DynastyStats.getMerit(player)));
        if (tier.questions().isEmpty()) {
            return;
        }
        KejuRules.Question question = tier.questions().get(player.getRandom().nextInt(tier.questions().size()));
        KejuSession session = sessions(server).open(player.getUUID(), tier, question, System.currentTimeMillis());
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                new OpenKejuPacket(session.token(), question.text(),
                        question.options().get(0), question.options().get(1), question.options().get(2)));
        player.displayClientMessage(Component.literal("§6[科举] §r" + tier.zh()
                + "：答对 +" + tier.merit() + " 功名"), false);
    }

    /** 玩家当前待答的题目令牌（无则 null）。/ Pending question token for a player, or null. */
    public static Integer pending(Player player) {
        MinecraftServer server = player instanceof ServerPlayer serverPlayer ? serverPlayer.getServer() : null;
        if (server == null) {
            return null;
        }
        KejuSession session = sessions(server).peek(player.getUUID());
        return session == null ? null : session.token();
    }

    /**
     * 判定答案并给予奖励。先验证再消费：只有令牌与选项都合法的那一次提交才结束本题。
     */
    public static void handleAnswer(ServerPlayer player, int token, int choice) {
        MinecraftServer server = player.getServer();
        KejuSessionRegistry.Submission verdict = sessions(server).submit(player.getUUID(), token, choice);
        switch (verdict.status()) {
            case NO_SESSION -> player.sendSystemMessage(Component.literal("§c[科举] 题目已失效，请重新开始考试。"));
            case WRONG_TOKEN -> player.sendSystemMessage(Component.literal("§c[科举] 这次提交已过期（当前题目仍然有效，请重新作答）。"));
            case ILLEGAL_CHOICE -> player.sendSystemMessage(Component.literal("§c[科举] 请选择 1 / 2 / 3。"));
            case ACCEPTED -> grant(player, verdict.session(), verdict.correct());
        }
    }

    /** 发放奖励：效果与书不受冷却限制；只有档位功名受 30 秒冷却限制（保持原语义）。 */
    private static void grant(ServerPlayer player, KejuSession session, boolean correct) {
        if (!correct) {
            player.sendSystemMessage(Component.literal("§c[科举] 答错了，正确答案是："
                    + session.correctOption()));
            return;
        }
        long now = System.currentTimeMillis();
        KejuCooldown meritCooldown = meritCooldown(player.getServer());
        player.addEffect(new MobEffectInstance(DynastyEffects.DRAGON_MIGHT.get(), 20 * 180, 0));
        player.addEffect(new MobEffectInstance(DynastyEffects.SWIFT_WIND.get(), 20 * 180, 0));
        player.addEffect(new MobEffectInstance(DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 180, 0));
        player.getInventory().add(new ItemStack(Items.WRITABLE_BOOK));
        if (meritCooldown.ready(player.getUUID(), now)) {
            meritCooldown.mark(player.getUUID(), now);
            meritCooldown.pruneExpired(now);
            DynastyStats.addMerit(player, session.merit());
            player.sendSystemMessage(Component.literal("§a[科举] " + session.tierZh()
                    + "中第！功名 +" + session.merit() + "（龙威 + 疾风 + 天命）"));
        } else {
            long left = meritCooldown.remaining(player.getUUID(), now) / 1000L + 1;
            player.sendSystemMessage(Component.literal("§a[科举] " + session.tierZh()
                    + "中第！功名奖励冷却中（还剩 " + left + " 秒），效果照给。"));
        }
        DynastyMerit.onEvent(player, "keju");
        DynastyAdvancements.awardForEvent(player, "keju");
    }

    /** 内置兜底题库（唯一来源就是上面的 FALLBACK 表，兜底题数下限由 KejuRules 校验）。 */
    private static List<KejuRules.Tier> fallbackTiers() {
        List<KejuRules.Question> questions = new ArrayList<>();
        for (String[] row : FALLBACK) {
            questions.add(new KejuRules.Question(row[0], List.of(row[1], row[2], row[3]), Integer.parseInt(row[4])));
        }
        return List.of(new KejuRules.Tier("county", "县试", "County Exam", 0, 12, questions));
    }

    /** 取现役题库：还没加载过就先按服务器资源管理器读一次（缺文件 / 非法则回落兜底）。 */
    private static List<KejuRules.Tier> bank(MinecraftServer server) {
        if (!KejuBankCache.loaded()) {
            onBankReload(server == null
                    ? KejuRules.load(null, KejuRules.BANK_RESOURCE_PATH)
                    : KejuReloadListener.readBank(server.getResourceManager(), BANK_LOCATION));
        }
        return KejuBankCache.active();
    }

    /**
     * 题库重载结果处理：整份合法才替换现役题库；校验失败或文件缺失时保留旧题库，
     * 首次加载（还没有有效题库）时回落到内置兜底。会话与冷却都不受影响。
     */
    public static void onBankReload(KejuRules.Load load) {
        if (load == null) {
            return;
        }
        if (load.ok()) {
            KejuBankCache.install(load);
            Dynasty.LOGGER.info("[Dynasty] 科举题库已装载：{} 档 / {} 题（{}）",
                    load.tiers().size(), load.questionCount(), load.source());
            return;
        }
        for (String problem : load.errors()) {
            Dynasty.LOGGER.warn("[Dynasty] 科举题库问题：{}", problem);
        }
        if (!KejuBankCache.loaded()) {
            List<KejuRules.Tier> fallback = fallbackTiers();
            List<String> fallbackProblems = new ArrayList<>();
            KejuRules.validateFallback(fallback, fallbackProblems);
            for (String problem : fallbackProblems) {
                Dynasty.LOGGER.error("[Dynasty] {}", problem);
            }
            KejuBankCache.installFallback(fallback, load.missingFile()
                    ? "内置兜底题库（缺少 " + load.source() + "）"
                    : "内置兜底题库（题库校验失败：" + load.errors().get(0) + "）");
            Dynasty.LOGGER.warn("[Dynasty] 科举题库不可用，回落到内置兜底题库（{} 题）",
                    fallback.get(0).questions().size());
            return;
        }
        if (load.missingFile()) {
            Dynasty.LOGGER.warn("[Dynasty] 科举题库文件缺失，继续沿用上一份有效题库：{}", load.source());
        } else {
            Dynasty.LOGGER.warn("[Dynasty] 科举题库校验失败，新题库不生效，继续沿用上一份有效题库");
        }
    }

    /** 服务器关闭：清空该实例的待答会话、奖励冷却与服务端题库缓存。 */
    public static void shutdown(MinecraftServer server) {
        STATE.shutdown(server);
        KejuBankCache.clear();
    }

    /** 玩家登出：丢弃待答会话，只清理已过期的冷却记录（冷却期内的记录保留）。 */
    public static void forgetPlayer(ServerPlayer player) {
        MinecraftServer server = player.getServer();
        if (server == null) {
            return;
        }
        sessions(server).forget(player.getUUID());
        meritCooldown(server).pruneExpired(System.currentTimeMillis());
    }
}
