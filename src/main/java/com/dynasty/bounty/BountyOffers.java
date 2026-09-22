package com.dynasty.bounty;

import com.dynasty.Dynasty;
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimplePreparableReloadListener;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.profiling.ProfilerFiller;

import java.io.BufferedReader;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 数据包加载：{@code data/<namespace>/bounty_offers/<id>.json}。
 *
 * 规则：
 *   * 每条定义独立校验，**坏定义只打印可定位日志并跳过**，绝不让服务器起不来；
 *   * 重载只替换「定义池」，不动玩家存档（已接委托的目标/奖励是快照，存在 SavedData 里）；
 *   * 委托 ID 默认取「命名空间:文件名」。
 */
public final class BountyOffers extends SimplePreparableReloadListener<Map<ResourceLocation, JsonElement>> {

    public static final String DIRECTORY = "bounty_offers";
    private static final Gson GSON = new Gson();

    private static volatile List<BountyModel.Offer> offers = List.of();
    private static volatile Map<String, BountyModel.Offer> byId = Map.of();

    public static List<BountyModel.Offer> all() {
        return offers;
    }

    public static BountyModel.Offer byId(String id) {
        return byId.get(id);
    }

    public static int size() {
        return offers.size();
    }

    @Override
    protected Map<ResourceLocation, JsonElement> prepare(ResourceManager manager, ProfilerFiller profiler) {
        Map<ResourceLocation, JsonElement> found = new HashMap<>();
        for (Map.Entry<ResourceLocation, Resource> entry
                : manager.listResources(DIRECTORY, path -> path.getPath().endsWith(".json")).entrySet()) {
            try (BufferedReader reader = entry.getValue().openAsReader()) {
                found.put(entry.getKey(), GSON.fromJson(reader, JsonElement.class));
            } catch (Exception error) {
                Dynasty.LOGGER.error("[bounty] 读不到委托定义 {}：{}", entry.getKey(), error.toString());
            }
        }
        return found;
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> found, ResourceManager manager, ProfilerFiller profiler) {
        List<BountyModel.Offer> loaded = new ArrayList<>();
        Map<String, BountyModel.Offer> index = new HashMap<>();
        List<String> problems = new ArrayList<>();
        for (Map.Entry<ResourceLocation, JsonElement> entry : found.entrySet()) {
            String where = entry.getKey().toString();
            try {
                if (!entry.getValue().isJsonObject()) {
                    problems.add(where + "：顶层必须是对象");
                    continue;
                }
                BountyModel.Offer offer = parse(entry.getKey(), entry.getValue().getAsJsonObject());
                String error = BountyRules.validate(offer);
                if (error != null) {
                    problems.add(where + "：" + error);
                    continue;
                }
                if (index.containsKey(offer.id)) {
                    problems.add(where + "：委托 ID 重复（" + offer.id + "）");
                    continue;
                }
                loaded.add(offer);
                index.put(offer.id, offer);
            } catch (RuntimeException error) {
                problems.add(where + "：解析失败 " + error);
            }
        }
        loaded.sort(Comparator.comparing(offer -> offer.id));
        offers = List.copyOf(loaded);
        byId = Map.copyOf(index);
        for (String problem : problems) {
            Dynasty.LOGGER.error("[bounty] 跳过一条委托定义 → {}", problem);
        }
        Dynasty.LOGGER.info("[bounty] 已加载 {} 条委托定义（跳过 {} 条）", offers.size(), problems.size());
    }

    private static BountyModel.Offer parse(ResourceLocation file, JsonObject json) {
        String path = file.getPath();
        String fileName = path.substring(path.lastIndexOf('/') + 1, path.length() - 5);
        String id = GsonHelper.getAsString(json, "id", file.getNamespace() + ":" + fileName);
        String shortId = id.substring(id.indexOf(':') + 1);
        BountyModel.Type type = BountyModel.Type.byName(GsonHelper.getAsString(json, "type"));
        BountyModel.TargetKind kind = BountyModel.TargetKind.byName(GsonHelper.getAsString(json, "target_kind"));
        String target = GsonHelper.getAsString(json, "target");
        int amount = GsonHelper.getAsInt(json, "amount", 1);
        int weight = GsonHelper.getAsInt(json, "weight", 10);
        String prerequisite = GsonHelper.getAsString(json, "prerequisite", null);
        String titleKey = GsonHelper.getAsString(json, "title", "dynasty.bounty." + shortId + ".title");
        String descKey = GsonHelper.getAsString(json, "description", "dynasty.bounty." + shortId + ".desc");
        BountyModel.Reward reward = parseReward(GsonHelper.getAsJsonObject(json, "reward"));
        return new BountyModel.Offer(id, type, titleKey, descKey, kind, target, amount, weight,
                prerequisite, reward);
    }

    private static BountyModel.Reward parseReward(JsonObject json) {
        int emeralds = GsonHelper.getAsInt(json, "emeralds", 0);
        int xp = GsonHelper.getAsInt(json, "experience", 0);
        List<BountyModel.Stack> supplies = new ArrayList<>();
        if (json.has("items")) {
            for (JsonElement element : GsonHelper.getAsJsonArray(json, "items")) {
                JsonObject stack = element.getAsJsonObject();
                supplies.add(new BountyModel.Stack(GsonHelper.getAsString(stack, "item"),
                        GsonHelper.getAsInt(stack, "count", 1)));
            }
        }
        return new BountyModel.Reward(emeralds, xp, supplies);
    }
}
