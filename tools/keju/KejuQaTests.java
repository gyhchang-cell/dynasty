import com.dynasty.keju.KejuBankCache;
import com.dynasty.keju.KejuCooldown;
import com.dynasty.keju.KejuLayout;
import com.dynasty.keju.KejuNet;
import com.dynasty.keju.KejuRules;
import com.dynasty.keju.KejuServerState;
import com.dynasty.keju.KejuSession;
import com.dynasty.keju.KejuSessionRegistry;
import com.dynasty.network.AnswerKejuPacket;
import com.dynasty.network.OpenKejuPacket;
import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkDirection;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 科举（题库校验 / 答题会话 / 奖励冷却 / 网络契约）的可重复测试。
 *
 * 这里**直接调用生产类**（KejuRules / KejuSessionRegistry / KejuCooldown /
 * KejuServerState / KejuBankCache / KejuNet / 两个网络包），不是另写一份模拟逻辑；
 * 临时题库都构造成字符串传给加载器，不会碰正式题库文件。
 *
 * 运行：tools/keju/run_keju_tests.sh
 */
public final class KejuQaTests {

    private static final String SRC = "data/dynasty/keju/questions.json";
    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    public static void main(String[] args) {
        bankLimits();
        bankShapes();
        bankQuestions();
        bankCache();
        sessions();
        cooldowns();
        serverStates();
        layoutChecks();
        network();
        System.out.println();
        if (failures.isEmpty()) {
            System.out.println("通过 " + passed + " 项，失败 0 项");
            System.out.println("✅ 科举题库 / 会话 / 冷却 / 网络 测试全部通过");
        } else {
            System.out.println("通过 " + passed + " 项，失败 " + failures.size() + " 项");
            for (String failure : failures) {
                System.out.println("  ❌ " + failure);
            }
            System.exit(1);
        }
    }

    /* ---------- 构造临时题库 ---------- */

    private static void check(String name, boolean ok) {
        if (ok) {
            passed++;
        } else {
            failures.add(name);
        }
    }

    private static void check(String name, boolean ok, String detail) {
        if (ok) {
            passed++;
        } else {
            failures.add(name + " —— " + detail);
        }
    }

    private static String q(String text, String a, String b, String c, String correct) {
        return "{\"q\":\"" + text + "\",\"a\":[\"" + a + "\",\"" + b + "\",\"" + c + "\"],\"correct\":" + correct + "}";
    }

    private static String repeat(char ch, int count) {
        StringBuilder builder = new StringBuilder(count);
        for (int i = 0; i < count; i++) {
            builder.append(ch);
        }
        return builder.toString();
    }

