package com.dynasty.client;

import java.util.ArrayList;
import java.util.List;

/** 客户端缓存的已装备饰品 / cached equipped trinkets on the client. */
public final class ClientTrinkets {

    private ClientTrinkets() {
    }

    private static List<String> ids = new ArrayList<>();

    public static void set(List<String> newIds) {
        ids = new ArrayList<>(newIds);
    }

    public static boolean has(String id) {
        return ids.contains(id);
    }
}
