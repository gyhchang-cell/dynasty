package com.dynasty.keju;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 科举规则的纯逻辑层（不引用任何 Minecraft / Forge 类，可直接用 javac 单测）。
 *
 * 这里同时是「题库契约」的唯一来源：档位与题目的上限、题干/选项长度、答案范围
 * 都写在本类的常量里，{@code DynastyKeju}（加载器）、网络包（{@code OpenKejuPacket}）
 * 与 Python 校验器 {@code tools/art/verify_keju.py} 都按同一份数字执行。
 * 校验只报错、绝不修正：答案越界不再被静默改成 1，选项多于三个不再被截断，
 * 门槛乱序不再被重排。
 *
 * Pure Keju rules: bank parsing/validation (single source of truth for limits),
 * tier selection and answer-range helpers. Never silently repairs bad data.
 */
public final class KejuRules {

    /** 每档最少题数 / minimum questions per tier */
    public static final int MIN_PER_TIER = 10;
    /** 每档最多题数 / maximum questions per tier */
    public static final int MAX_PER_TIER = 200;
    /** 最多档位数 / maximum tiers */
    public static final int MAX_TIERS = 8;
    /** 题库总题数上限 / maximum questions in the whole bank */
    public static final int MAX_TOTAL_QUESTIONS = 800;
    /** 题干长度上限（字符）/ question text limit */
    public static final int MAX_QUESTION_CHARS = 200;
    /** 单个选项长度上限（字符）/ option text limit */
    public static final int MAX_OPTION_CHARS = 100;
    /** 每题选项个数 / options per question */
    public static final int CHOICES = 3;
    /** 合法答案范围 / legal answer range */
    public static final int MIN_CHOICE = 1;
    public static final int MAX_CHOICE = 3;
    /** 档位功名奖励冷却（毫秒），与旧版一致 30 秒 / merit reward cooldown (unchanged) */
    public static final long REWARD_COOLDOWN_MS = 30_000L;
    /** 题库数据包路径 / datapack path of the bank */
    public static final String BANK_RESOURCE_PATH = "data/dynasty/keju/questions.json";
    /** 内置兜底题库最低题数 / minimum built-in fallback questions */
    public static final int FALLBACK_MIN_QUESTIONS = 7;

    private KejuRules() {
    }

    /** 一题：题干 + 三个选项 + 正确答案（1..3）。/ one question with an immutable option list. */
    public record Question(String text, List<String> options, int correct) {
        public Question(String text, List<String> options, int correct) {
            this.text = text;
            this.options = List.copyOf(options);
            this.correct = correct;
        }

        /** 正确答案的文本（越界时返回空串，不抛异常）。/ text of the correct option. */
        public String correctOption() {
            return correct >= 1 && correct <= options.size() ? options.get(correct - 1) : "";
        }
    }

    /** 一档：县试 / 会试 / 殿试。/ one tier. */
    public record Tier(String id, String zh, String en, int minMerit, int merit, List<Question> questions) {
        public Tier(String id, String zh, String en, int minMerit, int merit, List<Question> questions) {
            this.id = id;
            this.zh = zh;
            this.en = en;
            this.minMerit = minMerit;
            this.merit = merit;
            this.questions = List.copyOf(questions);
        }
    }

    /**
     * 一次加载的结果：成功时 {@code errors} 为空且 {@code tiers} 非空。
     * {@code missingFile} 表示数据包里没有这份题库（与「内容非法」区分开）。
     */
    public record Load(String source, List<Tier> tiers, List<String> errors, boolean missingFile) {
        public Load(String source, List<Tier> tiers, List<String> errors, boolean missingFile) {
            this.source = source;
            this.tiers = List.copyOf(tiers);
            this.errors = List.copyOf(errors);
            this.missingFile = missingFile;
        }

        public boolean ok() {
            return errors.isEmpty() && !tiers.isEmpty();
        }

        public int questionCount() {
            int total = 0;
            for (Tier tier : tiers) {
                total += tier.questions().size();
            }
            return total;
        }
    }