    /** 生成 count 道题干互不相同的合法题目（答案固定 1）。 */
    private static String questions(int count, String prefix) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < count; i++) {
            if (i > 0) {
                builder.append(',');
            }
            builder.append(q(prefix + i, "A" + i, "B" + i, "C" + i, "1"));
        }
        return builder.toString();
    }

    private static String tier(String id, String zh, String en, String minMerit, String merit, String questions) {
        return "{\"id\":\"" + id + "\",\"zh\":\"" + zh + "\",\"en\":\"" + en + "\",\"minMerit\":" + minMerit
                + ",\"merit\":" + merit + ",\"questions\":[" + questions + "]}";
    }

    private static String tier(String id, String minMerit, String merit, String questions) {
        return tier(id, "档 " + id, "Tier " + id, minMerit, merit, questions);
    }

    private static String bank(String... tiers) {
        return "{\"tiers\":[" + String.join(",", tiers) + "]}";
    }

    /** 3 档 / 每档 10 题：门槛 0 / 400 / 1600，奖励 12 / 25 / 45（与正式题库同形）。 */
    private static String validBank() {
        return bank(tier("county", "县试", "County Exam", "0", "12", questions(10, "县试第")),
                tier("metropolitan", "会试", "Metropolitan", "400", "25", questions(10, "会试第")),
                tier("palace", "殿试", "Palace", "1600", "45", questions(10, "殿试第")));
    }

    private static KejuRules.Load load(String json) {
        return KejuRules.load(json, SRC);
    }

    private static boolean hasError(KejuRules.Load load, String needle) {
        for (String error : load.errors()) {
            if (error.contains(needle)) {
                return true;
            }
        }
        return false;
    }

    private static KejuRules.Question question(String text) {
        return new KejuRules.Question(text, List.of("甲", "乙", "丙"), 1);
    }

    private static KejuRules.Tier tierEntity(String id, int minMerit, int merit, int questionCount) {
        List<KejuRules.Question> list = new ArrayList<>();
        for (int i = 0; i < questionCount; i++) {
            list.add(question(id + "题" + i));
        }
        return new KejuRules.Tier(id, id, id, minMerit, merit, list);
    }

    private static KejuRules.Question firstQuestion(KejuRules.Tier tier) {
        return tier.questions().get(0);
    }

    /* ---------- 题库：上限与整体形状 ---------- */

    private static void bankLimits() {
        check("题库：契约常量（每档 10..200 题 / 最多 8 档 / 总 800 题 / 题干 200 字 / 选项 100 字 / 答案 1..3 / 冷却 30 秒）",
                KejuRules.MIN_PER_TIER == 10 && KejuRules.MAX_PER_TIER == 200 && KejuRules.MAX_TIERS == 8
                        && KejuRules.MAX_TOTAL_QUESTIONS == 800 && KejuRules.MAX_QUESTION_CHARS == 200
                        && KejuRules.MAX_OPTION_CHARS == 100 && KejuRules.CHOICES == 3
                        && KejuRules.MIN_CHOICE == 1 && KejuRules.MAX_CHOICE == 3
                        && KejuRules.REWARD_COOLDOWN_MS == 30_000L);

        KejuRules.Load good = load(validBank());
        check("题库：合法题库整份通过（3 档 / 30 题）",
                good.ok() && good.tiers().size() == 3 && good.questionCount() == 30, good.errors().toString());
        check("题库：门槛与奖励按文件顺序保留（0/400/1600，12/25/45）",
                good.ok() && good.tiers().get(0).minMerit() == 0 && good.tiers().get(1).minMerit() == 400
                        && good.tiers().get(2).minMerit() == 1600 && good.tiers().get(0).merit() == 12
                        && good.tiers().get(1).merit() == 25 && good.tiers().get(2).merit() == 45);
        check("题库：按功名挑档（0/399/400/1599/1600/99999）",
                good.ok() && KejuRules.tierFor(good.tiers(), 0) == 0 && KejuRules.tierFor(good.tiers(), 399) == 0
                        && KejuRules.tierFor(good.tiers(), 400) == 1 && KejuRules.tierFor(good.tiers(), 1599) == 1
                        && KejuRules.tierFor(good.tiers(), 1600) == 2 && KejuRules.tierFor(good.tiers(), 99999) == 2);

        KejuRules.Load missing = KejuRules.load(null, SRC);
        check("题库：缺文件被明确记录且不生效（调用方据此回落兜底）",
                !missing.ok() && missing.missingFile() && missing.tiers().isEmpty()
                        && hasError(missing, SRC) && hasError(missing, "题库文件缺失"), missing.errors().toString());

        KejuRules.Load broken = load("{\"tiers\":[{\"id\":\"a\",");
        check("题库：损坏 JSON 报出原因而不是抛异常",
                !broken.ok() && !broken.missingFile() && hasError(broken, "JSON 解析失败") && hasError(broken, SRC),
                broken.errors().toString());

        KejuRules.Load notObject = load("[]");
        check("题库：根节点不是对象时报错", !notObject.ok() && hasError(notObject, "根节点必须是 JSON 对象"));

        KejuRules.Load noTiers = load("{}");
        check("题库：缺少 tiers 数组时报错", !noTiers.ok() && hasError(noTiers, "缺少 tiers 数组"));

        KejuRules.Load tooManyTiers = load(bank(
                tier("a", "0", "5", questions(10, "a")), tier("b", "1", "5", questions(10, "b")),
                tier("c", "2", "5", questions(10, "c")), tier("d", "3", "5", questions(10, "d")),
                tier("e", "4", "5", questions(10, "e")), tier("f", "5", "5", questions(10, "f")),
                tier("g", "6", "5", questions(10, "g")), tier("h", "7", "5", questions(10, "h")),
                tier("i", "8", "5", questions(10, "i"))));
        check("题库：档位多于 8 档被拒绝", !tooManyTiers.ok() && hasError(tooManyTiers, "档位过多"));

        KejuRules.Load tooManyQuestions = load(bank(
                tier("a", "0", "5", questions(200, "a")), tier("b", "1", "5", questions(200, "b")),
                tier("c", "2", "5", questions(200, "c")), tier("d", "3", "5", questions(200, "d")),
                tier("e", "4", "5", questions(200, "e"))));
        check("题库：总题数超过 800 被拒绝", !tooManyQuestions.ok() && hasError(tooManyQuestions, "总题数过多"));

        KejuRules.Load tooFew = load(bank(tier("a", "0", "5", questions(9, "a"))));
        check("题库：每档少于 10 题被拒绝", !tooFew.ok() && hasError(tooFew, "题目不足 10 条"));

        KejuRules.Load tooManyPerTier = load(bank(tier("a", "0", "5", questions(201, "a"))));
        check("题库：单档多于 200 题被拒绝", !tooManyPerTier.ok() && hasError(tooManyPerTier, "题目过多"));

        KejuRules.Load positioned = load(bank(tier("county", "0", "5", questions(10, "县试第")),
                tier("metropolitan", "1", "5", questions(9, "会试第"))));
        boolean allPointAtPosition = !positioned.ok() && !positioned.errors().isEmpty();
        for (String error : positioned.errors()) {
            allPointAtPosition = allPointAtPosition && error.startsWith(SRC)
                    && (error.contains("档位 #") || error.contains("根节点"));
        }
        check("题库：错误信息带题库路径与档位位置", allPointAtPosition, positioned.errors().toString());
    }

    /* ---------- 题库：档位字段（拒绝错类型 / 空白 / 乱序） ---------- */

    private static void bankShapes() {
        KejuRules.Load blankId = load(bank(tier("   ", "0", "5", questions(10, "a"))));
        check("档位：id 为空白字符串被拒绝", !blankId.ok() && hasError(blankId, "空白字符串"));
        KejuRules.Load emptyId = load(bank(tier("", "0", "5", questions(10, "a"))));
        check("档位：id 为空字符串被拒绝", !emptyId.ok(), emptyId.errors().toString());
        KejuRules.Load duplicateId = load(bank(tier("county", "0", "5", questions(10, "a")),
                tier("county", "400", "5", questions(10, "b"))));
        check("档位：id 重复被拒绝", !duplicateId.ok() && hasError(duplicateId, "重复"));
        KejuRules.Load blankZh = load(bank(tier("county", "  ", "Tier", "0", "5", questions(10, "a"))));
        check("档位：zh 空白被拒绝", !blankZh.ok() && hasError(blankZh, "zh"));
        KejuRules.Load blankEn = load(bank(tier("county", "县试", "", "0", "5", questions(10, "a"))));
        check("档位：en 空白被拒绝", !blankEn.ok() && hasError(blankEn, "en"));
        KejuRules.Load stringMerit = load(bank(tier("county", "0", "\"5\"", questions(10, "a"))));
        check("档位：merit 是字符串被拒绝（不再静默修正）", !stringMerit.ok() && hasError(stringMerit, "merit"));
        KejuRules.Load boolMinMerit = load(bank(tier("county", "true", "5", questions(10, "a"))));
        check("档位：minMerit 是布尔被拒绝", !boolMinMerit.ok() && hasError(boolMinMerit, "minMerit"));
        KejuRules.Load stringMinMerit = load(bank(tier("county", "\"0\"", "5", questions(10, "a"))));
        check("档位：minMerit 是字符串被拒绝", !stringMinMerit.ok() && hasError(stringMinMerit, "minMerit"));
        KejuRules.Load negativeMinMerit = load(bank(tier("county", "-1", "5", questions(10, "a"))));
        check("档位：minMerit 为负被拒绝", !negativeMinMerit.ok() && hasError(negativeMinMerit, "不能为负"));
        KejuRules.Load firstNotZero = load(bank(tier("a", "10", "5", questions(10, "a"))));
        check("档位：第一档门槛不为 0 被拒绝（否则低功名玩家无档可考）",
                !firstNotZero.ok() && hasError(firstNotZero, "第一档 minMerit 必须是 0"));
        KejuRules.Load equalThresholds = load(bank(tier("a", "0", "5", questions(10, "a")),
                tier("b", "0", "5", questions(10, "b"))));
        check("档位：门槛相等（非严格递增）被拒绝",
                !equalThresholds.ok() && hasError(equalThresholds, "严格递增"));
        KejuRules.Load reversedThresholds = load(bank(tier("a", "0", "5", questions(10, "a")),
                tier("b", "400", "5", questions(10, "b")), tier("c", "200", "5", questions(10, "c"))));
        check("档位：门槛倒序被拒绝且不重排（整份不生效）",
                !reversedThresholds.ok() && hasError(reversedThresholds, "严格递增")
                        && reversedThresholds.tiers().isEmpty());
        KejuRules.Load zeroReward = load(bank(tier("a", "0", "0", questions(10, "a"))));
        check("档位：奖励功名必须为正", !zeroReward.ok() && hasError(zeroReward, "正整数"));
        KejuRules.Load emptyQuestions = load(bank(tier("a", "0", "5", "")));
        check("档位：questions 为空被拒绝（题目不足）", !emptyQuestions.ok() && hasError(emptyQuestions, "题目不足"));
        KejuRules.Load noQuestionsField = load("{\"tiers\":[{\"id\":\"a\",\"zh\":\"甲\",\"en\":\"A\","
                + "\"minMerit\":0,\"merit\":5}]}");
        check("档位：缺少 questions 数组被拒绝",
                !noQuestionsField.ok() && hasError(noQuestionsField, "缺少 questions"));
    }

    /* ---------- 题库：题目与三个选项 ---------- */

    private static void bankQuestions() {
        String ten = questions(10, "题");
        KejuRules.Load fourOptions = load(bank(tier("a", "0", "5",
                ten.replace("\"a\":[\"A0\",\"B0\",\"C0\"]", "\"a\":[\"A0\",\"B0\",\"C0\",\"D0\"]"))));
        check("题目：四个选项被拒绝且不截断",
                !fourOptions.ok() && hasError(fourOptions, "选项超过 3 个") && fourOptions.tiers().isEmpty(),
                fourOptions.errors().toString());
        KejuRules.Load twoOptions = load(bank(tier("a", "0", "5",
                ten.replace("\"a\":[\"A0\",\"B0\",\"C0\"]", "\"a\":[\"A0\",\"B0\"]"))));
        check("题目：选项不足三个被拒绝", !twoOptions.ok() && hasError(twoOptions, "选项不足 3 个"));
        KejuRules.Load duplicateOptions = load(bank(tier("a", "0", "5",
                ten.replace("\"a\":[\"A0\",\"B0\",\"C0\"]", "\"a\":[\"A0\",\"A0\",\"C0\"]"))));
        check("题目：选项互相重复被拒绝",
                !duplicateOptions.ok() && hasError(duplicateOptions, "选项与本页其它选项重复"));
        KejuRules.Load blankQuestion = load(bank(tier("a", "0", "5",
                ten.replace("\"q\":\"题0\"", "\"q\":\"   \""))));
        check("题目：空白题干被拒绝", !blankQuestion.ok() && hasError(blankQuestion, "题干不能是空白字符串"));
        KejuRules.Load emptyQuestion = load(bank(tier("a", "0", "5", ten.replace("\"q\":\"题0\"", "\"q\":\"\""))));
        check("题目：空题干被拒绝", !emptyQuestion.ok(), emptyQuestion.errors().toString());
        KejuRules.Load numericQuestion = load(bank(tier("a", "0", "5", ten.replace("\"q\":\"题0\"", "\"q\":123"))));
        check("题目：题干不是字符串被拒绝",
                !numericQuestion.ok() && hasError(numericQuestion, "题干必须是非空字符串"));
        KejuRules.Load duplicateQuestion = load(bank(tier("a", "0", "5", ten), tier("b", "400", "5", ten)));
        check("题目：题干全库重复被拒绝", !duplicateQuestion.ok() && hasError(duplicateQuestion, "题干与"));
        KejuRules.Load longQuestion = load(bank(tier("a", "0", "5", ten.replace("题0", repeat('长', 201)))));
        check("题目：题干超过 200 字被拒绝", !longQuestion.ok() && hasError(longQuestion, "题干过长"));
        KejuRules.Load longOption = load(bank(tier("a", "0", "5",
                ten.replace("\"A0\"", "\"" + repeat('甲', 101) + "\""))));
        check("题目：选项超过 100 字被拒绝", !longOption.ok() && hasError(longOption, "选项过长"));
        KejuRules.Load nearLimit = load(bank(tier("edge", "0", "5",
                questions(10, repeat('长', 195)).replace("\"A0\"", "\"" + repeat('甲', 100) + "\""))));
        check("题目：接近上限（题干 196 字 / 选项 100 字）仍然通过",
                nearLimit.ok(), nearLimit.errors().toString());

        KejuRules.Load answerZero = load(bank(tier("a", "0", "5", ten.replace("\"correct\":1}", "\"correct\":0}"))));
        check("答案：0 被拒绝", !answerZero.ok() && hasError(answerZero, "correct 越界：0"));
        KejuRules.Load answerFour = load(bank(tier("a", "0", "5", ten.replace("\"correct\":1}", "\"correct\":4}"))));
        check("答案：4 被拒绝", !answerFour.ok() && hasError(answerFour, "correct 越界：4"));
        KejuRules.Load answerBool = load(bank(tier("a", "0", "5",
                ten.replace("\"correct\":1}", "\"correct\":true}"))));
        check("答案：布尔 true 被拒绝（不接受冒充整数）",
                !answerBool.ok() && hasError(answerBool, "correct 必须是整数"));
        KejuRules.Load answerString = load(bank(tier("a", "0", "5",
                ten.replace("\"correct\":1}", "\"correct\":\"1\"}"))));
        check("答案：字符串 \"1\" 被拒绝", !answerString.ok() && hasError(answerString, "correct 必须是整数"));
        KejuRules.Load answerFloat = load(bank(tier("a", "0", "5",
                ten.replace("\"correct\":1}", "\"correct\":1.5}"))));
        check("答案：小数 1.5 被拒绝", !answerFloat.ok() && hasError(answerFloat, "correct 必须是整数"));
        KejuRules.Load answerMissing = load(bank(tier("a", "0", "5", ten.replace(",\"correct\":1}", "}"))));
        check("答案：缺少 correct 被拒绝", !answerMissing.ok() && hasError(answerMissing, "correct 必须是整数"));
        check("题库：非法题库整份不生效（不部分采用、不改写答案）",
                answerFour.tiers().isEmpty() && answerBool.tiers().isEmpty()
                        && answerMissing.tiers().isEmpty() && duplicateQuestion.tiers().isEmpty());
    }

    /* ---------- 题库缓存：整份替换 / 失败保留旧库 / 兜底 ---------- */

    private static void bankCache() {
        KejuBankCache.clear();
        check("缓存：清空后视为未加载", !KejuBankCache.loaded() && KejuBankCache.active().isEmpty());

        long before = KejuBankCache.generation();
        boolean installed = KejuBankCache.install(load(validBank()));
        check("缓存：合法题库装入后生效且 generation 递增",
                installed && KejuBankCache.loaded() && KejuBankCache.active().size() == 3
                        && !KejuBankCache.usingFallback() && KejuBankCache.generation() == before + 1);

        KejuRules.Tier keep = KejuBankCache.active().get(0);
        KejuRules.Load bad = load(bank(tier("county", "0", "5", questions(9, "坏"))));
        boolean badInstalled = KejuBankCache.install(bad);
        check("缓存：非法新题库不生效（旧题库原样保留，重载失败不破坏现役题库）",
                !badInstalled && KejuBankCache.loaded() && KejuBankCache.active().get(0) == keep
                        && !KejuBankCache.errors().isEmpty() && KejuBankCache.source().contains("keju"),
                KejuBankCache.errors().toString());

        List<KejuRules.Tier> fallback = List.of(tierEntity("county", 0, 12, 7));
        KejuBankCache.installFallback(fallback, "测试兜底");
        check("缓存：兜底题库装入并标记 usingFallback",
                KejuBankCache.loaded() && KejuBankCache.usingFallback()
                        && KejuBankCache.active().get(0).questions().size() == 7);

        List<String> fallbackErrors = new ArrayList<>();
        KejuRules.validateFallback(fallback, fallbackErrors);
        check("兜底：7 题兜底题库自检通过（题数 / 三个选项 / 答案范围）",
                fallbackErrors.isEmpty(), fallbackErrors.toString());
        List<String> tooSmall = new ArrayList<>();
        KejuRules.validateFallback(List.of(tierEntity("county", 0, 12, 6)), tooSmall);
        check("兜底：少于 7 题会被自检拦下", !tooSmall.isEmpty() && tooSmall.get(0).contains("少于 7 题"),
                tooSmall.toString());

        KejuBankCache.clear();
        check("缓存：服务器关闭后清空", !KejuBankCache.loaded() && KejuBankCache.active().isEmpty()
                && !KejuBankCache.usingFallback());
    }

    /* ---------- 答题会话：先验证再消费 ---------- */

    private static void sessions() {
        UUID alice = UUID.fromString("11111111-1111-1111-1111-111111111111");
        UUID bob = UUID.fromString("22222222-2222-2222-2222-222222222222");
        KejuRules.Tier county = tierEntity("county", 0, 12, 10);
        KejuRules.Question question = firstQuestion(county);
        KejuSessionRegistry registry = new KejuSessionRegistry(1000);

        KejuSession first = registry.open(alice, county, question, 5_000L);
        check("会话：开题的令牌与题目下标无关（不再是 档位*1000+下标）",
                first.token() >= 1000 && first.player().equals(alice) && first.merit() == 12
                        && first.tierId().equals("county") && first.correct() == 1 && first.createdAt() == 5_000L);
        check("会话：pending 能看到当前令牌",
                registry.peek(alice) != null && registry.peek(alice).token() == first.token());

        KejuSessionRegistry.Submission wrongToken = registry.submit(alice, first.token() + 7, 1);
        check("会话：错误令牌被拒绝且不吃掉当前有效题目",
                wrongToken.status() == KejuSessionRegistry.Status.WRONG_TOKEN && !wrongToken.accepted()
                        && registry.peek(alice) != null && registry.peek(alice).token() == first.token());

        KejuSessionRegistry.Submission noSession = registry.submit(bob, first.token(), 1);
        check("会话：没有会话的玩家得到 NO_SESSION（也动不了别人的题）",
                noSession.status() == KejuSessionRegistry.Status.NO_SESSION && registry.peek(alice) != null);

        for (int illegal : new int[]{0, 4, -1, 99}) {
            KejuSessionRegistry.Submission bad = registry.submit(alice, first.token(), illegal);
            check("会话：非法选项 " + illegal + " 被拒绝且不消费会话",
                    bad.status() == KejuSessionRegistry.Status.ILLEGAL_CHOICE && !bad.accepted()
                            && registry.peek(alice) != null);
        }

        KejuSessionRegistry.Submission accepted = registry.submit(alice, first.token(), 1);
        check("会话：令牌与选项都合法才消费，并给出判分结果",
                accepted.accepted() && accepted.correct() && accepted.session().token() == first.token()
                        && registry.peek(alice) == null);
        KejuSessionRegistry.Submission replay = registry.submit(alice, first.token(), 1);
        check("会话：同一令牌重复提交不再生效（不会二次奖励）",
                replay.status() == KejuSessionRegistry.Status.NO_SESSION && !replay.accepted());

        KejuSession older = registry.open(alice, county, question, 6_000L);
        KejuSession newer = registry.open(alice, county, question, 7_000L);
        check("会话：重新开题会换令牌且令牌严格递增、不复用",
                newer.token() != older.token() && newer.token() == older.token() + 1
                        && registry.peekNextToken() == newer.token() + 1);
        KejuSessionRegistry.Submission stalePacket = registry.submit(alice, older.token(), 2);
        check("会话：重开题后旧令牌失效，但不会破坏新题",
                stalePacket.status() == KejuSessionRegistry.Status.WRONG_TOKEN
                        && registry.peek(alice) != null && registry.peek(alice).token() == newer.token());
        KejuSessionRegistry.Submission newPacket = registry.submit(alice, newer.token(), 2);
        check("会话：新题按新会话判分（答 2 判错，正确答案取自快照）",
                newPacket.accepted() && !newPacket.correct() && "甲".equals(newPacket.session().correctOption()));
        check("会话：答错也结束本次题目", registry.peek(alice) == null);

        KejuSession bobSession = registry.open(bob, county, question, 8_000L);
        KejuSession aliceSession = registry.open(alice, county, question, 8_000L);
        KejuSessionRegistry.Submission foreign = registry.submit(bob, aliceSession.token(), 1);
        check("会话：拿着别人的令牌提交被拒，自己的题还在",
                foreign.status() == KejuSessionRegistry.Status.WRONG_TOKEN
                        && registry.peek(bob) != null && registry.peek(bob).token() == bobSession.token()
                        && registry.peek(alice) != null);

        registry.forget(bob);
        check("会话：登出清理后提交得到 NO_SESSION",
                registry.peek(bob) == null
                        && registry.submit(bob, bobSession.token(), 1).status() == KejuSessionRegistry.Status.NO_SESSION);
        registry.clear();
        check("会话：清空后无人待答", registry.size() == 0 && registry.peek(alice) == null);

        KejuSessionRegistry afterReloadRegistry = new KejuSessionRegistry(500);
        KejuRules.Tier oldTier = new KejuRules.Tier("county", "旧县试", "Old", 0, 12, List.of(question("旧题")));
        KejuSession snapshot = afterReloadRegistry.open(alice, oldTier, firstQuestion(oldTier), 1_000L);
        KejuRules.Tier newTier = new KejuRules.Tier("county", "新县试", "New", 0, 99, List.of(question("新题")));
        afterReloadRegistry.open(bob, newTier, firstQuestion(newTier), 2_000L);
        KejuSessionRegistry.Submission afterReload = afterReloadRegistry.submit(alice, snapshot.token(), 1);
        check("会话：题库重载后旧会话仍按开题快照判分与给奖（题目 / 档位 / 奖励不变）",
                afterReload.accepted() && afterReload.correct() && afterReload.session().question().equals("旧题")
                        && afterReload.session().merit() == 12 && afterReload.session().tierZh().equals("旧县试"));
        KejuSessionRegistry.Submission bobAfterReload =
                afterReloadRegistry.submit(bob, afterReloadRegistry.peek(bob).token(), 1);
        check("会话：重载后新开的题用新题库（奖励 99）",
                bobAfterReload.accepted() && bobAfterReload.session().merit() == 99
                        && bobAfterReload.session().question().equals("新题"));
    }

    /* ---------- 奖励冷却（时钟由测试注入，不真等 30 秒） ---------- */

    private static void cooldowns() {
        UUID alice = UUID.fromString("11111111-1111-1111-1111-111111111111");
        UUID bob = UUID.fromString("22222222-2222-2222-2222-222222222222");
        KejuCooldown cooldown = new KejuCooldown(KejuRules.REWARD_COOLDOWN_MS);
        check("冷却：窗口仍是 30 秒", cooldown.windowMs() == 30_000L);
        check("冷却：从未拿过奖励时可领", cooldown.ready(alice, 0L));

        cooldown.mark(alice, 1_000L);
        check("冷却：刚领完不可再领", !cooldown.ready(alice, 1_000L) && !cooldown.ready(alice, 1_001L));
        check("冷却：29.999 秒仍不可领", !cooldown.ready(alice, 1_000L + 29_999L));
        check("冷却：正好满 30 秒恢复可领（含端点）", cooldown.ready(alice, 1_000L + 30_000L));
        check("冷却：剩余时间计算正确",
                cooldown.remaining(alice, 1_000L) == 30_000L
                        && cooldown.remaining(alice, 16_000L) == 15_000L
                        && cooldown.remaining(alice, 40_000L) == 0L);
        check("冷却：只对本人生效（别人不受影响）", cooldown.ready(bob, 1_000L));

        cooldown.mark(bob, 10_000L);
        cooldown.pruneExpired(31_000L);
        check("冷却：登出只清理已过期条目（冷却期内的记录保留）",
                cooldown.size() == 1 && !cooldown.ready(bob, 39_000L));
        check("冷却：断线重连后仍要等满 30 秒", cooldown.ready(bob, 40_000L));
        cooldown.pruneExpired(40_000L);
        check("冷却：过期条目可清理，不会无限积累", cooldown.size() == 0);

        cooldown.mark(alice, 0L);
        cooldown.mark(bob, 5_000L);
        cooldown.pruneExpired(30_000L);
        check("冷却：清理时保留仍在冷却期内的玩家",
                cooldown.size() == 1 && cooldown.ready(alice, 30_000L) && !cooldown.ready(bob, 34_999L));
        cooldown.clear();
        check("冷却：服务器关闭时清空", cooldown.size() == 0);
    }

    /* ---------- 每个服务器实例一份会话与冷却 ---------- */

    private static void serverStates() {
        Object serverA = new Object();
        Object serverB = new Object();
        UUID alice = UUID.fromString("11111111-1111-1111-1111-111111111111");
        KejuRules.Tier county = tierEntity("county", 0, 12, 10);
        KejuServerState<Object> state = new KejuServerState<>(KejuRules.REWARD_COOLDOWN_MS);

        check("服务器槽位：初始未绑定", state.owner() == null);
        KejuSession sessionA = state.sessions(serverA).open(alice, county, firstQuestion(county), 1_000L);
        state.cooldown(serverA).mark(alice, 1_000L);
        check("服务器槽位：绑定到第一个服务器实例", state.owner() == serverA);

        KejuSessionRegistry registryA = state.sessions(serverA);
        KejuCooldown cooldownA = state.cooldown(serverA);
        check("服务器槽位：同一实例反复取到同一份会话与冷却（重开界面 / 重载不会重置）",
                state.sessions(serverA) == registryA && state.cooldown(serverA) == cooldownA);

        check("服务器槽位：换服务器实例后会话与冷却都隔离",
                state.sessions(serverB) != registryA && state.cooldown(serverB) != cooldownA
                        && state.sessions(serverB).size() == 0 && state.cooldown(serverB).ready(alice, 1_000L)
                        && state.owner() == serverB);
        check("服务器槽位：新实例里拿不到旧实例的令牌",
                state.sessions(serverB).submit(alice, sessionA.token(), 1)
                        .status() == KejuSessionRegistry.Status.NO_SESSION);

        state.shutdown(serverB);
        check("服务器槽位：关闭当前实例后清空该实例的会话（槽位解除绑定）",
                state.owner() == null && state.sessions(serverB).size() == 0
                        && state.cooldown(serverB).ready(alice, 1_000L));

        KejuSessionRegistry rebound = state.sessions(serverA);
        rebound.open(alice, county, firstQuestion(county), 9_000L);
        state.shutdown(serverB);
        check("服务器槽位：关闭另一个实例不影响当前实例（不误清别人）",
                state.owner() == serverA && state.sessions(serverA) == rebound && rebound.size() == 1);
        state.shutdown(serverA);
        check("服务器槽位：关闭当前实例后槽位再次清空", state.owner() == null);
    }

    /* ---------- 界面几何：小窗口 / 高缩放 / 长文本不越界且能滚动 ---------- */

    private static void layoutChecks() {
        // 窗口逻辑尺寸（已含 GUI 缩放）：1280×720@1x、@2x、@3x、高缩放、很矮、很窄
        int[][] windows = {{1280, 720}, {640, 360}, {426, 240}, {320, 180}, {214, 120}, {200, 110}, {150, 90}};
        boolean insideAll = true;
        boolean viewportAll = true;
        boolean shortNoScroll = true;
        boolean longScrollable = true;
        boolean revealFits = true;
        boolean monotonic = true;
        for (int[] window : windows) {
            KejuLayout layout = KejuLayout.of(window[0], window[1]);
            insideAll = insideAll && layout.panelX() >= 0 && layout.panelY() >= 0
                    && layout.panelX() + layout.panelW() <= window[0]
                    && layout.panelY() + layout.panelH() <= window[1]
                    && layout.viewBottom() <= layout.panelY() + layout.panelH();
            viewportAll = viewportAll && layout.viewportHeight() >= KejuLayout.MIN_VIEWPORT
                    && layout.textWidth() >= 40;

            int shortContent = KejuLayout.contentHeight(1, 1, 1, 1);
            if (window[1] >= 240) {
                // 短内容 + 正常窗口：不该出现滚动条，也不该把整页顶上去
                shortNoScroll = shortNoScroll && layout.maxScroll(shortContent) == 0;
            }

            int[] optionLines = {5, 4, 6};
            int longContent = KejuLayout.contentHeight(8, optionLines);
            int max = layout.maxScroll(longContent);
            longScrollable = longScrollable && max == Math.max(0, longContent - layout.viewportHeight())
                    && layout.clampScroll(-50, longContent) == 0
                    && layout.clampScroll(max + 500, longContent) == max;
            if (window[1] <= 360) {
                // 小窗口下同一份长文本必须能滚（大窗口够高时不该硬造滚动条）
                longScrollable = longScrollable && max > 0;
            }

            int[] tops = KejuLayout.optionTops(8, optionLines);
            int lastTop = tops[tops.length - 1];
            int lastBottom = lastTop + KejuLayout.optionHeight(optionLines[optionLines.length - 1]);
            revealFits = revealFits && layout.contentTop(max) + lastBottom <= layout.viewBottom() + 1;

            monotonic = monotonic && tops[0] == KejuLayout.questionBlockHeight(8);
            for (int i = 1; i < tops.length; i++) {
                monotonic = monotonic
                        && tops[i] - tops[i - 1] == KejuLayout.optionHeight(optionLines[i - 1]) + KejuLayout.OPTION_GAP;
            }
        }
        check("界面：所有窗口尺寸下面板与可视区都不越出窗口", insideAll);
        check("界面：可视区与文本宽度始终可用（小窗口也不塌成负值）", viewportAll);
        check("界面：内容不超高时不滚动（正常窗口）", shortNoScroll);
        check("界面：长题干 / 长选项时可滚动且滚动值被夹住", longScrollable);
        check("界面：滚到底能看到最后一个选项（不截断文字）", revealFits);
        check("界面：选项偏移递增且间隔一致", monotonic);

        KejuLayout small = KejuLayout.of(320, 180);
        int[] optionLines = {3, 3, 3};
        int[] tops = KejuLayout.optionTops(6, optionLines);
        int content = KejuLayout.contentHeight(6, optionLines);
        int scroll = small.clampScroll(30, content);
        int probeY = small.contentTop(scroll) + tops[1] + 2;
        boolean hitInside = small.insideViewport(small.panelX() + 5, probeY)
                && probeY - small.contentTop(scroll) >= tops[1]
                && probeY - small.contentTop(scroll) < tops[1] + KejuLayout.optionHeight(optionLines[1]);
        boolean outsideRejected = !small.insideViewport(small.panelX() + 5, small.viewTop() - 1)
                && !small.insideViewport(small.panelX() - 1, small.viewTop() + 5)
                && !small.insideViewport(small.panelX() + 5, small.viewBottom());
        check("界面：鼠标命中换算与可视区判定一致（可视区外不选中）", hitInside && outsideRejected);

        KejuLayout tall = KejuLayout.of(640, 360);
        int content2 = KejuLayout.contentHeight(6, optionLines);
        int[] tops2 = KejuLayout.optionTops(6, optionLines);
        int lastBottom = tops2[2] + KejuLayout.optionHeight(optionLines[2]);
        int revealed = tall.scrollToReveal(tops2[2], lastBottom, 0, content2);
        int back = tall.scrollToReveal(tops2[0], tops2[0] + KejuLayout.optionHeight(optionLines[0]), revealed, content2);
        check("界面：键盘切换会把目标选项滚进可视区（前后都夹在范围内）",
                revealed >= 0 && revealed <= tall.maxScroll(content2)
                        && back >= 0 && back <= revealed
                        && tall.contentTop(revealed) + lastBottom <= tall.viewBottom() + 1);

        for (int[] window : windows) {
            KejuLayout layout = KejuLayout.of(window[0], window[1]);
            System.out.printf("   窗口 %4d×%-4d → 面板 %3d×%-3d 可视区 %3d 文字宽 %3d 长内容滚动上限 %d%n",
                    window[0], window[1], layout.panelW(), layout.panelH(), layout.viewportHeight(),
                    layout.textWidth(), layout.maxScroll(KejuLayout.contentHeight(8, 5, 4, 6)));
        }
    }

    /* ---------- 网络：方向 / 长度上限 / 编解码往返 ---------- */

    private static void network() {
        check("网络：方向常量与现有注册一致（Open 只收 PLAY_TO_CLIENT，Answer 只收 PLAY_TO_SERVER）",
                KejuNet.OPEN_DIRECTION == NetworkDirection.PLAY_TO_CLIENT
                        && KejuNet.ANSWER_DIRECTION == NetworkDirection.PLAY_TO_SERVER
                        && KejuNet.acceptsOpen(NetworkDirection.PLAY_TO_CLIENT)
                        && !KejuNet.acceptsOpen(NetworkDirection.PLAY_TO_SERVER)
                        && !KejuNet.acceptsOpen(null)
                        && KejuNet.acceptsAnswer(NetworkDirection.PLAY_TO_SERVER)
                        && !KejuNet.acceptsAnswer(NetworkDirection.PLAY_TO_CLIENT)
                        && !KejuNet.acceptsAnswer(null));
        check("网络：长度上限与题库校验同源",
                KejuNet.MAX_QUESTION_CHARS == KejuRules.MAX_QUESTION_CHARS
                        && KejuNet.MAX_OPTION_CHARS == KejuRules.MAX_OPTION_CHARS);

        OpenKejuPacket open = new OpenKejuPacket(4242, "题干一行", "甲", "乙", "丙");
        FriendlyByteBuf buffer = new FriendlyByteBuf(Unpooled.buffer());
        OpenKejuPacket.encode(open, buffer);
        OpenKejuPacket decoded = OpenKejuPacket.decode(buffer);
        check("网络：Open 包（一个 int + 四个字符串）往返一致",
                decoded.index() == 4242 && "题干一行".equals(decoded.question())
                        && "甲".equals(decoded.options()[0]) && "乙".equals(decoded.options()[1])
                        && "丙".equals(decoded.options()[2]));

        FriendlyByteBuf longQuestion = new FriendlyByteBuf(Unpooled.buffer());
        longQuestion.writeInt(1);
        longQuestion.writeUtf(repeat('长', KejuNet.MAX_QUESTION_CHARS + 1), 32767);
        longQuestion.writeUtf("甲", 32767);
        longQuestion.writeUtf("乙", 32767);
        longQuestion.writeUtf("丙", 32767);
        check("网络：超长题干被拒绝（解码异常，不截断、不崩服）",
                rejected(() -> OpenKejuPacket.decode(longQuestion)));

        FriendlyByteBuf longOption = new FriendlyByteBuf(Unpooled.buffer());
        longOption.writeInt(1);
        longOption.writeUtf("题干", 32767);
        longOption.writeUtf(repeat('甲', KejuNet.MAX_OPTION_CHARS + 1), 32767);
        longOption.writeUtf("乙", 32767);
        longOption.writeUtf("丙", 32767);
        check("网络：超长选项被拒绝", rejected(() -> OpenKejuPacket.decode(longOption)));

        AnswerKejuPacket answer = new AnswerKejuPacket(4242, 3);
        FriendlyByteBuf answerBuffer = new FriendlyByteBuf(Unpooled.buffer());
        AnswerKejuPacket.encode(answer, answerBuffer);
        AnswerKejuPacket decodedAnswer = AnswerKejuPacket.decode(answerBuffer);
        check("网络：Answer 包（两个 int）往返一致",
                decodedAnswer.index() == 4242 && decodedAnswer.choice() == 3);
        AnswerKejuPacket illegalChoice =
                AnswerKejuPacket.decode(new FriendlyByteBuf(Unpooled.buffer().writeInt(9).writeInt(7)));
        check("网络：越界选项不在解码期被改成 1（交给服务端会话裁定）", illegalChoice.choice() == 7);
    }

    /** 期望某个操作被拒绝（抛运行时异常）。 */
    private static boolean rejected(Runnable action) {
        try {
            action.run();
            return false;
        } catch (RuntimeException error) {
            return true;
        }
    }
}
