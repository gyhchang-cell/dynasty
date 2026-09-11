package com.dynasty;

import com.mojang.logging.LogUtils;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/**
 * 王朝模组主类：注册全部内容（方块、物品、装备、效果、药水、生物、结构、网络、命令）。
 * Dynasty main class: registers all content (blocks, items, gear, effects, potions, entities,
 * worldgen structures, networking and commands).
 */
@Mod(Dynasty.MODID)
public class Dynasty {

    /** 模组 ID。/ Mod id. */
    public static final String MODID = "dynasty";

    public static final Logger LOGGER = LogUtils.getLogger();

    public Dynasty(FMLJavaModLoadingContext context) {
        IEventBus modEventBus = context.getModEventBus();

        // 王朝全部内容 / all Dynasty content
        DynastyContent.register(modEventBus);
        DynastyCuriosSetup.register(modEventBus);

        LOGGER.info("[Dynasty] content registered under namespace '{}'", MODID);
    }
}
