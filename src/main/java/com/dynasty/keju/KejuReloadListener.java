package com.dynasty.keju;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimplePreparableReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;

import java.io.BufferedReader;
import java.util.Optional;
import java.util.function.Consumer;

/**
 * 科举题库的数据包重载监听器（唯一的 Minecraft 胶水层）。
 *
 * {@code /reload} 与服务器启动时由 {@link KejuEvents} 挂到服务端数据重载事件上：
 * {@code prepare} 在工作线程读取并严格校验，{@code apply} 在主线程决定是否替换现役题库。
 * 校验失败只记日志、保留旧题库；不会破坏正在进行的答题会话，也不动奖励冷却。
 *
 * Datapack reload glue for the Keju bank: read + validate on the reload worker,
 * swap the active bank only when the whole new bank is valid.
 */
public final class KejuReloadListener extends SimplePreparableReloadListener<KejuRules.Load> {

    private final ResourceLocation bank;
    private final Consumer<KejuRules.Load> sink;

    public KejuReloadListener(ResourceLocation bank, Consumer<KejuRules.Load> sink) {
        this.bank = bank;
        this.sink = sink;
    }

    @Override
    protected KejuRules.Load prepare(ResourceManager manager, ProfilerFiller profiler) {
        return readBank(manager, bank);
    }

    @Override
    protected void apply(KejuRules.Load load, ResourceManager manager, ProfilerFiller profiler) {
        if (sink != null) {
            sink.accept(load);
        }
    }

    /**
     * 读取题库并严格校验：文件缺失返回 {@code missingFile} 结果，读取异常变成可读错误，
     * 两种情况都不会抛出到重载流程外。
     */
    public static KejuRules.Load readBank(ResourceManager manager, ResourceLocation id) {
        String source = "data/" + id.getNamespace() + "/" + id.getPath();
        if (manager == null) {
            return KejuRules.load(null, source);
        }
        Optional<Resource> resource = manager.getResource(id);
        if (resource.isEmpty()) {
            return KejuRules.load(null, source);
        }
        try (BufferedReader reader = resource.get().openAsReader()) {
            StringBuilder json = new StringBuilder();
            char[] buffer = new char[4096];
            int read;
            while ((read = reader.read(buffer)) >= 0) {
                json.append(buffer, 0, read);
            }
            return KejuRules.load(json.toString(), source);
        } catch (Exception error) {
            return KejuRules.readFailure(source, error);
        }
    }
}