    /** 读取失败（IO 异常等）时构造的结果，原因写进 errors。/ build a load failure with a reason. */
    public static Load readFailure(String source, Throwable error) {
        String why = error == null ? "未知原因" : error.getClass().getSimpleName()
                + (error.getMessage() == null ? "" : "：" + error.getMessage());
        return new Load(source, List.of(), List.of(source + "：题库读取失败：" + why), false);
    }

    /** 从 JSON 文本加载并严格校验。{@code rawJson == null} 表示文件缺失。 */
    public static Load load(String rawJson, String source) {
        if (rawJson == null) {
            return new Load(source, List.of(), List.of(source + "：题库文件缺失（沿用上一份有效题库；"
                    + "首次加载回落到内置 " + FALLBACK_MIN_QUESTIONS + " 题兜底）"), true);
        }
        JsonElement root;
        try {
            root = JsonParser.parseString(rawJson);
        } catch (RuntimeException error) {
            return new Load(source, List.of(), List.of(source + "：JSON 解析失败：" + error.getClass().getSimpleName()
                    + (error.getMessage() == null ? "" : "：" + error.getMessage())), false);
        }
        if (!root.isJsonObject()) {
            return new Load(source, List.of(), List.of(source + "：题库根节点必须是 JSON 对象"), false);
        }
        List<String> errors = new ArrayList<>();
        List<Tier> tiers = parse(root.getAsJsonObject(), source, errors);
        if (!errors.isEmpty()) {
            return new Load(source, List.of(), errors, false);
        }
        if (tiers.isEmpty()) {
            return new Load(source, List.of(), List.of(source + "：题库没有任何可用档位"), false);
        }
        return new Load(source, tiers, List.of(), false);
    }

    /** 逐档解析并收集全部问题（不提前中断，一次能看完所有错）。 */
    private static List<Tier> parse(JsonObject root, String source, List<String> errors) {
        List<Tier> tiers = new ArrayList<>();
        JsonElement rawTiers = root.get("tiers");
        if (rawTiers == null || !rawTiers.isJsonArray()) {
            errors.add(at(source, "根节点", "缺少 tiers 数组"));
            return tiers;
        }
        JsonArray array = rawTiers.getAsJsonArray();
        if (array.isEmpty()) {
            errors.add(at(source, "根节点", "tiers 为空，至少要有一档"));
            return tiers;
        }
        if (array.size() > MAX_TIERS) {
            errors.add(at(source, "根节点", "档位过多：" + array.size() + " > 上限 " + MAX_TIERS));
        }
        Map<String, String> seenIds = new LinkedHashMap<>();
        Map<String, String> seenQuestions = new LinkedHashMap<>();
        int total = 0;
        int previousMin = -1;
        for (int ti = 0; ti < array.size(); ti++) {
            String where = "档位 #" + ti;
            JsonElement element = array.get(ti);
            if (!element.isJsonObject()) {
                errors.add(at(source, where, "档位必须是 JSON 对象"));
                continue;
            }
            JsonObject tier = element.getAsJsonObject();
            String id = string(tier.get("id"));
            if (id == null) {
                errors.add(at(source, where, "id 必须是非空字符串"));
            } else if (id.trim().isEmpty()) {
                errors.add(at(source, where, "id 不能是空白字符串"));
            } else {
                where = "档位 #" + ti + "（id=" + id + "）";
                String other = seenIds.get(id);
                if (other != null) {
                    errors.add(at(source, where, "id 与 " + other + " 重复"));
                } else {
                    seenIds.put(id, where);
                }
            }
            String zh = string(tier.get("zh"));
            if (zh == null || zh.trim().isEmpty()) {
                errors.add(at(source, where, "zh 中文名必须是非空字符串"));
            }
            String en = string(tier.get("en"));
            if (en == null || en.trim().isEmpty()) {
                errors.add(at(source, where, "en 英文名必须是非空字符串"));
            }
            Integer minMerit = integer(tier.get("minMerit"));
            if (minMerit == null) {
                errors.add(at(source, where, "minMerit 必须是整数（不接受字符串 / 布尔 / 小数）"));
            } else {
                if (minMerit < 0) {
                    errors.add(at(source, where, "minMerit 不能为负：" + minMerit));
                }
                if (ti == 0 && minMerit != 0) {
                    errors.add(at(source, where, "第一档 minMerit 必须是 0，否则低功名玩家没有可考档位"));
                }
                if (ti > 0 && previousMin >= 0 && minMerit <= previousMin) {
                    errors.add(at(source, where, "minMerit 必须严格递增：" + minMerit + " 不大于上一档 " + previousMin));
                }
                previousMin = minMerit;
            }
            Integer merit = integer(tier.get("merit"));
            if (merit == null) {
                errors.add(at(source, where, "merit 必须是整数（不接受字符串 / 布尔 / 小数）"));
            } else if (merit <= 0) {
                errors.add(at(source, where, "merit 必须是正整数：" + merit));
            }
            JsonElement rawQuestions = tier.get("questions");
            if (rawQuestions == null || !rawQuestions.isJsonArray()) {
                errors.add(at(source, where, "缺少 questions 数组"));
                continue;
            }
            JsonArray questions = rawQuestions.getAsJsonArray();
            if (questions.size() < MIN_PER_TIER) {
                errors.add(at(source, where, "题目不足 " + MIN_PER_TIER + " 条：" + questions.size()));
            }
            if (questions.size() > MAX_PER_TIER) {
                errors.add(at(source, where, "题目过多：" + questions.size() + " > 上限 " + MAX_PER_TIER));
            }
            total += questions.size();
            List<Question> parsed = new ArrayList<>();
            for (int qi = 0; qi < questions.size(); qi++) {
                parseQuestion(questions.get(qi), source, where + " 题目 #" + qi, seenQuestions, parsed, errors);
            }
            tiers.add(new Tier(id == null ? "?" : id, zh == null ? "?" : zh, en == null ? "?" : en,
                    minMerit == null ? 0 : minMerit, merit == null ? 0 : merit, parsed));
        }
        if (total > MAX_TOTAL_QUESTIONS) {
            errors.add(at(source, "根节点", "题库总题数过多：" + total + " > 上限 " + MAX_TOTAL_QUESTIONS));
        }
        return tiers;
    }

