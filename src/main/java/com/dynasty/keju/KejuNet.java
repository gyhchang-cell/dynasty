package com.dynasty.keju;

import net.minecraftforge.network.NetworkDirection;

/**
 * 科举两种包的线协议契约（方向 + 长度上限，与 {@link KejuRules} 同源）。
 *
 * Open 包：一个 int（本次令牌）+ 四个字符串（题干 + 三个选项）
 * Answer 包：两个 int（本次令牌 + 选项 1..3）
 *
 * 字段数量、顺序、类型都不变；这里只做「方向必须匹配」与长度上限的判定，
 * 上限直接引用 {@link KejuRules} 的常量，避免网络层与题库校验各写一套数字。
 *
 * Wire contract: direction and length limits, both sourced from KejuRules.
 */
public final class KejuNet {

    private KejuNet() {
    }

    /** Open 包只允许服务端 → 客户端。/ OpenKejuPacket is server -> client only. */
    public static final NetworkDirection OPEN_DIRECTION = NetworkDirection.PLAY_TO_CLIENT;

    /** Answer 包只允许客户端 → 服务端。/ AnswerKejuPacket is client -> server only. */
    public static final NetworkDirection ANSWER_DIRECTION = NetworkDirection.PLAY_TO_SERVER;

    /** 题干在包里的字符上限。/ question limit on the wire. */
    public static final int MAX_QUESTION_CHARS = KejuRules.MAX_QUESTION_CHARS;

    /** 单个选项在包里的字符上限。/ option limit on the wire. */
    public static final int MAX_OPTION_CHARS = KejuRules.MAX_OPTION_CHARS;

    public static boolean acceptsOpen(NetworkDirection actual) {
        return actual == OPEN_DIRECTION;
    }

    public static boolean acceptsAnswer(NetworkDirection actual) {
        return actual == ANSWER_DIRECTION;
    }
}
