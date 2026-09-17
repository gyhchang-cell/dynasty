package com.dynasty;

import com.dynasty.network.DynastyNetwork;
import com.dynasty.network.OpenKejuPacket;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.network.PacketDistributor;

import java.io.BufferedReader;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * 科举系统（服务端逻辑）：题库驱动的出题、判定与奖励。
 *
 * 题目来自数据包 `data/dynasty/keju/questions.json`：三档（县试 / 会试 / 殿试），
 * 每档带功名门槛与奖励，出题时按玩家功名自动挑档；文件缺失或损坏时回落到内置题库。
 * 答对给效果 + 功名（功名奖励有 30 秒冷却，防止刷分）。
 *
 * Keju: a datapack-driven question bank with three tiers (merit-gated), graceful
 * fallback to the built-in questions, and a cooldown on the merit reward.
 */
@SuppressWarnings("null")
public final class DynastyKeju {

    private DynastyKeju() {
    }

    /** 题库文件 / the question bank file */
    private static final ResourceLocation BANK = new ResourceLocation("dynasty", "keju/questions.json");

    /** 功名奖励冷却（毫秒）/ merit reward cooldown */
    private static final long REWARD_COOLDOWN_MS = 30_000L;

    /** 一题 / one question（correct 为 1..3）*/
    private record Question(String text, String[] options, int correct) {
    }

    /** 一档 / one tier */
    private record Tier(String zh, String en, int minMerit, int merit, List<Question> questions) {
    }

    /** 内置兜底题库（数据包缺失时使用）/ fallback bank */
    private static final String[][] FALLBACK = {
            {"秦始皇统一六国是在公元前哪一年？", "前 221 年", "前 206 年", "前 256 年", "1"},
            {"「贞观之治」出现在哪个朝代？", "汉朝", "唐朝", "宋朝", "2"},
            {"科举制度正式创立于哪个朝代？", "隋朝", "明朝", "清朝", "1"},
            {"「文景之治」属于哪个朝代？", "秦朝", "汉朝", "唐朝", "2"},
            {"中国古代四大发明不包括？", "造纸术", "指南针", "地动仪", "3"},
            {"「开元盛世」是哪位皇帝在位时期？", "汉武帝", "唐玄宗", "宋太祖", "2"},
            {"《史记》的作者是谁？", "司马迁", "班固", "司马光", "1"},
    };

    private static List<Tier> BANK_CACHE;
    private static MinecraftServer BANK_OWNER;

    private static final Map<UUID, Integer> PENDING = new HashMap<>();
    private static final Map<UUID, Long> LAST_REWARD = new HashMap<>();