    /** 单题校验：题干 / 三个选项 / 答案范围，任何一个不合法都只报错不修正。 */
    private static void parseQuestion(JsonElement element, String source, String where,
                                     Map<String, String> seenQuestions, List<Question> parsed, List<String> errors) {
        if (!element.isJsonObject()) {
            errors.add(at(source, where, "题目必须是 JSON 对象"));
            return;
        }
        JsonObject question = element.getAsJsonObject();
        String text = string(question.get("q"));
        boolean textOk = true;
        if (text == null) {
            errors.add(at(source, where, "题干必须是非空字符串"));
            textOk = false;
        } else if (text.trim().isEmpty()) {
            errors.add(at(source, where, "题干不能是空白字符串"));
            textOk = false;
        } else {
            if (text.length() > MAX_QUESTION_CHARS) {
                errors.add(at(source, where, "题干过长：" + text.length() + " 字 > 上限 " + MAX_QUESTION_CHARS));
                textOk = false;
            }
            String other = seenQuestions.get(text);
            if (other != null) {
                errors.add(at(source, where, "题干与 " + other + " 重复"));
                textOk = false;
            } else {
                seenQuestions.put(text, where);
            }
        }
        List<String> options = new ArrayList<>();
        JsonElement rawOptions = question.get("a");
        if (rawOptions == null || !rawOptions.isJsonArray()) {
            errors.add(at(source, where, "缺少 a 选项数组"));
        } else {
            JsonArray array = rawOptions.getAsJsonArray();
            if (array.size() < CHOICES) {
                errors.add(at(source, where, "选项不足 " + CHOICES + " 个：" + array.size()));
            } else if (array.size() > CHOICES) {
                errors.add(at(source, where, "选项超过 " + CHOICES + " 个：" + array.size() + "（禁止截断）"));
            }
            for (int oi = 0; oi < array.size(); oi++) {
                String option = string(array.get(oi));
                String oWhere = where + " 选项 #" + oi;
                if (option == null) {
                    errors.add(at(source, oWhere, "选项必须是非空字符串"));
                    continue;
                }
                if (option.trim().isEmpty()) {
                    errors.add(at(source, oWhere, "选项不能是空白字符串"));
                    continue;
                }
                if (option.length() > MAX_OPTION_CHARS) {
                    errors.add(at(source, oWhere, "选项过长：" + option.length() + " 字 > 上限 " + MAX_OPTION_CHARS));
                    continue;
                }
                if (options.contains(option)) {
                    errors.add(at(source, oWhere, "选项与本页其它选项重复：" + option));
                    continue;
                }
                options.add(option);
            }
        }
        Integer correct = integer(question.get("correct"));
        if (correct == null) {
            errors.add(at(source, where, "correct 必须是整数 " + MIN_CHOICE + ".." + MAX_CHOICE
                    + "（不接受字符串 / 布尔 / 小数）"));
        } else if (correct < MIN_CHOICE || correct > MAX_CHOICE) {
            errors.add(at(source, where, "correct 越界：" + correct + "，必须 " + MIN_CHOICE + ".." + MAX_CHOICE));
        }
        if (textOk && options.size() == CHOICES && correct != null
                && correct >= MIN_CHOICE && correct <= MAX_CHOICE) {
            parsed.add(new Question(text, options, correct));
        }
    }

