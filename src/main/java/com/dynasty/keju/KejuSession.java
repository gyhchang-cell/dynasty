package com.dynasty.keju;

import java.util.List;
import java.util.UUID;

/**
 * 一次答题会话的不可变快照。
 *
 * 开题时把「本次令牌 + 玩家 UUID + 档位奖励 + 题目与答案」一起固定下来，
 * 之后题库重载 / 重新排序 / 删题都不会改变这一题的判分与奖励。
 * 客户端只知道 {@code token}，拿不到 {@code correct} 与 {@code merit}。
 *
 * Immutable snapshot of one exam session: the token, the owner, the tier reward
 * and the question itself are frozen at open time.
 */
public record KejuSession(int token, UUID player, String tierId, String tierZh, int merit,
                          String question, List<String> options, int correct, long createdAt) {

    public KejuSession {
        options = List.copyOf(options);
    }

    /** 令牌是否属于本次会话。/ does the submitted token belong to this session. */
    public boolean matches(int candidate) {
        return token == candidate;
    }

    /** 提交的选项是否正确。/ is the submitted choice the right one. */
    public boolean isCorrect(int choice) {
        return choice == correct;
    }

    /** 正确答案文本（用于答错时反馈，取自快照而非题库）。 */
    public String correctOption() {
        return correct >= 1 && correct <= options.size() ? options.get(correct - 1) : "";
    }
}