    /** 打开科举界面：按功名挑档、随机出题并发给玩家。/ Opens the exam GUI with a tier-appropriate question. */
    public static void openExam(ServerPlayer player) {
        List<Tier> bank = bank(player);
        if (bank.isEmpty()) {
            return;
        }
        int tierIndex = tierFor(bank, DynastyStats.getMerit(player));
        Tier tier = bank.get(tierIndex);
        if (tier.questions().isEmpty()) {
            return;
        }
        int index = player.getRandom().nextInt(tier.questions().size());
        Question question = tier.questions().get(index);
        int token = tierIndex * 1000 + index;
        PENDING.put(player.getUUID(), token);
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                new OpenKejuPacket(token, question.text(),
                        question.options()[0], question.options()[1], question.options()[2]));
        player.displayClientMessage(Component.literal("§6[科举] §r" + tier.zh()
                + "：答对 +" + tier.merit() + " 功名"), false);
    }

    /** 玩家当前待答的题目令牌（无则 null）。/ Pending question token for a player, or null. */
    public static Integer pending(net.minecraft.world.entity.player.Player player) {
        return PENDING.get(player.getUUID());
    }

    /** 判定答案并给予奖励。/ Grades the answer and grants rewards. */
    public static void handleAnswer(ServerPlayer player, int index, int choice) {
        Integer token = PENDING.remove(player.getUUID());
        if (token == null || token != index) {
            player.sendSystemMessage(Component.literal("§c[科举] 题目已失效，请重新开始考试。"));
            return;
        }
        List<Tier> bank = bank(player);
        if (bank.isEmpty()) {
            return;
        }
        int tierIndex = Math.max(0, Math.min(bank.size() - 1, index / 1000));
        Tier tier = bank.get(tierIndex);
        int qi = index % 1000;
        Question question = qi >= 0 && qi < tier.questions().size() ? tier.questions().get(qi) : null;
        if (question == null) {
            return;
        }

        if (choice == question.correct()) {
            player.addEffect(new MobEffectInstance(DynastyEffects.DRAGON_MIGHT.get(), 20 * 180, 0));
            player.addEffect(new MobEffectInstance(DynastyEffects.SWIFT_WIND.get(), 20 * 180, 0));
            player.addEffect(new MobEffectInstance(DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 180, 0));
            player.getInventory().add(new ItemStack(Items.WRITABLE_BOOK));
            long now = System.currentTimeMillis();
            Long last = LAST_REWARD.get(player.getUUID());
            if (last == null || now - last >= REWARD_COOLDOWN_MS) {
                LAST_REWARD.put(player.getUUID(), now);
                DynastyStats.addMerit(player, tier.merit());
                player.sendSystemMessage(Component.literal("§a[科举] " + tier.zh()
                        + "中第！功名 +" + tier.merit() + "（龙威 + 疾风 + 天命）"));
            } else {
                long left = (REWARD_COOLDOWN_MS - (now - last)) / 1000L + 1;
                player.sendSystemMessage(Component.literal("§a[科举] " + tier.zh()
                        + "中第！功名奖励冷却中（还剩 " + left + " 秒），效果照给。"));
            }
            DynastyMerit.onEvent(player, "keju");
            DynastyAdvancements.awardForEvent(player, "keju");
        } else {
            player.sendSystemMessage(Component.literal("§c[科举] 答错了，正确答案是："
                    + question.options()[question.correct() - 1]));
        }
    }

    /** 按功名挑档（题库按门槛升序，取最高够格的一档）。/ highest tier the merit qualifies for. */
    private static int tierFor(List<Tier> bank, int merit) {
        int best = 0;
        for (int i = 0; i < bank.size(); i++) {
            if (merit >= bank.get(i).minMerit()) {
                best = i;
            }
        }
        return best;
    }

    /** 取题库：数据包优先，服务器换实例时重新读一次。/ bank from the datapack, cached per server. */
    private static List<Tier> bank(ServerPlayer player) {
        MinecraftServer server = player.getServer();
        if (BANK_CACHE != null && BANK_OWNER == server) {
            return BANK_CACHE;
        }
        List<Tier> loaded = load(server);
        BANK_CACHE = loaded;
        BANK_OWNER = server;
        return loaded;
    }

    private static List<Tier> load(MinecraftServer server) {
        if (server != null) {
            try {
                Optional<Resource> resource = server.getResourceManager().getResource(BANK);
                if (resource.isPresent()) {
                    try (BufferedReader reader = resource.get().openAsReader()) {
                        JsonObject root = JsonParser.parseReader(reader).getAsJsonObject();
                        List<Tier> tiers = parse(root);
                        if (!tiers.isEmpty()) {
                            return tiers;
                        }
                    }
                }
            } catch (Exception error) {
                Dynasty.LOGGER.warn("[Dynasty] 科举题库读取失败，改用内置题库 / keju bank load failed", error);
            }
        }
        return fallback();
    }

    private static List<Tier> parse(JsonObject root) {
        List<Tier> tiers = new ArrayList<>();
        JsonArray array = root.getAsJsonArray("tiers");
        if (array == null) {
            return tiers;
        }
        for (JsonElement element : array) {
            if (!element.isJsonObject()) {
                continue;
            }
            JsonObject tier = element.getAsJsonObject();
            JsonArray raw = tier.getAsJsonArray("questions");
            List<Question> questions = new ArrayList<>();
            if (raw != null) {
                for (JsonElement candidate : raw) {
                    if (!candidate.isJsonObject()) {
                        continue;
                    }
                    JsonObject q = candidate.getAsJsonObject();
                    JsonArray options = q.getAsJsonArray("a");
                    if (q.get("q") == null || options == null || options.size() < 3) {
                        continue;
                    }
                    int correct = q.has("correct") ? q.get("correct").getAsInt() : 1;
                    if (correct < 1 || correct > 3) {
                        correct = 1;
                    }
                    questions.add(new Question(q.get("q").getAsString(),
                            new String[]{options.get(0).getAsString(), options.get(1).getAsString(),
                                    options.get(2).getAsString()}, correct));
                }
            }
            if (questions.isEmpty()) {
                continue;
            }
            tiers.add(new Tier(tier.has("zh") ? tier.get("zh").getAsString() : "科举",
                    tier.has("en") ? tier.get("en").getAsString() : "Exam",
                    tier.has("minMerit") ? tier.get("minMerit").getAsInt() : 0,
                    tier.has("merit") ? tier.get("merit").getAsInt() : 10,
                    List.copyOf(questions)));
        }
        tiers.sort(Comparator.comparingInt(Tier::minMerit));
        return tiers;
    }

    private static List<Tier> fallback() {
        List<Question> questions = new ArrayList<>();
        for (String[] row : FALLBACK) {
            questions.add(new Question(row[0], new String[]{row[1], row[2], row[3]}, Integer.parseInt(row[4])));
        }
        return List.of(new Tier("县试", "County Exam", 0, 12, List.copyOf(questions)));
    }
}