    /** 只有 JSON 字符串才返回，其它类型（数字 / 布尔 / 对象 / 数组）返回 null。 */
    private static String string(JsonElement element) {
        if (element == null || !element.isJsonPrimitive()) {
            return null;
        }
        JsonPrimitive primitive = element.getAsJsonPrimitive();
        return primitive.isString() ? primitive.getAsString() : null;
    }

    /** 只有「真正的整数」才返回：拒绝布尔、字符串、小数、NaN 与越界值。 */
    private static Integer integer(JsonElement element) {
        if (element == null || !element.isJsonPrimitive()) {
            return null;
        }
        JsonPrimitive primitive = element.getAsJsonPrimitive();
        if (primitive.isBoolean() || primitive.isString() || !primitive.isNumber()) {
            return null;
        }
        double value = primitive.getAsDouble();
        if (Double.isNaN(value) || Double.isInfinite(value) || value != Math.rint(value)) {
            return null;
        }
        if (value < Integer.MIN_VALUE || value > Integer.MAX_VALUE) {
            return null;
        }
        return (int) value;
    }

    private static String at(String source, String where, String reason) {
        return source + "：" + where + "：" + reason;
    }

    /** 答案是否在 1..3。/ is the submitted choice legal. */
    public static boolean isChoice(int choice) {
        return choice >= MIN_CHOICE && choice <= MAX_CHOICE;
    }

    /** 按功名挑档：取门槛最高且已达标的一档（题库已保证第一档门槛为 0）。 */
    public static int tierFor(List<Tier> tiers, int merit) {
        int best = 0;
        for (int i = 0; i < tiers.size(); i++) {
            if (merit >= tiers.get(i).minMerit()) {
                best = i;
            }
        }
        return best;
    }

    /** 内置兜底题库自检（题数 / 选项 / 答案范围），问题写进 errors。 */
    public static void validateFallback(List<Tier> fallback, List<String> errors) {
        if (fallback == null || fallback.isEmpty()) {
            errors.add("内置兜底题库为空");
            return;
        }
        int total = 0;
        for (Tier tier : fallback) {
            for (Question question : tier.questions()) {
                total++;
                if (question.text() == null || question.text().trim().isEmpty()) {
                    errors.add("内置兜底题库 第 " + total + " 题题干为空");
                }
                if (question.options().size() != CHOICES) {
                    errors.add("内置兜底题库 第 " + total + " 题选项不是 " + CHOICES + " 个");
                } else if (question.options().stream().distinct().count() != (long) CHOICES) {
                    errors.add("内置兜底题库 第 " + total + " 题选项重复");
                }
                if (!isChoice(question.correct())) {
                    errors.add("内置兜底题库 第 " + total + " 题答案越界：" + question.correct());
                }
            }
        }
        if (total < FALLBACK_MIN_QUESTIONS) {
            errors.add("内置兜底题库少于 " + FALLBACK_MIN_QUESTIONS + " 题（当前 " + total + "）");
        }
    }
}
