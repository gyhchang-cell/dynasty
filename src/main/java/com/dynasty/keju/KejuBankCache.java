package com.dynasty.keju;

import java.util.List;

/**
 * 当前生效的科举题库（纯逻辑）。
 *
 * 只有「整份校验通过」的新题库才会替换现役题库；校验失败时旧题库原样保留，
 * 首次加载（还没有任何有效题库）时由调用方装入内置七题兜底。
 *
 * Holds the active bank. A failing reload never replaces the working bank.
 */
public final class KejuBankCache {

    private static List<KejuRules.Tier> active = List.of();
    private static List<String> errors = List.of();
    private static String source = "";
    private static boolean fallback;
    private static long generation;

    private KejuBankCache() {
    }

    /** 装入新题库；校验失败返回 false 且不改变现役题库。 */
    public static synchronized boolean install(KejuRules.Load load) {
        if (load == null) {
            return false;
        }
        source = load.source() == null ? "" : load.source();
        if (!load.ok()) {
            errors = load.errors();
            return false;
        }
        active = load.tiers();
        errors = List.of();
        fallback = false;
        generation++;
        return true;
    }

    /** 装入内置兜底题库（仅在没有任何有效题库时使用）。 */
    public static synchronized void installFallback(List<KejuRules.Tier> tiers, String reason) {
        active = List.copyOf(tiers);
        errors = List.of(reason == null ? "使用内置兜底题库" : reason);
        fallback = true;
        generation++;
    }

    /** 当前现役题库（可能为空，表示还没加载过）。/ currently active bank. */
    public static List<KejuRules.Tier> active() {
        return active;
    }

    public static boolean loaded() {
        return !active.isEmpty();
    }

    public static boolean usingFallback() {
        return fallback;
    }

    public static String source() {
        return source;
    }

    public static List<String> errors() {
        return errors;
    }

    /** 每次成功装入递增，用于测试「新会话用新题库」。/ bumped on every successful install. */
    public static long generation() {
        return generation;
    }

    /** 服务器关闭时清空。/ cleared when the server stops. */
    public static synchronized void clear() {
        active = List.of();
        errors = List.of();
        source = "";
        fallback = false;
    }
}
