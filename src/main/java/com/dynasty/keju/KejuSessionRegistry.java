package com.dynasty.keju;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.UUID;

/**
 * 每名玩家最多一个待答会话的注册表（纯逻辑，可单测）。
 *
 * 关键点：**先验证，再消费**。只有「令牌存在且匹配 + 选项在 1..3」的那次提交才会
 * 消费会话；没有会话、令牌过期、令牌不属于本玩家、选项非法都只是被拒绝，
 * 不会破坏当前仍然有效的题目。
 *
 * 令牌由服务端本进程的计数器发放（起始值随机），不再与题目下标挂钩，也不能反解。
 *
 * One-session-per-player registry: validate first, consume only on a fully legal
 * submission. Tokens come from a per-process counter, unrelated to question index.
 */
public final class KejuSessionRegistry {

    /** 一次提交的裁定结果。/ the verdict of one submission. */
    public enum Status {
        /** 合法提交，会话已被消费 / legal submission, session consumed */
        ACCEPTED,
        /** 该玩家没有待答题目 / no pending session */
        NO_SESSION,
        /** 令牌不对（旧令牌 / 别人的令牌 / 伪造）/ stale or foreign token */
        WRONG_TOKEN,
        /** 选项不在 1..3 / choice outside 1..3 */
        ILLEGAL_CHOICE
    }

    public record Submission(Status status, KejuSession session, boolean correct) {

        static Submission rejected(Status status) {
            return new Submission(status, null, false);
        }

        public boolean accepted() {
            return status == Status.ACCEPTED;
        }
    }

    private final Map<UUID, KejuSession> sessions = new HashMap<>();
    private int nextToken;

    public KejuSessionRegistry() {
        this(new Random().nextInt(1 << 20) + 1);
    }

    /**
     * 指定起始令牌（仅测试与确定性场景使用）。
     * 起始值会被规整到 1..2^30，保证 token 永不为 0 且呈现递增。
     */
    public KejuSessionRegistry(int firstToken) {
        this.nextToken = Math.floorMod(firstToken, 1 << 30) + 1;
    }

    /**
     * 开题：替换该玩家已有的会话（旧令牌立刻失效），返回新会话。
     * Opening a new exam replaces any previous session for that player.
     */
    public synchronized KejuSession open(UUID player, KejuRules.Tier tier, KejuRules.Question question, long now) {
        int token = nextToken++;
        KejuSession session = new KejuSession(token, player, tier.id(), tier.zh(), tier.merit(),
                question.text(), question.options(), question.correct(), now);
        sessions.put(player, session);
        return session;
    }

    /** 先验证再消费。/ validate first, consume only when everything is legal. */
    public synchronized Submission submit(UUID player, int token, int choice) {
        KejuSession session = sessions.get(player);
        if (session == null) {
            return Submission.rejected(Status.NO_SESSION);
        }
        if (!session.matches(token)) {
            return Submission.rejected(Status.WRONG_TOKEN);
        }
        if (!KejuRules.isChoice(choice)) {
            return Submission.rejected(Status.ILLEGAL_CHOICE);
        }
        sessions.remove(player);
        return new Submission(Status.ACCEPTED, session, session.isCorrect(choice));
    }

    /** 当前待答会话（不改动状态）。/ current session without consuming it. */
    public synchronized KejuSession peek(UUID player) {
        return sessions.get(player);
    }

    /** 丢弃该玩家的会话（关界面 / 断线 / 重开）。/ drop the session. */
    public synchronized KejuSession forget(UUID player) {
        return sessions.remove(player);
    }

    /** 清空全部会话（服务器关闭）。/ drop every session. */
    public synchronized void clear() {
        sessions.clear();
    }

    public synchronized int size() {
        return sessions.size();
    }

    /** 下一个将发放的令牌（仅供测试断言单调性）。/ next token, for tests. */
    public synchronized int peekNextToken() {
        return nextToken;
    }
}
